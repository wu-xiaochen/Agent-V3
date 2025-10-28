# Agent-V3 项目结构说明

## 📁 目录结构

```
Agent-V3/
├── config/                          # 配置文件（核心）
│   ├── base/                        # 基础配置
│   │   ├── agents.yaml             # 智能体配置
│   │   ├── prompts.yaml            # 提示词配置
│   │   ├── services.yaml           # 服务配置（LLM、Redis等）
│   │   ├── logging.yaml            # 日志配置
│   │   ├── database.yaml           # 数据库配置
│   │   └── README.md               # 基础配置说明
│   ├── environments/               # 环境配置
│   │   ├── development.yaml        # 开发环境
│   │   ├── staging.yaml            # 预发环境
│   │   ├── production.yaml         # 生产环境
│   │   └── README.md               # 环境配置说明
│   ├── examples/                   # 配置示例
│   │   └── crewai_configs/         # CrewAI配置示例
│   ├── schemas/                    # 配置Schema
│   │   └── README.md
│   └── tools/                      # 工具配置
│       ├── tools_config.json       # 主工具配置
│       └── README.md               # 工具配置说明
│
├── src/                            # 源代码（核心）
│   ├── agents/                     # 智能体层
│   │   ├── contracts/             # 智能体契约/接口
│   │   ├── factories/             # 智能体工厂
│   │   ├── shared/                # 共享组件
│   │   │   ├── tools.py           # 工具管理
│   │   │   ├── dynamic_tool_loader.py  # 动态工具加载
│   │   │   ├── mcp_stdio_tool.py  # MCP Stdio工具
│   │   │   ├── api_tool.py        # API工具
│   │   │   └── output_formatter.py # 输出格式化
│   │   ├── supply_chain/          # 供应链智能体
│   │   │   └── supply_chain_agent.py
│   │   └── unified/               # 统一智能体
│   │       └── unified_agent.py
│   │
│   ├── config/                    # 配置加载器
│   │   └── config_loader.py
│   │
│   ├── core/                      # 核心业务逻辑
│   │   ├── domain/                # 领域模型
│   │   └── services/              # 核心服务
│   │
│   ├── infrastructure/            # 基础设施层
│   │   ├── llm/                  # LLM工厂
│   │   ├── cache/                # 缓存服务
│   │   ├── database/             # 数据库服务
│   │   ├── embedding/            # 向量嵌入
│   │   └── vector_store/         # 向量存储
│   │
│   ├── interfaces/                # 接口适配层
│   │   ├── api/                  # API接口
│   │   ├── events/               # 事件处理
│   │   ├── crewai_runtime.py     # CrewAI运行时
│   │   └── crewai_config_template.py  # CrewAI配置模板
│   │
│   ├── prompts/                   # 提示词管理
│   │   ├── prompt_loader.py      # 提示词加载器
│   │   ├── prompts.py            # 提示词定义
│   │   └── supply_chain_prompts.py  # 供应链提示词
│   │
│   ├── shared/                    # 共享组件
│   │   ├── exceptions/           # 异常定义
│   │   ├── types/                # 类型定义
│   │   ├── utils/                # 工具函数
│   │   └── debug_filter.py       # 调试过滤器
│   │
│   ├── storage/                   # 存储层
│   │   └── redis_chat_history.py # Redis记忆存储
│   │
│   ├── tools/                     # 专业工具
│   │   ├── supply_chain_tools.py # 供应链工具
│   │   ├── crewai_generator.py   # CrewAI生成器
│   │   ├── crewai_runtime_tool.py # CrewAI运行工具
│   │   └── crewai_config_validator.py  # 配置验证
│   │
│   └── utils/                     # 工具模块
│       ├── check_services_config.py
│       ├── debug_config.py
│       └── debug_tools.py
│
├── tests/                         # 测试套件（核心）
│   ├── comprehensive/            # 综合测试
│   │   ├── test_agent_core_functionality.py  # 核心功能测试
│   │   └── test_system_integration.py        # 系统集成测试
│   ├── integration/              # 集成测试
│   │   ├── test_n8n_mcp_integration.py
│   │   └── test_supply_chain_comprehensive.py
│   ├── supply_chain/             # 供应链测试
│   │   └── test_supply_chain_workflow.py
│   ├── unit/                     # 单元测试
│   │   ├── agents/
│   │   └── test_*.py
│   ├── config/                   # 配置测试
│   ├── tools/                    # 工具测试
│   ├── agents/                   # 智能体测试
│   └── test_all.py              # 测试运行器
│
├── docs/                         # 文档（核心）
│   ├── api/                      # API文档
│   │   ├── api_reference.md
│   │   └── README.md
│   ├── deployment/               # 部署文档
│   │   ├── deployment_guide.md
│   │   └── README.md
│   ├── development/              # 开发文档
│   │   ├── project_rules.md     # 项目规则
│   │   └── README.md
│   ├── ARCHITECTURE.md           # 架构文档
│   ├── QUICKSTART.md            # 快速开始
│   ├── TESTING.md               # 测试指南
│   ├── PROJECT_STRUCTURE.md     # 项目结构（本文档）
│   └── README.md                # 文档索引
│
├── examples/                     # 示例代码
│   ├── example_unified_agent.py      # 统一智能体示例
│   ├── example_supply_chain_agent.py # 供应链智能体示例
│   └── example_crewai_usage.py       # CrewAI使用示例
│
├── scripts/                      # 运维脚本
│   ├── setup/                    # 安装脚本
│   │   ├── quick_start.sh
│   │   ├── quick_start.bat
│   │   ├── start.sh
│   │   ├── start.bat
│   │   └── setup_postgresql.sh
│   ├── deployment/               # 部署脚本
│   │   └── README.md
│   ├── maintenance/              # 维护脚本
│   │   └── README.md
│   ├── monitoring/               # 监控脚本
│   │   └── README.md
│   └── README.md
│
├── requirements/                 # 依赖管理
│   ├── base.yaml                # 基础依赖
│   ├── development.yaml         # 开发依赖
│   ├── production.yaml          # 生产依赖
│   └── README.md
│
├── logs/                         # 日志目录
│   └── agent.log
│
├── .github/                      # GitHub配置
│   └── workflows/               # CI/CD工作流
│
├── main.py                       # 程序入口
├── verify_project.py            # 项目验证脚本
├── requirements.txt             # Python依赖
├── README.md                    # 项目主文档
├── PROJECT_SUMMARY.md           # 项目总结
├── CONTRIBUTING.md              # 贡献指南
├── docker-compose.yml           # Docker编排
├── Dockerfile                   # Docker镜像
└── pyproject.toml              # Python项目配置
```

