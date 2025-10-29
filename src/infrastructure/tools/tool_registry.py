"""
工具注册器 - 统一管理所有工具的注册、加载和访问
"""

import logging
import importlib
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import yaml
from langchain.tools import BaseTool
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ToolDefinition:
    """工具定义"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name")
        self.display_name = config.get("display_name", self.name)
        self.type = config.get("type")  # builtin, mcp, api
        self.mode = config.get("mode")  # stdio, http (仅用于 MCP)
        self.enabled = config.get("enabled", True)
        self.description = config.get("description", "")
        self.module = config.get("module")
        self.class_name = config.get("class")
        self.function = config.get("function")
        self.parameters = config.get("parameters", {})
        self.config = config.get("config", {})
        self.fallback = config.get("fallback")
        
    def __repr__(self):
        return f"ToolDefinition(name={self.name}, type={self.type}, enabled={self.enabled})"


class ToolRegistry:
    """
    工具注册器 - 单例模式
    
    功能：
    1. 从配置文件加载工具定义
    2. 支持工具注册和注销
    3. 按需加载工具实例
    4. 支持工具组管理
    5. 提供工具查询接口
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._tools: Dict[str, ToolDefinition] = {}
            self._instances: Dict[str, BaseTool] = {}
            self._tool_groups: Dict[str, List[str]] = {}
            self._loading_config: Dict[str, Any] = {}
            ToolRegistry._initialized = True
            logger.info("🔧 工具注册器已初始化")
    
    def load_from_config(self, config_path: str = "config/tools/unified_tools.yaml") -> bool:
        """
        从配置文件加载工具定义
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            是否成功加载
        """
        try:
            from src.config.config_loader import ConfigLoader
            config_loader = ConfigLoader()
            
            # 尝试使用绝对路径
            full_path = Path(config_path)
            if not full_path.is_absolute():
                full_path = config_loader.config_dir / config_path.replace("config/", "")
            
            if not full_path.exists():
                logger.error(f"❌ 工具配置文件不存在: {full_path}")
                return False
            
            with open(full_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 加载工具定义
            tools_config = config.get("tools", [])
            for tool_config in tools_config:
                tool_def = ToolDefinition(tool_config)
                self._tools[tool_def.name] = tool_def
                logger.debug(f"  📌 注册工具: {tool_def.name} ({tool_def.type})")
            
            # 加载工具组
            self._tool_groups = config.get("tool_groups", {})
            
            # 加载配置
            self._loading_config = config.get("loading", {})
            
            logger.info(f"✅ 成功加载 {len(self._tools)} 个工具定义")
            return True
            
        except Exception as e:
            logger.error(f"❌ 加载工具配置失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def register_tool(self, name: str, tool_def: ToolDefinition):
        """注册单个工具"""
        self._tools[name] = tool_def
        logger.debug(f"📌 手动注册工具: {name}")
    
    def unregister_tool(self, name: str):
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            if name in self._instances:
                del self._instances[name]
            logger.debug(f"🗑️  注销工具: {name}")
    
    def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
        """获取工具定义"""
        return self._tools.get(name)
    
    def get_enabled_tools(self) -> List[str]:
        """获取所有启用的工具名称"""
        return [name for name, tool_def in self._tools.items() if tool_def.enabled]
    
    def get_tools_by_group(self, group_name: str) -> List[str]:
        """获取工具组中的工具"""
        group = self._tool_groups.get(group_name, {})
        return group.get("tools", [])
    
    def list_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """列出所有工具及其信息"""
        return {
            name: {
                "display_name": tool_def.display_name,
                "type": tool_def.type,
                "enabled": tool_def.enabled,
                "description": tool_def.description
            }
            for name, tool_def in self._tools.items()
        }
    
    def clear(self):
        """清空所有注册的工具"""
        self._tools.clear()
        self._instances.clear()
        self._tool_groups.clear()
        logger.info("🗑️  工具注册器已清空")


class ToolFactory:
    """
    工具工厂 - 根据工具定义动态创建工具实例
    
    支持：
    1. Builtin 工具：直接导入类实例化
    2. MCP 工具：创建 MCP Stdio/HTTP 工具
    3. API 工具：调用工厂函数或实例化类
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    def create_tool(self, name: str) -> Optional[BaseTool]:
        """
        根据名称创建工具实例
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例，如果失败返回 None
        """
        tool_def = self.registry.get_tool_definition(name)
        if not tool_def:
            self.logger.error(f"❌ 未找到工具定义: {name}")
            return None
        
        if not tool_def.enabled:
            self.logger.debug(f"⏭️  工具未启用: {name}")
            return None
        
        try:
            if tool_def.type == "builtin":
                return self._create_builtin_tool(tool_def)
            elif tool_def.type == "mcp":
                return self._create_mcp_tool(tool_def)
            elif tool_def.type == "api":
                return self._create_api_tool(tool_def)
            else:
                self.logger.error(f"❌ 未知工具类型: {tool_def.type}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ 创建工具 '{name}' 失败: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            
            # 尝试使用 fallback
            if tool_def.fallback:
                self.logger.info(f"🔄 尝试使用 fallback 创建工具: {name}")
                return self._create_fallback_tool(tool_def)
            
            return None
    
    def _create_builtin_tool(self, tool_def: ToolDefinition) -> Optional[BaseTool]:
        """创建内置工具"""
        try:
            module = importlib.import_module(tool_def.module)
            tool_class = getattr(module, tool_def.class_name)
            
            # 传递参数
            if tool_def.parameters:
                tool_instance = tool_class(**tool_def.parameters)
            else:
                tool_instance = tool_class()
            
            self.logger.debug(f"✅ 创建内置工具: {tool_def.name}")
            return tool_instance
            
        except (ImportError, AttributeError, TypeError, ValueError) as e:
            self.logger.error(f"❌ 创建内置工具失败 '{tool_def.name}': {e}")
            return None
    
    def _create_mcp_tool(self, tool_def: ToolDefinition) -> Optional[BaseTool]:
        """创建 MCP 工具"""
        try:
            if tool_def.mode == "stdio":
                from src.agents.shared.n8n_mcp_client import create_n8n_mcp_client
                
                # 从配置中提取参数
                container_name = tool_def.config.get("container_name", "n8n-mcp-server")
                timeout = tool_def.config.get("timeout", 120)
                
                tool_instance = create_n8n_mcp_client(
                    container_name=container_name,
                    timeout=timeout
                )
                
                self.logger.debug(f"✅ 创建 MCP Stdio 工具: {tool_def.name}")
                return tool_instance
                
            elif tool_def.mode == "http":
                # 未来支持 HTTP 模式
                self.logger.warning(f"⚠️ MCP HTTP 模式暂未实现: {tool_def.name}")
                return None
            else:
                self.logger.error(f"❌ 未知 MCP 模式: {tool_def.mode}")
                return None
                
        except (ImportError, ConnectionError, TimeoutError, Exception) as e:
            self.logger.error(f"❌ 创建 MCP 工具失败 '{tool_def.name}': {e}")
            return None
    
    def _create_api_tool(self, tool_def: ToolDefinition) -> Optional[BaseTool]:
        """创建 API 工具"""
        try:
            module = importlib.import_module(tool_def.module)
            
            # 支持两种方式：类或函数
            if tool_def.class_name:
                # 类方式
                tool_class = getattr(module, tool_def.class_name)
                if tool_def.parameters:
                    tool_instance = tool_class(**tool_def.parameters)
                else:
                    tool_instance = tool_class()
                    
            elif tool_def.function:
                # 函数方式
                tool_function = getattr(module, tool_def.function)
                if tool_def.parameters:
                    result = tool_function(**tool_def.parameters)
                else:
                    result = tool_function()
                
                # 函数可能返回单个工具或工具列表
                if isinstance(result, list):
                    tool_instance = result[0] if result else None
                else:
                    tool_instance = result
            else:
                self.logger.error(f"❌ API 工具缺少 class 或 function 定义: {tool_def.name}")
                return None
            
            self.logger.debug(f"✅ 创建 API 工具: {tool_def.name}")
            return tool_instance
            
        except (ImportError, AttributeError, TypeError, ValueError) as e:
            self.logger.error(f"❌ 创建 API 工具失败 '{tool_def.name}': {e}")
            return None
    
    def _create_fallback_tool(self, tool_def: ToolDefinition) -> Optional[BaseTool]:
        """使用 fallback 配置创建工具"""
        try:
            fallback = tool_def.fallback
            fallback_type = fallback.get("type")
            
            if fallback_type == "api":
                module = importlib.import_module(fallback["module"])
                
                if "class" in fallback:
                    tool_class = getattr(module, fallback["class"])
                    params = fallback.get("parameters", {})
                    return tool_class(**params) if params else tool_class()
                elif "function" in fallback:
                    tool_function = getattr(module, fallback["function"])
                    params = fallback.get("parameters", {})
                    result = tool_function(**params) if params else tool_function()
                    return result[0] if isinstance(result, list) else result
            
            self.logger.error(f"❌ 不支持的 fallback 类型: {fallback_type}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Fallback 创建失败: {e}")
            return None
    
    def create_tools(self, tool_names: List[str], parallel: bool = True) -> List[BaseTool]:
        """
        批量创建工具
        
        Args:
            tool_names: 工具名称列表
            parallel: 是否并行加载
            
        Returns:
            成功创建的工具列表
        """
        tools = []
        
        if parallel:
            # 并行加载
            max_workers = min(len(tool_names), 10)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_name = {
                    executor.submit(self.create_tool, name): name 
                    for name in tool_names
                }
                
                for future in as_completed(future_to_name):
                    tool_name = future_to_name[future]
                    try:
                        tool = future.result()
                        if tool:
                            tools.append(tool)
                    except Exception as e:
                        self.logger.error(f"❌ 并行加载工具 '{tool_name}' 失败: {e}")
        else:
            # 串行加载
            for name in tool_names:
                tool = self.create_tool(name)
                if tool:
                    tools.append(tool)
        
        self.logger.info(f"✅ 成功创建 {len(tools)}/{len(tool_names)} 个工具")
        return tools


# 全局单例
_registry = ToolRegistry()
_factory = ToolFactory(_registry)


def get_tool_registry() -> ToolRegistry:
    """获取工具注册器单例"""
    return _registry


def get_tool_factory() -> ToolFactory:
    """获取工具工厂单例"""
    return _factory

