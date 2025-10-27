"""
缓存服务模块

提供缓存操作的抽象接口及实现。
"""

from .cache_service import CacheService, RedisCacheService, MemoryCacheService, CacheServiceFactory

__all__ = [
    "CacheService",
    "RedisCacheService",
    "MemoryCacheService", 
    "CacheServiceFactory"
]