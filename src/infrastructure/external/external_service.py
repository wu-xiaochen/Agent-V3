"""
外部服务接口
定义与外部系统交互的标准接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import logging
import json
import httpx
from datetime import datetime

from src.shared.exceptions.exceptions import ExternalServiceError


class ExternalService(ABC):
    """外部服务抽象基类"""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化外部服务
        
        Args:
            base_url: 服务基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
            logger: 日志记录器
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._client = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()
    
    async def connect(self) -> None:
        """连接外部服务"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers()
            )
            self.logger.info(f"已连接到外部服务: {self.base_url}")
    
    async def disconnect(self) -> None:
        """断开外部服务连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
            self.logger.info(f"已断开外部服务连接: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            params: 查询参数
            data: 请求数据
            headers: 请求头
            
        Returns:
            响应数据
        """
        if not self._client:
            await self.connect()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers
            )
            
            # 检查响应状态
            if response.status_code >= 400:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise ExternalServiceError(error_msg)
            
            return response.json()
        except httpx.RequestError as e:
            error_msg = f"API请求异常: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalServiceError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"API响应解析失败: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalServiceError(error_msg)
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送GET请求"""
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送POST请求"""
        return await self._make_request("POST", endpoint, data=data)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送PUT请求"""
        return await self._make_request("PUT", endpoint, data=data)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送DELETE请求"""
        return await self._make_request("DELETE", endpoint, params=params)


