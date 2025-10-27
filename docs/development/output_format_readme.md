# 输出格式配置功能

## 功能概述

Agent-V3现在支持通过配置文件灵活控制输出格式，无需修改代码即可切换不同的输出样式。系统支持三种内置格式（normal、markdown、json）以及自定义模板。

## 实现内容

### 1. 配置文件修改

在 `config/base/services.yaml` 中添加了输出格式配置：

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

### 2. 配置加载器增强

扩展了 `src/config/config_loader.py`，添加了 `get_output_config()` 方法，用于获取输出格式配置。

### 3. 输出格式化器实现

创建了 `src/agent/output_formatter.py`，实现了：
- 三种内置格式（normal、markdown、json）的支持
- 自定义模板支持
- 格式选项（include_metadata、pretty_print等）
- 动态格式切换

### 4. UnifiedAgent集成

修改了 `src/agent/unified_agent.py`，集成输出格式化器：
- 初始化时加载输出格式配置
- 提供 `get_output_format()` 和 `set_output_format()` 方法
- 在响应返回前应用格式化

### 5. 主程序适配

修改了 `main.py`，确保正确处理和显示格式化后的响应：
- 检查响应类型，提取格式化后的内容
- 流式输出和非流式输出均正确处理

## 使用方法

### 修改默认输出格式

直接修改 `config/base/services.yaml` 中的 `format` 字段：

```yaml
output:
  format: "markdown"  # 将默认格式改为markdown
```

### 自定义模板

修改 `custom_templates` 中的模板：

```yaml
output:
  custom_templates:
    normal: "🤖 {agent_name} 回答: {response}"
    json: |
      {
        "agent": "{agent_name}",
        "response": "{response}",
        "query": "{query}",
        "timestamp": "{timestamp}"
      }
```

### 代码中使用

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建智能体（自动使用配置文件中的默认格式）
agent = UnifiedAgent()

# 获取当前输出格式
current_format = agent.get_output_format()

# 动态切换输出格式
agent.set_output_format("markdown")
response = agent.run("你好")
print(response["response"])
```

## 测试验证

### 测试脚本

创建了多个测试脚本验证功能：

1. `tests/config/test_config_loader.py` - 测试配置加载器
2. `tests/config/test_custom_templates.py` - 测试自定义模板
3. `tests/config/test_output_format_application.py` - 测试输出格式应用
4. `examples/output_format_example.py` - 输出格式示例脚本

### 测试结果

所有测试均通过，验证了：
- 配置文件正确加载输出格式设置
- 三种内置格式正常工作
- 自定义模板正确应用
- 动态格式切换功能正常

## 文档

创建了详细的使用文档：
- `docs/development/output_format_configuration.md` - 输出格式配置指南

## 优势

1. **灵活性**：无需修改代码即可切换输出格式
2. **可扩展性**：支持自定义模板，满足特定需求
3. **环境适配**：可为不同环境配置不同输出格式
4. **动态切换**：支持运行时动态更改输出格式
5. **向后兼容**：不影响现有功能，平滑升级

## 注意事项

1. 自定义模板使用Python的字符串格式化语法
2. JSON模板必须生成有效的JSON格式
3. 环境变量可以覆盖配置文件中的设置
4. 配置文件必须使用有效的YAML格式

## 后续扩展

可以考虑的后续扩展：
1. 支持更多内置格式（如XML、CSV等）
2. 添加模板验证功能
3. 支持从外部文件加载模板
4. 添加输出格式预览功能