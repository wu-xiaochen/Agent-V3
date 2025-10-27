"""
消息领域模型

定义智能体消息的核心属性和行为。
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


class MessageType(Enum):
    """消息类型枚举"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"


class MessageStatus(Enum):
    """消息状态枚举"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


@dataclass
class MessageMetadata:
    """消息元数据"""
    model: Optional[str] = None
    temperature: Optional[float] = None
    tokens: Optional[int] = None
    cost: Optional[float] = None
    latency: Optional[float] = None
    tools_used: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageModel:
    """消息领域模型"""
    id: str
    session_id: str
    content: str
    type: MessageType
    status: MessageStatus = MessageStatus.SENT
    metadata: Optional[MessageMetadata] = None
    parent_id: Optional[str] = None  # 用于消息回复链
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def deliver(self) -> None:
        """标记消息已送达"""
        self.status = MessageStatus.DELIVERED
        self.updated_at = datetime.now()
    
    def read(self) -> None:
        """标记消息已读"""
        self.status = MessageStatus.READ
        self.updated_at = datetime.now()
    
    def fail(self) -> None:
        """标记消息发送失败"""
        self.status = MessageStatus.FAILED
        self.updated_at = datetime.now()
    
    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """更新消息元数据"""
        if not self.metadata:
            self.metadata = MessageMetadata()
        
        if "model" in new_metadata:
            self.metadata.model = new_metadata["model"]
        if "temperature" in new_metadata:
            self.metadata.temperature = new_metadata["temperature"]
        if "tokens" in new_metadata:
            self.metadata.tokens = new_metadata["tokens"]
        if "cost" in new_metadata:
            self.metadata.cost = new_metadata["cost"]
        if "latency" in new_metadata:
            self.metadata.latency = new_metadata["latency"]
        if "tools_used" in new_metadata:
            self.metadata.tools_used.extend(new_metadata["tools_used"])
        if "custom_data" in new_metadata:
            self.metadata.custom_data.update(new_metadata["custom_data"])
        
        self.updated_at = datetime.now()
    
    def set_parent(self, parent_id: str) -> None:
        """设置父消息ID（用于回复链）"""
        self.parent_id = parent_id
        self.updated_at = datetime.now()
    
    def is_from_user(self) -> bool:
        """判断是否来自用户"""
        return self.type == MessageType.USER
    
    def is_from_agent(self) -> bool:
        """判断是否来自智能体"""
        return self.type == MessageType.AGENT
    
    def is_system_message(self) -> bool:
        """判断是否为系统消息"""
        return self.type == MessageType.SYSTEM
    
    def is_tool_message(self) -> bool:
        """判断是否为工具消息"""
        return self.type == MessageType.TOOL