"""
工具配置数据模型

用于管理系统中所有工具的配置信息
"""
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ToolConfig(BaseModel):
    """单个工具配置模型"""
    tool_id: str = Field(..., description="工具唯一ID")
    name: str = Field(..., description="工具名称")
    description: str = Field(default="", description="工具描述")
    enabled: bool = Field(default=True, description="是否启用")
    mode: Literal["API", "MCP"] = Field(default="API", description="工具模式")
    config: Dict[str, Any] = Field(default_factory=dict, description="工具配置参数")
    updated_at: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolConfigList(BaseModel):
    """工具配置列表"""
    tools: List[ToolConfig] = Field(default_factory=list, description="工具列表")
    total: int = Field(default=0, description="工具总数")
    
    
class ToolConfigUpdate(BaseModel):
    """工具配置更新模型"""
    enabled: bool | None = None
    mode: Literal["API", "MCP"] | None = None
    config: Dict[str, Any] | None = None
    description: str | None = None


class ToolConfigResponse(BaseModel):
    """工具配置响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    tool: ToolConfig | None = Field(default=None, description="工具配置")
    tools: List[ToolConfig] | None = Field(default=None, description="工具配置列表")

