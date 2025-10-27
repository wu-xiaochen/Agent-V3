"""
会话领域模型

定义智能体会话的核心属性和行为。
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


class SessionStatus(Enum):
    """会话状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"


@dataclass
class SessionContext:
    """会话上下文"""
    user_id: str
    agent_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionModel:
    """会话领域模型"""
    id: str
    title: str
    context: SessionContext
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def update_activity(self) -> None:
        """更新最后活动时间"""
        self.last_activity = datetime.now()
        self.updated_at = datetime.now()
    
    def close(self) -> None:
        """关闭会话"""
        self.status = SessionStatus.CLOSED
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """激活会话"""
        self.status = SessionStatus.ACTIVE
        self.update_activity()
    
    def deactivate(self) -> None:
        """停用会话"""
        self.status = SessionStatus.INACTIVE
        self.updated_at = datetime.now()
    
    def update_context(self, new_context: Dict[str, Any]) -> None:
        """更新会话上下文"""
        if "metadata" in new_context:
            self.context.metadata.update(new_context["metadata"])
        if "variables" in new_context:
            self.context.variables.update(new_context["variables"])
        self.update_activity()
    
    def get_context_variable(self, key: str, default: Any = None) -> Any:
        """获取上下文变量"""
        return self.context.variables.get(key, default)
    
    def set_context_variable(self, key: str, value: Any) -> None:
        """设置上下文变量"""
        self.context.variables[key] = value
        self.update_activity()