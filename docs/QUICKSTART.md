# Agent-V3 快速开始指南

本指南将帮助您快速上手 Agent-V3 供应链智能体系统。

## 📋 前置要求

- Python 3.8+
- pip 或 conda
- Redis 6.0+（推荐，用于记忆持久化）
- 硅基流动 API 密钥（或其他LLM提供商密钥）

## 🚀 5分钟快速启动

### 1. 克隆和安装

```bash
# 克隆项目
git clone https://github.com/wu-xiaochen/Agent-V3.git
cd Agent-V3

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 设置API密钥
export SILICONFLOW_API_KEY="your_api_key_here"

# 可选：配置Redis（如果不配置，将使用内存存储）
export REDIS_PASSWORD="your_redis_password"
```

### 3. 启动Redis（可选但推荐）

```bash
# 使用Docker启动Redis
docker run -d -p 6379:6379 redis:latest

# 或使用本地Redis
redis-server
```

### 4. 运行智能体

```bash
# 交互模式
python main.py --interactive

# 单次查询
python main.py --query "帮我优化库存管理流程"
```

## 💬 第一次对话

启动交互模式后，您可以：

```
您: 你好，请介绍一下你自己

助手: 我是一位专业的供应链管理专家...

您: 我们公司的库存周转率很低，怎么优化？

助手: 针对库存周转率低的问题，我建议从以下几个方面入手：
1. 数据分析...
2. ABC分类管理...
3. 安全库存优化...

您: 能帮我生成一个n8n工作流来自动化这个流程吗？

助手: 当然可以，我来帮您生成一个n8n工作流...
```

## 📝 基础使用示例

### Python脚本使用

创建文件 `my_agent.py`：

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建智能体
agent = UnifiedAgent(
    provider="siliconflow",  # LLM提供商
    memory=True,             # 启用记忆
    session_id="my_session"  # 会话ID
)

# 发起对话
response = agent.run("我需要优化供应链管理")
print(response["response"])

# 继续对话（保持上下文）
response2 = agent.run("具体应该从哪些方面入手？")
print(response2["response"])

# 查看对话历史
memory = agent.get_memory()
print(f"对话历史数量：{len(memory)}")
```

运行：
```bash
python my_agent.py
```

### 多轮对话示例

```python
from src.agents.unified.unified_agent import UnifiedAgent

agent = UnifiedAgent(
    provider="siliconflow",
    memory=True,
    session_id="supply_chain_optimization"
)

# 第1轮：描述问题
agent.run("""
我们是一家制造企业，目前面临：
1. 库存积压严重
2. 供应商交货不稳定
3. 需求预测不准确
""")

# 第2轮：深入讨论
agent.run("重点说说库存优化的方法")

# 第3轮：请求自动化
agent.run("帮我生成一个CrewAI团队配置来执行这个优化方案")

# 第4轮：生成工作流
agent.run("同时生成一个n8n工作流来自动化库存监控")
```

## 🔧 常用功能

### 1. 会话管理

```python
# 创建不同的会话
agent1 = UnifiedAgent(session_id="user_001")
agent2 = UnifiedAgent(session_id="user_002")

# 独立运行
agent1.run("查询1")
agent2.run("查询2")

# 获取会话信息
info = agent1.get_session_info()
print(info)
```

### 2. 记忆管理

```python
# 查看记忆
memory = agent.get_memory()
for msg in memory:
    print(f"{msg.type}: {msg.content}")

# 清除记忆
agent.clear_memory()
```

### 3. 流式输出

```python
for chunk in agent.stream("请详细介绍供应链管理"):
    if isinstance(chunk, dict) and "response" in chunk:
        print(chunk["response"], end="", flush=True)
```

### 4. 异步调用

```python
import asyncio

async def main():
    agent = UnifiedAgent(provider="siliconflow")
    response = await agent.arun("异步查询")
    print(response["response"])

asyncio.run(main())
```

## 🛠️ 工具使用

### 自动工具调用

智能体会根据您的查询自动选择和调用工具：

```python
agent = UnifiedAgent(provider="siliconflow", memory=True)

# 自动调用时间工具
agent.run("现在几点了？")

# 自动调用计算器工具
agent.run("计算 123 * 456")

# 自动调用搜索工具
agent.run("搜索最新的供应链管理趋势")

# 自动调用n8n工具
agent.run("帮我创建一个订单处理的工作流")
```

## ✅ 运行测试

验证系统是否正常工作：

```bash
# 运行核心功能测试
python tests/test_all.py core

# 运行系统集成测试
python tests/test_all.py system

# 运行所有测试
python tests/test_all.py
```

## 🔍 故障排查

### 问题1：无法连接Redis

**症状**：提示 "无法连接到Redis"

**解决方案**：
```bash
# 检查Redis是否运行
redis-cli ping

# 如果返回PONG，说明Redis正常
# 如果失败，启动Redis
redis-server
```

### 问题2：API密钥错误

**症状**：提示 "API key错误"

**解决方案**：
```bash
# 检查环境变量
echo $SILICONFLOW_API_KEY

# 如果为空，设置环境变量
export SILICONFLOW_API_KEY="your_api_key"
```

### 问题3：工具未找到

**症状**：智能体提示找不到某个工具

**解决方案**：
```bash
# 验证工具配置
python -c "
from src.agents.shared.tools import get_tools_for_agent
tools = get_tools_for_agent('unified_agent')
print([t.name for t in tools])
"
```

## 📚 下一步

- 阅读 [完整文档](README.md)
- 查看 [API参考](docs/api/api_reference.md)
- 学习 [配置系统](docs/development/configuration.md)
- 探索 [示例代码](examples/)

## 💡 最佳实践

1. **使用Redis**：强烈建议使用Redis进行记忆持久化
2. **会话管理**：为每个用户分配独立的session_id
3. **错误处理**：在生产环境中添加适当的错误处理
4. **日志记录**：启用日志以便调试和监控
5. **定期清理**：定期清理过期的会话数据

## 🆘 获取帮助

- [GitHub Issues](https://github.com/wu-xiaochen/Agent-V3/issues)
- [文档中心](docs/)
- [示例代码](examples/)

---

**开始您的供应链智能化之旅！** 🚀

