"""
Agent配置数据模型

用于管理系统中所有Agent的配置信息
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentConfig(BaseModel):
    """Agent配置模型"""
    id: str = Field(..., description="Agent唯一ID")
    name: str = Field(..., description="Agent名称")
    description: str = Field(default="", description="Agent描述")
    system_prompt: str = Field(..., description="系统提示词")
    model: str = Field(default="gpt-4", description="使用的模型")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, description="最大token数")
    tools: List[str] = Field(default_factory=list, description="可用工具列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentConfigCreate(BaseModel):
    """创建Agent配置模型"""
    name: str = Field(..., min_length=1, description="Agent名称")
    description: str = Field(default="", description="Agent描述")
    system_prompt: str = Field(..., min_length=1, description="系统提示词")
    model: str = Field(default="gpt-4", description="使用的模型")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, description="最大token数")
    tools: List[str] = Field(default_factory=list, description="可用工具列表")


class AgentConfigUpdate(BaseModel):
    """更新Agent配置模型"""
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    tools: Optional[List[str]] = None


class AgentConfigResponse(BaseModel):
    """Agent配置响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    agent: Optional[AgentConfig] = Field(default=None, description="Agent配置")
    agents: Optional[List[AgentConfig]] = Field(default=None, description="Agent配置列表")
    total: int = Field(default=0, description="总数")

