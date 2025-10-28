# Agent-V3 运维手册

**版本**: 1.0  
**更新日期**: 2025-10-28  

---

## 📋 目录

1. [日常运维](#日常运维)
2. [监控和告警](#监控和告警)
3. [性能优化](#性能优化)
4. [安全维护](#安全维护)
5. [故障应急](#故障应急)
6. [变更管理](#变更管理)

---

## 🔧 日常运维

### 1. 服务健康检查

#### 每日检查清单

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Agent-V3 日常健康检查 ==="
echo "检查时间: $(date)"
echo ""

# 1. 检查服务状态
echo "1. 服务状态检查"
docker compose ps | grep -v "Exit 0"

# 2. 检查健康端点
echo "2. 健康检查"
curl -f http://localhost:8000/health || echo "❌ 健康检查失败"

# 3. 检查资源使用
echo "3. 资源使用情况"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 4. 检查磁盘空间
echo "4. 磁盘空间"
df -h | grep -E '(Filesystem|/dev/)'

# 5. 检查日志错误
echo "5. 最近错误日志"
docker compose logs --tail=100 agent-v3 | grep -i error | tail -10

# 6. 检查数据库连接
echo "6. 数据库连接"
docker compose exec postgres pg_isready || echo "❌ PostgreSQL 不可用"
docker compose exec redis redis-cli ping || echo "❌ Redis 不可用"

echo ""
echo "=== 检查完成 ==="
```

#### 定时执行

```bash
# 添加到 crontab
crontab -e

# 每小时执行健康检查
0 * * * * /opt/agent-v3/scripts/daily_health_check.sh >> /var/log/agent-v3-health.log 2>&1
```

### 2. 日志管理

#### 日志查看

```bash
# 实时日志
docker compose logs -f agent-v3

# 按时间过滤
docker compose logs --since "2025-01-28T10:00:00" agent-v3

# 按服务过滤
docker compose logs redis postgres

# 搜索特定关键词
docker compose logs agent-v3 | grep "ERROR\|CRITICAL"
```

#### 日志轮转

```bash
# 配置 logrotate
sudo tee /etc/logrotate.d/agent-v3 > /dev/null <<EOF
/opt/agent-v3/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 agent-v3 agent-v3
    sharedscripts
    postrotate
        docker compose exec agent-v3 kill -HUP 1 2>/dev/null || true
    endscript
}
EOF
```

### 3. 备份验证

#### 每周备份测试

```bash
#!/bin/bash
# weekly_backup_test.sh

LATEST_BACKUP=$(ls -t /opt/backups/agent-v3/postgres_*.sql.gz | head -1)

echo "测试备份: $LATEST_BACKUP"

# 创建测试数据库
docker compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS test_restore;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE test_restore;"

# 恢复备份
gunzip -c $LATEST_BACKUP | \
  docker compose exec -T postgres psql -U $POSTGRES_USER -d test_restore

# 验证数据
docker compose exec postgres psql -U $POSTGRES_USER -d test_restore -c "\dt"

echo "备份测试完成"
```

---

## 📊 监控和告警

### 1. 关键指标

#### 应用指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 响应时间 (P95) | > 2s | Warning |
| 响应时间 (P95) | > 5s | Critical |
| 错误率 | > 1% | Warning |
| 错误率 | > 5% | Critical |
| 请求量 | < 10 req/min | Warning |
| 内存使用 | > 85% | Warning |
| 内存使用 | > 95% | Critical |

#### 基础设施指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| CPU 使用率 | > 80% | Warning |
| 磁盘空间 | < 20% | Warning |
| 磁盘空间 | < 10% | Critical |
| Redis 内存 | > 90% | Warning |
| PG 连接数 | > 80 | Warning |

### 2. Grafana 仪表盘

#### 关键仪表盘

1. **Agent-V3 Overview**
   - 服务状态
   - 请求量趋势
   - 响应时间分布
   - 错误率统计

2. **Performance Dashboard**
   - API 延迟
   - LLM 调用时间
   - Tool 执行时间
   - 缓存命中率

3. **Infrastructure Dashboard**
   - CPU/内存/磁盘
   - 网络流量
   - 数据库连接
   - Redis 性能

#### 访问地址

```
生产环境: https://grafana.your-domain.com
用户名: admin
密码: 见 .env.production
```

### 3. 告警通道

#### Prometheus Alertmanager 配置

```yaml
# monitoring/alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@your-company.com'
  smtp_auth_username: 'alerts@your-company.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-ops'
  routes:
    - match:
        severity: critical
      receiver: 'team-ops-critical'
    - match:
        severity: warning
      receiver: 'team-ops-warning'

receivers:
  - name: 'team-ops'
    email_configs:
      - to: 'ops@your-company.com'
    webhook_configs:
      - url: 'https://your-slack-webhook-url'

  - name: 'team-ops-critical'
    email_configs:
      - to: 'ops@your-company.com,oncall@your-company.com'
    webhook_configs:
      - url: 'https://your-slack-webhook-url'

  - name: 'team-ops-warning'
    email_configs:
      - to: 'ops@your-company.com'
```

---

## ⚡ 性能优化

### 1. 数据库优化

#### PostgreSQL 慢查询分析

```bash
# 查看慢查询
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB <<EOF
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
EOF
```

#### 索引优化

```sql
-- 查找缺失索引
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.1;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

#### 连接池调优

```yaml
# config/base/database.yaml
database:
  main:
    pool_size: 20  # 基础连接数
    max_overflow: 40  # 额外连接数
    pool_timeout: 30  # 获取连接超时
    pool_recycle: 3600  # 连接回收时间
```

### 2. Redis 优化

#### 内存分析

```bash
# 查看内存使用
docker compose exec redis redis-cli INFO memory

# 查看键分布
docker compose exec redis redis-cli --bigkeys

# 查看慢日志
docker compose exec redis redis-cli SLOWLOG GET 10
```

#### 缓存策略

```python
# 推荐的缓存 TTL
CACHE_TTL = {
    "llm_response": 86400,  # 1 天
    "tool_result": 3600,    # 1 小时
    "user_session": 7200,   # 2 小时
    "config": 300,          # 5 分钟
}
```

### 3. 应用性能优化

#### 并发控制

```python
# 限制并发 LLM 调用
import asyncio
from asyncio import Semaphore

class LLMRateLimiter:
    def __init__(self, max_concurrent=10):
        self.semaphore = Semaphore(max_concurrent)
    
    async def call_llm(self, prompt):
        async with self.semaphore:
            return await llm.agenerate(prompt)
```

#### 连接池复用

```python
# HTTP 连接池
import httpx

client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
    ),
    timeout=httpx.Timeout(30.0)
)
```

---

## 🔐 安全维护

### 1. 定期安全检查

#### 每月安全检查清单

- [ ] 更新系统软件包
- [ ] 更新 Docker 镜像
- [ ] 检查漏洞扫描结果
- [ ] 审计访问日志
- [ ] 验证备份可用性
- [ ] 检查 SSL 证书有效期
- [ ] 审查用户权限
- [ ] 更新密钥和令牌

#### 漏洞扫描

```bash
# Docker 镜像扫描
docker scan agent-v3:latest

# Python 依赖扫描
pip-audit

# 操作系统扫描
sudo apt update
sudo apt upgrade --dry-run | grep -i security
```

### 2. 密钥轮换

#### 定期轮换密钥

```bash
#!/bin/bash
# rotate_secrets.sh

# 生成新密钥
NEW_JWT_SECRET=$(openssl rand -hex 32)
NEW_API_KEY=$(openssl rand -hex 32)

# 更新配置
sed -i "s/JWT_SECRET=.*/JWT_SECRET=$NEW_JWT_SECRET/" .env.production
sed -i "s/API_KEY=.*/API_KEY=$NEW_API_KEY/" .env.production

# 重启服务
docker compose restart agent-v3

echo "密钥已轮换"
```

### 3. 访问控制

#### IP 白名单

```nginx
# nginx/conf.d/security.conf
geo $whitelist {
    default 0;
    10.0.0.0/8 1;  # 内网
    1.2.3.4 1;     # 办公网 IP
}

server {
    location /api/admin {
        if ($whitelist = 0) {
            return 403;
        }
        proxy_pass http://agent-v3:8000;
    }
}
```

---

## 🚨 故障应急

### 1. 应急响应流程

```
发现问题 → 评估影响 → 通知相关人员 → 应急处理 → 根因分析 → 总结改进
```

### 2. 常见故障处理

#### 服务宕机

```bash
# 1. 检查服务状态
docker compose ps

# 2. 查看错误日志
docker compose logs --tail=100 agent-v3 | grep ERROR

# 3. 重启服务
docker compose restart agent-v3

# 4. 如果无法恢复，回滚
git checkout <last-stable-version>
docker compose down
docker compose up -d
```

#### 数据库锁表

```sql
-- 查看锁
SELECT * FROM pg_locks WHERE NOT granted;

-- 查看活动查询
SELECT pid, query_start, state, query 
FROM pg_stat_activity 
WHERE state != 'idle';

-- 终止慢查询
SELECT pg_terminate_backend(pid);
```

#### Redis 内存溢出

```bash
# 1. 检查内存使用
docker compose exec redis redis-cli INFO memory

# 2. 清理过期键
docker compose exec redis redis-cli --scan --pattern "*" | \
  xargs docker compose exec redis redis-cli DEL

# 3. 如果必要，重启 Redis
docker compose restart redis
```

### 3. 应急联系人

| 角色 | 姓名 | 电话 | 邮箱 | 职责 |
|------|------|------|------|------|
| On-Call | 值班 | 13800138000 | oncall@company.com | 第一响应人 |
| DBA | 数据库管理员 | 13800138001 | dba@company.com | 数据库问题 |
| DevOps | 运维工程师 | 13800138002 | devops@company.com | 基础设施 |
| Tech Lead | 技术负责人 | 13800138003 | tech@company.com | 技术决策 |

---

## 🔄 变更管理

### 1. 变更流程

```
提出变更 → 风险评估 → 审批 → 测试验证 → 执行变更 → 验证 → 文档更新
```

### 2. 变更类别

| 类别 | 审批要求 | 示例 |
|------|----------|------|
| P0 紧急 | CTO 口头 | 安全漏洞修复 |
| P1 重要 | Tech Lead | 新功能上线 |
| P2 常规 | Team Lead | 配置调整 |
| P3 计划 | 自助 | 文档更新 |

### 3. 变更记录

#### 变更模板

```markdown
## 变更记录 #YYYYMMDD-001

**日期**: 2025-01-28  
**类别**: P1 重要变更  
**负责人**: @username  
**审批人**: @tech-lead

### 变更内容
- 升级 PostgreSQL 从 14 到 15
- 优化数据库索引

### 影响范围
- 服务停机时间: 约 30 分钟
- 影响用户: 所有用户

### 回滚方案
1. 恢复数据库备份
2. 回滚应用版本

### 风险评估
- 风险等级: 中
- 缓解措施: 提前通知、完整备份

### 执行步骤
1. [ ] 通知用户
2. [ ] 备份数据
3. [ ] 停止服务
4. [ ] 执行升级
5. [ ] 验证功能
6. [ ] 恢复服务

### 验证结果
- [ ] 服务正常启动
- [ ] 数据库连接正常
- [ ] API 响应正常
- [ ] 性能符合预期
```

---

## 📚 相关文档

- [生产部署指南](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- [故障排查指南](./TROUBLESHOOTING.md)
- [架构文档](../ARCHITECTURE.md)
- [API 文档](../api/api_reference.md)

---

**最后更新**: 2025-10-28  
**维护团队**: DevOps Team  
**联系方式**: ops@your-company.com

