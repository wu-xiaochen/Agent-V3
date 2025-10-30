"""
智能体模块
包含智能体实现、工厂和管理器

注意：为避免循环导入，请直接从子模块导入，例如：
from src.agents.unified.unified_agent import UnifiedAgent
"""

# 🆕 注释掉顶层导入以避免循环依赖
# from .contracts.base_agent import BaseAgent, CrewAIAgent, AgentType
# from .factories.agent_factory import AgentFactory, CrewAIAgentFactory, AgentManager
# from .supply_chain.supply_chain_agent import SupplyChainAgent
# from .unified.unified_agent import UnifiedAgent

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