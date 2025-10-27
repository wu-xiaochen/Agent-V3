# Agent-V3 部署指南

## 概述

本指南详细介绍了如何在不同环境中部署 Agent-V3 系统，包括开发环境、测试环境和生产环境的部署步骤和最佳实践。

## 目录

- [环境要求](#环境要求)
- [配置管理](#配置管理)
- [开发环境部署](#开发环境部署)
- [测试环境部署](#测试环境部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [Kubernetes 部署](#kubernetes-部署)
- [监控与日志](#监控与日志)
- [故障排除](#故障排除)

## 环境要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核或更多 |
| 内存 | 4GB | 8GB或更多 |
| 存储 | 20GB | 50GB或更多 |
| 网络 | 100Mbps | 1Gbps或更多 |

### 软件要求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.8或更高 |
| Redis | 6.0或更高 |
| PostgreSQL | 12或更高（可选） |
| Docker | 20.10或更高（Docker部署） |
| Kubernetes | 1.20或更高（K8s部署） |

## 配置管理

### 环境变量

创建 `.env` 文件并设置以下环境变量：

```bash
# LLM配置
OPENAI_API_KEY=your_openai_api_key
SILICONFLOW_API_KEY=your_siliconflow_api_key

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agent_v3
DB_USERNAME=postgres
DB_PASSWORD=your_db_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# 应用配置
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key
```

### 配置文件

配置文件位于 `config/` 目录下：

- `config/base/`: 基础配置
- `config/environments/`: 环境特定配置
- `config/schemas/`: 配置模式

## 开发环境部署

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/Agent-V3.git
cd Agent-V3
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements/development.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

### 5. 初始化数据库（可选）

```bash
# 如果使用PostgreSQL
createdb agent_v3

# 运行数据库迁移
python -m src.db.migrate
```

### 6. 启动Redis（可选）

```bash
# 使用Docker启动Redis
docker run -d --name redis -p 6379:6379 redis:6-alpine

# 或使用本地安装的Redis
redis-server
```

### 7. 运行应用

```bash
# 运行主应用
python -m src.main

# 或使用脚本
./scripts/run_local.sh
```

### 8. 验证部署

```bash
# 运行测试
python -m pytest tests/

# 检查应用状态
curl http://localhost:8000/health
```

## 测试环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3 python3-pip python3-venv redis-server
```

### 2. 部署应用

```bash
# 创建应用目录
sudo mkdir -p /opt/agent-v3
sudo chown $USER:$USER /opt/agent-v3
cd /opt/agent-v3

# 克隆代码
git clone https://github.com/your-username/Agent-V3.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements/production.txt
```

### 3. 配置环境

```bash
# 复制环境配置
cp .env.example .env

# 编辑配置文件
nano .env

# 设置测试环境配置
APP_ENV=staging
LOG_LEVEL=DEBUG
```

### 4. 配置服务

创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/agent-v3.service
```

内容如下：

```ini
[Unit]
Description=Agent-V3 Application
After=network.target

[Service]
Type=simple
User=agent-v3
WorkingDirectory=/opt/agent-v3
Environment=PATH=/opt/agent-v3/venv/bin
ExecStart=/opt/agent-v3/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 创建用户
sudo useradd -r -s /bin/false agent-v3
sudo chown -R agent-v3:agent-v3 /opt/agent-v3

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable agent-v3
sudo systemctl start agent-v3

# 检查状态
sudo systemctl status agent-v3
```

### 5. 配置Nginx（可选）

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/agent-v3
```

内容如下：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/agent-v3 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 生产环境部署

### 1. 安全加固

```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# 禁用root登录
sudo nano /etc/ssh/sshd_config
# 设置 PermitRootLogin no
sudo systemctl restart ssh
```

### 2. SSL证书配置

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 数据库配置

```bash
# 安装PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE agent_v3;
CREATE USER agent_v3_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE agent_v3 TO agent_v3_user;
\q

# 配置连接
sudo nano /etc/postgresql/12/main/postgresql.conf
# 设置 listen_addresses = 'localhost'

sudo nano /etc/postgresql/12/main/pg_hba.conf
# 添加以下行
local   agent_v3    agent_v3_user                     md5
host    agent_v3    agent_v3_user    127.0.0.1/32     md5

sudo systemctl restart postgresql
```

### 4. 性能优化

```bash
# 调整系统参数
sudo nano /etc/sysctl.conf
# 添加以下行
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30

# 应用更改
sudo sysctl -p

# 调整文件描述符限制
sudo nano /etc/security/limits.conf
# 添加以下行
* soft nofile 65535
* hard nofile 65535
```

## Docker 部署

### 1. 创建Dockerfile

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements/production.txt requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "src.main"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DB_HOST=db
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: agent_v3
      POSTGRES_USER: agent_v3_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass secure_redis_password
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. 部署命令

```bash
# 构建和启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

## Kubernetes 部署

### 1. 创建命名空间

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: agent-v3
```

### 2. 创建配置映射

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-v3-config
  namespace: agent-v3
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  DB_HOST: "postgres-service"
  REDIS_HOST: "redis-service"
```

### 3. 创建密钥

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-v3-secrets
  namespace: agent-v3
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-key>
  DB_PASSWORD: <base64-encoded-password>
  REDIS_PASSWORD: <base64-encoded-password>
```

### 4. 创建部署

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-v3-deployment
  namespace: agent-v3
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-v3
  template:
    metadata:
      labels:
        app: agent-v3
    spec:
      containers:
      - name: agent-v3
        image: your-registry/agent-v3:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: agent-v3-config
        - secretRef:
            name: agent-v3-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 5. 创建服务

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agent-v3-service
  namespace: agent-v3
spec:
  selector:
    app: agent-v3
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

### 6. 创建入口

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-v3-ingress
  namespace: agent-v3
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: agent-v3-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent-v3-service
            port:
              number: 80
```

### 7. 部署命令

```bash
# 应用所有配置
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# 查看部署状态
kubectl get pods -n agent-v3
kubectl get services -n agent-v3
kubectl get ingress -n agent-v3

# 查看日志
kubectl logs -f deployment/agent-v3-deployment -n agent-v3
```

## 监控与日志

### 1. 应用监控

```bash
# 安装Prometheus和Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack
```

### 2. 日志收集

```yaml
# fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: agent-v3
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*agent-v3*.log
      pos_file /var/log/fluentd-agent-v3.log.pos
      tag kubernetes.*
      format json
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name agent-v3
    </match>
```

### 3. 健康检查

```python
# 在应用中添加健康检查端点
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/ready')
def readiness_check():
    # 检查依赖服务
    if check_dependencies():
        return jsonify({"status": "ready"})
    else:
        return jsonify({"status": "not ready"}), 503
```

## 故障排除

### 常见问题

1. **应用启动失败**
   ```bash
   # 查看应用日志
   docker-compose logs app
   # 或
   kubectl logs deployment/agent-v3-deployment -n agent-v3
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库连接
   python -c "
   from src.config.config_loader import config_loader
   db_config = config_loader.get_database_config()
   print(db_config)
   "
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   docker stats
   # 或
   kubectl top pods -n agent-v3
   ```

4. **性能问题**
   ```bash
   # 分析性能瓶颈
   python -m cProfile -o profile.stats -m src.main
   python -c "
   import pstats
   p = pstats.Stats('profile.stats')
   p.sort_stats('cumulative').print_stats(20)
   "
   ```

### 调试技巧

1. **启用调试模式**
   ```bash
   export LOG_LEVEL=DEBUG
   python -m src.main
   ```

2. **使用调试器**
   ```python
   import pdb; pdb.set_trace()
   ```

3. **性能分析**
   ```python
   import cProfile
   import pstats

   def profile_function(func):
       def wrapper(*args, **kwargs):
           pr = cProfile.Profile()
           pr.enable()
           result = func(*args, **kwargs)
           pr.disable()
           stats = pstats.Stats(pr)
           stats.sort_stats('cumulative').print_stats(10)
           return result
       return wrapper
   ```

---

如有问题或需要帮助，请联系运维团队或提交 [Issue](https://github.com/your-username/Agent-V3/issues)。