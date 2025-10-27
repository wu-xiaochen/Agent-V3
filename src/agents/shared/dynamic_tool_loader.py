"""
动态工具加载器
支持从JSON配置文件加载和实例化各种类型的工具
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Union, Type, TYPE_CHECKING
from pathlib import Path
from abc import ABC, abstractmethod

from .tool_config_models import (
    ToolsConfiguration, 
    ToolType, 
    BuiltinToolConfig, 
    APIToolConfig, 
    MCPToolConfig,
    AuthType
)

# 使用TYPE_CHECKING避免循环导入
if TYPE_CHECKING:
    from .tools import BaseTool
else:
    # 运行时也需要BaseTool类型引用，从langchain导入
    from langchain.tools import BaseTool


class ToolLoaderError(Exception):
    """工具加载错误"""
    pass


class EnvironmentVariableResolver:
    """环境变量解析器"""
    
    @staticmethod
    def resolve(value: Any) -> Any:
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
    def create_tool(self, config: Union[BuiltinToolConfig, APIToolConfig, MCPToolConfig]) -> BaseTool:
        """创建工具实例"""
        pass


class BuiltinToolFactory(BaseToolFactory):
    """内置工具工厂"""
    
    def create_tool(self, config: BuiltinToolConfig) -> "BaseTool":
        """创建内置工具实例"""
        # 延迟导入以避免循环导入
        from .tools import get_builtin_tool_class
        
        tool_class = get_builtin_tool_class(config.name)
        if not tool_class:
            raise ToolLoaderError(f"Unknown builtin tool: {config.name}")
        
        # 解析配置中的环境变量
        resolved_config = EnvironmentVariableResolver.resolve(config.config)
        
        # 创建工具实例
        return tool_class(**resolved_config)


class APIToolFactory(BaseToolFactory):
    """API工具工厂"""
    
    def create_tool(self, config: APIToolConfig) -> "BaseTool":
        """创建API工具实例"""
        # 延迟导入以避免循环导入
        from .api_tool import APITool
        
        # 解析配置中的环境变量
        resolved_config = EnvironmentVariableResolver.resolve(config.dict())
        
        # 创建API工具实例
        return APITool.from_config(resolved_config)


class MCPToolFactory(BaseToolFactory):
    """MCP工具工厂"""
    
    def create_tool(self, config: MCPToolConfig) -> "BaseTool":
        """创建MCP工具实例"""
        # 延迟导入以避免循环导入
        from .mcp_tool import MCPTool
        
        # 解析配置中的环境变量
        resolved_config = EnvironmentVariableResolver.resolve(config.dict())
        
        # 创建MCP工具实例
        return MCPTool.from_config(resolved_config)


class DynamicToolLoader:
    """动态工具加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self._factories: Dict[ToolType, BaseToolFactory] = {
            ToolType.BUILTIN: BuiltinToolFactory(),
            ToolType.API: APIToolFactory(),
            ToolType.MCP: MCPToolFactory()
        }
        self._config_cache: Dict[str, ToolsConfiguration] = {}
        self._default_config_path = config_path
    
    def load_config_from_file(self, config_path: str) -> ToolsConfiguration:
        """从文件加载工具配置"""
        # 检查缓存
        if config_path in self._config_cache:
            return self._config_cache[config_path]
        
        # 检查文件是否存在
        if not os.path.exists(config_path):
            raise ToolLoaderError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 解析环境变量
            resolved_config = EnvironmentVariableResolver.resolve(config_data)
            
            # 验证并创建配置对象
            config = ToolsConfiguration(**resolved_config)
            
            # 缓存配置
            self._config_cache[config_path] = config
            
            return config
        except json.JSONDecodeError as e:
            raise ToolLoaderError(f"Invalid JSON in config file {config_path}: {str(e)}")
        except Exception as e:
            raise ToolLoaderError(f"Error loading config from {config_path}: {str(e)}")
    
    def load_tools_from_config(self, config_path: str, agent_type: Optional[str] = None) -> List["BaseTool"]:
        """从配置文件加载工具"""
        config = self.load_config_from_file(config_path)
        
        # 如果指定了智能体类型，只加载该智能体的工具
        if agent_type:
            tool_configs = config.get_tools_for_agent(agent_type)
        else:
            tool_configs = config.get_enabled_tools()
        
        # 创建工具实例
        tools = []
        for tool_config in tool_configs:
            try:
                tool = self.create_tool(tool_config)
                tools.append(tool)
            except Exception as e:
                # 记录错误但继续加载其他工具
                print(f"Error creating tool {tool_config.name}: {str(e)}")
        
        return tools
    
    def create_tool(self, config: Union[BuiltinToolConfig, APIToolConfig, MCPToolConfig]) -> "BaseTool":
        """创建单个工具实例"""
        factory = self._factories.get(config.type)
        if not factory:
            raise ToolLoaderError(f"No factory for tool type: {config.type}")
        
        return factory.create_tool(config)
    
    def get_available_tool_types(self) -> List[ToolType]:
        """获取支持的工具类型"""
        return list(self._factories.keys())
    
    def register_factory(self, tool_type: ToolType, factory: BaseToolFactory):
        """注册自定义工具工厂"""
        self._factories[tool_type] = factory
    
    def clear_cache(self):
        """清除配置缓存"""
        self._config_cache.clear()
    
    def get_tools_for_agent(self, agent_name: str) -> List["BaseTool"]:
        """
        根据智能体名称获取对应的工具列表
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            工具实例列表
        """
        # 获取配置文件路径
        config_path = self._default_config_path
        if config_path is None:
            config_path = os.environ.get("TOOLS_CONFIG_PATH")
            
            if config_path is None:
                # 根据环境确定默认配置文件
                env = os.environ.get("ENVIRONMENT", "development")
                config_path = f"config/tools/{env}.json"
                
                # 检查文件是否存在
                if not os.path.exists(config_path):
                    # 回退到示例配置
                    config_path = "config/tools/tools_config_example.json"
        
        # 从配置文件加载工具
        return self.load_tools_from_config(config_path, agent_name)
    
    def validate_config(self, config_path: str) -> List[str]:
        """验证配置文件，返回错误列表"""
        errors = []
        
        try:
            config = self.load_config_from_file(config_path)
            
            # 检查工具组引用的工具是否存在
            for group in config.tool_groups:
                for tool_name in group.tools:
                    if not config.get_tool_by_name(tool_name):
                        errors.append(f"Tool group '{group.name}' references unknown tool '{tool_name}'")
            
            # 检查智能体映射引用的工具组是否存在
            for agent_type, group_names in config.agent_tool_mapping.items():
                for group_name in group_names:
                    if not config.get_tool_group_by_name(group_name):
                        errors.append(f"Agent '{agent_type}' references unknown tool group '{group_name}'")
            
            # 尝试创建工具实例
            for tool_config in config.get_enabled_tools():
                try:
                    self.create_tool(tool_config)
                except Exception as e:
                    errors.append(f"Failed to create tool '{tool_config.name}': {str(e)}")
        
        except Exception as e:
            errors.append(f"Config validation failed: {str(e)}")
        
        return errors


# 全局工具加载器实例
_tool_loader = DynamicToolLoader()


def get_tool_loader() -> DynamicToolLoader:
    """获取全局工具加载器实例"""
    return _tool_loader


def load_tools_from_config(config_path: str, agent_type: Optional[str] = None) -> List["BaseTool"]:
    """便捷函数：从配置文件加载工具"""
    return _tool_loader.load_tools_from_config(config_path, agent_type)


def validate_tools_config(config_path: str) -> List[str]:
    """便捷函数：验证工具配置文件"""
    return _tool_loader.validate_config(config_path)