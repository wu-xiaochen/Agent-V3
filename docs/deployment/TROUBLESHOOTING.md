# Agent-V3 故障排查指南

**版本**: 1.0  
**更新日期**: 2025-10-28

---

## 📋 目录

1. [故障排查流程](#故障排查流程)
2. [服务启动问题](#服务启动问题)
3. [连接问题](#连接问题)
4. [性能问题](#性能问题)
5. [功能异常](#功能异常)
6. [数据问题](#数据问题)
7. [工具和命令](#工具和命令)

---

## 🔍 故障排查流程

### 标准排查步骤

```
1. 确认问题 → 收集信息 → 隔离问题 → 分析根因 → 实施修复 → 验证解决 → 文档记录
```

### 信息收集清单

```bash
# 1. 系统基本信息
uname -a
docker --version
docker compose version

# 2. 服务状态
docker compose ps
docker compose logs --tail=100 agent-v3

# 3. 资源使用
docker stats --no-stream
df -h
free -h

# 4. 网络连接
netstat -tuln | grep -E '(:8000|:6379|:5432)'
curl -I http://localhost:8000/health

# 5. 配置检查
docker compose config
env | grep -E '(POSTGRES|REDIS|API)'
```

---

## 🚫 服务启动问题

### 问题 1: Docker 容器启动失败

#### 症状
```bash
$ docker compose up -d
ERROR: Container agent-v3-app exited with code 1
```

#### 检查步骤

**1. 查看容器日志**
```bash
docker compose logs agent-v3
```

**2. 检查端口占用**
```bash
sudo lsof -i :8000
# 如果端口被占用
sudo kill -9 <PID>
```

**3. 检查环境变量**
```bash
docker compose config
# 验证所有必需的环境变量已设置
```

**4. 检查磁盘空间**
```bash
df -h
# 确保有足够空间
```

#### 常见原因和解决方案

| 原因 | 解决方案 |
|------|----------|
| 端口冲突 | 修改 docker-compose.yml 中的端口映射 |
| 环境变量缺失 | 检查 .env 文件，补充缺失变量 |
| 磁盘空间不足 | 清理 Docker 镜像: `docker system prune -a` |
| 权限问题 | 检查文件权限: `chmod -R 755 /opt/agent-v3` |

### 问题 2: 数据库初始化失败

#### 症状
```
ERROR: database "agent_v3" does not exist
```

#### 解决方案

**手动创建数据库**
```bash
# 连接到 PostgreSQL
docker compose exec postgres psql -U postgres

# 创建数据库
CREATE DATABASE agent_v3;
CREATE USER agent_v3_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE agent_v3 TO agent_v3_user;
\q

# 重启应用
docker compose restart agent-v3
```

### 问题 3: Redis 连接失败

#### 症状
```
redis.exceptions.ConnectionError: Error 111 connecting to redis:6379. Connection refused.
```

#### 检查步骤

**1. 验证 Redis 状态**
```bash
docker compose ps redis
docker compose logs redis
```

**2. 测试 Redis 连接**
```bash
docker compose exec redis redis-cli ping
# 应该返回: PONG
```

**3. 检查密码配置**
```bash
# 如果设置了密码
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

#### 解决方案

```bash
# 1. 重启 Redis
docker compose restart redis

# 2. 如果仍然失败，检查配置
docker compose exec redis redis-cli CONFIG GET requirepass

# 3. 清除 Redis 数据并重启
docker compose stop redis
docker volume rm agent-v3_redis_data
docker compose up -d redis
```

---

## 🔌 连接问题

### 问题 4: API 请求 502 Bad Gateway

#### 症状
```bash
$ curl http://localhost/api/health
<html>
<head><title>502 Bad Gateway</title></head>
</html>
```

#### 检查步骤

**1. 检查应用服务**
```bash
docker compose ps agent-v3
# 确保状态为 Up
```

**2. 检查 Nginx 配置**
```bash
docker compose exec nginx nginx -t
# 验证配置语法
```

**3. 查看 Nginx 日志**
```bash
docker compose logs nginx | tail -50
```

**4. 测试后端直接访问**
```bash
curl http://localhost:8000/health
# 绕过 Nginx 直接访问
```

#### 解决方案

| 原因 | 解决方案 |
|------|----------|
| 应用未启动 | `docker compose restart agent-v3` |
| Nginx 配置错误 | 修正 nginx.conf 并重载: `docker compose exec nginx nginx -s reload` |
| 网络问题 | 重建网络: `docker compose down && docker compose up -d` |
| 超时配置 | 增加 proxy_read_timeout 在 nginx.conf |

### 问题 5: N8N API 连接失败

#### 症状
```
Connection error when calling N8N API
```

#### 检查步骤

**1. 验证 N8N 服务**
```bash
# 检查 N8N 是否运行
curl http://localhost:5678/healthz

# 或使用 Docker 网络内地址
docker compose exec agent-v3 curl http://n8n:5678/healthz
```

**2. 检查 API Key**
```bash
# 验证环境变量
docker compose exec agent-v3 printenv | grep N8N
```

**3. 测试 API 调用**
```bash
curl -X GET http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: your-api-key"
```

#### 解决方案

**修复 host.docker.internal 问题**
```python
# 在 tools.py 中已修复
api_url = api_url.replace("host.docker.internal", "localhost")
```

**重新生成 API Key**
```bash
# 在 N8N UI 中:
# Settings → API → Create API Key
# 更新 .env 文件中的 N8N_API_KEY
```

---

## ⚡ 性能问题

### 问题 6: 响应时间过长

#### 症状
- API 响应时间 > 5 秒
- 用户反馈系统卡顿

#### 诊断步骤

**1. 检查资源使用**
```bash
docker stats
# 查看 CPU/内存使用情况
```

**2. 查看慢查询**
```bash
# PostgreSQL 慢查询
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB <<EOF
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
EOF
```

**3. 检查 Redis 慢日志**
```bash
docker compose exec redis redis-cli SLOWLOG GET 10
```

**4. 分析应用日志**
```bash
docker compose logs agent-v3 | grep "execution_time"
```

#### 优化方案

**1. 启用缓存**
```python
# 在 .env 中
CACHE_ENABLED=true
LLM_CACHE_ENABLED=true
```

**2. 优化数据库**
```sql
-- 添加索引
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_messages_session_id ON messages(session_id);

-- 分析表
ANALYZE sessions;
ANALYZE messages;
```

**3. 增加连接池**
```yaml
# config/base/database.yaml
database:
  main:
    pool_size: 20  # 增加连接数
    max_overflow: 40
```

**4. 横向扩展**
```bash
# 启动多个实例
docker compose up -d --scale agent-v3=3
```

### 问题 7: 内存泄漏

#### 症状
- 内存使用持续增长
- 最终导致 OOM (Out of Memory)

#### 诊断步骤

**1. 监控内存趋势**
```bash
# 使用 Prometheus 查询
rate(container_memory_usage_bytes[5m])
```

**2. 获取内存快照**
```bash
docker compose exec agent-v3 python -c "
import objgraph
objgraph.show_most_common_types(limit=20)
"
```

**3. 检查 Redis 内存**
```bash
docker compose exec redis redis-cli INFO memory
```

#### 解决方案

**1. 限制容器内存**
```yaml
# docker-compose.yml
services:
  agent-v3:
    mem_limit: 4g
    memswap_limit: 4g
```

**2. 配置 Redis 最大内存**
```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

**3. 清理未使用对象**
```python
import gc
gc.collect()
```

---

## 🐛 功能异常

### 问题 8: LLM 调用失败

#### 症状
```
Error: LLM API call failed with status 401
```

#### 检查步骤

**1. 验证 API Key**
```bash
docker compose exec agent-v3 printenv | grep API_KEY
```

**2. 测试 API 连接**
```bash
curl -X POST https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "Pro/deepseek-ai/DeepSeek-V3.1-Terminus", "messages": [{"role": "user", "content": "Hello"}]}'
```

**3. 检查配额**
```bash
# 查看 API 使用情况
# 登录 SiliconFlow 控制台查看配额
```

#### 解决方案

| 错误代码 | 原因 | 解决方案 |
|----------|------|----------|
| 401 | API Key 无效 | 更新正确的 API Key |
| 429 | 速率限制 | 降低请求频率或升级计划 |
| 500 | 服务器错误 | 稍后重试，或联系 API 提供商 |
| 503 | 服务不可用 | 检查 API 状态页 |

### 问题 9: 记忆功能失效

#### 症状
- 智能体无法记住之前的对话
- 每次对话都像新会话

#### 检查步骤

**1. 验证 Redis 连接**
```bash
docker compose exec redis redis-cli -a $REDIS_PASSWORD PING
```

**2. 检查会话存储**
```bash
docker compose exec redis redis-cli -a $REDIS_PASSWORD KEYS "chat_history:*"
```

**3. 查看会话内容**
```bash
docker compose exec redis redis-cli -a $REDIS_PASSWORD GET "chat_history:your-session-id"
```

#### 解决方案

**1. 检查配置**
```python
# 确保 memory=True
agent = UnifiedAgent(
    provider='siliconflow',
    memory=True,  # ← 必须为 True
    redis_url='redis://localhost:6379/0',
    session_id='user_001'
)
```

**2. 验证 Prompt 模板**
```python
# 确保包含 {chat_history}
template = """...
Previous conversation history:
{chat_history}
...
"""
```

**3. 清除并重建**
```bash
# 清除 Redis 缓存
docker compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB

# 重启应用
docker compose restart agent-v3
```

---

## 💾 数据问题

### 问题 10: 数据丢失

#### 症状
- 历史对话消失
- 用户数据缺失

#### 恢复步骤

**1. 检查备份**
```bash
ls -lh /opt/backups/agent-v3/
# 找到最近的备份
```

**2. 恢复数据库**
```bash
# 停止应用
docker compose stop agent-v3

# 恢复 PostgreSQL
gunzip -c /opt/backups/agent-v3/postgres_20250128_120000.sql.gz | \
  docker compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB

# 恢复 Redis
docker compose stop redis
docker cp /opt/backups/agent-v3/dump_20250128_120000.rdb agent-v3-redis:/data/dump.rdb
docker compose start redis

# 重启应用
docker compose start agent-v3
```

**3. 验证恢复**
```bash
# 检查数据
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT COUNT(*) FROM sessions;"
```

### 问题 11: 数据不一致

#### 症状
- Redis 和 PostgreSQL 数据不匹配
- 应用行为异常

#### 诊断步骤

**1. 对比数据**
```bash
# PostgreSQL 记录数
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT COUNT(*) FROM sessions;"

# Redis 记录数
docker compose exec redis redis-cli -a $REDIS_PASSWORD DBSIZE
```

**2. 检查同步日志**
```bash
docker compose logs agent-v3 | grep -i "sync"
```

#### 解决方案

**重建缓存**
```bash
# 1. 清空 Redis
docker compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB

# 2. 重启应用（自动重建缓存）
docker compose restart agent-v3

# 3. 验证
docker compose logs -f agent-v3
```

---

## 🛠️ 工具和命令

### 快速诊断脚本

创建 `scripts/diagnose.sh`:

```bash
#!/bin/bash
# Agent-V3 快速诊断工具

echo "=== Agent-V3 Diagnostic Tool ==="
echo "Time: $(date)"
echo ""

# 服务状态
echo "1. Service Status:"
docker compose ps
echo ""

# 健康检查
echo "2. Health Check:"
curl -f http://localhost:8000/health && echo "✅ Healthy" || echo "❌ Unhealthy"
echo ""

# 资源使用
echo "3. Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

# 最近错误
echo "4. Recent Errors:"
docker compose logs --tail=20 agent-v3 | grep -i error
echo ""

# 数据库连接
echo "5. Database Connections:"
docker compose exec postgres pg_isready && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL Down"
docker compose exec redis redis-cli ping && echo "✅ Redis OK" || echo "❌ Redis Down"
echo ""

# 网络检查
echo "6. Network Check:"
netstat -tuln | grep -E '(:8000|:6379|:5432)'
echo ""

echo "=== Diagnostic Complete ==="
```

### 常用命令速查

```bash
# 查看所有服务状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启特定服务
docker compose restart <service-name>

# 进入容器 shell
docker compose exec agent-v3 bash

# 查看容器资源使用
docker stats

# 清理未使用资源
docker system prune -a

# 检查配置
docker compose config

# 扩容服务
docker compose up -d --scale agent-v3=3

# 查看网络
docker network inspect agent-v3-network

# 查看数据卷
docker volume ls
docker volume inspect <volume-name>
```

---

## 📞 获取帮助

### 内部支持

1. **文档**: 查看 [docs/](../) 目录
2. **日志**: 检查 `/opt/agent-v3/logs/`
3. **监控**: 访问 Grafana 仪表盘

### 外部支持

1. **GitHub Issues**: https://github.com/your-org/agent-v3/issues
2. **技术支持**: tech-support@your-company.com
3. **紧急热线**: 400-xxx-xxxx

### 提交问题时请包含

- 问题描述和复现步骤
- 错误日志 (`docker compose logs`)
- 系统信息 (`uname -a`, `docker --version`)
- 配置信息 (`docker compose config`)
- 相关截图

---

**最后更新**: 2025-10-28  
**维护团队**: DevOps & SRE Team  
**联系方式**: sre@your-company.com

