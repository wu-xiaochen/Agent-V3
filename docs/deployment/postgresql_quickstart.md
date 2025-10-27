# PostgreSQL 数据库快速设置指南

本指南提供在 Agent-V3 项目中快速设置 PostgreSQL 数据库的步骤。

## 🚀 快速开始

### 方法 1: 使用自动化脚本（推荐）

1. **运行初始化脚本**:
   ```bash
   ./scripts/setup_postgresql.sh
   ```

2. **按照提示输入密码**（至少8个字符）

3. **脚本将自动完成**:
   - 检查 PostgreSQL 安装状态
   - 创建数据库 `trae_agents`
   - 创建用户 `agent_user`
   - 更新 `.env` 文件
   - 测试数据库连接

### 方法 2: 手动设置

1. **安装 PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Linux (Ubuntu/Debian)
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **创建数据库和用户**:
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE trae_agents;
   CREATE USER agent_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE trae_agents TO agent_user;
   \c trae_agents;
   GRANT ALL ON SCHEMA public TO agent_user;
   \q
   ```

3. **更新 .env 文件**:
   ```bash
   DB_NAME=trae_agents
   DB_USERNAME=agent_user
   DB_PASSWORD=your_secure_password
   ```

4. **测试连接**:
   ```bash
   psql -h localhost -U agent_user -d trae_agents
   ```

## 📋 验证设置

运行项目验证数据库配置是否正确:

```bash
python main.py --interactive --stream
```

如果项目能够正常启动且没有数据库连接错误，说明配置成功。

## 📚 更多信息

- 详细设置指南: [PostgreSQL 设置指南](postgresql_setup.md)
- 数据库配置说明: [数据库配置说明](database_configuration.md)

## 🔧 常见问题

### 问题: 连接被拒绝
```bash
# 检查服务状态
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql     # Linux

# 启动服务
brew services start postgresql@15    # macOS
sudo systemctl start postgresql       # Linux
```

### 问题: 认证失败
1. 确认用户名和密码正确
2. 检查 `.env` 文件中的配置
3. 确认数据库用户已创建并授予权限

### 问题: 数据库不存在
```bash
sudo -u postgres psql
CREATE DATABASE trae_agents;
\q
```

---

如需更多帮助，请参考完整文档或联系项目维护者。