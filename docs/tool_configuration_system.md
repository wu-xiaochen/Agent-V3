# 智能体工具配置系统

本文档介绍如何使用智能体工具配置系统，该系统允许通过JSON配置文件灵活配置智能体可用的工具，包括内置工具、API工具和MCP工具。

## 目录结构

```
config/tools/
├── tools_config.json          # 主工具配置文件
└── environments/              # 环境特定配置
    ├── development.json
    ├── staging.json
    └── production.json
```

## 配置文件格式

### 基本结构

```json
{
  "version": "1.0",
  "description": "工具配置描述",
  "tools": [
    // 工具定义列表
  ],
  "tool_groups": {
    // 工具组定义
  },
  "agent_tool_mapping": {
    // 智能体工具映射
  }
}
```

### 工具类型

#### 1. 内置工具 (builtin)

```json
{
  "type": "builtin",
  "name": "time",
  "description": "获取当前时间",
  "enabled": true
}
```

可用的内置工具：
- `time`: 获取当前时间
- `search`: 网络搜索
- `calculator`: 数学计算
- `weather`: 天气查询
- `file_operations`: 文件操作
- `memory`: 记忆管理
- `code_interpreter`: 代码解释器
- `web_scraper`: 网页抓取
- `email`: 邮件发送
- `database`: 数据库操作

#### 2. API工具 (api)

```json
{
  "type": "api",
  "name": "weather_api",
  "description": "天气查询API",
  "url": "https://api.openweathermap.org/data/2.5/weather",
  "method": "GET",
  "auth_type": "api_key",
  "auth_config": {
    "key": "${WEATHER_API_KEY}",
    "header": "X-API-Key"
  },
  "parameters": {
    "q": {
      "type": "string",
      "description": "城市名称",
      "required": true
    },
    "units": {
      "type": "string",
      "description": "单位系统",
      "default": "metric"
    }
  },
  "response_mapping": {
    "temperature": "$.main.temp",
    "humidity": "$.main.humidity",
    "description": "$.weather[0].description",
    "city": "$.name"
  }
}
```

API工具配置字段：
- `url`: API端点URL
- `method`: HTTP方法 (GET, POST, PUT, DELETE)
- `auth_type`: 认证类型 (bearer, basic, api_key, none)
- `auth_config`: 认证配置
- `parameters`: 请求参数定义
- `response_mapping`: 响应数据映射 (使用JSONPath)
- `headers`: 自定义请求头
- `timeout`: 请求超时时间 (秒)
- `retry_count`: 重试次数

#### 3. MCP工具 (mcp)

```json
{
  "type": "mcp",
  "name": "n8n_workflow",
  "description": "N8N工作流执行工具",
  "server_url": "http://localhost:5678",
  "tool_name": "execute_workflow",
  "auth_type": "bearer",
  "auth_config": {
    "token": "${N8N_API_TOKEN}"
  },
  "parameters": {
    "workflow_id": {
      "type": "string",
      "description": "工作流ID",
      "required": true
    },
    "data": {
      "type": "object",
      "description": "输入数据",
      "default": {}
    }
  },
  "response_mapping": {
    "result": "$.result.data",
    "execution_id": "$.executionId",
    "status": "$.result.status"
  }
}
```

MCP工具配置字段：
- `server_url`: MCP服务器URL
- `tool_name`: 要调用的工具名称
- `auth_type`: 认证类型 (bearer, api_key, none)
- `auth_config`: 认证配置
- `parameters`: 工具参数定义
- `response_mapping`: 响应数据映射 (使用JSONPath)

### 工具组

工具组允许将多个工具组合在一起，便于批量引用：

```json
{
  "tool_groups": {
    "basic": ["time", "search", "calculator"],
    "external_apis": ["weather_api", "github_api"],
    "mcp_tools": ["n8n_workflow", "slack_mcp"],
    "all": ["time", "search", "calculator", "weather_api", "github_api", "n8n_workflow", "slack_mcp"]
  }
}
```

### 智能体工具映射

为不同的智能体指定可用的工具：

```json
{
  "agent_tool_mapping": {
    "unified_agent": ["time", "search", "calculator", "weather_api"],
    "api_agent": ["weather_api", "github_api"],
    "mcp_agent": ["n8n_workflow", "slack_mcp"],
    "dev_agent": ["time", "search", "calculator", "github_api"],
    "notification_agent": ["time", "slack_mcp"],
    "full_stack_agent": ["time", "search", "calculator", "weather_api", "github_api", "n8n_workflow", "slack_mcp"]
  }
}
```

## 环境变量

配置文件支持使用环境变量，格式为 `${VARIABLE_NAME}`：

```json
{
  "auth_config": {
    "key": "${WEATHER_API_KEY}",
    "header": "X-API-Key"
  }
}
```

## 使用方法

### 1. 加载所有工具

```python
from src.agents.shared.tools import get_tools

# 使用默认配置路径
tools = get_tools()

# 使用自定义配置路径
tools = get_tools(config_path="/path/to/tools_config.json")
```

### 2. 为特定智能体加载工具

