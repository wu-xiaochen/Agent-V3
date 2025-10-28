# Agent-V3 系统架构文档

## 📐 架构概览

Agent-V3 采用**分层架构**和**领域驱动设计**，专注于供应链智能体系统的构建和运行。

```
┌────────────────────────────────────────────────────────────┐
│                       用户接口层                            │
│              (CLI / API / Web Interface)                   │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                       智能体层                              │
│         UnifiedAgent  │  SupplyChainAgent                  │
│         (ReAct Architecture + LangChain)                   │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                    工具和服务层                             │
│  Built-in Tools │ Supply Chain Tools │ Integration Tools  │
│  (Calculator, Search)  │  (Analyzer, Forecasting)         │
│                   │  (CrewAI, n8n)                         │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                    基础设施层                               │
│  LLM Factory │ Redis Store │ Config Loader │ Formatters   │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                    外部服务层                               │
│  OpenAI/SiliconFlow │ Redis │ n8n │ Search APIs           │
└────────────────────────────────────────────────────────────┘
```

## 🎯 架构设计原则

### 1. 分层架构
- **接口层**：处理用户交互
- **智能体层**：实现智能体逻辑
- **服务层**：提供工具和服务
- **基础设施层**：底层技术支持
- **外部服务层**：第三方集成

### 2. 配置驱动
- 所有配置外部化
- 支持多环境配置
- 环境变量覆盖
- 零硬编码

### 3. 依赖注入
- 构造函数注入
- 接口隔离
- 松耦合设计

### 4. 可测试性
- 单元测试覆盖
- 集成测试验证
- 端到端测试
- Mock友好设计

### 5. 可扩展性
- 插件式工具系统
- 动态加载机制
- 模块化设计
- 清晰的扩展点

## 🏗️ 核心组件

### 1. 智能体层 (Agents Layer)

#### UnifiedAgent
**职责**: 通用智能体，处理各类任务

```python
class UnifiedAgent:
    def __init__(
        self,
        provider: Optional[str] = None,
        memory: bool = True,
        redis_url: Optional[str] = None,
        session_id: Optional[str] = None,
        model_name: Optional[str] = None,
        tools: Optional[List[str]] = None,
        **kwargs
    )
```

**特性**:
- ReAct架构
- 多轮对话记忆
- 工具调用能力
- 可配置输出格式
- Redis持久化

**工作流程**:
```
用户输入 → 加载配置 → 创建LLM → 加载工具 → 创建智能体 
         → ReAct推理 → 工具调用 → 格式化输出
```

#### SupplyChainAgent
**职责**: 供应链专业智能体

**特性**:
- 供应链领域知识
- 业务流程规划
- CrewAI配置生成
- 多阶段对话管理

**对话状态**:
- `需求收集` → `方案生成` → `方案确认` → `配置生成`

### 2. 工具系统 (Tool System)

#### 工具分类

**Built-in Tools** (内置工具):
- `TimeTool`: 获取时间
- `SearchTool`: 网络搜索
- `CalculatorTool`: 数学计算

**Supply Chain Tools** (供应链工具):
- `DataAnalyzerTool`: 数据分析
- `ForecastingTool`: 需求预测
- `OptimizationTool`: 优化引擎
- `RiskAssessmentTool`: 风险评估

**Integration Tools** (集成工具):
- `CrewAIGeneratorTool`: CrewAI配置生成
- `CrewAIRuntimeTool`: CrewAI运行时
- `N8NMCPTool`: n8n工作流生成

#### 动态工具加载

```python
# config/tools/tools_config.json
{
  "tools": [
    {
      "type": "builtin",
      "name": "calculator",
      "enabled": true
    },
    {
      "type": "mcp_stdio",
      "name": "n8n_mcp_generator",
      "command": "docker",
      "args": ["exec", "n8n-mcp", "node", "dist/mcp/index.js"],
      "enabled": true
    }
  ],
  "agent_tool_mapping": {
    "unified_agent": ["calculator", "search", "n8n_mcp_generator"]
  }
}
```

**加载流程**:
```
读取配置 → 解析工具定义 → 实例化工具 
        → 注册到智能体 → 运行时调用
```

### 3. 配置系统 (Configuration System)

#### 配置分层

```
config/
├── base/                       # 基础配置（最低优先级）
│   ├── agents.yaml            # 智能体配置
│   ├── prompts.yaml           # 提示词配置
│   ├── services.yaml          # 服务配置
│   ├── logging.yaml           # 日志配置
│   └── database.yaml          # 数据库配置
├── environments/              # 环境配置（中优先级）
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
└── tools/                     # 工具配置
    └── tools_config.json
```

