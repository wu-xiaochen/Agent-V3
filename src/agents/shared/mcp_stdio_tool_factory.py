"""
MCP Stdio工具工厂
用于创建MCP Stdio工具实例
"""

import os
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

from .mcp_stdio_tool import MCPStdioTool
from .tool_config_models import MCPStdioToolConfig

if TYPE_CHECKING:
    from langchain.tools import BaseTool


class EnvironmentVariableResolver:
    """环境变量解析器"""
    
    @staticmethod
    def resolve(value):
        """递归解析值中的环境变量"""
        if isinstance(value, str):
            # 匹配 ${VAR_NAME} 格式的环境变量
            pattern = r'\$\{([^}]+)\}'
            
            def replace_var(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))  # 如果环境变量不存在，保持原样
            
            return re.sub(pattern, replace_var, value)
        elif isinstance(value, dict):
            return {k: EnvironmentVariableResolver.resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [EnvironmentVariableResolver.resolve(item) for item in value]
        else:
            return value


class BaseToolFactory(ABC):
    """工具工厂基类"""
    
    @abstractmethod
    def create_tool(self, config: MCPStdioToolConfig) -> "BaseTool":
        """创建工具实例"""
        pass


class MCPStdioToolFactory(BaseToolFactory):
    """MCP Stdio工具工厂"""
    
    def create_tool(self, config: MCPStdioToolConfig) -> "BaseTool":
        """创建MCP Stdio工具实例"""
        # 解析配置中的环境变量
        # Pydantic v2兼容性：优先使用model_dump()，回退到dict()
        if hasattr(config, 'model_dump'):
            config_dict = config.model_dump()
        else:
            config_dict = config.dict()
        
        resolved_config = EnvironmentVariableResolver.resolve(config_dict)
        
        # 创建MCP Stdio工具实例
        return MCPStdioTool.from_config(resolved_config)