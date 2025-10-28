# 环境配置指南

本文档说明如何配置 Agent-V3 项目的环境变量。

---

## 📋 快速开始

### 1. 创建 `.env` 文件

在项目根目录创建 `.env` 文件：

```bash
cd /Users/xiaochenwu/Desktop/Agent-V3
touch .env
```

### 2. 填写配置

将以下内容复制到 `.env` 文件中，并填写实际值：

```bash
# ========================================
# Agent-V3 环境配置
# ========================================

# ========== 环境设置 ==========
ENVIRONMENT=development  # development, staging, production
DEBUG=false

# ========== N8N 配置 ==========
N8N_API_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key_here

# ========== Redis 配置 ==========
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_TTL=86400  # 24小时

# ========== LLM 配置 - SiliconFlow ==========
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_DEFAULT_MODEL=Pro/deepseek-ai/DeepSeek-V3.1-Terminus

# ========== LLM 配置 - OpenAI ==========
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# ========== LLM 配置 - Anthropic ==========
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ========== LLM 配置 - Ollama ==========
OLLAMA_BASE_URL=http://localhost:11434

# ========== 执行限制 ==========
MAX_ITERATIONS=25
MAX_EXECUTION_TIME=180  # 秒
MAX_TOKENS=4000
TIMEOUT=120  # 秒

# ========== CrewAI 配置 ==========
CREWAI_MAX_TOKENS=8000
CREWAI_TIMEOUT=60
CREWAI_TEMPERATURE=0.7

# ========== 日志配置 ==========
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json, text
```

### 3. 验证配置

运行以下命令验证配置是否正确：

```bash
python -c "from src.config.env_manager import EnvManager; EnvManager.print_config_summary()"
```

---

## 🔧 配置项说明

### N8N 配置

- `N8N_API_URL`: n8n 实例的 API 地址
  - 默认: `http://localhost:5678`
  - Docker: `http://localhost:5678`
  - 远程: `https://your-n8n-domain.com`

- `N8N_API_KEY`: n8n API 密钥
  - 获取方式: n8n 设置 → API → 创建 API Key
  - **必须配置**，否则 n8n 工具无法使用

### Redis 配置

- `REDIS_HOST`: Redis 主机地址
  - 本地: `localhost`
  - Docker: `redis` (容器名)
  - 远程: IP 或域名

- `REDIS_PORT`: Redis 端口
  - 默认: `6379`

- `REDIS_DB`: Redis 数据库编号
  - 默认: `0`
  - 范围: 0-15

- `REDIS_PASSWORD`: Redis 密码
  - 如果 Redis 没有设置密码，留空

- `REDIS_TTL`: 对话历史过期时间（秒）
  - 默认: `86400` (24小时)

### LLM 配置

#### SiliconFlow（推荐）

- `SILICONFLOW_API_KEY`: API 密钥
  - 获取: https://cloud.siliconflow.cn
  - **必须配置**

- `SILICONFLOW_DEFAULT_MODEL`: 默认模型
  - 推荐: `Pro/deepseek-ai/DeepSeek-V3.1-Terminus`

#### OpenAI

- `OPENAI_API_KEY`: OpenAI API 密钥
  - 获取: https://platform.openai.com/api-keys
  - 可选（如果使用 OpenAI）

#### Anthropic

- `ANTHROPIC_API_KEY`: Anthropic API 密钥
  - 获取: https://console.anthropic.com
  - 可选（如果使用 Claude）

#### Ollama

- `OLLAMA_BASE_URL`: Ollama 服务地址
  - 默认: `http://localhost:11434`
  - 需要本地运行 Ollama

### 执行限制

- `MAX_ITERATIONS`: 单次执行最大迭代次数
  - 默认: `25`
  - 建议: 25-50

- `MAX_EXECUTION_TIME`: 单次执行最大时间（秒）
  - 默认: `180` (3分钟)
  - 建议: 120-300

- `MAX_TOKENS`: LLM 最大输出 tokens
  - 默认: `4000`
  - 建议: 4000-8000

- `TIMEOUT`: 单次请求超时（秒）
  - 默认: `120`
  - 建议: 60-180

### CrewAI 配置

- `CREWAI_MAX_TOKENS`: CrewAI 最大 tokens
  - 默认: `8000`
  - 建议: 8000-16000（防止输出截断）

- `CREWAI_TIMEOUT`: CrewAI 超时时间
  - 默认: `60`
  - 建议: 60-120

- `CREWAI_TEMPERATURE`: CrewAI 温度参数
  - 默认: `0.7`
  - 范围: 0.0-1.0

### 日志配置

