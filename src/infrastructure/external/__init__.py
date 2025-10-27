"""
外部服务模块

提供与外部API交互的抽象接口及实现。
"""

from .external_service import ExternalService, LLMService, WeatherService, NewsService, ExternalServiceFactory

__all__ = [
    "ExternalService",
    "LLMService",
    "WeatherService",
    "NewsService",
    "ExternalServiceFactory"
]