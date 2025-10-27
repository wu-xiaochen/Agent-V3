"""
缓存服务接口
定义缓存操作的标准接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import json
import logging
import pickle
from datetime import timedelta

from src.shared.exceptions.exceptions import CacheError


class CacheService(ABC):
    """缓存服务抽象基类"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化缓存服务
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """连接缓存服务"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开缓存服务连接"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """检查是否已连接"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒数或timedelta对象）
            
        Returns:
            是否设置成功
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        pass
    
    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置缓存过期时间
        
        Args:
            key: 缓存键
            seconds: 过期秒数
            
        Returns:
            是否设置成功
        """
        pass
    
    @abstractmethod
    async def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间
        
        Args:
            key: 缓存键
            
        Returns:
            剩余秒数，如果不存在或永不过期则返回-1
        """
        pass
    
    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的所有键
        
        Args:
            pattern: 匹配模式
            
        Returns:
            键列表
        """
        pass
    
    @abstractmethod
    async def flushdb(self) -> bool:
        """
        清空当前数据库
        
        Returns:
            是否清空成功
        """
        pass


class RedisCacheService(CacheService):
    """Redis缓存服务"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化Redis缓存服务
        
        Args:
            host: Redis主机地址
            port: Redis端口
            db: 数据库编号
            password: 密码
            logger: 日志记录器
        """
        super().__init__(logger)
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self._redis = None
    
    async def connect(self) -> None:
        """连接Redis"""
        try:
            import redis.asyncio as redis
            
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=False  # 保持二进制数据
            )
            
            # 测试连接
            await self._redis.ping()
            self._connected = True
            self.logger.info(f"已连接到Redis: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            self.logger.error(f"连接Redis失败: {str(e)}")
            raise CacheError(f"连接Redis失败: {str(e)}")
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._connected = False
            self.logger.info("已断开Redis连接")
    
    async def is_connected(self) -> bool:
        """检查是否已连接"""
        if not self._redis:
            return False
        
        try:
            await self._redis.ping()
            return True
        except:
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            value = await self._redis.get(key)
            if value is None:
                return None
            
            # 尝试反序列化
            try:
                return pickle.loads(value)
            except:
                # 如果反序列化失败，尝试JSON解析
                try:
                    return json.loads(value)
                except:
                    # 如果都失败，直接返回字符串
                    return value.decode('utf-8') if isinstance(value, bytes) else value
        except Exception as e:
            self.logger.error(f"获取缓存失败: {str(e)}")
            raise CacheError(f"获取缓存失败: {str(e)}")
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置缓存值"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            # 序列化值
            if isinstance(value, (str, int, float, bool)):
                serialized_value = str(value).encode('utf-8')
            else:
                serialized_value = pickle.dumps(value)
            
            # 设置过期时间
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            
            if expire:
                result = await self._redis.setex(key, expire, serialized_value)
            else:
                result = await self._redis.set(key, serialized_value)
            
            return result
        except Exception as e:
            self.logger.error(f"设置缓存失败: {str(e)}")
            raise CacheError(f"设置缓存失败: {str(e)}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"删除缓存失败: {str(e)}")
            raise CacheError(f"删除缓存失败: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            result = await self._redis.exists(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"检查缓存存在性失败: {str(e)}")
            raise CacheError(f"检查缓存存在性失败: {str(e)}")
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置缓存过期时间"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            result = await self._redis.expire(key, seconds)
            return result
        except Exception as e:
            self.logger.error(f"设置缓存过期时间失败: {str(e)}")
            raise CacheError(f"设置缓存过期时间失败: {str(e)}")
    
    async def ttl(self, key: str) -> int:
        """获取缓存剩余过期时间"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            self.logger.error(f"获取缓存TTL失败: {str(e)}")
            raise CacheError(f"获取缓存TTL失败: {str(e)}")
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的所有键"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            keys = await self._redis.keys(pattern)
            # 将bytes转换为str
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            self.logger.error(f"获取缓存键列表失败: {str(e)}")
            raise CacheError(f"获取缓存键列表失败: {str(e)}")
    
    async def flushdb(self) -> bool:
        """清空当前数据库"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            result = await self._redis.flushdb()
            return result
        except Exception as e:
            self.logger.error(f"清空缓存数据库失败: {str(e)}")
            raise CacheError(f"清空缓存数据库失败: {str(e)}")


class MemoryCacheService(CacheService):
    """内存缓存服务"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化内存缓存服务
        
        Args:
            logger: 日志记录器
        """
        super().__init__(logger)
        self._cache: Dict[str, Any] = {}
        self._expires: Dict[str, float] = {}
        self._connected = True
    
    async def connect(self) -> None:
        """连接缓存服务（内存缓存无需连接）"""
        self._connected = True
        self.logger.info("内存缓存服务已启动")
    
    async def disconnect(self) -> None:
        """断开缓存服务连接（内存缓存无需断开）"""
        self._connected = False
        self.logger.info("内存缓存服务已停止")
    
    async def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        # 检查是否过期
        if key in self._expires and self._expires[key] < 0:
            # 如果设置了过期时间，检查是否已过期
            import time
            if time.time() > self._expires[key]:
                await self.delete(key)
                return None
        
        return self._cache.get(key)
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置缓存值"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        try:
            self._cache[key] = value
            
            # 设置过期时间
            if expire:
                import time
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                self._expires[key] = time.time() + expire
            elif key in self._expires:
                del self._expires[key]
            
            return True
        except Exception as e:
            self.logger.error(f"设置缓存失败: {str(e)}")
            raise CacheError(f"设置缓存失败: {str(e)}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        try:
            deleted = key in self._cache
            if key in self._cache:
                del self._cache[key]
            if key in self._expires:
                del self._expires[key]
            return deleted
        except Exception as e:
            self.logger.error(f"删除缓存失败: {str(e)}")
            raise CacheError(f"删除缓存失败: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        # 检查是否过期
        if key in self._expires and self._expires[key] > 0:
            import time
            if time.time() > self._expires[key]:
                await self.delete(key)
                return False
        
        return key in self._cache
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置缓存过期时间"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        try:
            if key in self._cache:
                import time
                self._expires[key] = time.time() + seconds
                return True
            return False
        except Exception as e:
            self.logger.error(f"设置缓存过期时间失败: {str(e)}")
            raise CacheError(f"设置缓存过期时间失败: {str(e)}")
    
    async def ttl(self, key: str) -> int:
        """获取缓存剩余过期时间"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        if key not in self._cache:
            return -2  # 不存在
        
        if key not in self._expires:
            return -1  # 永不过期
        
        import time
        remaining = self._expires[key] - time.time()
        if remaining <= 0:
            await self.delete(key)
            return -2  # 已过期
        
        return int(remaining)
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的所有键"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        import fnmatch
        return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
    
    async def flushdb(self) -> bool:
        """清空当前数据库"""
        if not self._connected:
            raise CacheError("缓存服务未连接")
        
        try:
            self._cache.clear()
            self._expires.clear()
            return True
        except Exception as e:
            self.logger.error(f"清空缓存数据库失败: {str(e)}")
            raise CacheError(f"清空缓存数据库失败: {str(e)}")


class CacheServiceFactory:
    """缓存服务工厂"""
    
    @staticmethod
    def create_service(
        cache_type: str,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> CacheService:
        """
        创建缓存服务实例
        
        Args:
            cache_type: 缓存类型 (redis, memory)
            config: 缓存配置
            logger: 日志记录器
            
        Returns:
            缓存服务实例
        """
        cache_type = cache_type.lower()
        
        if cache_type == "redis":
            return RedisCacheService(
                host=config.get("host", "localhost"),
                port=config.get("port", 6379),
                db=config.get("db", 0),
                password=config.get("password"),
                logger=logger
            )
        elif cache_type == "memory":
            return MemoryCacheService(logger=logger)
        else:
            raise CacheError(f"不支持的缓存类型: {cache_type}")