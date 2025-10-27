"""
API工具实现
支持通过HTTP API调用外部服务
"""

import json
import time
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .tools import BaseTool
from .tool_config_models import APIToolConfig, AuthType


class APITool(BaseTool):
    """API工具类，用于调用外部HTTP API"""
    
    def __init__(
        self,
        name: str,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        response_mapping: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        auth: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ):
        """
        初始化API工具
        
        Args:
            name: 工具名称
            endpoint: API端点URL
            method: HTTP方法
            headers: 请求头
            parameters: 参数定义
            response_mapping: 响应映射
            timeout: 请求超时时间(秒)
            retry_count: 重试次数
            retry_delay: 重试延迟(秒)
            auth: 认证配置
            description: 工具描述
        """
        super().__init__(name=name, description=description)
        self.endpoint = endpoint
        self.method = method.upper()
        self.headers = headers or {}
        self.parameters = parameters or {}
        self.response_mapping = response_mapping or {}
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.auth_config = auth or {}
        
        # 创建会话对象
        self.session = requests.Session()
        
        # 设置重试策略
        if retry_count > 0:
            retry_strategy = Retry(
                total=retry_count + 1,
                backoff_factor=retry_delay,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        
        # 设置认证
        self._setup_auth()
    
    def _setup_auth(self):
        """设置认证"""
        auth_type = self.auth_config.get("type", AuthType.NONE)
        
        if auth_type == AuthType.BEARER:
            token = self.auth_config.get("token")
            if token:
                self.headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == AuthType.BASIC:
            username = self.auth_config.get("username")
            password = self.auth_config.get("password")
            if username and password:
                self.session.auth = HTTPBasicAuth(username, password)
        
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
        """执行API调用"""
        # 准备请求参数
        request_kwargs = {
            "timeout": self.timeout,
            "headers": self.headers
        }
        
        # 根据HTTP方法设置参数
        if self.method in ["GET", "DELETE"]:
            request_kwargs["params"] = kwargs
        else:
            request_kwargs["json"] = kwargs
        
        try:
            # 发送请求
            response = self.session.request(
                method=self.method,
                url=self.endpoint,
                **request_kwargs
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}
            
            # 映射响应数据
            mapped_data = self._map_response(response_data)
            
            # 添加元数据
            mapped_data["_metadata"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url
            }
            
            return mapped_data
        
        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e),
                "type": type(e).__name__
            }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """异步执行API调用"""
        import aiohttp
        import asyncio
        
        # 准备请求参数
        headers = self.headers.copy()
        
        # 根据HTTP方法设置参数
        if self.method in ["GET", "DELETE"]:
            params = kwargs
            data = None
        else:
            params = None
            data = json.dumps(kwargs)
            headers["Content-Type"] = "application/json"
        
        # 设置认证
        auth = None
        auth_type = self.auth_config.get("type", AuthType.NONE)
        
        if auth_type == AuthType.BASIC:
            username = self.auth_config.get("username")
            password = self.auth_config.get("password")
            if username and password:
                auth = aiohttp.BasicAuth(username, password)
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers, auth=auth) as session:
                async with session.request(
                    method=self.method,
                    url=self.endpoint,
                    params=params,
                    data=data
                ) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 解析响应
                    try:
                        response_data = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        response_data = {"raw_response": await response.text()}
                    
                    # 映射响应数据
                    mapped_data = self._map_response(response_data)
                    
                    # 添加元数据
                    mapped_data["_metadata"] = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "url": str(response.url)
                    }
                    
                    return mapped_data
        
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "type": type(e).__name__
            }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "APITool":
        """从配置字典创建API工具实例"""
        return cls(
            name=config.get("name", "api_tool"),
            endpoint=config.get("endpoint", ""),
            method=config.get("method", "GET"),
            headers=config.get("headers", {}),
            parameters=config.get("parameters", {}),
            response_mapping=config.get("response_mapping", {}),
            timeout=config.get("timeout", 30),
            retry_count=config.get("retry_count", 0),
            retry_delay=config.get("retry_delay", 1.0),
            auth=config.get("auth", {}),
            description=config.get("description", "API工具")
        )