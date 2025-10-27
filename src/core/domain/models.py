"""
领域模型定义
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AgentState(str, Enum):
    """智能体状态枚举"""
    INITIAL = "INITIAL"
    PLANNING = "PLANNING"
    CONFIRMATION = "CONFIRMATION"
    CREWAI_GENERATION = "CREWAI_GENERATION"
    GUIDANCE = "GUIDANCE"
    EXECUTION = "EXECUTION"
    COMPLETED = "COMPLETED"


class CrewAgent(BaseModel):
    """CrewAI智能体定义"""
    id: str = Field(description="智能体ID")
    name: str = Field(description="智能体名称")
    role: str = Field(description="智能体角色")
    goal: str = Field(description="智能体目标")
    backstory: str = Field(description="智能体背景故事")
    tools: List[str] = Field(default_factory=list, description="智能体工具列表")
    llm: str = Field(default="gpt-4", description="使用的LLM模型")


class CrewTask(BaseModel):
    """CrewAI任务定义"""
    id: str = Field(description="任务ID")
    name: str = Field(description="任务名称")
    description: str = Field(description="任务描述")
    agent_id: str = Field(description="执行任务的智能体ID")
    expected_output: str = Field(description="预期输出")
    dependencies: List[str] = Field(default_factory=list, description="任务依赖")


class CrewConfig(BaseModel):
    """CrewAI配置"""
    id: str = Field(description="配置ID")
    name: str = Field(description="配置名称")
    description: str = Field(description="配置描述")
    agents: List[CrewAgent] = Field(description="智能体列表")
    tasks: List[CrewTask] = Field(description="任务列表")
    process: str = Field(default="sequential", description="执行流程")
    manager_llm: str = Field(default="gpt-4", description="管理器LLM")


class ConversationMessage(BaseModel):
    """对话消息模型"""
    role: str = Field(description="消息角色，如user、assistant")
    content: str = Field(description="消息内容")
    timestamp: Optional[str] = Field(None, description="消息时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="消息元数据")


class BusinessPlan(BaseModel):
    """业务计划模型"""
    id: str = Field(description="计划ID")
    title: str = Field(description="计划标题")
    description: str = Field(description="计划描述")
    domain: str = Field(description="业务领域")
    objectives: List[str] = Field(description="目标列表")
    steps: List[str] = Field(description="执行步骤")
    resources: List[str] = Field(description="所需资源")
    timeline: str = Field(description="时间线")
    success_metrics: List[str] = Field(description="成功指标")


class SupplyChainContext(BaseModel):
    """供应链上下文模型"""
    id: str = Field(description="上下文ID")
    business_type: str = Field(description="业务类型")
    scale: str = Field(description="业务规模")
    region: str = Field(description="业务区域")
    current_challenges: List[str] = Field(description="当前挑战")
    goals: List[str] = Field(description="业务目标")
    constraints: List[str] = Field(description="约束条件")
    stakeholders: List[str] = Field(description="利益相关者")