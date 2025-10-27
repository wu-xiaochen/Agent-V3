# Agent-V3 API 文档

## 概述

Agent-V3 是一个多智能体系统，提供供应链智能体和统一智能体等功能。本文档描述了系统的API接口、使用方法和最佳实践。

## 目录

- [快速开始](#快速开始)
- [智能体API](#智能体api)
  - [统一智能体](#统一智能体)
  - [供应链智能体](#供应链智能体)
- [配置API](#配置api)
- [工具API](#工具api)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [示例代码](#示例代码)

## 快速开始

### 安装

```bash
pip install -r requirements/base.txt
```

### 基本使用

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建统一智能体
agent = UnifiedAgent(provider="openai", model_name="gpt-4")

# 运行智能体
result = agent.run("请帮我分析供应链风险")
print(result["response"])
```

## 智能体API

### 统一智能体

#### 初始化

```python
UnifiedAgent(
    provider: Optional[str] = None, 
    memory: bool = True,
    redis_url: Optional[str] = None,
    session_id: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
)
```

**参数:**
- `provider`: LLM提供商 (如 "openai", "siliconflow")
- `memory`: 是否启用记忆功能
- `redis_url`: Redis连接URL
- `session_id`: 会话ID，用于区分不同对话
- `model_name`: 模型名称
- `**kwargs`: 额外的LLM参数

**示例:**
```python
# 使用OpenAI GPT-4
agent = UnifiedAgent(provider="openai", model_name="gpt-4")

# 使用SiliconFlow
agent = UnifiedAgent(provider="siliconflow", model_name="Qwen/Qwen2-72B-Instruct")

# 启用Redis记忆
agent = UnifiedAgent(
    provider="openai", 
    memory=True, 
    redis_url="redis://localhost:6379/0",
    session_id="user123"
)
```

#### 运行智能体

```python
result = agent.run(query: str, session_id: str = "default") -> Dict[str, Any]
```

**参数:**
- `query`: 用户查询
- `session_id`: 会话ID，用于区分不同对话

**返回值:**
```python
{
    "response": "智能体的响应",
    "metadata": {
        "query": "用户查询",
        "tools_used": ["tool1", "tool2"],
        "agent_type": "unified",
        "output_format": "normal",
        "session_id": "session123",
        "has_memory": True,
        "memory_type": "redis"
    }
}
```

**示例:**
```python
result = agent.run("分析当前供应链中的潜在风险")
print(result["response"])

# 获取元数据
metadata = result["metadata"]
print(f"使用的工具: {metadata['tools_used']}")
```

#### 异步运行

```python
result = await agent.arun(query: str, session_id: str = "default") -> Dict[str, Any]
```

### 供应链智能体

#### 初始化

```python
SupplyChainAgent(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
)
```

**参数:**
- `provider`: LLM提供商
- `model_name`: 模型名称
- `**kwargs`: 额外的LLM参数

#### 运行智能体

```python
result = agent.run(query: str, session_id: str = "default") -> Dict[str, Any]
```

**返回值:**
```python
{
    "response": "智能体的响应",
    "metadata": {
        "query": "用户查询",
        "agent_type": "supply_chain",
        "session_id": "session123",
        "state": "completed",
        "tools_used": []
    }
}
```

**示例:**
```python
from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent

agent = SupplyChainAgent(provider="openai", model_name="gpt-4")
result = agent.run("请帮我分析当前供应链中的潜在风险")
print(result["response"])
```

## 配置API

### 配置加载器

```python
from src.config.config_loader import config_loader

# 获取智能体配置
agents_config = config_loader.get_agents_config()

# 获取特定智能体配置
unified_config = config_loader.get_specific_agent_config("unified_agent")
supply_chain_config = config_loader.get_specific_agent_config("supply_chain_agent")

# 获取LLM配置
llm_config = config_loader.get_llm_config("openai")

# 获取数据库配置
db_config = config_loader.get_database_config()
```

### 提示词加载器

```python
from src.prompts.prompt_loader import prompt_loader

# 获取提示词
system_prompt = prompt_loader.get_prompt("src/prompts/prompts.py", "SUPPLY_CHAIN_SYSTEM_PROMPT")

# 重新加载提示词
prompt_loader.reload_prompts("src/prompts/prompts.py")
```

## 工具API

### 获取可用工具

```python
from src.agents.shared.tools import get_tools

tools = get_tools()
for tool in tools:
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
```

### 自定义工具

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class CustomToolInput(BaseModel):
    query: str = Field(description="查询参数")

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "自定义工具描述"
    args_schema = CustomToolInput
    
    def _run(self, query: str) -> str:
        # 工具逻辑
        return f"处理结果: {query}"
    
    async def _arun(self, query: str) -> str:
        # 异步工具逻辑
        return f"异步处理结果: {query}"

# 注册工具
tools = get_tools()
tools.append(CustomTool())
```

## 错误处理

### 常见错误类型

1. **配置错误**
```python
from src.config.exceptions import ConfigurationError

try:
    config = config_loader.load_config("invalid_config")
except ConfigurationError as e:
    print(f"配置错误: {e}")
```

2. **智能体运行错误**
```python
result = agent.run("无效查询")
if "error" in result["metadata"]:
    print(f"运行错误: {result['metadata']['error']}")
```

3. **工具执行错误**
```python
# 在工具实现中
def _run(self, query: str) -> str:
    try:
        # 工具逻辑
        return result
    except Exception as e:
        raise ValueError(f"工具执行失败: {e}")
```

### 错误处理最佳实践

1. **捕获特定异常**
```python
try:
    result = agent.run(query)
except ConfigurationError as e:
    # 处理配置错误
    logger.error(f"配置错误: {e}")
except ValueError as e:
    # 处理值错误
    logger.error(f"值错误: {e}")
except Exception as e:
    # 处理其他未知错误
    logger.error(f"未知错误: {e}")
```

2. **提供有用的错误信息**
```python
def validate_input(input_data):
    if not input_data:
        raise ValueError("输入数据不能为空")
    if len(input_data) > 1000:
        raise ValueError("输入数据长度不能超过1000个字符")
```

## 最佳实践

### 1. 会话管理

```python
# 为不同用户使用不同的会话ID
user_id = "user123"
session_id = f"session_{user_id}"

result = agent.run(query, session_id=session_id)
```

### 2. 记忆管理

```python
# 对于长期会话，使用Redis存储
agent = UnifiedAgent(
    provider="openai",
    memory=True,
    redis_url="redis://localhost:6379/0"
)

# 对于短期会话，使用内存存储
agent = UnifiedAgent(
    provider="openai",
    memory=True
)
```

### 3. 性能优化

```python
# 重用智能体实例
agent = UnifiedAgent(provider="openai")

# 批量处理查询
queries = ["查询1", "查询2", "查询3"]
results = [agent.run(query) for query in queries]
```

### 4. 安全考虑

```python
# 验证用户输入
def validate_user_input(input_text):
    if len(input_text) > 10000:
        raise ValueError("输入过长")
    # 其他验证逻辑
    return input_text

# 清理敏感信息
def sanitize_output(output_text):
    # 移除或替换敏感信息
    return output_text
```

## 示例代码

### 完整示例：供应链分析

```python
from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent
from src.config.config_loader import config_loader

def analyze_supply_chain_risks():
    # 初始化智能体
    agent = SupplyChainAgent(provider="openai", model_name="gpt-4")
    
    # 定义分析查询
    query = """
    请分析以下供应链情况中的潜在风险:
    1. 供应商集中在单一地区
    2. 库存水平低于安全阈值
    3. 物流运输依赖单一渠道
    
    请提供风险等级评估和缓解建议。
    """
    
    # 运行智能体
    result = agent.run(query, session_id="supply_chain_analysis")
    
    # 处理结果
    response = result["response"]
    metadata = result["metadata"]
    
    print("分析结果:")
    print(response)
    print("\n元数据:")
    print(f"智能体类型: {metadata['agent_type']}")
    print(f"会话ID: {metadata['session_id']}")
    print(f"状态: {metadata.get('state', 'unknown')}")

if __name__ == "__main__":
    analyze_supply_chain_risks()
```

### 完整示例：多轮对话

```python
from src.agents.unified.unified_agent import UnifiedAgent

def multi_turn_conversation():
    # 初始化智能体，启用记忆
    agent = UnifiedAgent(
        provider="openai",
        memory=True,
        session_id="customer_service"
    )
    
    # 第一轮对话
    query1 = "我想了解你们的产品退货政策"
    result1 = agent.run(query1)
    print(f"用户: {query1}")
    print(f"助手: {result1['response']}")
    
    # 第二轮对话
    query2 = "如果我已经使用了30天，还能退货吗？"
    result2 = agent.run(query2)
    print(f"\n用户: {query2}")
    print(f"助手: {result2['response']}")
    
    # 第三轮对话
    query3 = "退货流程是怎样的？"
    result3 = agent.run(query3)
    print(f"\n用户: {query3}")
    print(f"助手: {result3['response']}")

if __name__ == "__main__":
    multi_turn_conversation()
```

## 更新日志

### v1.0.0
- 初始版本发布
- 支持统一智能体和供应链智能体
- 实现配置管理和提示词加载
- 添加工具支持和记忆功能

---

如有问题或建议，请提交 [Issue](https://github.com/your-username/Agent-V3/issues) 或联系项目维护者。