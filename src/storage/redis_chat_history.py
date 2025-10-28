"""
Redis 缓存对话存储系统

这个模块实现了基于 Redis 的对话历史存储，替代原有的内存存储方式。
支持持久化存储、分布式访问和会话管理。
"""

import json
import redis
from typing import List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
import logging

logger = logging.getLogger(__name__)


class RedisChatMessageHistory(ChatMessageHistory):
    """
    基于 Redis 的聊天消息历史记录类
    
    扩展了 LangChain 的 ChatMessageHistory，使用 Redis 作为后端存储
    """
    
    def __init__(
        self,
        session_id: str,
        redis_url: str = "redis://localhost:6379/0",
        ttl: int = 86400,  # 默认24小时过期
        prefix: str = "chat_history:",
        **kwargs
    ):
        """
        初始化 Redis 聊天消息历史记录
        
        Args:
            session_id: 会话ID
            redis_url: Redis 连接URL
            ttl: 过期时间（秒）
            prefix: Redis键前缀
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        # 使用 object.__setattr__ 避免 Pydantic 验证错误
        object.__setattr__(self, 'session_id', session_id)
        object.__setattr__(self, 'redis_key', f"{prefix}{session_id}")
        
        try:
            redis_client = redis.from_url(redis_url)
            # 测试连接
            redis_client.ping()
            logger.info(f"成功连接到Redis: {redis_url}")
            object.__setattr__(self, 'redis_client', redis_client)
        except Exception as e:
            logger.error(f"连接Redis失败: {e}")
            raise ConnectionError(f"无法连接到Redis: {e}")
        
        object.__setattr__(self, 'ttl', ttl)
        self._load_messages()
    
    def _load_messages(self):
        """从Redis加载消息历史"""
        try:
            data = self.redis_client.get(self.redis_key)
            if data:
                messages_data = json.loads(data)
                self.messages = [
                    self._message_from_dict(msg) for msg in messages_data
                ]
                logger.info(f"从Redis加载了 {len(self.messages)} 条消息")
            else:
                self.messages = []
                logger.info(f"会话 {self.session_id} 无历史消息，创建新会话")
        except Exception as e:
            logger.error(f"从Redis加载消息失败: {e}")
            self.messages = []
    
    def _save_messages(self):
        """保存消息到Redis"""
        try:
            messages_data = [
                self._message_to_dict(msg) for msg in self.messages
            ]
            self.redis_client.set(
                self.redis_key,
                json.dumps(messages_data),
                ex=self.ttl
            )
            logger.debug(f"保存了 {len(self.messages)} 条消息到Redis")
        except Exception as e:
            logger.error(f"保存消息到Redis失败: {e}")
    
    def _message_to_dict(self, message: BaseMessage) -> Dict[str, Any]:
        """将消息对象转换为字典"""
        if isinstance(message, HumanMessage):
            return {"type": "human", "content": message.content}
        elif isinstance(message, AIMessage):
            return {"type": "ai", "content": message.content}
        else:
            # 其他类型的消息
            return {
                "type": message.__class__.__name__,
                "content": message.content,
                "additional_kwargs": getattr(message, "additional_kwargs", {})
            }
    
    def _message_from_dict(self, data: Dict[str, Any]) -> BaseMessage:
        """从字典创建消息对象"""
        msg_type = data.get("type", "human")
        content = data.get("content", "")
        
        if msg_type == "human":
            return HumanMessage(content=content)
        elif msg_type == "ai":
            return AIMessage(content=content)
        else:
            # 其他类型的消息，返回AI消息作为默认
            return AIMessage(content=content)
    
    def add_message(self, message: BaseMessage) -> None:
        """添加消息并保存到Redis"""
        super().add_message(message)
        self._save_messages()
    
    def clear(self) -> None:
        """清除消息历史"""
        super().clear()
        try:
            self.redis_client.delete(self.redis_key)
            logger.info(f"已清除会话 {self.session_id} 的消息历史")
        except Exception as e:
            logger.error(f"清除Redis消息失败: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        try:
            ttl = self.redis_client.ttl(self.redis_key)
            return {
                "session_id": self.session_id,
                "message_count": len(self.messages),
                "ttl_seconds": ttl,
                "redis_key": self.redis_key
            }
        except Exception as e:
            logger.error(f"获取会话信息失败: {e}")
            return {"error": str(e)}


class RedisConversationStore:
    """
    Redis 对话存储管理器
    
    提供更高级的对话管理功能，包括会话列表、会话清理等
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        prefix: str = "chat_history:",
        default_ttl: int = 86400
    ):
        """
        初始化 Redis 对话存储管理器
        
        Args:
            redis_url: Redis 连接URL
            prefix: Redis键前缀
            default_ttl: 默认过期时间（秒）
        """
        self.redis_url = redis_url
        self.prefix = prefix
        self.default_ttl = default_ttl
        
        try:
            self.redis_client = redis.from_url(redis_url)
            # 测试连接
            self.redis_client.ping()
            logger.info(f"成功连接到Redis: {redis_url}")
        except Exception as e:
            logger.error(f"连接Redis失败: {e}")
            raise ConnectionError(f"无法连接到Redis: {e}")
    
    def get_history(self, session_id: str, ttl: Optional[int] = None) -> RedisChatMessageHistory:
        """
        获取指定会话的消息历史
        
        Args:
            session_id: 会话ID
            ttl: 过期时间（秒），如果为None则使用默认值
            
        Returns:
            RedisChatMessageHistory 对象
        """
        if ttl is None:
            ttl = self.default_ttl
            
        return RedisChatMessageHistory(
            session_id=session_id,
            redis_url=self.redis_url,
            ttl=ttl,
            prefix=self.prefix
        )
    
    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            session_ids = [
                key.decode('utf-8').replace(self.prefix, '') 
                for key in keys
            ]
            return session_ids
        except Exception as e:
            logger.error(f"列出会话失败: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """删除指定会话"""
        try:
            redis_key = f"{self.prefix}{session_id}"
            result = self.redis_client.delete(redis_key)
            return result > 0
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    def clear_all_sessions(self) -> int:
        """清除所有会话"""
        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"清除了 {result} 个会话")
                return result
            return 0
        except Exception as e:
            logger.error(f"清除所有会话失败: {e}")
            return 0
    
    def get_session_count(self) -> int:
        """获取会话总数"""
        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            return len(keys)
        except Exception as e:
            logger.error(f"获取会话总数失败: {e}")
            return 0