class LLMService(ExternalService):
    """LLM服务接口"""
    
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化LLM服务
        
        Args:
            provider: 提供商 (openai, anthropic, etc.)
            model: 模型名称
            api_key: API密钥
            base_url: 自定义API基础URL
            temperature: 温度参数
            max_tokens: 最大令牌数
            logger: 日志记录器
        """
        # 设置默认基础URL
        if not base_url:
            if provider.lower() == "openai":
                base_url = "https://api.openai.com/v1"
            elif provider.lower() == "anthropic":
                base_url = "https://api.anthropic.com/v1"
            else:
                raise ExternalServiceError(f"不支持的LLM提供商: {provider}")
        
        super().__init__(base_url, api_key, logger=logger)
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = super()._get_headers()
        
        if self.provider == "anthropic":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
            # 移除Authorization头，因为Anthropic使用x-api-key
            if "Authorization" in headers:
                del headers["Authorization"]
        
        return headers
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.provider == "openai":
            return await self._generate_openai_text(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
        elif self.provider == "anthropic":
            return await self._generate_anthropic_text(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
        else:
            raise ExternalServiceError(f"不支持的LLM提供商: {self.provider}")
    
    async def _generate_openai_text(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """使用OpenAI API生成文本"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = await self.post("chat/completions", data=data)
        return response["choices"][0]["message"]["content"]
    
    async def _generate_anthropic_text(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """使用Anthropic API生成文本"""
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        # Anthropic使用messages格式
        data["messages"] = [{"role": "user", "content": prompt}]
        
        response = await self.post("messages", data=data)
        return response["content"][0]["text"]
    
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        获取文本嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型，如果不提供则使用默认模型
            
        Returns:
            嵌入向量
        """
        if self.provider != "openai":
            raise ExternalServiceError(f"提供商 {self.provider} 不支持嵌入功能")
        
        embedding_model = model or "text-embedding-ada-002"
        
        data = {
            "model": embedding_model,
            "input": text
        }
        
        response = await self.post("embeddings", data=data)
        return response["data"][0]["embedding"]
    
    def get_llm(self):
        """获取LLM实例，用于CrewAI"""
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.api_key
            )
        elif self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                anthropic_api_key=self.api_key
            )
        else:
            raise ExternalServiceError(f"不支持的LLM提供商: {self.provider}")


class WeatherService(ExternalService):
    """天气服务接口"""
    
    def __init__(
        self,
        api_key: str,
        provider: str = "openweathermap",
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化天气服务
        
        Args:
            api_key: API密钥
            provider: 提供商
            base_url: 自定义API基础URL
            logger: 日志记录器
        """
        # 设置默认基础URL
        if not base_url:
            if provider.lower() == "openweathermap":
                base_url = "https://api.openweathermap.org/data/2.5"
            else:
                raise ExternalServiceError(f"不支持的天气服务提供商: {provider}")
        
        super().__init__(base_url, api_key=api_key, logger=logger)
        self.provider = provider.lower()
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        # 天气服务通常不需要特殊的认证头
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def get_current_weather(
        self,
        city: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        获取当前天气
        
        Args:
            city: 城市名称
            units: 单位系统 (metric, imperial, kelvin)
            
        Returns:
            天气数据
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        response = await self.get("weather", params=params)
        return response
    
    async def get_weather_forecast(
        self,
        city: str,
        days: int = 5,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        获取天气预报
        
        Args:
            city: 城市名称
            days: 预报天数
            units: 单位系统 (metric, imperial, kelvin)
            
        Returns:
            天气预报数据
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
            "cnt": days * 8  # 每天8个时间点（3小时间隔）
        }
        
        response = await self.get("forecast", params=params)
        return response


class NewsService(ExternalService):
    """新闻服务接口"""
    
    def __init__(
        self,
        api_key: str,
        provider: str = "newsapi",
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化新闻服务
        
        Args:
            api_key: API密钥
            provider: 提供商
            base_url: 自定义API基础URL
            logger: 日志记录器
        """
        # 设置默认基础URL
        if not base_url:
            if provider.lower() == "newsapi":
                base_url = "https://newsapi.org/v2"
            else:
                raise ExternalServiceError(f"不支持的新闻服务提供商: {provider}")
        
        super().__init__(base_url, api_key=api_key, logger=logger)
        self.provider = provider.lower()
    
    async def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取头条新闻
        
        Args:
            country: 国家代码
            category: 新闻类别
            page_size: 每页数量
            
        Returns:
            头条新闻数据
        """
        params = {
            "country": country,
            "pageSize": page_size
        }
        
        if category:
            params["category"] = category
        
        response = await self.get("top-headlines", params=params)
        return response
    
    async def search_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            from_date: 开始日期 (YYYY-MM-DD)
            to_date: 结束日期 (YYYY-MM-DD)
            language: 语言代码
            page_size: 每页数量
            
        Returns:
            搜索结果
        """
        params = {
            "q": query,
            "language": language,
            "pageSize": page_size
        }
        
        if from_date:
            params["from"] = from_date
        
        if to_date:
            params["to"] = to_date
        
        response = await self.get("everything", params=params)
        return response


class ExternalServiceFactory:
    """外部服务工厂"""
    
    @staticmethod
    def create_llm_service(
        provider: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        logger: Optional[logging.Logger] = None
    ) -> LLMService:
        """
        创建LLM服务实例
        
        Args:
            provider: 提供商
            model: 模型名称
            api_key: API密钥
            base_url: 自定义API基础URL
            temperature: 温度参数
            max_tokens: 最大令牌数
            logger: 日志记录器
            
        Returns:
            LLM服务实例
        """
        return LLMService(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            logger=logger
        )
    
    @staticmethod
    def create_weather_service(
        api_key: str,
        provider: str = "openweathermap",
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ) -> WeatherService:
        """
        创建天气服务实例
        
        Args:
            api_key: API密钥
            provider: 提供商
            base_url: 自定义API基础URL
            logger: 日志记录器
            
        Returns:
            天气服务实例
        """
        return WeatherService(
            api_key=api_key,
            provider=provider,
            base_url=base_url,
            logger=logger
        )
    
    @staticmethod
    def create_news_service(
        api_key: str,
        provider: str = "newsapi",
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ) -> NewsService:
        """
        创建新闻服务实例
        
        Args:
            api_key: API密钥
            provider: 提供商
            base_url: 自定义API基础URL
            logger: 日志记录器
            
        Returns:
            新闻服务实例
        """
        return NewsService(
            api_key=api_key,
            provider=provider,
            base_url=base_url,
            logger=logger
        )