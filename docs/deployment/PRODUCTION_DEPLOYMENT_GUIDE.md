# Agent-V3 生产环境部署指南

**版本**: 1.0  
**更新日期**: 2025-10-28  
**状态**: 生产就绪

---

## 📋 目录

1. [部署前准备](#部署前准备)
2. [环境要求](#环境要求)
3. [安全配置](#安全配置)
4. [部署步骤](#部署步骤)
5. [服务配置](#服务配置)
6. [监控和告警](#监控和告警)
7. [备份和恢复](#备份和恢复)
8. [故障排查](#故障排查)
9. [回滚方案](#回滚方案)

---

## 🎯 部署前准备

### 1. 检查清单

在开始部署前，请确保完成以下检查：

- [ ] 服务器资源满足最低要求
- [ ] 网络端口已开放
- [ ] SSL 证书已准备
- [ ] 数据库已创建
- [ ] 环境变量已配置
- [ ] 备份策略已制定
- [ ] 监控系统已就绪
- [ ] 回滚方案已准备

### 2. 部署架构

#### 单机部署（适合小规模）

```
┌─────────────────────────────────────┐
│        Production Server            │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │ Agent-V3 │  │  Redis   │       │
│  └──────────┘  └──────────┘       │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Nginx   │       │
│  └──────────┘  └──────────┘       │
└─────────────────────────────────────┘
```

#### 高可用部署（推荐）

```
              ┌─────────────┐
              │ Load Balancer│
              └──────┬───────┘
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
    │Agent-V3│  │Agent-V3│  │Agent-V3│
    │ Node 1 │  │ Node 2 │  │ Node 3 │
    └────┬───┘  └───┬────┘  └──┬─────┘
         └───────────┼───────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
    │ Redis  │  │Postgres│  │Monitoring│
    │Cluster │  │  HA    │  │  Stack  │
    └────────┘  └────────┘  └─────────┘
```

---

## 💻 环境要求

### 最低配置

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **CPU** | 4 核 | 8 核 |
| **内存** | 8 GB | 16 GB |
| **存储** | 50 GB SSD | 200 GB SSD |
| **网络** | 100 Mbps | 1 Gbps |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### 软件依赖

| 软件 | 版本 | 用途 |
|------|------|------|
| Docker | 24.0+ | 容器运行时 |
| Docker Compose | 2.20+ | 服务编排 |
| Python | 3.11+ | 应用运行时 |
| PostgreSQL | 15+ | 主数据库 |
| Redis | 7+ | 缓存和会话 |
| Nginx | 1.25+ | 反向代理 |

### 网络端口

| 端口 | 服务 | 说明 | 外部访问 |
|------|------|------|----------|
| 80 | Nginx HTTP | HTTP 访问 | ✅ |
| 443 | Nginx HTTPS | HTTPS 访问 | ✅ |
| 8000 | Agent-V3 | 应用服务 | ❌ 内部 |
| 5432 | PostgreSQL | 数据库 | ❌ 内部 |
| 6379 | Redis | 缓存 | ❌ 内部 |
| 9090 | Prometheus | 监控 | ❌ VPN only |
| 3000 | Grafana | 仪表盘 | ❌ VPN only |

---

## 🔒 安全配置

### 1. 创建 .env 文件

**⚠️ 重要**: 永远不要将 `.env` 文件提交到 git！

```bash
# 创建生产环境配置
cp .env.example .env.production

# 设置严格权限
chmod 600 .env.production
```

#### .env.production 模板

```bash
# ========================================
# 生产环境配置
# ========================================

# 环境标识
ENVIRONMENT=production

# ========================================
# LLM 服务配置
# ========================================
SILICONFLOW_API_KEY=sk-your-production-api-key-here
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ========================================
# 数据库配置
# ========================================
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=agent_v3_prod
POSTGRES_USER=agent_v3_user
POSTGRES_PASSWORD=CHANGE_THIS_STRONG_PASSWORD_123!

# 数据库连接池
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# ========================================
# Redis 配置
# ========================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_THIS_REDIS_PASSWORD_456!
REDIS_DB=0
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# ========================================
# N8N 配置
# ========================================
N8N_API_URL=http://n8n:5678
N8N_API_KEY=your-n8n-api-key-here

# ========================================
# 安全配置
# ========================================
# JWT Secret (生成方式: openssl rand -hex 32)
JWT_SECRET=CHANGE_THIS_TO_RANDOM_64_CHAR_STRING

# API Key (生成方式: openssl rand -hex 32)
API_KEY=CHANGE_THIS_TO_RANDOM_64_CHAR_STRING

# Session Secret
SESSION_SECRET=CHANGE_THIS_TO_RANDOM_64_CHAR_STRING

# ========================================
# SSL/TLS 配置
# ========================================
SSL_ENABLED=true
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem

# PostgreSQL SSL
POSTGRES_SSL_MODE=require

# Redis TLS
REDIS_TLS_ENABLED=true

# ========================================
# 监控配置
# ========================================
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=CHANGE_THIS_GRAFANA_PASSWORD_789!

# ========================================
# 日志配置
# ========================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/app/logs/agent.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10

# ========================================
# 性能配置
# ========================================
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
TIMEOUT=120

# ========================================
# 限流配置
# ========================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# ========================================
# 邮件告警（可选）
# ========================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=ops@your-company.com
```

### 2. 密码生成

使用以下命令生成强密码：

```bash
# 生成 32 字符随机密码
openssl rand -base64 32

# 生成 64 字符十六进制密码
openssl rand -hex 32

# 生成 UUID
uuidgen
```

### 3. SSL/TLS 证书

#### 使用 Let's Encrypt（推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# 证书路径
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem

# 自动续期
sudo crontab -e
# 添加: 0 3 * * * certbot renew --quiet
```

#### 使用自签名证书（测试环境）

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=YourCompany/CN=your-domain.com"
```

### 4. 防火墙配置

```bash
# UFW 防火墙配置
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 检查状态
sudo ufw status verbose
```

---

## 🚀 部署步骤

### 方法 1: Docker Compose 部署（推荐）

#### 步骤 1: 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sudo sh

# 安装 Docker Compose
sudo apt install docker-compose-plugin

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker compose version
```

#### 步骤 2: 克隆代码

```bash
# 创建应用目录
sudo mkdir -p /opt/agent-v3
sudo chown $USER:$USER /opt/agent-v3
cd /opt/agent-v3

# 克隆代码（替换为你的仓库地址）
git clone https://github.com/your-org/agent-v3.git .

# 或使用 rsync 从本地上传
rsync -avz --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  /path/to/local/agent-v3/ user@server:/opt/agent-v3/
```

#### 步骤 3: 配置环境

```bash
# 复制并编辑环境变量
cp .env.example .env.production
nano .env.production

# 修改所有 CHANGE_THIS 标记的值
# 设置强密码
# 配置 SSL 证书路径
```

#### 步骤 4: 准备配置文件

```bash
# 创建 Nginx 配置
mkdir -p nginx/conf.d nginx/ssl
cp nginx/nginx.conf.example nginx/nginx.conf

# 编辑 Nginx 配置
nano nginx/nginx.conf
# 替换 your-domain.com 为你的域名
# 配置 SSL 证书路径
```

#### 步骤 5: 构建和启动

```bash
# 使用生产环境配置
export ENV_FILE=.env.production

# 构建镜像
docker compose --env-file .env.production build

# 启动服务（基础服务）
docker compose --env-file .env.production up -d redis postgres

# 等待数据库就绪
sleep 10

# 初始化数据库
docker compose --env-file .env.production exec postgres \
  psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/init_db.sql

# 启动应用
docker compose --env-file .env.production up -d agent-v3

# 启动 Nginx（可选，如果使用）
docker compose --profile nginx --env-file .env.production up -d

# 启动监控（可选）
docker compose --profile monitoring --env-file .env.production up -d
```

#### 步骤 6: 验证部署

```bash
# 检查服务状态
docker compose --env-file .env.production ps

# 查看日志
docker compose --env-file .env.production logs -f agent-v3

# 健康检查
curl -f http://localhost:8000/health || echo "Health check failed"

# 测试 API
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"message": "Hello, Agent-V3!"}'
```

### 方法 2: 直接部署（不使用 Docker）

#### 步骤 1: 准备 Python 环境

```bash
# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# 创建虚拟环境
python3.11 -m venv /opt/agent-v3/venv

# 激活虚拟环境
source /opt/agent-v3/venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤 2: 安装系统服务

```bash
# 创建 Systemd 服务文件
sudo tee /etc/systemd/system/agent-v3.service > /dev/null <<EOF
[Unit]
Description=Agent-V3 Application
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=agent-v3
Group=agent-v3
WorkingDirectory=/opt/agent-v3
Environment="PYTHONPATH=/opt/agent-v3"
EnvironmentFile=/opt/agent-v3/.env.production
ExecStart=/opt/agent-v3/venv/bin/python main.py --server --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/agent-v3/app.log
StandardError=append:/var/log/agent-v3/error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建用户
sudo useradd -r -s /bin/false agent-v3

# 设置权限
sudo chown -R agent-v3:agent-v3 /opt/agent-v3
sudo mkdir -p /var/log/agent-v3
sudo chown agent-v3:agent-v3 /var/log/agent-v3

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start agent-v3
sudo systemctl enable agent-v3

# 查看状态
sudo systemctl status agent-v3
```

---

## ⚙️ 服务配置

### 1. Nginx 反向代理配置

创建 `nginx/nginx.conf`：

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_status 429;

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS 主站
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL 证书
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # SSL 配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_stapling on;
        ssl_stapling_verify on;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # API 代理
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://agent-v3:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
            
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
        }

        # 健康检查
        location /health {
            proxy_pass http://agent-v3:8000/health;
            access_log off;
        }

        # 静态文件（如果有）
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 2. PostgreSQL 配置优化

编辑 `postgresql.conf`:

```conf
# 连接设置
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB

# 日志设置
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# SSL 设置
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
```

### 3. Redis 配置优化

编辑 `redis.conf`:

```conf
# 基础配置
bind 0.0.0.0
port 6379
requirepass CHANGE_THIS_REDIS_PASSWORD_456!
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# 性能优化
tcp-backlog 511
timeout 300
tcp-keepalive 300
databases 16

# 慢查询日志
slowlog-log-slower-than 10000
slowlog-max-len 128

# 安全
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
```

---

## 📊 监控和告警

### 1. Prometheus 配置

创建 `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'agent-v3-prod'
    environment: 'production'

# 告警规则
rule_files:
  - 'alerts/*.yml'

# 抓取配置
scrape_configs:
  # Agent-V3 应用
  - job_name: 'agent-v3'
    static_configs:
      - targets: ['agent-v3:8000']
    metrics_path: '/metrics'

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis_exporter:9121']

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']

  # Node Exporter（系统指标）
  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']

  # Nginx
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx_exporter:9113']
```

### 2. 告警规则

创建 `monitoring/alerts/agent-v3.yml`:

```yaml
groups:
  - name: agent-v3-alerts
    interval: 30s
    rules:
      # 服务可用性
      - alert: AgentV3Down
        expr: up{job="agent-v3"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Agent-V3 服务宕机"
          description: "{{ $labels.instance }} 已宕机超过 2 分钟"

      # 高错误率
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "高错误率检测"
          description: "错误率超过 5%，当前: {{ $value }}"

      # 高响应时间
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "响应时间过高"
          description: "P95 响应时间: {{ $value }}s"

      # Redis 连接
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis 服务宕机"

      # PostgreSQL 连接
      - alert: PostgresDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL 服务宕机"

      # 磁盘空间
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "磁盘空间不足"
          description: "剩余空间: {{ $value | humanizePercentage }}"

      # 内存使用
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "内存使用率: {{ $value | humanizePercentage }}"
```

### 3. Grafana 仪表盘

导入预配置的仪表盘：

- **Agent-V3 Overview**: 总体监控
- **API Performance**: API 性能
- **Resource Usage**: 资源使用
- **Database Metrics**: 数据库指标

仪表盘 JSON 文件位于 `monitoring/grafana/dashboards/`

---

## 💾 备份和恢复

### 1. 自动备份脚本

创建 `scripts/backup.sh`:

```bash
#!/bin/bash
set -e

# 配置
BACKUP_DIR="/opt/backups/agent-v3"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# PostgreSQL 备份
echo "备份 PostgreSQL..."
docker compose exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB | \
  gzip > $BACKUP_DIR/postgres_$TIMESTAMP.sql.gz

# Redis 备份
echo "备份 Redis..."
docker compose exec -T redis redis-cli --rdb /data/dump_$TIMESTAMP.rdb
docker cp agent-v3-redis:/data/dump_$TIMESTAMP.rdb $BACKUP_DIR/

# 配置文件备份
echo "备份配置文件..."
tar -czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
  config/ \
  .env.production \
  docker-compose.yml

# 删除旧备份
echo "清理旧备份..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

# 上传到对象存储（可选）
# aws s3 sync $BACKUP_DIR s3://your-backup-bucket/agent-v3/

echo "备份完成: $TIMESTAMP"
```

### 2. 恢复脚本

创建 `scripts/restore.sh`:

```bash
#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "用法: $0 <备份时间戳>"
  echo "示例: $0 20250128_120000"
  exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="/opt/backups/agent-v3"

# PostgreSQL 恢复
echo "恢复 PostgreSQL..."
gunzip -c $BACKUP_DIR/postgres_$TIMESTAMP.sql.gz | \
  docker compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB

# Redis 恢复
echo "恢复 Redis..."
docker compose stop redis
docker cp $BACKUP_DIR/dump_$TIMESTAMP.rdb agent-v3-redis:/data/dump.rdb
docker compose start redis

echo "恢复完成"
```

### 3. 设置定时备份

```bash
# 添加到 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /opt/agent-v3/scripts/backup.sh >> /var/log/agent-v3-backup.log 2>&1
```

---

## 🔍 故障排查

### 常见问题

#### 1. 服务无法启动

**症状**: `docker compose up` 失败

**检查**:
```bash
# 查看日志
docker compose logs agent-v3

# 检查端口占用
sudo lsof -i :8000

# 检查环境变量
docker compose config
```

#### 2. 数据库连接失败

**症状**: `Connection refused` 错误

**检查**:
```bash
# 检查 PostgreSQL 状态
docker compose exec postgres pg_isready

# 测试连接
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB

# 检查网络
docker network inspect agent-v3-network
```

#### 3. Redis 连接失败

**症状**: `NOAUTH Authentication required`

**检查**:
```bash
# 测试 Redis 连接
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping

# 检查密码配置
docker compose exec redis redis-cli CONFIG GET requirepass
```

#### 4. 高内存使用

**症状**: 系统响应慢

**检查**:
```bash
# 查看容器资源使用
docker stats

# 检查内存泄漏
docker compose exec agent-v3 python -m memory_profiler main.py
```

### 日志查看

```bash
# 实时日志
docker compose logs -f agent-v3

# 最近 100 行
docker compose logs --tail=100 agent-v3

# 按时间过滤
docker compose logs --since "2025-01-28T10:00:00" agent-v3

# 所有服务
docker compose logs -f
```

---

## ↩️ 回滚方案

### 1. 快速回滚

```bash
# 停止当前版本
docker compose down

# 回滚到上一个版本
git checkout <previous-version-tag>

# 重新构建和启动
docker compose build
docker compose up -d

# 验证
curl http://localhost:8000/health
```

### 2. 数据库回滚

```bash
# 如果需要回滚数据库
./scripts/restore.sh <backup-timestamp>

# 验证数据
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT version();"
```

### 3. 蓝绿部署（零停机）

```bash
# 启动新版本（绿环境）
docker compose -p agent-v3-green up -d

# 健康检查
while ! curl -f http://localhost:8001/health; do sleep 1; done

# 切换流量（更新 Nginx 配置）
# 修改 upstream 指向新版本

# 重载 Nginx
docker compose exec nginx nginx -s reload

# 验证新版本正常后，停止旧版本
docker compose -p agent-v3-blue down
```

---

## ✅ 部署后检查清单

- [ ] 所有服务状态正常 (`docker compose ps`)
- [ ] 健康检查通过 (`curl /health`)
- [ ] 数据库连接正常
- [ ] Redis 连接正常
- [ ] SSL 证书有效
- [ ] 日志正常输出
- [ ] 监控指标正常
- [ ] 告警规则生效
- [ ] 备份脚本运行
- [ ] API 响应正常
- [ ] 性能符合预期

---

## 📞 支持和联系

### 技术支持

- **文档**: [docs/](../README.md)
- **问题反馈**: [GitHub Issues](https://github.com/your-org/agent-v3/issues)
- **紧急联系**: ops@your-company.com

### 维护窗口

- **定期维护**: 每周日 02:00-04:00 (UTC+8)
- **紧急维护**: 随时，提前通知

---

**最后更新**: 2025-10-28  
**文档版本**: 1.0  
**适用版本**: Agent-V3 v3.0+

---

## 📚 相关文档

- [架构文档](../ARCHITECTURE.md)
- [运维手册](./OPERATIONS_MANUAL.md)
- [故障排查](./TROUBLESHOOTING.md)
- [API 文档](../api/api_reference.md)

