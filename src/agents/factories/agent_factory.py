"""
智能体工厂模块
用于创建和管理智能体实例
"""

from typing import Dict, Any, Optional, Type, List
import logging
from abc import ABC, abstractmethod

from src.agents.contracts.base_agent import BaseAgent, CrewAIAgent, AgentType
from src.core.domain.models import CrewAgent, CrewConfig
from src.core.services.interfaces import LLMService
from src.shared.exceptions.exceptions import (
    AgentException, 
    ConfigurationError,
    ValidationError
)
from src.shared.types.types import AgentConfig
from src.config.config_loader import config_loader
from src.agents.unified.unified_agent import UnifiedAgent
from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent


class AgentFactory(ABC):
    """智能体工厂抽象基类"""
    
    @abstractmethod
    def create_agent(
        self,
        agent_type: AgentType,
        agent_id: str,
        config: Optional[AgentConfig] = None,
        **kwargs
    ) -> BaseAgent:
        """
        创建智能体实例
        
        Args:
            agent_type: 智能体类型
            agent_id: 智能体ID
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            智能体实例
        """
        pass
    
    @abstractmethod
    def get_supported_agent_types(self) -> List[AgentType]:
        """获取支持的智能体类型"""
        pass


class CrewAIAgentFactory(AgentFactory):
    """CrewAI智能体工厂"""
    
    def __init__(
        self,
        llm_service: LLMService,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化CrewAI智能体工厂
        
        Args:
            llm_service: LLM服务
            logger: 日志记录器
        """
        self.llm_service = llm_service
        self.logger = logger or logging.getLogger(__name__)
        
        # 注册智能体类型
        self._agent_types: Dict[AgentType, Type[BaseAgent]] = {
            AgentType.SUPPLY_CHAIN: self._create_supply_chain_agent,
            AgentType.UNIFIED: self._create_unified_agent,
            AgentType.MANAGER: self._create_manager_agent,
            AgentType.WORKER: self._create_worker_agent
        }
    
    def create_agent(
        self,
        agent_type: AgentType,
        agent_id: str,
        config: Optional[AgentConfig] = None,
        **kwargs
    ) -> BaseAgent:
        """
        创建智能体实例
        
        Args:
            agent_type: 智能体类型
            agent_id: 智能体ID
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            智能体实例
        """
        if agent_type not in self._agent_types:
            raise AgentException(f"不支持的智能体类型: {agent_type.value}")
        
        # 如果没有提供配置，从配置加载器获取
        if config is None:
            config = self._get_agent_config(agent_type)
        
        # 创建智能体
        agent_creator = self._agent_types[agent_type]
        return agent_creator(agent_id, config, **kwargs)
    
    def get_supported_agent_types(self) -> List[AgentType]:
        """获取支持的智能体类型"""
        return list(self._agent_types.keys())
    
    def _get_agent_config(self, agent_type: AgentType) -> AgentConfig:
        """
        获取智能体配置
        
        Args:
            agent_type: 智能体类型
            
        Returns:
            智能体配置
        """
        agents_config = config_loader.get_agents_config()
        
        if agent_type == AgentType.SUPPLY_CHAIN:
            return agents_config.get("supply_chain", {})
        elif agent_type == AgentType.UNIFIED:
            return agents_config.get("unified", {})
        else:
            # 默认配置
            return agents_config.get("default", {
                "role": "助手",
                "goal": "帮助用户完成任务",
                "backstory": "我是一个专业的助手",
                "verbose": True,
                "allow_delegation": False
            })
    
    def _create_supply_chain_agent(
        self,
        agent_id: str,
        config: AgentConfig,
        **kwargs
    ) -> BaseAgent:
        """
        创建供应链智能体
        
        Args:
            agent_id: 智能体ID
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            供应链智能体实例
        """
        return SupplyChainAgent(
            agent_id=agent_id,
            config=config,
            llm_service=self.llm_service,
            logger=self.logger,
            **kwargs
        )
    
    def _create_unified_agent(
        self,
        agent_id: str,
        config: AgentConfig,
        **kwargs
    ) -> BaseAgent:
        """
        创建统一智能体
        
        Args:
            agent_id: 智能体ID
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            统一智能体实例
        """
        return UnifiedAgent(
            agent_id=agent_id,
            config=config,
            llm_service=self.llm_service,
            logger=self.logger,
            **kwargs
        )
    
    def _create_manager_agent(
        self,
        agent_id: str,
        config: AgentConfig,
        **kwargs
    ) -> BaseAgent:
        """
        创建管理智能体
        
        Args:
            agent_id: 智能体ID
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            管理智能体实例
        """
        # 创建CrewAI智能体配置
        crew_agent = CrewAgent(
            role=config.get("role", "项目经理"),
            goal=config.get("goal", "协调团队成员完成任务"),
            backstory=config.get("backstory", "我是一个经验丰富的项目经理，擅长协调团队资源"),
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", True),
            tools=config.get("tools", [])
        )
        
        return CrewAIAgent(
            agent_id=agent_id,
            agent_type=AgentType.MANAGER,
            config=config,
            llm_service=self.llm_service,
            crew_agent=crew_agent,
            logger=self.logger
        )
    
    def _create_worker_agent(
        self,
        agent_id: str,
        config: AgentConfig,
        **kwargs
    ) -> BaseAgent:
        """
        创建工作智能体
        
        Args:
            agent_id: 智能体ID
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            工作智能体实例
        """
        # 创建CrewAI智能体配置
        crew_agent = CrewAgent(
            role=config.get("role", "专业助手"),
            goal=config.get("goal", "完成分配的任务"),
            backstory=config.get("backstory", "我是一个专业的助手，专注于完成特定任务"),
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
            tools=config.get("tools", [])
        )
        
        return CrewAIAgent(
            agent_id=agent_id,
            agent_type=AgentType.WORKER,
            config=config,
            llm_service=self.llm_service,
            crew_agent=crew_agent,
            logger=self.logger
        )
    
    def register_agent_type(
        self,
        agent_type: AgentType,
        creator_func: callable
    ) -> None:
        """
        注册新的智能体类型
        
        Args:
            agent_type: 智能体类型
            creator_func: 创建函数
        """
        self._agent_types[agent_type] = creator_func
        self.logger.info(f"注册智能体类型: {agent_type.value}")
    
    def unregister_agent_type(self, agent_type: AgentType) -> None:
        """
        注销智能体类型
        
        Args:
            agent_type: 智能体类型
        """
        if agent_type in self._agent_types:
            del self._agent_types[agent_type]
            self.logger.info(f"注销智能体类型: {agent_type.value}")
        else:
            self.logger.warning(f"尝试注销不存在的智能体类型: {agent_type.value}")


class AgentManager:
    """智能体管理器"""
    
    def __init__(
        self,
        agent_factory: AgentFactory,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化智能体管理器
        
        Args:
            agent_factory: 智能体工厂
            logger: 日志记录器
        """
        self.agent_factory = agent_factory
        self.logger = logger or logging.getLogger(__name__)
        
        # 智能体实例存储
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, AgentType] = {}
    
    def create_agent(
        self,
        agent_type: AgentType,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        **kwargs
    ) -> BaseAgent:
        """
        创建智能体
        
        Args:
            agent_type: 智能体类型
            agent_id: 智能体ID，如果不提供则自动生成
            config: 智能体配置
            **kwargs: 其他参数
            
        Returns:
            智能体实例
        """
        if agent_id is None:
            from src.shared.utils.helpers import generate_session_id
            agent_id = generate_session_id()
        
        if agent_id in self._agents:
            raise AgentException(f"智能体ID已存在: {agent_id}")
        
        # 创建智能体
        agent = self.agent_factory.create_agent(
            agent_type=agent_type,
            agent_id=agent_id,
            config=config,
            **kwargs
        )
        
        # 存储智能体
        self._agents[agent_id] = agent
        self._agent_types[agent_id] = agent_type
        
        self.logger.info(f"创建智能体: {agent_id} (类型: {agent_type.value})")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        获取智能体
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            智能体实例，如果不存在则返回None
        """
        return self._agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """
        根据类型获取智能体列表
        
        Args:
            agent_type: 智能体类型
            
        Returns:
            智能体列表
        """
        return [
            agent for agent_id, agent in self._agents.items()
            if self._agent_types.get(agent_id) == agent_type
        ]
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        移除智能体
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            是否成功移除
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            del self._agent_types[agent_id]
            self.logger.info(f"移除智能体: {agent_id}")
            return True
        return False
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """获取所有智能体"""
        return self._agents.copy()
    
    def get_agent_count(self) -> int:
        """获取智能体数量"""
        return len(self._agents)
    
    def get_agent_count_by_type(self, agent_type: AgentType) -> int:
        """
        根据类型获取智能体数量
        
        Args:
            agent_type: 智能体类型
            
        Returns:
            智能体数量
        """
        return len(self.get_agents_by_type(agent_type))
    
    def clear_all_agents(self) -> None:
        """清除所有智能体"""
        self._agents.clear()
        self._agent_types.clear()
        self.logger.info("清除所有智能体")
    
    def get_supported_agent_types(self) -> List[AgentType]:
        """获取支持的智能体类型"""
        return self.agent_factory.get_supported_agent_types()
    
    def create_crew(
        self,
        manager_id: Optional[str] = None,
        worker_ids: Optional[List[str]] = None,
        manager_config: Optional[AgentConfig] = None,
        worker_config: Optional[AgentConfig] = None,
        crew_config: Optional[CrewConfig] = None
    ) -> Dict[str, Any]:
        """
        创建Crew团队
        
        Args:
            manager_id: 管理智能体ID
            worker_ids: 工作智能体ID列表
            manager_config: 管理智能体配置
            worker_config: 工作智能体配置
            crew_config: Crew配置
            
        Returns:
            包含管理智能体、工作智能体和Crew实例的字典
        """
        # 创建管理智能体
        manager = self.create_agent(
            agent_type=AgentType.MANAGER,
            agent_id=manager_id,
            config=manager_config
        )
        
        # 创建工作智能体
        workers = []
        if worker_ids is None:
            worker_ids = []
        
        for i, worker_id in enumerate(worker_ids):
            worker = self.create_agent(
                agent_type=AgentType.WORKER,
                agent_id=worker_id,
                config=worker_config
            )
            workers.append(worker)
        
        # 创建Crew实例
        from crewai import Crew
        
        crew_agents = [manager.get_crewai_agent()] + [worker.get_crewai_agent() for worker in workers]
        
        crew = Crew(
            agents=crew_agents,
            verbose=crew_config.verbose if crew_config else True,
            process=crew_config.process if crew_config else "hierarchical",
            manager_llm=self.agent_factory.llm_service.get_llm()
        )
        
        return {
            "manager": manager,
            "workers": workers,
            "crew": crew
        }