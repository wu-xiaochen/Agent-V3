# 工具配置系统说明

本目录包含智能体工具配置系统的各种配置文件和模板，支持灵活配置智能体可用的工具集合。

## 文件说明

### 配置模板和示例

1. **tools_config_template.json** - 完整的工具配置模板，包含所有支持的配置选项
2. **tools_config_example.json** - 简化版工具配置示例，适合快速开始
3. **development.json** - 开发环境工具配置，包含调试和测试工具
4. **production.json** - 生产环境工具配置，包含性能优化和日志记录
5. **mcp_tools_example.json** - MCP工具配置示例，展示如何配置MCP服务器工具

## 配置结构

### 工具定义

每个工具包含以下基本属性：

- `name`: 工具名称，唯一标识符
- `type`: 工具类型（builtin/api/mcp）
- `enabled`: 是否启用该工具
- `description`: 工具描述
- `config`: 工具特定配置（可选）

### 工具类型

#### 1. 内置工具 (builtin)

系统预置的工具，如搜索、计算器、时间工具等。

```json
{
  "name": "search",
  "type": "builtin",
  "enabled": true,
  "description": "搜索引擎工具",
  "config": {
    "provider": "serper",
    "max_results": 10
  }
}
```

#### 2. API工具 (api)

通过HTTP API调用的外部工具。

```json
{
  "name": "weather_api",
  "type": "api",
  "enabled": true,
  "description": "天气API工具",
  "config": {
    "endpoint": "https://api.openweathermap.org/data/2.5/weather",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer ${WEATHER_API_KEY}"
    },
    "parameters": {
      "q": {
        "type": "string",
        "required": true,
        "description": "城市名称"
      }
    },
    "response_mapping": {
      "temperature": "$.main.temp",
      "description": "$.weather[0].description"
    },
    "timeout": 30
  }
}
```

#### 3. MCP工具 (mcp)

通过MCP(Model Context Protocol)协议连接的工具服务器。

```json
{
  "name": "n8n_workflow_executor",
  "type": "mcp",
  "enabled": true,
  "description": "n8n工作流执行器",
  "config": {
    "server_url": "http://localhost:5678",
    "server_name": "n8n_mcp_server",
    "tool_name": "execute_workflow",
    "timeout": 120,
    "auth": {
      "type": "bearer",
      "token": "${N8N_API_TOKEN}"
    },
    "parameters": {
      "workflow_id": {
        "type": "string",
        "required": true,
        "description": "工作流ID"
      }
    },
    "response_mapping": {
      "execution_id": "$.executionId",
      "status": "$.status"
    }
  }
}
```

### 工具组

工具组是相关工具的集合，便于批量管理：

```json
{
  "name": "core_tools",
  "description": "核心工具集",
  "tools": ["search", "calculator", "time"]
}
```

### 智能体工具映射

为不同类型的智能体分配不同的工具组：

```json
{
  "agent_tool_mapping": {
    "unified_agent": ["core_tools", "crewai_tools"],
    "supply_chain_agent": ["core_tools", "crewai_tools", "external_tools"],
    "default": ["core_tools"]
  }
}
```

## 环境变量

配置中可以使用环境变量，格式为 `${VARIABLE_NAME}`：

```json
{
  "headers": {
    "Authorization": "Bearer ${API_KEY}"
  }
}
```

## 使用方法

1. 根据需求选择或修改配置文件
2. 将配置文件路径传递给智能体初始化函数
3. 智能体将根据配置加载相应的工具

## 最佳实践

1. **环境分离**: 为不同环境创建不同的配置文件
2. **安全性**: 敏感信息使用环境变量
3. **模块化**: 使用工具组管理相关工具
4. **文档**: 为自定义工具提供清晰的描述
5. **测试**: 在开发环境充分测试工具配置

## 配置验证

系统会自动验证配置文件的格式和内容，确保：

- JSON格式正确
- 必需字段存在
- 工具名称唯一
- 工具组引用的工具存在
- 智能体映射的工具组存在

## 扩展支持

系统支持通过插件方式扩展新的工具类型，详见工具扩展文档。