```python
from src.agents.shared.tools import get_tools_for_agent

# 为unified_agent加载工具
tools = get_tools_for_agent("unified_agent")

# 使用自定义配置路径
tools = get_tools_for_agent("unified_agent", "/path/to/tools_config.json")
```

### 3. 在智能体中使用

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建智能体实例，自动加载配置的工具
agent = UnifiedAgent(
    llm=llm,
    memory=memory,
    # 工具将自动从配置加载
)
```

## 实现架构

### 核心组件

#### 1. 动态工具加载器 (DynamicToolLoader)

位置：`src/agents/shared/dynamic_tool_loader.py`

主要功能：
- 加载和解析工具配置文件
- 根据配置动态创建和实例化工具
- 支持环境变量解析
- 提供工具验证和错误处理

#### 2. API工具 (APITool)

位置：`src/agents/shared/api_tool.py`

主要功能：
- 实现HTTP API调用
- 支持多种认证方式（Bearer、Basic、API Key）
- 提供请求重试和错误处理
- 支持响应数据映射

#### 3. MCP工具 (MCPTool)

位置：`src/agents/shared/mcp_tool.py`

主要功能：
- 实现MCP协议工具调用
- 支持同步和异步调用
- 提供工具发现和模式获取
- 支持响应数据映射

#### 4. 工具集成 (tools.py)

位置：`src/agents/shared/tools.py`

主要功能：
- 提供统一的工具加载接口
- 集成动态工具加载器
- 支持智能体特定工具加载
- 提供默认工具列表

### 工具生命周期

1. 配置加载：从JSON文件读取工具配置
2. 环境变量解析：解析配置中的环境变量引用
3. 工具实例化：根据配置创建工具实例
4. 工具注册：将工具注册到智能体
5. 工具执行：智能体调用工具执行任务
6. 资源清理：释放工具占用的资源

## 配置示例

### 示例1: 基础配置

```json
{
  "version": "1.0",
  "description": "基础工具配置",
  "tools": [
    {
      "type": "builtin",
      "name": "time",
      "description": "获取当前时间",
      "enabled": true
    },
    {
      "type": "builtin",
      "name": "calculator",
      "description": "数学计算",
      "enabled": true
    }
  ],
  "tool_groups": {
    "basic": ["time", "calculator"]
  },
  "agent_tool_mapping": {
    "basic_agent": ["time", "calculator"]
  }
}
```

### 示例2: API工具配置

```json
{
  "version": "1.0",
  "description": "API工具配置",
  "tools": [
    {
      "type": "api",
      "name": "weather_api",
      "description": "天气查询API",
      "url": "https://api.openweathermap.org/data/2.5/weather",
      "method": "GET",
      "auth_type": "api_key",
      "auth_config": {
        "key": "${WEATHER_API_KEY}",
        "header": "X-API-Key"
      },
      "parameters": {
        "q": {
          "type": "string",
          "description": "城市名称",
          "required": true
        }
      },
      "response_mapping": {
        "temperature": "$.main.temp",
        "description": "$.weather[0].description"
      }
    }
  ]
}
```

### 示例3: MCP工具配置

```json
{
  "version": "1.0",
  "description": "MCP工具配置",
  "tools": [
    {
      "type": "mcp",
      "name": "n8n_workflow",
      "description": "N8N工作流执行",
      "server_url": "http://localhost:5678",
      "tool_name": "execute_workflow",
      "auth_type": "bearer",
      "auth_config": {
        "token": "${N8N_API_TOKEN}"
      },
      "parameters": {
        "workflow_id": {
          "type": "string",
          "description": "工作流ID",
          "required": true
        }
      },
      "response_mapping": {
        "result": "$.result.data",
        "execution_id": "$.executionId"
      }
    }
  ]
}
```

## 最佳实践

1. **环境分离**: 为不同环境创建不同的配置文件
2. **安全**: 使用环境变量存储敏感信息
3. **版本控制**: 为配置文件添加版本号
4. **文档**: 为每个工具提供清晰的描述
5. **测试**: 为配置创建测试用例
6. **备份**: 定期备份配置文件

## 故障排除

### 常见问题

1. **工具加载失败**
   - 检查配置文件语法
   - 验证工具类型和必需字段
   - 确认环境变量设置

2. **API工具调用失败**
   - 验证API端点URL
   - 检查认证配置
   - 确认参数格式

3. **MCP工具连接失败**
   - 检查MCP服务器URL
   - 验证认证信息
   - 确认工具名称

### 调试技巧

1. 使用日志记录工具加载过程
2. 测试单个工具配置
3. 验证环境变量解析
4. 检查网络连接

## 扩展

### 添加新工具类型

1. 在`src/agents/shared/`目录下创建新工具类
2. 实现`from_config`方法
3. 在`DynamicToolLoader`中注册新工具类型
4. 更新配置文档

### 自定义认证类型

1. 在工具类中实现新的认证逻辑
2. 更新配置验证模式
3. 添加相应的测试用例

## 相关文档

- [动态工具加载器文档](./dynamic_tool_loader.md)
- [API工具文档](./api_tool.md)
- [MCP工具文档](./mcp_tool.md)
- [智能体开发指南](../agents/README.md)
- 工具性能监控和日志记录