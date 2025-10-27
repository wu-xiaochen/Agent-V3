# Agent-V3: 智能体系统

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/wu-xiaochen/Agent-V3/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellow.svg)](https://codecov.io/gh/wu-xiaochen/Agent-V3)

Agent-V3 是一个基于大语言模型的智能体系统，提供统一的智能体框架和多种专用智能体，支持复杂任务处理和智能决策。

## 🌟 特性

- **统一智能体框架**: 提供统一的智能体架构和接口，支持快速开发和部署
- **多种专用智能体**: 内置供应链、客服、分析等多种专用智能体
- **灵活的配置管理**: 支持多环境配置和动态配置更新
- **强大的提示词管理**: 提供提示词加载、版本管理和优化功能
- **高性能执行**: 基于 ReAct 架构，支持工具调用和复杂推理
- **可扩展设计**: 支持自定义智能体、工具和提示词
- **完整的监控和日志**: 提供全面的系统监控和日志记录
- **支持多种LLM提供商**: OpenAI、Anthropic Claude、Hugging Face、硅基流动等

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Redis 6.0 或更高版本（可选，用于会话存储）
- PostgreSQL 12 或更高版本（可选，用于持久化存储）

### 安装

1. 克隆仓库
```bash
git clone https://github.com/wu-xiaochen/Agent-V3.git
cd Agent-V3
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements/base.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

### 基本使用

```python
from src.agents.unified.unified_agent import UnifiedAgent
from src.config.config_loader import config_loader

# 创建统一智能体
agent = UnifiedAgent()

# 运行智能体
response = agent.run("帮我分析一下最近的供应链风险")
print(response)
```

### 使用专用智能体

```python
from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent

# 创建供应链智能体
agent = SupplyChainAgent()

# 运行智能体
response = agent.run("分析当前供应链中的潜在风险点")
print(response)
```

### 交互模式

```bash
python main.py --interactive
# 或者
python main.py -i
```

### 单次查询模式

```bash
python main.py --query "你的问题"
```

### 指定LLM提供商

```bash
python main.py --provider openai --interactive
python main.py --provider anthropic --query "你的问题"
python main.py --provider siliconflow --interactive
```

### 使用自定义配置文件

```bash
python main.py --config /path/to/your/config.yaml --interactive
```

## 📁 项目结构

```
Agent-V3/
├── config/                           # 配置文件目录
│   ├── base/                         # 基础配置
│   │   ├── agents.yaml              # Agent基础配置
│   │   ├── database.yaml            # 数据库配置
│   │   ├── logging.yaml             # 日志配置
│   │   └── services.yaml            # 服务配置
│   ├── environments/                # 环境配置
│   │   ├── development.yaml         # 开发环境
│   │   ├── staging.yaml             # 预发环境
│   │   └── production.yaml          # 生产环境
│   └── schemas/                     # 配置Schema
├── src/
│   ├── agents/                       # Agent实现层
│   │   ├── {agent_name}/            # 每个Agent独立目录
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # Agent主逻辑
│   │   ├── contracts/               # Agent契约定义
│   │   ├── factories/               # Agent工厂
│   │   └── supply_chain_agent.py    # 供应链智能体实现
│   ├── core/                        # 核心业务逻辑
│   │   ├── domain/                  # 领域模型
│   │   └── services/                # 核心服务
│   ├── infrastructure/              # 基础设施层
│   │   ├── database/
│   │   ├── cache/
│   │   └── external/
│   ├── interfaces/                  # 接口适配层
│   │   ├── api/                     # API接口
│   │   └── events/                  # 事件处理
│   ├── shared/                      # 共享组件
│   │   ├── utils/
│   │   ├── exceptions/
│   │   └── types/
│   ├── agent/                       # 统一智能体
│   │   └── unified_agent.py
│   ├── config/                      # 配置管理
│   │   └── config_loader.py
│   ├── llm/                         # LLM管理
│   │   ├── llm_factory.py
│   │   └── llm_manager.py
│   ├── prompts/                     # 提示词管理
│   │   ├── prompt_loader.py
│   │   └── prompt_optimizer.py
│   ├── tools/                       # 工具管理
│   │   ├── tool_manager.py
│   │   └── tools/
│   └── main.py                      # 应用入口
├── tests/
│   ├── unit/                        # 单元测试
│   ├── integration/                 # 集成测试
│   ├── e2e/                         # 端到端测试
│   └── fixtures/                    # 测试数据
├── docs/                            # 项目文档
│   ├── api/                         # API文档
│   ├── deployment/                  # 部署文档
│   └── development/                 # 开发文档
├── scripts/                         # 运维脚本
│   ├── deployment/
│   ├── monitoring/
│   └── maintenance/
├── .github/                         # CI/CD配置
│   └── workflows/
├── prompts/                         # 提示词文件
│   ├── unified_agent/
│   ├── supply_chain_agent/
│   └── common/
├── requirements/                    # 依赖管理
│   ├── base.yaml
│   ├── development.yaml
│   └── production.yaml
├── .env.example                     # 环境变量示例
├── docker-compose.yml               # Docker编排文件
├── Dockerfile                       # Docker镜像构建文件
├── README.md                        # 项目说明
└── LICENSE                          # 许可证
```

## 🔧 配置

### 环境变量

创建 `.env` 文件并设置以下环境变量：

```bash
# LLM配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
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

### LLM配置

支持多种LLM提供商：OpenAI、Anthropic、Hugging Face和硅基流动。每种提供商都有自己的配置选项：

- `api_key`: API密钥
- `base_url`: (仅OpenAI) API基础URL，默认为"https://api.openai.com/v1"，可修改为OpenAI兼容的API地址
- `model`: 模型名称
- `temperature`: 温度参数（控制随机性）
- `max_tokens`: 最大令牌数

#### 使用OpenAI兼容模型

要使用OpenAI兼容的模型（如本地部署的模型或其他API服务），只需修改配置中的`base_url`：

```yaml
openai:
  api_key: "your-api-key"
  base_url: "https://your-api-endpoint.com/v1"  # 修改为您的API端点
  model: "your-model-name"
  # ... 其他配置
```

这样配置后，智能体将使用您指定的API端点，而不是默认的OpenAI API。

## 🧪 测试

运行测试：

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行端到端测试
pytest tests/e2e/

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 📚 文档

- [API文档](docs/api/api_reference.md)
- [开发指南](docs/development/development_guide.md)
- [部署指南](docs/deployment/deployment_guide.md)
- [项目规则](docs/development/project_rules.md)
- [贡献指南](CONTRIBUTING.md)

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与项目。

### 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 🐳 Docker 部署

使用 Docker 快速部署：

```bash
# 构建镜像
docker build -t agent-v3 .

# 运行容器
docker run -p 8000:8000 --env-file .env agent-v3

# 或使用 docker-compose
docker-compose up -d
```

## ☸️ Kubernetes 部署

使用 Kubernetes 部署：

```bash
# 应用配置
kubectl apply -f k8s/

# 查看状态
kubectl get pods -n agent-v3
```

## 📊 监控

系统提供全面的监控和日志功能：

- 应用性能监控
- 错误追踪
- 日志聚合
- 健康检查

访问监控仪表板：http://your-domain.com/monitoring

## 🆘 支持

如果您遇到问题或有疑问：

1. 查看 [FAQ](docs/faq.md)
2. 搜索 [Issues](https://github.com/wu-xiaochen/Agent-V3/issues)
3. 创建新的 [Issue](https://github.com/wu-xiaochen/Agent-V3/issues/new)
4. 联系维护团队

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和社区成员！

---

如果这个项目对您有帮助，请给我们一个 ⭐️！