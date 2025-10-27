"""
会话服务

提供会话管理的核心业务逻辑。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..domain.session_model import SessionModel, SessionStatus, SessionContext
from ...infrastructure.database import DatabaseService
from ...infrastructure.cache import CacheService


class SessionService:
    """会话服务类"""
    
    def __init__(self, db_service: DatabaseService, cache_service: CacheService):
        self.db_service = db_service
        self.cache_service = cache_service
        self._sessions_cache_key = "sessions"
    
    async def create_session(
        self,
        title: str,
        user_id: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> SessionModel:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        context = SessionContext(
            user_id=user_id,
            agent_id=agent_id,
            metadata=metadata or {},
            variables=variables or {}
        )
        
        session = SessionModel(
            id=session_id,
            title=title,
            context=context
        )
        
        # 保存到数据库
        await self.db_service.save("sessions", session_id, session.__dict__)
        
        # 更新缓存
        await self._update_sessions_cache()
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[SessionModel]:
        """获取会话"""
        # 先从缓存获取
        sessions_cache = await self.cache_service.get(self._sessions_cache_key)
        if sessions_cache and session_id in sessions_cache:
            session_data = sessions_cache[session_id]
            return self._dict_to_session_model(session_data)
        
        # 从数据库获取
        session_data = await self.db_service.get("sessions", session_id)
        if not session_data:
            return None
            
        return self._dict_to_session_model(session_data)
    
    async def get_sessions_by_user(self, user_id: str) -> List[SessionModel]:
        """根据用户ID获取会话列表"""
        sessions = await self.get_all_sessions()
        return [session for session in sessions if session.context.user_id == user_id]
    
    async def get_sessions_by_agent(self, agent_id: str) -> List[SessionModel]:
        """根据智能体ID获取会话列表"""
        sessions = await self.get_all_sessions()
        return [session for session in sessions if session.context.agent_id == agent_id]
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[SessionModel]:
        """获取活跃会话"""
        sessions = await self.get_all_sessions()
        active_sessions = [session for session in sessions if session.status == SessionStatus.ACTIVE]
        
        if user_id:
            active_sessions = [session for session in active_sessions if session.context.user_id == user_id]
        
        return active_sessions
    
    async def get_all_sessions(self) -> List[SessionModel]:
        """获取所有会话"""
        # 先从缓存获取
        sessions_cache = await self.cache_service.get(self._sessions_cache_key)
        if sessions_cache:
            return [self._dict_to_session_model(session_data) for session_data in sessions_cache.values()]
        
        # 从数据库获取
        sessions_data = await self.db_service.query("sessions", {})
        sessions = [self._dict_to_session_model(session_data) for session_data in sessions_data]
        
        # 更新缓存
        sessions_dict = {session.id: session.__dict__ for session in sessions}
        await self.cache_service.set(self._sessions_cache_key, sessions_dict, expire=3600)
        
        return sessions
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[SessionModel]:
        """更新会话"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # 更新字段
        if "title" in updates:
            session.title = updates["title"]
        if "context" in updates:
            session.update_context(updates["context"])
        
        # 更新数据库
        await self.db_service.update("sessions", session_id, session.__dict__)
        
        # 更新缓存
        await self._update_sessions_cache()
        
        return session
    
    async def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        session = await self.get_session(session_id)
        if not session or session.status == SessionStatus.CLOSED:
            return False
        
        session.close()
        
        # 更新数据库
        await self.db_service.update("sessions", session_id, session.__dict__)
        
        # 更新缓存
        await self._update_sessions_cache()
        
        return True
    
    async def activate_session(self, session_id: str) -> bool:
        """激活会话"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.activate()
        
        # 更新数据库
        await self.db_service.update("sessions", session_id, session.__dict__)
        
        # 更新缓存
        await self._update_sessions_cache()
        
        return True
    
    async def deactivate_session(self, session_id: str) -> bool:
        """停用会话"""
        session = await self.get_session(session_id)
        if not session or session.status != SessionStatus.ACTIVE:
            return False
        
        session.deactivate()
        
        # 更新数据库
        await self.db_service.update("sessions", session_id, session.__dict__)
        
        # 更新缓存
        await self._update_sessions_cache()
        
        return True
    
    async def update_session_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """更新会话上下文"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.update_context(context_updates)
        
        # 更新数据库
        await self.db_service.update("sessions", session_id, session.__dict__)
        
        # 更新缓存
        await self._update_sessions_cache()
        
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        # 从数据库删除
        result = await self.db_service.delete("sessions", session_id)
        
        if result:
            # 更新缓存
            await self._update_sessions_cache()
        
        return result
    
    async def _update_sessions_cache(self) -> None:
        """更新会话缓存"""
        sessions_data = await self.db_service.query("sessions", {})
        sessions_dict = {session_data["id"]: session_data for session_data in sessions_data}
        await self.cache_service.set(self._sessions_cache_key, sessions_dict, expire=3600)
    
    def _dict_to_session_model(self, session_data: Dict[str, Any]) -> SessionModel:
        """将字典转换为SessionModel对象"""
        # 处理枚举类型
        if "status" in session_data and isinstance(session_data["status"], str):
            session_data["status"] = SessionStatus(session_data["status"])
        
        # 处理上下文对象
        if "context" in session_data and session_data["context"]:
            context_data = session_data["context"]
            session_data["context"] = SessionContext(
                user_id=context_data["user_id"],
                agent_id=context_data["agent_id"],
                metadata=context_data.get("metadata", {}),
                variables=context_data.get("variables", {})
            )
        
        # 处理日期时间
        for field in ["created_at", "updated_at", "last_activity"]:
            if field in session_data and session_data[field] and isinstance(session_data[field], str):
                session_data[field] = datetime.fromisoformat(session_data[field])
        
        return SessionModel(**session_data)