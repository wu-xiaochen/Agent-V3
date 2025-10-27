"""
核心服务定义
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from src.core.domain.models import (
    AgentState, 
    CrewConfig, 
    ConversationMessage, 
    BusinessPlan,
    SupplyChainContext
)


class AgentService(ABC):
    """智能体服务接口"""
    
    @abstractmethod
    async def process_message(self, message: str, session_id: str) -> str:
        """处理消息"""
        pass
    
    @abstractmethod
    async def get_state(self, session_id: str) -> AgentState:
        """获取当前状态"""
        pass
    
    @abstractmethod
    async def set_state(self, session_id: str, state: AgentState) -> None:
        """设置状态"""
        pass
    
    @abstractmethod
    async def get_conversation_history(self, session_id: str) -> List[ConversationMessage]:
        """获取对话历史"""
        pass
    
    @abstractmethod
    async def stream_response(self, message: str, session_id: str) -> AsyncGenerator[str, None]:
        """流式响应"""
        pass


class CrewAIService(ABC):
    """CrewAI服务接口"""
    
    @abstractmethod
    async def generate_crew_config(self, context: Dict[str, Any]) -> CrewConfig:
        """生成CrewAI配置"""
        pass
    
    @abstractmethod
    async def execute_crew(self, config: CrewConfig) -> Dict[str, Any]:
        """执行CrewAI任务"""
        pass
    
    @abstractmethod
    async def validate_config(self, config: CrewConfig) -> bool:
        """验证配置"""
        pass


class BusinessPlanService(ABC):
    """业务计划服务接口"""
    
    @abstractmethod
    async def create_plan(self, context: SupplyChainContext) -> BusinessPlan:
        """创建业务计划"""
        pass
    
    @abstractmethod
    async def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> BusinessPlan:
        """更新业务计划"""
        pass
    
    @abstractmethod
    async def get_plan(self, plan_id: str) -> Optional[BusinessPlan]:
        """获取业务计划"""
        pass
    
    @abstractmethod
    async def list_plans(self, filters: Dict[str, Any]) -> List[BusinessPlan]:
        """列出业务计划"""
        pass


class StorageService(ABC):
    """存储服务接口"""
    
    @abstractmethod
    async def save_message(self, session_id: str, message: ConversationMessage) -> None:
        """保存消息"""
        pass
    
    @abstractmethod
    async def get_messages(self, session_id: str, limit: int = 100) -> List[ConversationMessage]:
        """获取消息"""
        pass
    
    @abstractmethod
    async def clear_session(self, session_id: str) -> None:
        """清除会话"""
        pass
    
    @abstractmethod
    async def save_state(self, session_id: str, state: AgentState) -> None:
        """保存状态"""
        pass
    
    @abstractmethod
    async def get_state(self, session_id: str) -> Optional[AgentState]:
        """获取状态"""
        pass


class LLMService(ABC):
    """LLM服务接口"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_structured_text(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成结构化文本"""
        pass
    
    @abstractmethod
    async def stream_text(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        pass