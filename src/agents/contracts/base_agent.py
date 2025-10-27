"""
智能体基类模块
定义所有智能体的基础接口和通用功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime

from src.core.domain.models import AgentState, CrewAgent, ConversationMessage
from src.core.services.interfaces import AgentService, LLMService
from src.shared.exceptions.exceptions import (
    AgentException, 
    StateTransitionError, 
    ConfigurationError,
    ValidationError
)
from src.shared.types.types import (
    JSONDict, 
    MessageCallback, 
    AgentConfig, 
    TaskResult
)
from src.shared.utils.helpers import generate_session_id


class AgentType(Enum):
    """智能体类型枚举"""
    SUPPLY_CHAIN = "supply_chain"
    UNIFIED = "unified"
    MANAGER = "manager"
    WORKER = "worker"


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        config: AgentConfig,
        llm_service: LLMService,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化智能体
        
        Args:
            agent_id: 智能体ID
            agent_type: 智能体类型
            config: 智能体配置
            llm_service: LLM服务
            logger: 日志记录器
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.llm_service = llm_service
        self.logger = logger or logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 状态管理
        self._state = AgentState.IDLE
        self._state_history: List[Dict[str, Any]] = []
        self._last_state_change = datetime.now()
        
        # 会话管理
        self._session_id = generate_session_id()
        self._conversation_history: List[ConversationMessage] = []
        
        # 任务管理
        self._current_task: Optional[str] = None
        self._task_results: Dict[str, TaskResult] = {}
        
        # 回调函数
        self._state_change_callbacks: List[MessageCallback] = []
        self._message_callbacks: List[MessageCallback] = []
        
        # 初始化智能体
        self._initialize()
    
    def _initialize(self) -> None:
        """初始化智能体"""
        try:
            self.logger.info(f"初始化智能体: {self.agent_id} (类型: {self.agent_type.value})")
            self._validate_config()
            self._setup_agent()
            self.logger.info(f"智能体 {self.agent_id} 初始化完成")
        except Exception as e:
            self.logger.error(f"智能体 {self.agent_id} 初始化失败: {str(e)}")
            raise AgentException(f"智能体初始化失败: {str(e)}")
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置"""
        pass
    
    @abstractmethod
    def _setup_agent(self) -> None:
        """设置智能体"""
        pass
    
    @abstractmethod
    async def process_message(self, message: str, context: Optional[JSONDict] = None) -> str:
        """
        处理消息
        
        Args:
            message: 输入消息
            context: 上下文信息
            
        Returns:
            处理后的响应消息
        """
        pass
    
    @abstractmethod
    async def execute_task(self, task: str, context: Optional[JSONDict] = None) -> TaskResult:
        """
        执行任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行结果
        """
        pass
    
    def get_state(self) -> AgentState:
        """获取当前状态"""
        return self._state
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """获取状态历史"""
        return self._state_history.copy()
    
    def get_session_id(self) -> str:
        """获取会话ID"""
        return self._session_id
    
    def get_conversation_history(self) -> List[ConversationMessage]:
        """获取对话历史"""
        return self._conversation_history.copy()
    
    def get_current_task(self) -> Optional[str]:
        """获取当前任务"""
        return self._current_task
    
    def get_task_results(self) -> Dict[str, TaskResult]:
        """获取任务结果"""
        return self._task_results.copy()
    
    def add_state_change_callback(self, callback: MessageCallback) -> None:
        """添加状态变化回调"""
        self._state_change_callbacks.append(callback)
    
    def add_message_callback(self, callback: MessageCallback) -> None:
        """添加消息回调"""
        self._message_callbacks.append(callback)
    
    def remove_state_change_callback(self, callback: MessageCallback) -> None:
        """移除状态变化回调"""
        if callback in self._state_change_callbacks:
            self._state_change_callbacks.remove(callback)
    
    def remove_message_callback(self, callback: MessageCallback) -> None:
        """移除消息回调"""
        if callback in self._message_callbacks:
            self._message_callbacks.remove(callback)
    
    async def set_state(self, new_state: AgentState) -> None:
        """
        设置状态
        
        Args:
            new_state: 新状态
        """
        if not self._can_transition_to(new_state):
            raise StateTransitionError(
                f"无法从状态 {self._state.value} 转换到 {new_state.value}"
            )
        
        old_state = self._state
        self._state = new_state
        self._last_state_change = datetime.now()
        
        # 记录状态变化
        state_change = {
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": self._last_state_change.isoformat(),
            "task": self._current_task
        }
        self._state_history.append(state_change)
        
        self.logger.info(f"智能体 {self.agent_id} 状态变化: {old_state.value} -> {new_state.value}")
        
        # 调用状态变化回调
        for callback in self._state_change_callbacks:
            try:
                await callback(state_change)
            except Exception as e:
                self.logger.error(f"状态变化回调执行失败: {str(e)}")
    
    def _can_transition_to(self, new_state: AgentState) -> bool:
        """检查是否可以转换到新状态"""
        # 基本状态转换规则
        valid_transitions = {
            AgentState.IDLE: [AgentState.PROCESSING, AgentState.ERROR],
            AgentState.PROCESSING: [AgentState.IDLE, AgentState.WAITING, AgentState.ERROR],
            AgentState.WAITING: [AgentState.PROCESSING, AgentState.IDLE, AgentState.ERROR],
            AgentState.ERROR: [AgentState.IDLE]
        }
        
        return new_state in valid_transitions.get(self._state, [])
    
    def _add_conversation_message(self, role: str, content: str, metadata: Optional[JSONDict] = None) -> None:
        """添加对话消息"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self._conversation_history.append(message)
        
        # 调用消息回调
        for callback in self._message_callbacks:
            try:
                asyncio.create_task(callback(message.dict()))
            except Exception as e:
                self.logger.error(f"消息回调执行失败: {str(e)}")
    
    def _set_current_task(self, task: str) -> None:
        """设置当前任务"""
        self._current_task = task
        self.logger.debug(f"智能体 {self.agent_id} 设置当前任务: {task}")
    
    def _add_task_result(self, task_id: str, result: TaskResult) -> None:
        """添加任务结果"""
        self._task_results[task_id] = result
        self.logger.debug(f"智能体 {self.agent_id} 添加任务结果: {task_id}")
    
    async def reset(self) -> None:
        """重置智能体状态"""
        await self.set_state(AgentState.IDLE)
        self._current_task = None
        self._conversation_history.clear()
        self._session_id = generate_session_id()
        self.logger.info(f"智能体 {self.agent_id} 已重置")
    
    def to_dict(self) -> JSONDict:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "state": self._state.value,
            "session_id": self._session_id,
            "current_task": self._current_task,
            "last_state_change": self._last_state_change.isoformat(),
            "config": self.config
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value}, state={self._state.value})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


class CrewAIAgent(BaseAgent):
    """CrewAI智能体基类"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        config: AgentConfig,
        llm_service: LLMService,
        crew_agent: Optional[CrewAgent] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化CrewAI智能体
        
        Args:
            agent_id: 智能体ID
            agent_type: 智能体类型
            config: 智能体配置
            llm_service: LLM服务
            crew_agent: CrewAI智能体配置
            logger: 日志记录器
        """
        self.crew_agent = crew_agent
        super().__init__(agent_id, agent_type, config, llm_service, logger)
    
    def _setup_agent(self) -> None:
        """设置CrewAI智能体"""
        if self.crew_agent is None:
            # 如果没有提供CrewAI智能体配置，使用默认配置创建
            from crewai import Agent as CrewAIAgentImpl
            
            self.crew_agent = CrewAgent(
                role=self.config.get("role", "助手"),
                goal=self.config.get("goal", "帮助用户完成任务"),
                backstory=self.config.get("backstory", "我是一个专业的助手"),
                verbose=self.config.get("verbose", True),
                allow_delegation=self.config.get("allow_delegation", False),
                tools=self.config.get("tools", [])
            )
            
            # 创建CrewAI智能体实例
            self.crewai_agent = CrewAIAgentImpl(
                role=self.crew_agent.role,
                goal=self.crew_agent.goal,
                backstory=self.crew_agent.backstory,
                verbose=self.crew_agent.verbose,
                allow_delegation=self.crew_agent.allow_delegation,
                tools=self.crew_agent.tools,
                llm=self.llm_service.get_llm()
            )
        else:
            # 使用提供的CrewAI智能体配置创建
            from crewai import Agent as CrewAIAgentImpl
            
            self.crewai_agent = CrewAIAgentImpl(
                role=self.crew_agent.role,
                goal=self.crew_agent.goal,
                backstory=self.crew_agent.backstory,
                verbose=self.crew_agent.verbose,
                allow_delegation=self.crew_agent.allow_delegation,
                tools=self.crew_agent.tools,
                llm=self.llm_service.get_llm()
            )
    
    async def process_message(self, message: str, context: Optional[JSONDict] = None) -> str:
        """处理消息"""
        await self.set_state(AgentState.PROCESSING)
        
        try:
            # 添加用户消息到对话历史
            self._add_conversation_message("user", message, context)
            
            # 使用CrewAI智能体处理消息
            from crewai import Task
            
            task = Task(
                description=message,
                agent=self.crewai_agent,
                expected_output="回答用户的问题"
            )
            
            # 执行任务
            result = task.execute()
            
            # 添加助手回复到对话历史
            self._add_conversation_message("assistant", result)
            
            await self.set_state(AgentState.IDLE)
            return result
            
        except Exception as e:
            self.logger.error(f"处理消息失败: {str(e)}")
            await self.set_state(AgentState.ERROR)
            raise AgentException(f"处理消息失败: {str(e)}")
    
    async def execute_task(self, task: str, context: Optional[JSONDict] = None) -> TaskResult:
        """执行任务"""
        await self.set_state(AgentState.PROCESSING)
        
        try:
            self._set_current_task(task)
            
            # 使用CrewAI智能体执行任务
            from crewai import Task
            
            crew_task = Task(
                description=task,
                agent=self.crewai_agent,
                expected_output="任务执行结果"
            )
            
            # 执行任务
            result = crew_task.execute()
            
            # 创建任务结果
            task_result = TaskResult(
                task_id=generate_session_id(),
                status="completed",
                result=result,
                metadata=context or {}
            )
            
            self._add_task_result(task_result.task_id, task_result)
            
            await self.set_state(AgentState.IDLE)
            return task_result
            
        except Exception as e:
            self.logger.error(f"执行任务失败: {str(e)}")
            await self.set_state(AgentState.ERROR)
            
            error_result = TaskResult(
                task_id=generate_session_id(),
                status="failed",
                error=str(e),
                metadata=context or {}
            )
            
            self._add_task_result(error_result.task_id, error_result)
            return error_result
    
    def _validate_config(self) -> None:
        """验证配置"""
        required_fields = ["role", "goal"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"缺少必需的配置字段: {field}")
    
    def get_crew_agent(self) -> CrewAgent:
        """获取CrewAI智能体配置"""
        return self.crew_agent
    
    def get_crewai_agent(self):
        """获取CrewAI智能体实例"""
        return self.crewai_agent