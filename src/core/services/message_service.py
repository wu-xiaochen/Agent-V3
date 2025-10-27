"""
消息服务

提供消息管理的核心业务逻辑。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..domain.message_model import MessageModel, MessageType, MessageStatus, MessageMetadata
from ...infrastructure.database import DatabaseService
from ...infrastructure.cache import CacheService


class MessageService:
    """消息服务类"""
    
    def __init__(self, db_service: DatabaseService, cache_service: CacheService):
        self.db_service = db_service
        self.cache_service = cache_service
        self._messages_cache_key = "messages"
    
    async def create_message(
        self,
        session_id: str,
        content: str,
        message_type: MessageType,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageModel:
        """创建新消息"""
        message_id = str(uuid.uuid4())
        
        # 创建元数据对象
        message_metadata = None
        if metadata:
            message_metadata = MessageMetadata(
                model=metadata.get("model"),
                temperature=metadata.get("temperature"),
                tokens=metadata.get("tokens"),
                cost=metadata.get("cost"),
                latency=metadata.get("latency"),
                tools_used=metadata.get("tools_used", []),
                custom_data=metadata.get("custom_data", {})
            )
        
        message = MessageModel(
            id=message_id,
            session_id=session_id,
            content=content,
            type=message_type,
            metadata=message_metadata,
            parent_id=parent_id
        )
        
        # 保存到数据库
        await self.db_service.save("messages", message_id, message.__dict__)
        
        # 更新缓存
        await self._update_messages_cache()
        
        return message
    
    async def get_message(self, message_id: str) -> Optional[MessageModel]:
        """获取消息"""
        # 先从缓存获取
        messages_cache = await self.cache_service.get(self._messages_cache_key)
        if messages_cache and message_id in messages_cache:
            message_data = messages_cache[message_id]
            return self._dict_to_message_model(message_data)
        
        # 从数据库获取
        message_data = await self.db_service.get("messages", message_id)
        if not message_data:
            return None
            
        return self._dict_to_message_model(message_data)
    
    async def get_messages_by_session(self, session_id: str) -> List[MessageModel]:
        """根据会话ID获取消息列表"""
        messages = await self.get_all_messages()
        return [message for message in messages if message.session_id == session_id]
    
    async def get_conversation(
        self, 
        session_id: str, 
        limit: int = 50,
        include_system: bool = True
    ) -> List[MessageModel]:
        """获取对话历史"""
        messages = await self.get_messages_by_session(session_id)
        
        # 过滤系统消息（如果需要）
        if not include_system:
            messages = [msg for msg in messages if not msg.is_system_message()]
        
        # 按时间排序
        messages.sort(key=lambda msg: msg.created_at)
        
        # 限制数量
        if len(messages) > limit:
            messages = messages[-limit:]
        
        return messages
    
    async def get_message_thread(self, message_id: str) -> List[MessageModel]:
        """获取消息线程（回复链）"""
        message = await self.get_message(message_id)
        if not message:
            return []
        
        # 获取同一会话的所有消息
        session_messages = await self.get_messages_by_session(message.session_id)
        
        # 构建消息线程
        thread = []
        current_id = message_id
        
        while current_id:
            current_msg = next((msg for msg in session_messages if msg.id == current_id), None)
            if not current_msg:
                break
                
            thread.insert(0, current_msg)  # 插入到开头，保持时间顺序
            current_id = current_msg.parent_id
        
        return thread
    
    async def get_all_messages(self) -> List[MessageModel]:
        """获取所有消息"""
        # 先从缓存获取
        messages_cache = await self.cache_service.get(self._messages_cache_key)
        if messages_cache:
            return [self._dict_to_message_model(message_data) for message_data in messages_cache.values()]
        
        # 从数据库获取
        messages_data = await self.db_service.query("messages", {})
        messages = [self._dict_to_message_model(message_data) for message_data in messages_data]
        
        # 更新缓存
        messages_dict = {message.id: message.__dict__ for message in messages}
        await self.cache_service.set(self._messages_cache_key, messages_dict, expire=3600)
        
        return messages
    
    async def update_message(self, message_id: str, updates: Dict[str, Any]) -> Optional[MessageModel]:
        """更新消息"""
        message = await self.get_message(message_id)
        if not message:
            return None
        
        # 更新字段
        if "content" in updates:
            message.content = updates["content"]
        if "metadata" in updates:
            message.update_metadata(updates["metadata"])
        
        # 更新数据库
        await self.db_service.update("messages", message_id, message.__dict__)
        
        # 更新缓存
        await self._update_messages_cache()
        
        return message
    
    async def deliver_message(self, message_id: str) -> bool:
        """标记消息已送达"""
        message = await self.get_message(message_id)
        if not message:
            return False
        
        message.deliver()
        
        # 更新数据库
        await self.db_service.update("messages", message_id, message.__dict__)
        
        # 更新缓存
        await self._update_messages_cache()
        
        return True
    
    async def read_message(self, message_id: str) -> bool:
        """标记消息已读"""
        message = await self.get_message(message_id)
        if not message:
            return False
        
        message.read()
        
        # 更新数据库
        await self.db_service.update("messages", message_id, message.__dict__)
        
        # 更新缓存
        await self._update_messages_cache()
        
        return True
    
    async def fail_message(self, message_id: str) -> bool:
        """标记消息发送失败"""
        message = await self.get_message(message_id)
        if not message:
            return False
        
        message.fail()
        
        # 更新数据库
        await self.db_service.update("messages", message_id, message.__dict__)
        
        # 更新缓存
        await self._update_messages_cache()
        
        return True
    
    async def delete_message(self, message_id: str) -> bool:
        """删除消息"""
        # 从数据库删除
        result = await self.db_service.delete("messages", message_id)
        
        if result:
            # 更新缓存
            await self._update_messages_cache()
        
        return result
    
    async def delete_messages_by_session(self, session_id: str) -> int:
        """删除会话的所有消息"""
        messages = await self.get_messages_by_session(session_id)
        deleted_count = 0
        
        for message in messages:
            if await self.delete_message(message.id):
                deleted_count += 1
        
        return deleted_count
    
    async def _update_messages_cache(self) -> None:
        """更新消息缓存"""
        messages_data = await self.db_service.query("messages", {})
        messages_dict = {message_data["id"]: message_data for message_data in messages_data}
        await self.cache_service.set(self._messages_cache_key, messages_dict, expire=3600)
    
    def _dict_to_message_model(self, message_data: Dict[str, Any]) -> MessageModel:
        """将字典转换为MessageModel对象"""
        # 处理枚举类型
        if "type" in message_data and isinstance(message_data["type"], str):
            message_data["type"] = MessageType(message_data["type"])
        if "status" in message_data and isinstance(message_data["status"], str):
            message_data["status"] = MessageStatus(message_data["status"])
        
        # 处理元数据对象
        if "metadata" in message_data and message_data["metadata"]:
            metadata_data = message_data["metadata"]
            message_data["metadata"] = MessageMetadata(
                model=metadata_data.get("model"),
                temperature=metadata_data.get("temperature"),
                tokens=metadata_data.get("tokens"),
                cost=metadata_data.get("cost"),
                latency=metadata_data.get("latency"),
                tools_used=metadata_data.get("tools_used", []),
                custom_data=metadata_data.get("custom_data", {})
            )
        
        # 处理日期时间
        for field in ["created_at", "updated_at"]:
            if field in message_data and message_data[field] and isinstance(message_data[field], str):
                message_data[field] = datetime.fromisoformat(message_data[field])
        
        return MessageModel(**message_data)