#### 配置加载流程

```python
config_loader = ConfigLoader(env="development")
# 加载顺序：
# 1. base/*.yaml
# 2. environments/{env}.yaml
# 3. 环境变量覆盖
```

**优先级**: 环境变量 > 环境配置 > 基础配置

#### 配置示例

```yaml
# config/base/agents.yaml
agents:
  unified_agent:
    enabled: true
    model: "Pro/deepseek-ai/DeepSeek-V3.1-Terminus"
    system_prompt: "supply_chain_planning"
    parameters:
      temperature: 0.7
      max_tokens: 4000
    tools:
      - calculator
      - search
      - time
      - n8n_mcp_generator
    memory:
      enabled: true
      type: "redis"
```

### 4. 存储层 (Storage Layer)

#### Redis Chat History

**功能**:
- 对话历史持久化
- 会话管理
- TTL自动过期
- 分布式支持

**实现**:
```python
from src.storage.redis_chat_history import RedisChatMessageHistory

history = RedisChatMessageHistory(
    session_id="user123",
    url="redis://localhost:6379/0",
    ttl=3600
)
```

**数据结构**:
```
Key: agent:chat:{session_id}
Type: List
Value: [
    {"type": "human", "content": "..."},
    {"type": "ai", "content": "..."}
]
TTL: 3600 seconds
```

### 5. LLM工厂 (LLM Factory)

#### 多提供商支持

```python
from src.infrastructure.llm.llm_factory import LLMFactory

# 创建LLM实例
llm = LLMFactory.create_llm(
    provider="siliconflow",
    model_name="deepseek-chat",
    temperature=0.7
)
```

**支持的提供商**:
- OpenAI (GPT-3.5, GPT-4)
- SiliconFlow (Qwen, DeepSeek)
- Anthropic (Claude)
- HuggingFace (本地模型)

**配置示例**:
```yaml
# config/base/services.yaml
services:
  llm:
    provider: "siliconflow"
    default_model: "deepseek-chat"
    parameters:
      temperature: 0.7
      max_tokens: 4000
    api_keys:
      openai: "${OPENAI_API_KEY}"
      siliconflow: "${SILICONFLOW_API_KEY}"
```

### 6. 提示词管理 (Prompt Management)

#### 提示词配置

```yaml
# config/base/prompts.yaml
prompts:
  supply_chain_planning:
    name: "供应链业务流程规划提示词"
    template: |
      你是一位专业的供应链管理专家...
      
      <核心职责>
      - 理解用户需求
      - 生成业务流程规划
      - 与用户确认方案
      </核心职责>
      
      <工具使用指南>
      - 使用n8n_mcp_generator生成工作流
      - 使用crewai_generator生成团队配置
      </工具使用指南>
```

#### 提示词加载

```python
from src.prompts.prompt_loader import PromptLoader

loader = PromptLoader()
prompt = loader.get_prompt("supply_chain_planning")
```

## 🔄 数据流

### 完整请求流程

```
┌─────────────┐
│  用户输入   │
└──────┬──────┘
       ↓
┌──────────────────────────────────────┐
│  main.py (入口)                      │
│  - 参数解析                          │
│  - 日志初始化                        │
│  - 智能体创建                        │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  UnifiedAgent.__init__()             │
│  - 加载配置 (ConfigLoader)          │
│  - 创建LLM (LLMFactory)             │
│  - 加载工具 (DynamicToolLoader)    │
│  - 创建记忆 (RedisChatHistory)     │
│  - 初始化智能体 (create_agent)     │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  UnifiedAgent.run(query)             │
│  - 创建执行器 (AgentExecutor)       │
│  - 添加记忆管理                      │
│  - 执行查询                          │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  ReAct Loop                          │
│  1. Thought: 分析问题                │
│  2. Action: 选择工具                 │
│  3. Action Input: 准备参数           │
│  4. Observation: 执行并获取结果      │
│  5. Final Answer: 生成最终答案       │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Tool Execution                      │
│  - 内置工具 (Built-in)              │
│  - MCP工具 (MCP Stdio)              │
│  - API工具 (REST API)               │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Response Formatting                 │
│  - 正常文本 (normal)                │
│  - Markdown (markdown)              │
│  - JSON (json)                      │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Memory Storage (Redis)              │
│  - 保存对话历史                      │
│  - 设置TTL                           │
└──────┬───────────────────────────────┘
       ↓
┌─────────────┐
│  用户输出   │
└─────────────┘
```

