# PostgreSQL 数据库设置指南

本文档提供在 Agent-V3 项目中设置和配置 PostgreSQL 数据库的详细指南。

## 目录
1. [安装 PostgreSQL](#安装-postgresql)
2. [创建数据库和用户](#创建数据库和用户)
3. [配置环境变量](#配置环境变量)
4. [验证连接](#验证连接)
5. [常见问题解决](#常见问题解决)

## 安装 PostgreSQL

### macOS 安装方式

#### 使用 Homebrew (推荐)

```bash
# 安装 PostgreSQL
brew install postgresql@15

# 启动 PostgreSQL 服务
brew services start postgresql@15

# 或者手动启动
pg_ctl -D /opt/homebrew/var/postgres start
```

#### 使用 Postgres.app

1. 下载 [Postgres.app](https://postgresapp.com/)
2. 将应用拖到 Applications 文件夹
3. 启动 Postgres.app
4. 点击 "Initialize" 创建数据库集群

### Linux 安装方式

#### Ubuntu/Debian

```bash
# 更新包列表
sudo apt update

# 安装 PostgreSQL 和 contrib 包
sudo apt install postgresql postgresql-contrib

# 启动并启用 PostgreSQL 服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### CentOS/RHEL/Fedora

```bash
# 安装 PostgreSQL
sudo dnf install postgresql-server postgresql-contrib

# 初始化数据库
sudo postgresql-setup --initdb

# 启动并启用 PostgreSQL 服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 创建数据库和用户

### 使用命令行方式

1. **切换到 postgres 用户**
   ```bash
   sudo -u postgres psql
   ```

2. **创建数据库**
   ```sql
   CREATE DATABASE trae_agents;
   ```

3. **创建用户并设置密码**
   ```sql
   CREATE USER agent_user WITH PASSWORD 'your_secure_password';
   ```

4. **授予用户权限**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE trae_agents TO agent_user;
   ```

5. **退出 psql**
   ```sql
   \q
   ```

### 使用 pgAdmin (图形界面)

1. 打开 pgAdmin
2. 连接到本地 PostgreSQL 服务器
3. 右键点击 "Databases" → "Create" → "Database"
4. 输入数据库名称 `trae_agents`
5. 右键点击 "Login/Group Roles" → "Create" → "Login/Group Role"
6. 输入角色名称 `agent_user`
7. 在 "Definition" 标签中设置密码
8. 在 "Privileges" 标签中授予必要权限
9. 保存更改

## 配置环境变量

编辑项目根目录下的 `.env` 文件，更新 PostgreSQL 配置：

```bash
# =============================================================================
# 数据库配置
# =============================================================================

# PostgreSQL配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trae_agents
DB_USERNAME=agent_user
DB_PASSWORD=your_secure_password
```

注意：
- `DB_NAME` 应与创建的数据库名称一致
- `DB_USERNAME` 应与创建的用户名一致
- `DB_PASSWORD` 应替换为实际设置的密码

## 验证连接

### 使用 psql 命令行验证

```bash
# 使用新创建的用户连接数据库
psql -h localhost -p 5432 -U agent_user -d trae_agents

# 如果提示输入密码，输入设置的密码
```

### 使用 Python 脚本验证

创建一个简单的 Python 脚本测试连接：

```python
import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    # 建立连接
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD")
    )
    
    print("✅ PostgreSQL 连接成功!")
    
    # 创建游标
    cur = conn.cursor()
    
    # 执行查询
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print(f"数据库版本: {db_version[0]}")
    
    # 关闭连接
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

### 运行项目验证

```bash
# 运行项目主程序
python main.py --interactive --stream
```

如果项目能够正常启动且没有数据库连接错误，说明配置成功。

## 常见问题解决

### 问题 1: 连接被拒绝 (Connection refused)

**错误信息**: `could not connect to server: Connection refused`

**解决方案**:
1. 检查 PostgreSQL 服务是否运行:
   ```bash
   # macOS (Homebrew)
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   ```

2. 如果服务未运行，启动服务:
   ```bash
   # macOS (Homebrew)
   brew services start postgresql@15
   
   # Linux
   sudo systemctl start postgresql
   ```

### 问题 2: 认证失败 (Authentication failed)

**错误信息**: `FATAL: password authentication failed for user "agent_user"`

**解决方案**:
1. 确认用户名和密码正确
2. 检查 pg_hba.conf 配置文件:
   ```bash
   sudo nano /etc/postgresql/15/main/pg_hba.conf
   ```
   确保有类似这样的行:
   ```
   local   all             all                                     md5
   host    all             all             127.0.0.1/32            md5
   host    all             all             ::1/128                 md5
   ```

3. 修改配置后重载 PostgreSQL:
   ```bash
   sudo systemctl reload postgresql
   ```

### 问题 3: 数据库不存在

**错误信息**: `FATAL: database "trae_agents" does not exist`

**解决方案**:
1. 连接到 PostgreSQL 默认数据库:
   ```bash
   psql -h localhost -U postgres
   ```

2. 创建数据库:
   ```sql
   CREATE DATABASE trae_agents;
   ```

3. 确认数据库已创建:
   ```sql
   \l
   ```

### 问题 4: 权限不足

**错误信息**: `ERROR: permission denied for relation ...`

**解决方案**:
1. 以 postgres 用户身份连接:
   ```bash
   psql -h localhost -U postgres -d trae_agents
   ```

2. 授予用户所有权限:
   ```sql
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agent_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agent_user;
   ```

3. 设置默认权限:
   ```sql
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO agent_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO agent_user;
   ```

## 高级配置

### 连接池配置

在 `config/base/database.yaml` 中，可以调整连接池参数:

```yaml
database:
  main:
    host: "localhost"
    port: 5432
    database: "trae_agents"
    username: "${DB_USERNAME}"
    password: "${DB_PASSWORD}"
    driver: "postgresql"
    pool_size: 10          # 连接池大小
    max_overflow: 20       # 超出池大小的最大连接数
    pool_timeout: 30       # 获取连接的超时时间(秒)
    pool_recycle: 3600     # 连接回收时间(秒)
    echo: false            # 是否打印SQL语句
    ssl_mode: "prefer"     # SSL模式
```

### SSL 连接配置

对于生产环境，建议启用 SSL 连接:

1. 生成 SSL 证书:
   ```bash
   # 在 PostgreSQL 数据目录中
   openssl req -new -x509 -days 365 -nodes -text -out server.crt -keyout server.key
   chmod 600 server.key
   ```

2. 更新 postgresql.conf:
   ```ini
   ssl = on
   ssl_cert_file = 'server.crt'
   ssl_key_file = 'server.key'
   ```

3. 更新 .env 文件:
   ```bash
   DB_SSL_MODE=require
   ```

## 备份和恢复

### 创建备份

```bash
# 完整备份
pg_dump -h localhost -U agent_user -d trae_agents > backup.sql

# 压缩备份
pg_dump -h localhost -U agent_user -d trae_agents | gzip > backup.sql.gz
```

### 恢复备份

```bash
# 从备份恢复
psql -h localhost -U agent_user -d trae_agents < backup.sql

# 从压缩备份恢复
gunzip -c backup.sql.gz | psql -h localhost -U agent_user -d trae_agents
```

## 性能优化建议

1. **调整共享缓冲区**:
   ```ini
   # postgresql.conf
   shared_buffers = 256MB  # 系统内存的25%左右
   ```

2. **调整工作内存**:
   ```ini
   work_mem = 4MB
   ```

3. **定期维护**:
   ```sql
   VACUUM ANALYZE;
   ```

4. **监控连接数**:
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```

---

如有其他问题，请参考 [PostgreSQL 官方文档](https://www.postgresql.org/docs/) 或项目维护者。