## 🎯 核心模块说明

### 1. 配置系统 (`config/`)
- **用途**：统一管理所有配置，支持多环境
- **特点**：分层配置、环境变量支持、热更新
- **关键文件**：
  - `agents.yaml` - 智能体配置
  - `prompts.yaml` - 提示词配置
  - `services.yaml` - 服务配置
  - `tools_config.json` - 工具配置

### 2. 智能体层 (`src/agents/`)
- **用途**：智能体实现和管理
- **架构**：
  - `unified/` - 通用智能体
  - `supply_chain/` - 供应链专业智能体
  - `shared/` - 共享组件（工具、格式化等）
- **设计模式**：工厂模式、策略模式

### 3. 基础设施层 (`src/infrastructure/`)
- **用途**：提供底层服务支持
- **包含**：
  - LLM工厂 - 多提供商支持
  - 缓存服务 - Redis集成
  - 向量存储 - 知识库支持

### 4. 存储层 (`src/storage/`)
- **用途**：数据持久化
- **核心**：Redis对话历史存储
- **特点**：会话管理、TTL支持、分布式

### 5. 工具系统 (`src/tools/` + `src/agents/shared/`)
- **用途**：专业工具和工具管理
- **类型**：
  - 内置工具（时间、计算器、搜索）
  - 供应链工具（分析、预测、优化）
  - 集成工具（CrewAI、n8n）
- **特点**：动态加载、配置驱动

### 6. 测试系统 (`tests/`)
- **覆盖**：单元、集成、端到端
- **组织**：
  - `comprehensive/` - 完整功能测试
  - `integration/` - 集成测试
  - `unit/` - 单元测试
- **工具**：pytest、pytest-asyncio

### 7. 文档系统 (`docs/`)
- **结构**：
  - 快速开始 - QUICKSTART.md
  - 架构设计 - ARCHITECTURE.md
  - 测试指南 - TESTING.md
  - API参考 - api/
  - 部署指南 - deployment/

## 📊 文件命名规范

### Python文件
- 模块文件：`小写_下划线.py`
- 类文件：`PascalCase.py` (如 `UnifiedAgent`)
- 测试文件：`test_*.py`

### 配置文件
- YAML配置：`小写.yaml`
- JSON配置：`小写_下划线.json`
- 环境配置：`环境名.yaml`

### 文档文件
- Markdown：`UPPERCASE.md` 或 `小写_下划线.md`
- 主文档：大写（如 `README.md`）
- 子文档：小写下划线（如 `api_reference.md`）

## 🔄 数据流向

```
用户输入
   ↓
main.py (入口)
   ↓
UnifiedAgent/SupplyChainAgent (智能体层)
   ↓
├─→ Config Loader (配置)
├─→ LLM Factory (LLM服务)
├─→ Tool System (工具调用)
├─→ Redis Storage (记忆存储)
└─→ Output Formatter (格式化)
   ↓
用户输出
```

## 🎨 设计原则

1. **分层架构**：清晰的层次划分
2. **配置驱动**：避免硬编码
3. **依赖注入**：解耦组件
4. **接口隔离**：单一职责
5. **测试优先**：高测试覆盖
6. **文档完整**：每层都有文档

## 🚀 扩展指南

### 添加新智能体
1. 在 `src/agents/` 创建新目录
2. 实现智能体类
3. 在 `config/base/agents.yaml` 添加配置
4. 在 `config/base/prompts.yaml` 添加提示词
5. 编写测试用例

### 添加新工具
1. 在 `src/tools/` 创建工具类
2. 在 `src/agents/shared/tools.py` 注册
3. 在 `config/tools/tools_config.json` 配置
4. 编写测试用例

### 添加新配置
1. 在 `config/base/` 添加YAML文件
2. 在 `config_loader.py` 添加加载方法
3. 更新文档

## 📝 维护建议

1. **定期更新依赖**：`pip list --outdated`
2. **运行测试**：`pytest tests/`
3. **检查覆盖率**：`pytest --cov=src`
4. **验证项目**：`python verify_project.py`
5. **更新文档**：保持文档同步

## 🔍 查找文件

- **智能体相关**：`src/agents/`
- **配置相关**：`config/`
- **测试相关**：`tests/`
- **文档相关**：`docs/`
- **工具相关**：`src/tools/` 和 `src/agents/shared/`

---

**保持项目结构清晰，代码组织有序！**

