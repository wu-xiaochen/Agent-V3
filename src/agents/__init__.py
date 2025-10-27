"""
智能体模块
包含智能体实现、工厂和管理器
"""

from .contracts.base_agent import BaseAgent, CrewAIAgent, AgentType
from .factories.agent_factory import AgentFactory, CrewAIAgentFactory, AgentManager
from .supply_chain.supply_chain_agent import SupplyChainAgent
from .unified.unified_agent import UnifiedAgent

# 导出主要类和接口
__all__ = [
    "BaseAgent",
    "CrewAIAgent", 
    "AgentType",
    "AgentFactory",
    "CrewAIAgentFactory",
    "AgentManager",
    "SupplyChainAgent",
    "UnifiedAgent"
]