### 工具调用流程

```
智能体 → Tool Router → Tool Selector
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                  ↓                   ↓
  Built-in Tool      API Tool           MCP Tool
        ↓                  ↓                   ↓
  直接执行        HTTP Request      Stdio Communication
        ↓                  ↓                   ↓
        └──────────────────┬──────────────────┘
                           ↓
                      Tool Result
                           ↓
                       智能体
```

## 🔌 集成系统

### n8n工作流集成

**通信方式**: MCP (Model Context Protocol) Stdio

**配置**:
```json
{
  "type": "mcp_stdio",
  "name": "n8n_mcp_generator",
  "command": "docker",
  "args": ["exec", "n8n-mcp", "node", "dist/mcp/index.js"],
  "env": {
    "N8N_API_URL": "http://host.docker.internal:5678",
    "N8N_API_KEY": "your_api_key"
  }
}
```

**可用工具**:
- `n8n_search_nodes`: 搜索n8n节点
- `n8n_get_node_info`: 获取节点信息
- `n8n_generate_workflow`: 生成工作流
- `n8n_validate_workflow`: 验证工作流
- `n8n_deploy_workflow`: 部署工作流

### CrewAI集成

**功能**:
- 生成团队配置
- 定义角色和任务
- 运行多智能体协作

**配置模板**:
```json
{
  "name": "供应链优化团队",
  "agents": [
    {
      "role": "数据分析师",
      "goal": "分析供应链数据",
      "backstory": "...",
      "tools": ["data_analyzer"]
    }
  ],
  "tasks": [...]
}
```

## 🧪 测试架构

### 测试金字塔

```
                  ┌─────────┐
                  │  E2E    │  10%
                  │  Tests  │
                ┌─┴─────────┴─┐
                │ Integration │  30%
                │   Tests     │
              ┌─┴─────────────┴─┐
              │  Unit Tests     │  60%
              └─────────────────┘
```

### 测试套件

1. **单元测试** (`tests/unit/`)
   - 独立组件测试
   - Mock外部依赖
   - 快速执行

2. **集成测试** (`tests/integration/`)
   - 组件协作测试
   - 真实依赖
   - n8n集成测试

3. **综合测试** (`tests/comprehensive/`)
   - 核心功能测试
   - 系统集成测试
   - 端到端场景

4. **供应链测试** (`tests/supply_chain/`)
   - 业务流程测试
   - 工作流验证

## 🔧 扩展点

### 1. 自定义智能体

```python
from src.agents.unified.unified_agent import UnifiedAgent

class MyCustomAgent(UnifiedAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 自定义初始化
    
    def custom_method(self):
        # 自定义功能
        pass
```

### 2. 自定义工具

```python
from langchain.tools import BaseTool

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "工具描述"
    
    def _run(self, query: str) -> str:
        # 实现工具逻辑
        return result
```

注册工具:
```python
# src/agents/shared/tools.py
TOOL_CLASSES = {
    "my_custom_tool": MyCustomTool,
    # ...
}
```

### 3. 自定义提示词

```yaml
# config/base/prompts.yaml
prompts:
  my_custom_prompt:
    name: "自定义提示词"
    template: |
      你是一个...
```

### 4. 自定义配置

```yaml
# config/base/my_config.yaml
my_service:
  enabled: true
  parameters:
    key: value
```

加载配置:
```python
# src/config/config_loader.py
def get_my_config(self):
    return self.config.get("my_service", {})
```

## 📊 性能优化

### 1. 缓存策略
- Redis缓存LLM响应
- 工具结果缓存
- 配置缓存

### 2. 并发处理
- 异步工具调用
- 批量请求处理
- 连接池管理

### 3. 资源管理
- 会话TTL管理
- 内存限制
- 超时控制

### 4. 监控指标
- 响应时间
- 工具调用次数
- 错误率
- 内存使用

## 🔒 安全性

### 1. API密钥管理
- 环境变量存储
- 加密传输
- 定期轮换

### 2. 输入验证
- 参数校验
- 注入防护
- 内容过滤

### 3. 访问控制
- 会话隔离
- 权限管理
- 审计日志

## 📈 可观测性

### 1. 日志系统
- 结构化日志
- 日志级别
- 日志轮转

### 2. 监控指标
- 系统指标
- 业务指标
- 自定义指标

### 3. 追踪系统
- 请求追踪
- 工具调用追踪
- 错误追踪

---

**架构持续演进中** | 最后更新：2025-10-28
