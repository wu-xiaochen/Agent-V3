# UnifiedAgent 使用指南

## 简介

UnifiedAgent 是一个基于 LangChain 的统一智能体实现，集成了多种工具和功能，提供灵活的对话和任务执行能力。

## 功能特性

- **多种工具支持**: 内置时间查询、搜索、计算器和天气查询工具
- **多种交互模式**: 支持同步运行、异步运行、流式输出和对话模式
- **记忆功能**: 可选的对话记忆功能，支持多会话管理
- **灵活配置**: 支持不同的 LLM 提供商和模型配置
- **格式化输出**: 支持多种输出格式（Markdown、JSON 等）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 基本使用

### 1. 创建智能体

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建基本智能体
agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')

# 创建带记忆功能的智能体
agent_with_memory = UnifiedAgent(
    provider='openai', 
    model_name='gpt-3.5-turbo', 
    memory=True
)
```

### 2. 基本对话

```python
# 同步运行
response = agent.run("你好，请介绍一下自己")
print(response)

# 异步运行
import asyncio
response = await agent.arun("你好，请介绍一下自己")
print(response)
```

### 3. 流式输出

```python
# 流式输出
for chunk in agent.stream("请写一首关于春天的短诗"):
    print(chunk, end='', flush=True)
```

### 4. 对话模式

```python
# 带记忆的对话
response1 = agent.chat("我的名字是小明", session_id="user_session")
response2 = agent.chat("你还记得我的名字吗？", session_id="user_session")
```

### 5. 工具使用

智能体会自动判断何时使用工具：

```python
# 查询时间
response = agent.run("现在几点了？")

# 数学计算
response = agent.run("计算一下 123 乘以 456 等于多少？")

# 天气查询
response = agent.run("北京今天天气怎么样？")

# 网络搜索
response = agent.run("最新的AI发展趋势是什么？")
```

## 配置选项

### LLM 配置

```python
agent = UnifiedAgent(
    provider='openai',  # LLM 提供商
    model_name='gpt-3.5-turbo',  # 模型名称
    temperature=0.7,  # 温度参数
    memory=True,  # 是否启用记忆
    output_format='markdown'  # 输出格式
)
```

### 支持的输出格式

- `markdown`: Markdown 格式（默认）
- `json`: JSON 格式
- `text`: 纯文本格式

## 示例脚本

运行 `example_unified_agent.py` 查看完整的使用示例：

```bash
python example_unified_agent.py
```

## 注意事项

1. 确保设置了正确的 API 密钥（如 OpenAI API Key）
2. 记忆功能需要指定相同的 `session_id` 才能保持连续性
3. 流式输出在 Jupyter Notebook 中可能需要特殊处理

## 扩展开发

### 添加自定义工具

```python
from src.tools import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"
    
    def _run(self, query: str) -> str:
        # 实现工具逻辑
        return "工具执行结果"

# 创建带自定义工具的智能体
agent = UnifiedAgent(
    provider='openai',
    model_name='gpt-3.5-turbo',
    tools=[MyCustomTool()]  # 添加自定义工具
)
```

### 自定义输出格式

```python
from src.formatters import BaseFormatter

class MyCustomFormatter(BaseFormatter):
    def format_response(self, response: str, metadata: dict) -> str:
        # 实现自定义格式化逻辑
        return f"自定义格式: {response}"

# 使用自定义格式化器
agent = UnifiedAgent(
    provider='openai',
    model_name='gpt-3.5-turbo',
    output_formatter=MyCustomFormatter()
)
```

## 常见问题

### Q: 如何切换到不同的 LLM 提供商？

A: 只需更改 `provider` 参数，例如：

```python
# 使用 Anthropic Claude
agent = UnifiedAgent(provider='anthropic', model_name='claude-3-sonnet')

# 使用 Google Gemini
agent = UnifiedAgent(provider='google', model_name='gemini-pro')
```

### Q: 如何处理长对话？

A: 启用记忆功能并使用相同的 `session_id`：

```python
agent = UnifiedAgent(memory=True)
response1 = agent.chat("第一句话", session_id="long_conversation")
response2 = agent.chat("第二句话", session_id="long_conversation")
```

### Q: 如何提高响应速度？

A: 可以尝试以下方法：
- 使用更快的模型（如 `gpt-3.5-turbo` 而非 `gpt-4`）
- 降低 `temperature` 参数
- 使用流式输出获得即时反馈

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进 UnifiedAgent！

## 许可证

MIT License