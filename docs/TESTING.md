# Agent-V3 测试指南

本文档介绍如何运行和编写 Agent-V3 的测试用例。

## 📋 测试套件概览

Agent-V3 提供了全面的测试套件，覆盖系统的各个层面：

### 1. 核心功能测试 (Core Functionality)
- **文件**：`tests/comprehensive/test_agent_core_functionality.py`
- **覆盖**：
  - 智能体初始化和配置
  - 对话能力（同步/异步/流式）
  - 记忆管理和持久化
  - 工具调用和集成
  - 错误处理和容错
  - 并发和性能测试

### 2. 系统集成测试 (System Integration)
- **文件**：`tests/comprehensive/test_system_integration.py`
- **覆盖**：
  - LLM提供商集成
  - 配置系统集成
  - Redis存储集成
  - 工具系统集成
  - 端到端工作流测试

### 3. 供应链业务测试 (Supply Chain)
- **文件**：`tests/supply_chain/test_supply_chain_workflow.py`
- **覆盖**：
  - 供应链业务流程
  - CrewAI集成
  - 供应链专业工具

### 4. n8n集成测试 (n8n Integration)
- **文件**：`tests/integration/test_n8n_mcp_integration.py`
- **覆盖**：
  - n8n MCP工具
  - 工作流生成
  - MCP Stdio通信

## 🚀 运行测试

### 快速开始

```bash
# 显示测试套件摘要
python tests/test_all.py --summary

# 运行所有测试
python tests/test_all.py

# 使用pytest运行
pytest tests/ -v
```

### 运行特定测试套件

```bash
# 核心功能测试（推荐首先运行）
python tests/test_all.py core

# 系统集成测试
python tests/test_all.py system

# 综合测试
python tests/test_all.py comprehensive

# 供应链业务测试
python tests/test_all.py supply_chain

# n8n集成测试
python tests/test_all.py n8n_integration
```

### 使用pytest

```bash
# 运行所有测试，详细输出
pytest tests/ -v -s

# 运行特定文件
pytest tests/comprehensive/test_agent_core_functionality.py -v

# 运行特定测试类
pytest tests/comprehensive/test_agent_core_functionality.py::TestAgentInitialization -v

# 运行特定测试方法
pytest tests/comprehensive/test_agent_core_functionality.py::TestAgentInitialization::test_basic_initialization -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 📊 测试详细说明

### 核心功能测试详解

#### 1. 初始化测试 (TestAgentInitialization)

```python
# 测试基本初始化
def test_basic_initialization()

# 测试带记忆的初始化
def test_initialization_with_memory()

# 测试Redis URL初始化
def test_initialization_with_redis_url()

# 测试工具加载
def test_tools_loaded()
```

**运行**：
```bash
pytest tests/comprehensive/test_agent_core_functionality.py::TestAgentInitialization -v
```

#### 2. 对话能力测试 (TestDialogueCapabilities)

```python
# 单轮对话
def test_single_turn_dialogue()

# 多轮对话
def test_multi_turn_dialogue()

# 上下文理解
def test_context_understanding()

# 异步对话
async def test_async_dialogue()

# 流式对话
def test_stream_dialogue()
```

**运行**：
```bash
pytest tests/comprehensive/test_agent_core_functionality.py::TestDialogueCapabilities -v -s
```

#### 3. 记忆管理测试 (TestMemoryManagement)

```python
# 记忆持久化
def test_memory_persistence()

# 记忆检索
def test_memory_retrieval()

# 记忆清除
def test_memory_clear()

# 会话隔离
def test_session_isolation()

# 跨重启持久化
def test_memory_across_restarts()
```

**运行**：
```bash
pytest tests/comprehensive/test_agent_core_functionality.py::TestMemoryManagement -v
```

#### 4. 工具调用测试 (TestToolInvocation)

```python
# 时间工具
def test_time_tool_invocation()

# 计算器工具
def test_calculator_tool_invocation()

# 搜索工具
def test_search_tool_invocation()

# 多工具调用
def test_multiple_tool_invocation()
```

**运行**：
```bash
pytest tests/comprehensive/test_agent_core_functionality.py::TestToolInvocation -v
```

### 系统集成测试详解

#### 1. LLM集成测试 (TestLLMIntegration)

```python
# SiliconFlow提供商
def test_siliconflow_provider()

# OpenAI提供商
def test_openai_provider()

# 自定义参数
def test_llm_with_custom_parameters()
```

#### 2. 配置系统测试 (TestConfigurationIntegration)

```python
# 分层配置
def test_hierarchical_config_loading()

# 环境变量解析
def test_environment_variable_resolution()

