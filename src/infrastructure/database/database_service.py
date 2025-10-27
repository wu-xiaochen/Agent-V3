"""
数据库服务接口
定义数据库操作的标准接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
import logging

from src.shared.exceptions.exceptions import DatabaseError


class DatabaseService(ABC):
    """数据库服务抽象基类"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化数据库服务
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """连接数据库"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开数据库连接"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """检查是否已连接"""
        pass
    
    @abstractmethod
    async def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        pass
    
    @abstractmethod
    async def fetch_one(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取单条记录
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            记录字典，如果没有找到则返回None
        """
        pass
    
    @abstractmethod
    async def fetch_all(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取所有记录
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            记录字典列表
        """
        pass
    
    @abstractmethod
    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Union[str, int]:
        """
        插入记录
        
        Args:
            table: 表名
            data: 数据字典
            
        Returns:
            插入记录的ID
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        更新记录
        
        Args:
            table: 表名
            data: 更新数据
            where: 条件
            
        Returns:
            受影响的行数
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """
        删除记录
        
        Args:
            table: 表名
            where: 条件
            
        Returns:
            受影响的行数
        """
        pass
    
    @abstractmethod
    async def begin_transaction(self) -> None:
        """开始事务"""
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> None:
        """提交事务"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> None:
        """回滚事务"""
        pass


class PostgreSQLService(DatabaseService):
    """PostgreSQL数据库服务"""
    
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化PostgreSQL服务
        
        Args:
            host: 主机地址
            port: 端口号
            database: 数据库名
            username: 用户名
            password: 密码
            logger: 日志记录器
        """
        super().__init__(logger)
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self._pool = None
    
    async def connect(self) -> None:
        """连接PostgreSQL数据库"""
        try:
            import asyncpg
            
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                min_size=1,
                max_size=10
            )
            
            self._connected = True
            self.logger.info(f"已连接到PostgreSQL数据库: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            self.logger.error(f"连接PostgreSQL数据库失败: {str(e)}")
            raise DatabaseError(f"连接PostgreSQL数据库失败: {str(e)}")
    
    async def disconnect(self) -> None:
        """断开PostgreSQL连接"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._connected = False
            self.logger.info("已断开PostgreSQL数据库连接")
    
    async def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self._pool is not None
    
    async def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """执行SQL查询"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            async with self._pool.acquire() as conn:
                if params:
                    result = await conn.execute(query, *params.values())
                else:
                    result = await conn.execute(query)
                return result
        except Exception as e:
            self.logger.error(f"执行SQL查询失败: {str(e)}")
            raise DatabaseError(f"执行SQL查询失败: {str(e)}")
    
    async def fetch_one(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            async with self._pool.acquire() as conn:
                if params:
                    row = await conn.fetchrow(query, *params.values())
                else:
                    row = await conn.fetchrow(query)
                
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"获取单条记录失败: {str(e)}")
            raise DatabaseError(f"获取单条记录失败: {str(e)}")
    
    async def fetch_all(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """获取所有记录"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            async with self._pool.acquire() as conn:
                if params:
                    rows = await conn.fetch(query, *params.values())
                else:
                    rows = await conn.fetch(query)
                
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取所有记录失败: {str(e)}")
            raise DatabaseError(f"获取所有记录失败: {str(e)}")
    
    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Union[str, int]:
        """插入记录"""
        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i+1}" for i in range(len(values))]
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        
        try:
            result = await self.fetch_one(query, dict(zip(columns, values)))
            return result["id"] if result else None
        except Exception as e:
            self.logger.error(f"插入记录失败: {str(e)}")
            raise DatabaseError(f"插入记录失败: {str(e)}")
    
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """更新记录"""
        set_clauses = []
        where_clauses = []
        params = {}
        
        # 构建SET子句
        for i, (column, value) in enumerate(data.items(), 1):
            set_clauses.append(f"{column} = ${i}")
            params[f"set_{column}"] = value
        
        # 构建WHERE子句
        for i, (column, value) in enumerate(where.items(), len(data) + 1):
            where_clauses.append(f"{column} = ${i}")
            params[f"where_{column}"] = value
        
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        
        try:
            result = await self.execute(query, params)
            # PostgreSQL的execute返回字符串，如"UPDATE 1"
            if isinstance(result, str):
                return int(result.split()[-1])
            return result
        except Exception as e:
            self.logger.error(f"更新记录失败: {str(e)}")
            raise DatabaseError(f"更新记录失败: {str(e)}")
    
    async def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """删除记录"""
        where_clauses = []
        params = {}
        
        # 构建WHERE子句
        for i, (column, value) in enumerate(where.items(), 1):
            where_clauses.append(f"{column} = ${i}")
            params[f"where_{column}"] = value
        
        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        
        try:
            result = await self.execute(query, params)
            # PostgreSQL的execute返回字符串，如"DELETE 1"
            if isinstance(result, str):
                return int(result.split()[-1])
            return result
        except Exception as e:
            self.logger.error(f"删除记录失败: {str(e)}")
            raise DatabaseError(f"删除记录失败: {str(e)}")
    
    async def begin_transaction(self) -> None:
        """开始事务"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("BEGIN")
        except Exception as e:
            self.logger.error(f"开始事务失败: {str(e)}")
            raise DatabaseError(f"开始事务失败: {str(e)}")
    
    async def commit_transaction(self) -> None:
        """提交事务"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("COMMIT")
        except Exception as e:
            self.logger.error(f"提交事务失败: {str(e)}")
            raise DatabaseError(f"提交事务失败: {str(e)}")
    
    async def rollback_transaction(self) -> None:
        """回滚事务"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("ROLLBACK")
        except Exception as e:
            self.logger.error(f"回滚事务失败: {str(e)}")
            raise DatabaseError(f"回滚事务失败: {str(e)}")


class SQLiteService(DatabaseService):
    """SQLite数据库服务"""
    
    def __init__(
        self,
        database_path: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化SQLite服务
        
        Args:
            database_path: 数据库文件路径
            logger: 日志记录器
        """
        super().__init__(logger)
        self.database_path = database_path
        self._connection = None
    
    async def connect(self) -> None:
        """连接SQLite数据库"""
        try:
            import aiosqlite
            
            self._connection = await aiosqlite.connect(self.database_path)
            self._connected = True
            self.logger.info(f"已连接到SQLite数据库: {self.database_path}")
        except Exception as e:
            self.logger.error(f"连接SQLite数据库失败: {str(e)}")
            raise DatabaseError(f"连接SQLite数据库失败: {str(e)}")
    
    async def disconnect(self) -> None:
        """断开SQLite连接"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._connected = False
            self.logger.info("已断开SQLite数据库连接")
    
    async def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self._connection is not None
    
    async def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """执行SQL查询"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            if params:
                cursor = await self._connection.execute(query, params)
            else:
                cursor = await self._connection.execute(query)
            
            await self._connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"执行SQL查询失败: {str(e)}")
            await self._connection.rollback()
            raise DatabaseError(f"执行SQL查询失败: {str(e)}")
    
    async def fetch_one(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            if params:
                cursor = await self._connection.execute(query, params)
            else:
                cursor = await self._connection.execute(query)
            
            row = await cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            self.logger.error(f"获取单条记录失败: {str(e)}")
            raise DatabaseError(f"获取单条记录失败: {str(e)}")
    
    async def fetch_all(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """获取所有记录"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            if params:
                cursor = await self._connection.execute(query, params)
            else:
                cursor = await self._connection.execute(query)
            
            rows = await cursor.fetchall()
            if rows:
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
        except Exception as e:
            self.logger.error(f"获取所有记录失败: {str(e)}")
            raise DatabaseError(f"获取所有记录失败: {str(e)}")
    
    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Union[str, int]:
        """插入记录"""
        columns = list(data.keys())
        placeholders = ["?" for _ in columns]
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        try:
            return await self.execute(query, values)
        except Exception as e:
            self.logger.error(f"插入记录失败: {str(e)}")
            raise DatabaseError(f"插入记录失败: {str(e)}")
    
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """更新记录"""
        set_clauses = []
        where_clauses = []
        values = []
        
        # 构建SET子句
        for column, value in data.items():
            set_clauses.append(f"{column} = ?")
            values.append(value)
        
        # 构建WHERE子句
        for column, value in where.items():
            where_clauses.append(f"{column} = ?")
            values.append(value)
        
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        
        try:
            cursor = await self._connection.execute(query, values)
            await self._connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.logger.error(f"更新记录失败: {str(e)}")
            await self._connection.rollback()
            raise DatabaseError(f"更新记录失败: {str(e)}")
    
    async def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """删除记录"""
        where_clauses = []
        values = []
        
        # 构建WHERE子句
        for column, value in where.items():
            where_clauses.append(f"{column} = ?")
            values.append(value)
        
        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        
        try:
            cursor = await self._connection.execute(query, values)
            await self._connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.logger.error(f"删除记录失败: {str(e)}")
            await self._connection.rollback()
            raise DatabaseError(f"删除记录失败: {str(e)}")
    
    async def begin_transaction(self) -> None:
        """开始事务"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            await self._connection.execute("BEGIN")
        except Exception as e:
            self.logger.error(f"开始事务失败: {str(e)}")
            raise DatabaseError(f"开始事务失败: {str(e)}")
    
    async def commit_transaction(self) -> None:
        """提交事务"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            await self._connection.commit()
        except Exception as e:
            self.logger.error(f"提交事务失败: {str(e)}")
            raise DatabaseError(f"提交事务失败: {str(e)}")
    
    async def rollback_transaction(self) -> None:
        """回滚事务"""
        if not await self.is_connected():
            await self.connect()
        
        try:
            await self._connection.rollback()
        except Exception as e:
            self.logger.error(f"回滚事务失败: {str(e)}")
            raise DatabaseError(f"回滚事务失败: {str(e)}")


class DatabaseServiceFactory:
    """数据库服务工厂"""
    
    @staticmethod
    def create_service(
        db_type: str,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> DatabaseService:
        """
        创建数据库服务实例
        
        Args:
            db_type: 数据库类型 (postgresql, sqlite)
            config: 数据库配置
            logger: 日志记录器
            
        Returns:
            数据库服务实例
        """
        db_type = db_type.lower()
        
        if db_type == "postgresql":
            return PostgreSQLService(
                host=config.get("host", "localhost"),
                port=config.get("port", 5432),
                database=config.get("database", ""),
                username=config.get("username", ""),
                password=config.get("password", ""),
                logger=logger
            )
        elif db_type == "sqlite":
            return SQLiteService(
                database_path=config.get("path", ""),
                logger=logger
            )
        else:
            raise DatabaseError(f"不支持的数据库类型: {db_type}")