- `LOG_LEVEL`: 日志级别
  - 选项: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - 开发: `DEBUG` 或 `INFO`
  - 生产: `WARNING` 或 `ERROR`

- `LOG_FORMAT`: 日志格式
  - 选项: `json`, `text`
  - 推荐: `json`（便于日志分析）

---

## 🌍 多环境配置

### 开发环境

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
MAX_ITERATIONS=25
```

### 测试环境

```bash
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
MAX_ITERATIONS=30
```

### 生产环境

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
MAX_ITERATIONS=50
MAX_EXECUTION_TIME=300
```

---

## 🔒 安全建议

1. **永远不要提交 `.env` 文件到 Git**
   - `.env` 已在 `.gitignore` 中
   - 确认: `git status` 不应显示 `.env`

2. **使用强密码**
   - Redis 密码
   - n8n API Key

3. **限制 API 访问**
   - 使用 IP 白名单
   - 定期轮换 API Keys

4. **环境隔离**
   - 开发/测试/生产使用不同的 API Keys
   - 不同环境使用不同的 Redis 数据库

---

## 📝 示例配置

### 最小配置（本地开发）

```bash
# 仅配置必需项
N8N_API_URL=http://localhost:5678
N8N_API_KEY=n8n_api_abc123
SILICONFLOW_API_KEY=sk-abc123
REDIS_HOST=localhost
```

### 完整配置（生产环境）

```bash
ENVIRONMENT=production
DEBUG=false

# n8n
N8N_API_URL=https://n8n.your-domain.com
N8N_API_KEY=n8n_prod_key_xxxxx

# Redis (远程)
REDIS_HOST=redis.your-domain.com
REDIS_PORT=6379
REDIS_PASSWORD=strong_password_here
REDIS_DB=1
REDIS_TTL=7200

# LLM
SILICONFLOW_API_KEY=sk-prod-xxxxx
OPENAI_API_KEY=sk-xxxxx

# 执行限制
MAX_ITERATIONS=50
MAX_EXECUTION_TIME=300
MAX_TOKENS=8000
TIMEOUT=180

# CrewAI
CREWAI_MAX_TOKENS=16000
CREWAI_TIMEOUT=120

# 日志
LOG_LEVEL=WARNING
LOG_FORMAT=json
```

---

## 🛠️ 故障排除

### 问题 1: n8n 工具无法使用

**原因**: `N8N_API_KEY` 未配置或错误

**解决**:
```bash
# 1. 检查配置
python -c "from src.config.env_manager import EnvManager; print(EnvManager.N8N_API_KEY)"

# 2. 验证 API Key
curl -H "X-N8N-API-KEY: your_key_here" http://localhost:5678/api/v1/workflows

# 3. 更新 .env 文件
N8N_API_KEY=正确的API密钥
```

### 问题 2: Redis 连接失败

**原因**: Redis 未运行或配置错误

**解决**:
```bash
# 1. 检查 Redis 是否运行
redis-cli ping  # 应返回 PONG

# 2. 启动 Redis (Docker)
docker run -d -p 6379:6379 redis:latest

# 3. 验证配置
python -c "from src.config.env_manager import EnvManager; print(EnvManager.get_redis_url())"
```

### 问题 3: LLM API 调用失败

**原因**: API Key 错误或网络问题

**解决**:
```bash
# 1. 验证 API Key
python -c "from src.config.env_manager import EnvManager; print(EnvManager.SILICONFLOW_API_KEY[:10])"

# 2. 测试网络连接
curl https://api.siliconflow.cn/v1/models

# 3. 检查配置
python -c "from src.config.env_manager import EnvManager; EnvManager.validate_config()"
```

---

## 📚 相关文档

- `src/config/env_manager.py` - 环境变量管理器源码
- `PHASE2_3_SUMMARY.md` - Phase 2 优化总结
- `README.md` - 项目主文档

---

## ✅ 配置检查清单

使用此清单确保配置完整：

- [ ] 创建 `.env` 文件
- [ ] 配置 `N8N_API_KEY`
- [ ] 配置至少一个 LLM API Key
- [ ] 验证 Redis 连接
- [ ] 运行配置验证命令
- [ ] 确认 `.env` 不在 Git 中
- [ ] 备份 `.env` 文件到安全位置

---

**配置完成后**，运行以下命令验证：

```bash
python -c "
from src.config.env_manager import EnvManager
EnvManager.print_config_summary()
result = EnvManager.validate_config()
print('\n验证结果:')
for service, is_valid in result.items():
    status = '✅' if is_valid else '❌'
    print(f'  {status} {service}')
"
```

如果所有服务都显示 ✅，说明配置完成！

