"""
MCP工具实现
支持通过MCP(Model Context Protocol)协议连接外部工具服务器
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
import aiohttp
import requests
from requests.auth import HTTPBasicAuth

from langchain.tools import BaseTool
from .tool_config_models import MCPToolConfig, AuthType


class MCPTool(BaseTool):
    """MCP工具类，用于通过MCP协议调用外部工具服务器"""
    
    def __init__(
        self,
        name: str,
        server_url: str,
        server_name: str,
        tool_name: str,
        timeout: int = 30,
        auth: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        response_mapping: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ):
        """
        初始化MCP工具
        
        Args:
            name: 工具名称
            server_url: MCP服务器URL
            server_name: MCP服务器名称
            tool_name: MCP工具名称
            timeout: 请求超时时间(秒)
            auth: 认证配置
            parameters: 参数定义
            response_mapping: 响应映射
            description: 工具描述
        """
        super().__init__(name=name, description=description)
        self.server_url = server_url.rstrip('/')
        self.server_name = server_name
        self.tool_name = tool_name
        self.timeout = timeout
        self.auth_config = auth or {}
        self.parameters = parameters or {}
        self.response_mapping = response_mapping or {}
        
        # 构建工具调用端点
        self.tool_endpoint = f"{self.server_url}/mcp/{self.server_name}/tools/{self.tool_name}"
        
        # 设置认证
        self._setup_auth()
    
    def _setup_auth(self):
        """设置认证"""
        auth_type = self.auth_config.get("type", AuthType.NONE)
        self.headers = {}
        self.auth = None
        
        if auth_type == AuthType.BEARER:
            token = self.auth_config.get("token")
            if token:
                self.headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == AuthType.BASIC:
            username = self.auth_config.get("username")
            password = self.auth_config.get("password")
            if username and password:
                self.auth = HTTPBasicAuth(username, password)
        
        elif auth_type == AuthType.API_KEY:
            key = self.auth_config.get("key")
            if key:
                # 默认使用X-API-Key头，可以通过additional_headers自定义
                key_header = self.auth_config.get("additional_headers", {}).get("api_key_header", "X-API-Key")
                self.headers[key_header] = key
        
        # 添加额外的认证头
        additional_headers = self.auth_config.get("additional_headers", {})
        if additional_headers:
            self.headers.update(additional_headers)
    
    def _map_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据映射规则提取响应数据"""
        if not self.response_mapping:
            return response_data
        
        result = {}
        for key, path in self.response_mapping.items():
            try:
                # 简单的JSON路径解析，支持$.key.subkey格式
                if path.startswith("$."):
                    path = path[2:]  # 去除$.前缀
                    value = response_data
                    for part in path.split('.'):
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                            value = value[int(part)]
                        else:
                            value = None
                            break
                    result[key] = value
                else:
                    result[key] = response_data.get(path)
            except Exception:
                result[key] = None
        
        return result
    
    def _run(self, **kwargs) -> Dict[str, Any]:
        """同步执行MCP工具调用"""
        try:
            # 准备请求参数
            request_data = {
                "parameters": kwargs
            }
            
            # 发送请求
            response = requests.post(
                url=self.tool_endpoint,
                json=request_data,
                headers=self.headers,
                auth=self.auth,
                timeout=self.timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}
            
            # 检查MCP响应格式
            if isinstance(response_data, dict) and "result" in response_data:
                # 标准MCP响应格式
                result_data = response_data["result"]
            else:
                # 非标准格式，直接使用
                result_data = response_data
            
            # 映射响应数据
            mapped_data = self._map_response(result_data)
            
            # 添加元数据
            mapped_data["_metadata"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url,
                "server_name": self.server_name,
                "tool_name": self.tool_name
            }
            
            return mapped_data
        
        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e),
                "type": type(e).__name__
            }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """异步执行MCP工具调用"""
        try:
            # 准备请求参数
            request_data = {
                "parameters": kwargs
            }
            
            # 设置认证
            auth = None
            auth_type = self.auth_config.get("type", AuthType.NONE)
            
            if auth_type == AuthType.BASIC:
                username = self.auth_config.get("username")
                password = self.auth_config.get("password")
                if username and password:
                    auth = aiohttp.BasicAuth(username, password)
            
            # 设置请求头
            headers = self.headers.copy()
            headers["Content-Type"] = "application/json"
            
            # 发送请求
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers, auth=auth) as session:
                async with session.post(
                    url=self.tool_endpoint,
                    json=request_data
                ) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 解析响应
                    try:
                        response_data = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        response_data = {"raw_response": await response.text()}
                    
                    # 检查MCP响应格式
                    if isinstance(response_data, dict) and "result" in response_data:
                        # 标准MCP响应格式
                        result_data = response_data["result"]
                    else:
                        # 非标准格式，直接使用
                        result_data = response_data
                    
                    # 映射响应数据
                    mapped_data = self._map_response(result_data)
                    
                    # 添加元数据
                    mapped_data["_metadata"] = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "url": str(response.url),
                        "server_name": self.server_name,
                        "tool_name": self.tool_name
                    }
                    
                    return mapped_data
        
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "type": type(e).__name__
            }
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """发现MCP服务器上可用的工具"""
        try:
            # 构建工具列表端点
            tools_endpoint = f"{self.server_url}/mcp/{self.server_name}/tools"
            
            # 设置认证
            auth = None
            auth_type = self.auth_config.get("type", AuthType.NONE)
            
            if auth_type == AuthType.BASIC:
                username = self.auth_config.get("username")
                password = self.auth_config.get("password")
                if username and password:
                    auth = aiohttp.BasicAuth(username, password)
            
            # 设置请求头
            headers = self.headers.copy()
            
            # 发送请求
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers, auth=auth) as session:
                async with session.get(url=tools_endpoint) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 解析响应
                    try:
                        response_data = await response.json()
                        
                        # 检查MCP响应格式
                        if isinstance(response_data, dict) and "tools" in response_data:
                            return response_data["tools"]
                        else:
                            return response_data if isinstance(response_data, list) else []
                    
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        return []
        
        except Exception as e:
            print(f"Error discovering tools: {str(e)}")
            return []
    
    async def get_tool_schema(self) -> Dict[str, Any]:
        """获取当前工具的详细模式"""
        try:
            # 构建工具模式端点
            schema_endpoint = f"{self.server_url}/mcp/{self.server_name}/tools/{self.tool_name}/schema"
            
            # 设置认证
            auth = None
            auth_type = self.auth_config.get("type", AuthType.NONE)
            
            if auth_type == AuthType.BASIC:
                username = self.auth_config.get("username")
                password = self.auth_config.get("password")
                if username and password:
                    auth = aiohttp.BasicAuth(username, password)
            
            # 设置请求头
            headers = self.headers.copy()
            
            # 发送请求
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers, auth=auth) as session:
                async with session.get(url=schema_endpoint) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 解析响应
                    try:
                        response_data = await response.json()
                        
                        # 检查MCP响应格式
                        if isinstance(response_data, dict) and "schema" in response_data:
                            return response_data["schema"]
                        else:
                            return response_data if isinstance(response_data, dict) else {}
                    
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        return {}
        
        except Exception as e:
            print(f"Error getting tool schema: {str(e)}")
            return {}
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MCPTool":
        """从配置字典创建MCP工具实例"""
        return cls(
            name=config.get("name", "mcp_tool"),
            server_url=config.get("server_url", ""),
            server_name=config.get("server_name", ""),
            tool_name=config.get("tool_name", ""),
            timeout=config.get("timeout", 30),
            auth=config.get("auth", {}),
            parameters=config.get("parameters", {}),
            response_mapping=config.get("response_mapping", {}),
            description=config.get("description", "MCP工具")
        )