# 提示词加载
def test_prompt_template_loading()
```

#### 3. 存储系统测试 (TestStorageIntegration)

```python
# Redis连接
def test_redis_connection()

# 会话持久化
def test_session_persistence()

# 多会话管理
def test_multiple_sessions()
```

## 🔧 测试环境配置

### 前置要求

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 启动Redis（用于记忆测试）
docker run -d -p 6379:6379 redis:latest

# 设置环境变量
export SILICONFLOW_API_KEY="your_api_key"
export SKIP_MCP_TESTS="false"  # 如果要跳过MCP测试，设为true
```

### 环境变量

```bash
# 必需
export SILICONFLOW_API_KEY="your_key"

# 可选
export OPENAI_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
export REDIS_PASSWORD="your_password"

# 测试控制
export SKIP_MCP_TESTS="true"  # 跳过MCP相关测试
export TEST_TIMEOUT="60"      # 测试超时时间（秒）
```

## 📝 编写测试

### 测试模板

```python
import pytest
from src.agents.unified.unified_agent import UnifiedAgent

class TestMyFeature:
    """我的功能测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_my_feature"
        )
        yield agent
        # 清理
        agent.clear_memory()
    
    def test_feature_works(self, agent):
        """测试功能正常工作"""
        response = agent.run("测试查询")
        
        assert response is not None
        assert "response" in response
        assert len(response["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_async_feature(self, agent):
        """测试异步功能"""
        response = await agent.arun("异步测试")
        assert response is not None
```

### 测试最佳实践

1. **使用Fixtures**：创建可重用的测试设置
2. **清理资源**：测试后清理会话和记忆
3. **独立性**：每个测试应独立运行
4. **命名规范**：使用描述性的测试名称
5. **断言明确**：使用清晰的断言消息
6. **跳过条件**：合理使用 `pytest.skip`

## 🎯 测试策略

### 推荐测试顺序

1. **核心功能测试**：验证基本功能正常
   ```bash
   python tests/test_all.py core
   ```

2. **系统集成测试**：验证各模块集成
   ```bash
   python tests/test_all.py system
   ```

3. **完整测试**：运行所有测试
   ```bash
   python tests/test_all.py
   ```

### 持续集成

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:latest
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        env:
          SILICONFLOW_API_KEY: ${{ secrets.SILICONFLOW_API_KEY }}
        run: |
          pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📈 测试覆盖率

### 生成覆盖率报告

```bash
# HTML报告
pytest tests/ --cov=src --cov-report=html

# 在浏览器中查看
open htmlcov/index.html

# XML报告（用于CI）
pytest tests/ --cov=src --cov-report=xml

# 终端报告
pytest tests/ --cov=src --cov-report=term-missing
```

### 覆盖率目标

- **整体覆盖率**：> 80%
- **核心模块**：> 90%
- **关键路径**：100%

## 🐛 调试测试

### 运行调试模式

```bash
# 显示print输出
pytest tests/ -v -s

# 在第一个失败处停止
pytest tests/ -x

# 显示完整traceback
pytest tests/ -v --tb=long

# 只运行失败的测试
pytest tests/ --lf

# 运行最后失败的测试
pytest tests/ --last-failed
```

### 调试工具

```python
# 使用pdb调试
def test_with_debug(agent):
    response = agent.run("测试")
    import pdb; pdb.set_trace()  # 设置断点
    assert response is not None

# 打印调试信息
def test_with_debug_output(agent):
    response = agent.run("测试")
    print(f"响应: {response}")
    print(f"元数据: {response.get('metadata')}")
```

## 🔍 常见问题

### 1. Redis连接失败

**问题**：测试提示 "无法连接到Redis"

**解决**：
```bash
# 启动Redis
docker run -d -p 6379:6379 redis:latest

# 或设置跳过Redis测试
export SKIP_REDIS_TESTS="true"
```

### 2. API密钥错误

**问题**：测试失败，提示API密钥错误

**解决**：
```bash
# 设置环境变量
export SILICONFLOW_API_KEY="your_key"

# 验证环境变量
echo $SILICONFLOW_API_KEY
```

### 3. 测试超时

**问题**：测试运行时间过长

**解决**：
```bash
# 设置超时
pytest tests/ --timeout=60

# 或跳过慢速测试
pytest tests/ -m "not slow"
```

### 4. 并发测试失败

**问题**：并发测试不稳定

**解决**：
```bash
# 串行运行测试
pytest tests/ -n 0

# 或增加超时时间
pytest tests/ --timeout=120
```

## 📚 更多资源

- [pytest文档](https://docs.pytest.org/)
- [pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [项目架构文档](ARCHITECTURE.md)
- [快速开始指南](QUICKSTART.md)

---

**保持测试覆盖率，确保代码质量！** ✅

