# 输出格式配置指南

## 概述

Agent-V3支持通过配置文件灵活控制输出格式，无需修改代码即可切换不同的输出样式。系统支持三种内置格式：normal（普通文本）、markdown（Markdown格式）和json（JSON格式），并允许用户自定义输出模板。

## 配置位置

输出格式配置位于 `config/base/services.yaml` 文件中的 `output` 部分：

```yaml
output:
  format: "normal"  # normal, markdown, json
  options:
    include_metadata: false
    pretty_print: true
    indent: 2
  custom_templates:
    normal: "{response}"
    markdown: "# 响应\n\n{response}"
    json: |
      {
        "response": "{response}",
        "timestamp": "{timestamp}",
        "agent": "{agent_name}"
      }
```

## 配置选项

### format
指定默认的输出格式，可选值：
- `normal`: 普通文本格式
- `markdown`: Markdown格式
- `json`: JSON格式

### options
输出格式的选项配置：
- `include_metadata`: 是否在输出中包含元数据（仅对normal和markdown格式有效）
- `pretty_print`: 是否格式化JSON输出（仅对json格式有效）
- `indent`: JSON缩进空格数（仅对json格式有效）

### custom_templates
自定义输出模板，支持以下占位符：
- `{response}`: 智能体的响应内容
- `{timestamp}`: 时间戳
- `{agent_name}`: 智能体名称
- `{query}`: 用户查询
- `{session_id}`: 会话ID

## 使用方法

### 修改默认格式

直接修改 `config/base/services.yaml` 中的 `format` 字段即可更改默认输出格式：

```yaml
output:
  format: "markdown"  # 将默认格式改为markdown
```

### 自定义模板

您可以根据需要自定义输出模板，例如：

```yaml
output:
  custom_templates:
    normal: "🤖 {agent_name} 回答: {response}"
    markdown: "## {agent_name} 的回答\n\n{response}\n\n*查询: {query}*"
    json: |
      {
        "agent": "{agent_name}",
        "response": "{response}",
        "query": "{query}",
        "timestamp": "{timestamp}",
        "session": "{session_id}"
      }
```

### 代码中使用

在代码中，您可以通过以下方式使用输出格式：

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建智能体（自动使用配置文件中的默认格式）
agent = UnifiedAgent()

# 获取当前输出格式
current_format = agent.get_output_format()
print(f"当前输出格式: {current_format}")

# 动态切换输出格式
agent.set_output_format("markdown")
response = agent.run("你好")
print(response["response"])

# 获取格式化后的响应
if isinstance(response, dict) and "response" in response:
    formatted_output = response["response"]
    metadata = response["metadata"]
```

## 环境特定配置

可以为不同环境设置不同的输出格式，在 `config/environments/` 目录下创建对应环境的配置文件：

```yaml
# config/environments/production.yaml
services:
  output:
    format: "json"
    options:
      include_metadata: true
      pretty_print: false
```

## 动态切换格式

在运行时，可以通过代码动态切换输出格式：

```python
from src.agents.unified.unified_agent import UnifiedAgent

agent = UnifiedAgent()

# 切换到markdown格式
agent.output_formatter.set_format("markdown")

# 切换到json格式
agent.output_formatter.set_format("json")
```

## 注意事项

1. 自定义模板中的占位符必须用花括号括起来，如 `{response}`
2. JSON模板需要确保格式正确，避免语法错误
3. 修改配置后需要重启应用程序才能生效
4. 环境特定配置会覆盖基础配置中的相应设置