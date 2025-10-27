"""
智能体领域模型

定义智能体的核心属性和行为。
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


class AgentType(Enum):
    """智能体类型枚举"""
    SUPPLY_CHAIN = "supply_chain"
    UNIFIED = "unified"
    CUSTOMER_SERVICE = "customer_service"
    DATA_ANALYST = "data_analyst"
    CONTENT_CREATOR = "content_creator"


class AgentStatus(Enum):
    """智能体状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    INITIALIZING = "initializing"
    TERMINATING = "terminating"


@dataclass
class AgentCapability:
    """智能体能力定义"""
    name: str
    description: str
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentModel:
    """智能体领域模型"""
    id: str
    name: str
    type: AgentType
    description: str
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[AgentCapability] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    
    def update_status(self, new_status: AgentStatus) -> None:
        """更新智能体状态"""
        self.status = new_status
        self.updated_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_capability(self, capability: AgentCapability) -> None:
        """添加智能体能力"""
        self.capabilities.append(capability)
        self.updated_at = datetime.now()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """更新智能体配置"""
        self.config.update(new_config)
        self.updated_at = datetime.now()
    
    def get_capability(self, name: str) -> Optional[AgentCapability]:
        """根据名称获取能力"""
        for capability in self.capabilities:
            if capability.name == name:
                return capability
        return None
    
    def is_capability_enabled(self, name: str) -> bool:
        """检查能力是否启用"""
        capability = self.get_capability(name)
        return capability.enabled if capability else False