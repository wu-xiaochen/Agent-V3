"""
工具配置数据模型
定义工具配置的数据结构和验证逻辑
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ToolType(str, Enum):
    """工具类型枚举"""
    BUILTIN = "builtin"
    API = "api"
    MCP = "mcp"
    MCP_STDIO = "mcp_stdio"


class AuthType(str, Enum):
    """认证类型枚举"""
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    NONE = "none"


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str  # string, integer, number, boolean, object, array
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    enum: Optional[List[str]] = None  # 用于枚举值


class AuthConfig(BaseModel):
    """认证配置"""
    type: AuthType = AuthType.NONE
    token: Optional[str] = None  # Bearer token
    username: Optional[str] = None  # Basic auth username
    password: Optional[str] = None  # Basic auth password
    key: Optional[str] = None  # API key
    additional_headers: Optional[Dict[str, str]] = None  # 额外的认证头


class ToolConfig(BaseModel):
    """工具配置基类"""
    name: str = Field(..., description="工具名称，必须唯一")
    type: ToolType = Field(..., description="工具类型")
    enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="工具描述")
    config: Dict[str, Any] = Field(default_factory=dict, description="工具特定配置")


class BuiltinToolConfig(ToolConfig):
    """内置工具配置"""
    type: ToolType = ToolType.BUILTIN


class APIToolConfig(ToolConfig):
    """API工具配置"""
    type: ToolType = ToolType.API
    endpoint: str = Field(..., description="API端点URL")
    method: str = Field("GET", description="HTTP方法")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP请求头")
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict, description="API参数定义")
    response_mapping: Dict[str, str] = Field(default_factory=dict, description="响应映射")
    timeout: int = Field(30, description="请求超时时间(秒)")
    retry_count: int = Field(0, description="重试次数")
    retry_delay: float = Field(1.0, description="重试延迟(秒)")
    auth: Optional[AuthConfig] = Field(None, description="认证配置")

    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if v.upper() not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")
        return v.upper()


class MCPToolConfig(ToolConfig):
    """MCP工具配置"""
    type: ToolType = ToolType.MCP
    server_url: str = Field(..., description="MCP服务器URL")
    server_name: str = Field(..., description="MCP服务器名称")
    tool_name: str = Field(..., description="MCP工具名称")
    timeout: int = Field(30, description="请求超时时间(秒)")
    auth: Optional[AuthConfig] = Field(None, description="认证配置")
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict, description="工具参数定义")
    response_mapping: Dict[str, str] = Field(default_factory=dict, description="响应映射")


class MCPStdioToolConfig(ToolConfig):
    """MCP Stdio工具配置"""
    type: ToolType = ToolType.MCP_STDIO
    command: str = Field(..., description="启动MCP服务器的命令")
    args: List[str] = Field(default_factory=list, description="命令参数")
    env: Dict[str, str] = Field(default_factory=dict, description="环境变量")
    timeout: int = Field(30, description="请求超时时间(秒)")
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict, description="工具参数定义")


class ToolGroup(BaseModel):
    """工具组定义"""
    name: str = Field(..., description="工具组名称，必须唯一")
    description: Optional[str] = Field(None, description="工具组描述")
    tools: List[str] = Field(..., description="工具名称列表")


class AgentToolMapping(BaseModel):
    """智能体工具映射"""
    agent_type: str = Field(..., description="智能体类型")
    tool_groups: List[str] = Field(..., description="分配给该智能体的工具组列表")


class ToolsConfiguration(BaseModel):
    """工具配置完整模型"""
    version: str = Field("1.0", description="配置版本")
    description: Optional[str] = Field(None, description="配置描述")
    tools: List[Union[BuiltinToolConfig, APIToolConfig, MCPToolConfig, MCPStdioToolConfig]] = Field(..., description="工具定义列表")
    tool_groups: List[ToolGroup] = Field(default_factory=list, description="工具组列表")
    agent_tool_mapping: Dict[str, List[str]] = Field(default_factory=dict, description="智能体到工具组的映射")

    @validator('tools')
    def validate_tool_names_unique(cls, v):
        names = [tool.name for tool in v]
        if len(names) != len(set(names)):
            raise ValueError("Tool names must be unique")
        return v

    @validator('tool_groups')
    def validate_tool_group_names_unique(cls, v):
        names = [group.name for group in v]
        if len(names) != len(set(names)):
            raise ValueError("Tool group names must be unique")
        return v

    def get_tool_by_name(self, name: str) -> Optional[Union[BuiltinToolConfig, APIToolConfig, MCPToolConfig, MCPStdioToolConfig]]:
        """根据名称获取工具配置"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_tool_group_by_name(self, name: str) -> Optional[ToolGroup]:
        """根据名称获取工具组"""
        for group in self.tool_groups:
            if group.name == name:
                return group
        return None

    def get_tools_for_agent(self, agent_type: str) -> List[Union[BuiltinToolConfig, APIToolConfig, MCPToolConfig, MCPStdioToolConfig]]:
        """获取指定智能体类型的工具列表"""
        # 获取智能体对应的工具组名称列表
        group_names = self.agent_tool_mapping.get(agent_type, self.agent_tool_mapping.get("default", []))
        
        # 收集所有工具名称
        tool_names = []
        for group_name in group_names:
            group = self.get_tool_group_by_name(group_name)
            if group:
                tool_names.extend(group.tools)
        
        # 去重并获取工具配置
        unique_tool_names = list(set(tool_names))
        tools = []
        for name in unique_tool_names:
            tool = self.get_tool_by_name(name)
            if tool and tool.enabled:
                tools.append(tool)
        
        return tools

    def get_enabled_tools(self) -> List[Union[BuiltinToolConfig, APIToolConfig, MCPToolConfig, MCPStdioToolConfig]]:
        """获取所有启用的工具"""
        return [tool for tool in self.tools if tool.enabled]