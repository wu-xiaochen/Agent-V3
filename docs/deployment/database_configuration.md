# 数据库配置说明

本文档详细说明了 Agent-V3 项目中数据库的配置方式和使用方法。

## 目录
1. [数据库架构](#数据库架构)
2. [配置文件说明](#配置文件说明)
3. [环境变量配置](#环境变量配置)
4. [数据库连接](#数据库连接)
5. [数据库迁移](#数据库迁移)
6. [备份与恢复](#备份与恢复)
7. [性能优化](#性能优化)

## 数据库架构

Agent-V3 项目使用多种数据库系统，每种系统负责不同的功能：

### 1. PostgreSQL (主数据库)

- **用途**: 存储应用程序的核心数据，包括用户信息、会话数据、Agent配置等
- **配置文件**: `config/base/database.yaml`
- **环境变量**: 以 `DB_` 开头的变量

### 2. Redis (缓存数据库)

- **用途**: 缓存频繁访问的数据、会话存储、消息队列等
- **配置文件**: `config/base/database.yaml`
- **环境变量**: 以 `REDIS_` 开头的变量

### 3. 向量数据库

项目支持多种向量数据库，用于存储嵌入向量：

- **ChromaDB**: 本地向量存储，默认选项
- **FAISS**: Facebook AI 相似性搜索库
- **Pinecone**: 云端向量数据库服务

## 配置文件说明

### 主配置文件: `config/base/database.yaml`

```yaml
version: "1.0"
description: "数据库配置"

database:
  # PostgreSQL 主数据库
  main:
    host: "localhost"
    port: 5432
    database: "trae_agents"
    username: "${DB_USERNAME}"
    password: "${DB_PASSWORD}"
    driver: "postgresql"
    pool_size: 10
    max_overflow: 20
    pool_timeout: 30
    pool_recycle: 3600
    echo: false
    ssl_mode: "prefer"

  # Redis 缓存数据库
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: "${REDIS_PASSWORD:}"
    max_connections: 10
    socket_timeout: 5
    socket_connect_timeout: 5
    retry_on_timeout: true
    health_check_interval: 30

  # SQLite 备用数据库
  sqlite:
    path: "./data/agents.db"
    echo: false
    pool_size: 5
    max_overflow: 10

  # 向量数据库配置
  chromadb:
    path: "./data/chroma"
    collection_name: "supply_chain"
    distance_function: "cosine"
    n_results: 10
```

### 环境特定配置

环境特定配置位于 `config/environments/` 目录下，会覆盖基础配置：

- `development.yaml`: 开发环境配置
- `staging.yaml`: 预发环境配置
- `production.yaml`: 生产环境配置

## 环境变量配置

### PostgreSQL 配置

```bash
# 数据库连接信息
DB_HOST=localhost          # 数据库主机地址
DB_PORT=5432              # 数据库端口
DB_NAME=trae_agents       # 数据库名称
DB_USERNAME=agent_user    # 数据库用户名
DB_PASSWORD=your_password # 数据库密码
```

### Redis 配置

```bash
# Redis 连接信息
REDIS_HOST=localhost      # Redis 主机地址
REDIS_PORT=6379          # Redis 端口
REDIS_PASSWORD=          # Redis 密码（可选）
REDIS_DB=0               # Redis 数据库编号
```

### 向量数据库配置

```bash
# ChromaDB 配置
CHROMADB_PATH=./data/chroma  # ChromaDB 数据存储路径

# Pinecone 配置（如果使用）
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=your_environment
```

## 数据库连接

### 使用配置加载器

项目提供了 `ConfigLoader` 类来管理数据库连接：

```python
from src.config.config_loader import ConfigLoader

# 加载配置
config_loader = ConfigLoader()

# 获取数据库配置
db_config = config_loader.get_database_config()

# 获取特定数据库配置
pg_config = config_loader.get_database_config("main")
redis_config = config_loader.get_database_config("redis")
```

### 直接连接示例

```python
import psycopg2
import redis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# PostgreSQL 连接
def connect_postgresql():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

# Redis 连接
def connect_redis():
    r = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PASSWORD") or None,
        db=int(os.getenv("REDIS_DB"))
    )
    return r
```

## 数据库迁移

### 创建迁移文件

```bash
# 使用 Alembic 创建迁移
alembic revision --autogenerate -m "描述迁移内容"
```

### 执行迁移

```bash
# 升级数据库到最新版本
alembic upgrade head

# 降级数据库到指定版本
alembic downgrade -1
```

### 初始化迁移环境

```bash
# 初始化 Alembic
alembic init alembic

# 创建第一个迁移
alembic revision --autogenerate -m "Initial migration"
```

## 备份与恢复

### PostgreSQL 备份与恢复

```bash
# 创建备份
pg_dump -h localhost -U agent_user -d trae_agents > backup.sql

# 压缩备份
pg_dump -h localhost -U agent_user -d trae_agents | gzip > backup.sql.gz

# 恢复备份
psql -h localhost -U agent_user -d trae_agents < backup.sql

# 从压缩备份恢复
gunzip -c backup.sql.gz | psql -h localhost -U agent_user -d trae_agents
```

### Redis 备份与恢复

```bash
# 创建 Redis 快照
redis-cli BGSAVE

# 复制 RDB 文件
cp /var/lib/redis/dump.rdb /backup/redis_backup.rdb

# 恢复 Redis 数据
redis-cli FLUSHALL
redis-cli --rdb /backup/redis_backup.rdb
```

## 性能优化

### PostgreSQL 优化

1. **调整连接池大小**:
   ```yaml
   database:
     main:
       pool_size: 20          # 根据并发需求调整
       max_overflow: 40       # 池外最大连接数
       pool_timeout: 30       # 获取连接超时时间
       pool_recycle: 3600     # 连接回收时间
   ```

2. **数据库服务器配置**:
   ```ini
   # postgresql.conf
   shared_buffers = 256MB     # 系统内存的25%
   effective_cache_size = 1GB # 系统内存的75%
   work_mem = 4MB            # 每个查询的内存
   maintenance_work_mem = 64MB
   ```

3. **索引优化**:
   ```sql
   -- 创建索引
   CREATE INDEX idx_table_column ON table_name(column_name);
   
   -- 分析表统计信息
   ANALYZE table_name;
   ```

### Redis 优化

1. **内存优化**:
   ```ini
   # redis.conf
   maxmemory 512mb
   maxmemory-policy allkeys-lru
   ```

2. **持久化配置**:
   ```ini
   # 启用 AOF 持久化
   appendonly yes
   appendfsync everysec
   ```

3. **连接池优化**:
   ```yaml
   database:
     redis:
       max_connections: 20    # 最大连接数
       socket_timeout: 5      # 套接字超时
       retry_on_timeout: true # 超时重试
   ```

### 向量数据库优化

1. **ChromaDB 优化**:
   ```python
   # 设置集合参数
   collection = client.get_or_create_collection(
       name="supply_chain",
       metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
   )
   ```

2. **FAISS 优化**:
   ```yaml
   database:
     faiss:
       index_type: "IndexIVFFlat"  # 使用 IVF 索引
       nlist: 100                  # 聚类中心数量
       nprobe: 10                  # 搜索时的聚类数量
   ```

## 监控与日志

### 启用查询日志

```yaml
database:
  main:
    echo: true  # 启用 SQL 查询日志
```

### 监控连接池

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # 监控连接池状态
    print(f"连接池状态: {connection_record}")
```

### 性能监控

```sql
-- 查看活动连接
SELECT * FROM pg_stat_activity;

-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('trae_agents'));

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public';
```

## 安全配置

### SSL 连接

```yaml
database:
  main:
    ssl_mode: "require"  # 强制 SSL 连接
```

### 访问控制

```sql
-- 创建只读用户
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE trae_agents TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

### 密码策略

```sql
-- 启用密码扩展
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建密码哈希函数
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(digest(password, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;
```

---

如需更多详细信息，请参考：
- [PostgreSQL 设置指南](postgresql_setup.md)
- [项目部署文档](deployment_guide.md)
- [API 文档](../api/api_reference.md)