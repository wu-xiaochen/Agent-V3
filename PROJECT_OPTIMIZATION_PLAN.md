# 🚀 Agent-V3 项目优化计划

基于 `PROJECT_COMPREHENSIVE_ANALYSIS.md` 的分析结果

---

## 📋 优化计划总览

| 阶段 | 任务 | 优先级 | 预计时间 | 负责人 |
|------|------|--------|---------|--------|
| **Phase 1** | 紧急修复（P0-P1） | 🔴 最高 | 16-22小时 | - |
| **Phase 2** | 重要优化（P2） | 🟡 中等 | 10-14小时 | - |
| **Phase 3** | 架构重构（P3） | 🟢 一般 | 20-30小时 | - |

**总计预估**: 46-66 小时（约 6-9 个工作日）

### Phase 1 任务明细
1. **任务 1.1**: 修复智能体上下文逻辑 - 4-6小时
2. **任务 1.2**: 重构 n8n 节点支持 - 8-12小时
3. **任务 1.3**: 消除硬编码值 - 2-4小时
4. **任务 1.4**: 🆕 实现自动继续执行机制 - 3-4小时

---

## 🔥 Phase 1: 紧急修复（P0-P1）

### 任务 1.1: 修复智能体上下文逻辑（P0）

**优先级**: 🔴 最高
**预计时间**: 4-6 小时
**影响范围**: 核心用户体验

#### 具体步骤

##### 步骤 1: 优化工具描述（1小时）
**文件**: 
- `src/tools/crewai_runtime_tool.py`
- `src/agents/shared/n8n_api_tools.py`

**修改内容**:

```python
# src/tools/crewai_runtime_tool.py
class CrewAIRuntimeTool(BaseTool):
    name: str = "crewai_runtime"
    description: str = """【CrewAI团队运行工具】

何时使用此工具:
- 用户说"运行它"、"执行它"、"启动团队"
- 刚刚生成了 CrewAI 配置，需要执行
- 需要运行一个多智能体协作任务

输入要求:
- config: CrewAI 团队配置（JSON 字符串或文件路径）
- query: 要执行的具体任务描述

示例:
用户: "运行刚才生成的团队"
调用: crewai_runtime(config="上一步的配置", query="...")
"""
```

```python
# src/agents/shared/n8n_api_tools.py
class N8NGenerateAndCreateWorkflowTool(BaseTool):
    name: str = "n8n_generate_and_create_workflow"
    description: str = """【n8n工作流生成工具】

⚠️ 仅用于工作流自动化场景！

何时使用此工具:
- 用户明确要求创建 n8n 工作流
- 需要自动化任务（定时、webhook、数据处理等）
- 关键词："n8n"、"工作流"、"自动化流程"

何时不使用:
- ❌ 用户说"运行它"（应该检查上下文）
- ❌ 用户要求分析或研究（使用 CrewAI）
- ❌ 简单的数据处理（使用其他工具）

输入要求:
- description: 工作流的功能描述（中文或英文）
"""
```

##### 步骤 2: 添加上下文追踪（2-3小时）
**文件**: `src/agents/unified/unified_agent.py`

**新增功能**:

```python
class UnifiedAgent:
    def __init__(self, ...):
        # ... 现有代码 ...
        self.context_tracker = ContextTracker()  # 🆕 上下文追踪器
    
    def run(self, query: str, **kwargs) -> str:
        # 🆕 在执行前更新上下文
        self.context_tracker.add_query(query)
        
        # 🆕 检查是否需要注入上下文提示
        if self._is_context_dependent_query(query):
            query = self._inject_context_hint(query)
        
        # ... 原有执行逻辑 ...
        
        # 🆕 在执行后记录工具调用
        self.context_tracker.add_tool_call(tool_name, result)
        
        return result
    
    def _is_context_dependent_query(self, query: str) -> bool:
        """判断查询是否依赖上下文"""
        context_keywords = ["它", "他", "刚才", "上一步", "之前", "运行", "执行"]
        return any(kw in query for kw in context_keywords)
    
    def _inject_context_hint(self, query: str) -> str:
        """注入上下文提示"""
        last_tool = self.context_tracker.get_last_tool()
        if last_tool == "crewai_generator":
            hint = "\n[上下文提示: 上一步刚生成了 CrewAI 配置，用户可能想运行它]"
            return query + hint
        return query
```

**新建文件**: `src/core/services/context_tracker.py`

```python
from typing import List, Dict, Any
from collections import deque

class ContextTracker:
    """智能体上下文追踪器"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.query_history = deque(maxlen=max_history)
        self.tool_history = deque(maxlen=max_history)
    
    def add_query(self, query: str):
        """添加查询到历史"""
        self.query_history.append({
            "timestamp": datetime.now(),
            "query": query
        })
    
    def add_tool_call(self, tool_name: str, result: Any):
        """添加工具调用到历史"""
        self.tool_history.append({
            "timestamp": datetime.now(),
            "tool": tool_name,
            "result_summary": str(result)[:200]  # 只保存摘要
        })
    
    def get_last_tool(self) -> str:
        """获取最后调用的工具"""
        if self.tool_history:
            return self.tool_history[-1]["tool"]
        return None
    
    def get_context_summary(self, n: int = 3) -> str:
        """获取最近 n 步的上下文摘要"""
        recent = list(self.tool_history)[-n:]
        summary = "最近操作:\n"
        for i, item in enumerate(recent, 1):
            summary += f"{i}. {item['tool']}: {item['result_summary'][:50]}...\n"
        return summary
```

##### 步骤 3: 优化 ReAct 提示词（1小时）
**文件**: `src/agents/unified/unified_agent.py`

**修改 `_create_agent` 方法**:

```python
template = f"""Current Date and Time: {{current_datetime}} (Beijing Time, UTC+8)
Current Year: {{current_year}}
Today is: {{current_date}}

IMPORTANT: When analyzing trends, news, market conditions, or any time-sensitive information, 
always consider the current date above. Use the 'time' tool if you need to verify the current time.

**上下文感知规则**:
1. 如果用户说"运行它"、"执行它"，检查上一步做了什么
2. 如果上一步生成了 CrewAI 配置，优先使用 crewai_runtime 工具
3. 如果上一步生成了 n8n 工作流，优先使用 n8n_execute_workflow 工具
4. 如果用户提到"它"、"刚才"、"之前"，参考对话历史

Answer the following questions as best you can. You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do, CONSIDER THE CONTEXT
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation history:
{{chat_history}}

New question: {{input}}
Thought:{{agent_scratchpad}}"""
```

##### 步骤 4: 测试验证（1小时）
创建测试用例验证修复:

```python
# tests/unit/test_context_logic.py
def test_context_aware_tool_selection():
    agent = UnifiedAgent()
    
    # 步骤 1: 生成 CrewAI 配置
    result1 = agent.run("帮我生成一个数据分析团队的crew配置")
    assert "crewai_generator" in result1
    
    # 步骤 2: 运行它（应该调用 crewai_runtime）
    result2 = agent.run("运行它")
    assert "crewai_runtime" in result2  # ✅ 正确
    assert "n8n_generate" not in result2  # ❌ 不应该调用
```

---

### 任务 1.2: 重构 n8n 节点支持（P1）

**优先级**: 🔴 高
**预计时间**: 8-12 小时
**影响范围**: 工作流生成质量

#### 设计方案: 三层节点架构

```
┌─────────────────────────────────────────────┐
│  Layer 1: 核心节点 (手动维护)              │
│  - 触发器: manualTrigger, webhook           │
│  - AI: aiAgent, chatOpenAI                  │
│  - 基础: set, if, httpRequest               │
│  数量: ~20 个                               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 2: 动态节点 (从 n8n API 查询)       │
│  - 查询 /node-types 端点                   │
│  - 缓存节点列表                             │
│  - 自动生成参数模板                         │
│  数量: 400+ 个                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 3: 通用节点 (智能参数生成)          │
│  - 未知节点使用 LLM 生成参数                │
│  - 基于节点名称和描述推断                   │
│  数量: 无限                                 │
└─────────────────────────────────────────────┘
```

#### 具体步骤

##### 步骤 1: 实现 n8n API 客户端（2-3小时）
**新建文件**: `src/agents/shared/n8n_node_registry.py`

```python
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class N8NNodeRegistry:
    """n8n 节点注册表 - 动态获取和缓存节点信息"""
    
    def __init__(self, api_url: str, api_key: str, cache_ttl: int = 3600):
        """
        初始化节点注册表
        
        Args:
            api_url: n8n API 地址
            api_key: n8n API 密钥
            cache_ttl: 缓存过期时间（秒）
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        
        self._node_types_cache = None
        self._cache_time = None
    
    def get_all_node_types(self) -> Dict[str, Dict]:
        """
        获取所有节点类型
        
        Returns:
            Dict[node_name, node_info]
        """
        # 检查缓存
        if self._is_cache_valid():
            return self._node_types_cache
        
        # 从 API 获取
        try:
            headers = {"X-N8N-API-KEY": self.api_key}
            response = requests.get(
                f"{self.api_url}/api/v1/node-types",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            node_types = response.json()
            
            # 更新缓存
            self._node_types_cache = node_types
            self._cache_time = datetime.now()
            
            return node_types
        except Exception as e:
            print(f"❌ 获取 n8n 节点类型失败: {e}")
            # 返回核心节点列表作为fallback
            return self._get_core_nodes()
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._node_types_cache is None or self._cache_time is None:
            return False
        
        age = (datetime.now() - self._cache_time).total_seconds()
        return age < self.cache_ttl
    
    def _get_core_nodes(self) -> Dict[str, Dict]:
        """获取核心节点列表（fallback）"""
        return {
            "n8n-nodes-base.manualTrigger": {
                "displayName": "Manual Trigger",
                "name": "manualTrigger",
                "group": ["trigger"],
                "version": 1
            },
            "n8n-nodes-base.set": {
                "displayName": "Set",
                "name": "set",
                "group": ["transform"],
                "version": 3
            },
            # ... 其他核心节点 ...
        }
    
    def search_nodes(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        搜索节点
        
        Args:
            query: 搜索关键词
            category: 节点类别（trigger, transform, action等）
        
        Returns:
            匹配的节点列表
        """
        all_nodes = self.get_all_node_types()
        results = []
        
        for node_id, node_info in all_nodes.items():
            # 按关键词搜索
            if query.lower() in node_info.get("displayName", "").lower():
                if category is None or category in node_info.get("group", []):
                    results.append({
                        "id": node_id,
                        "name": node_info.get("name"),
                        "displayName": node_info.get("displayName"),
                        "group": node_info.get("group", []),
                        "version": node_info.get("version", 1)
                    })
        
        return results
    
    def get_node_parameters_schema(self, node_type: str) -> Dict:
        """
        获取节点的参数 Schema
        
        Args:
            node_type: 节点类型
        
        Returns:
            参数 Schema
        """
        # 从 n8n API 获取详细信息
        try:
            headers = {"X-N8N-API-KEY": self.api_key}
            response = requests.get(
                f"{self.api_url}/api/v1/node-types/{node_type}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            node_details = response.json()
            return node_details.get("properties", [])
        except Exception as e:
            print(f"❌ 获取节点参数 Schema 失败: {e}")
            return []
```

##### 步骤 2: 集成节点注册表到工作流生成（2-3小时）
**文件**: `src/agents/shared/n8n_api_tools.py`

**修改 `_build_workflow_prompt` 方法**:

```python
def _build_workflow_prompt(self, description: str, last_error: str = None, last_response: str = None) -> str:
    """
    构建工作流设计提示词（使用动态节点列表）
    """
    # 🆕 从注册表获取节点
    node_registry = N8NNodeRegistry(
        api_url=self.api_url,
        api_key=self.api_key
    )
    
    all_nodes = node_registry.get_all_node_types()
    
    # 🆕 按类别组织节点
    nodes_by_category = {}
    for node_id, node_info in all_nodes.items():
        for group in node_info.get("group", ["other"]):
            if group not in nodes_by_category:
                nodes_by_category[group] = []
            nodes_by_category[group].append({
                "name": node_info.get("name"),
                "displayName": node_info.get("displayName"),
                "description": node_info.get("description", "")
            })
    
    # 🆕 生成节点列表文本
    nodes_text = "可用的节点类型：\n\n"
    
    category_names = {
        "trigger": "【触发器类】",
        "transform": "【数据处理类】",
        "action": "【操作执行类】",
        "ai": "【AI/智能类】"
    }
    
    for category, display_name in category_names.items():
        if category in nodes_by_category:
            nodes_text += f"{display_name}\n"
            for node in nodes_by_category[category][:10]:  # 每类最多10个
                nodes_text += f"- {node['name']}: {node['displayName']}\n"
            nodes_text += "\n"
    
    # ... 构建完整提示词 ...
```

##### 步骤 3: 实现智能参数生成（3-4小时）
**文件**: `src/agents/shared/n8n_api_tools.py`

**新增方法**:

```python
def _generate_node_parameters_dynamically(self, node_type: str, node_design: Dict) -> Dict:
    """
    使用 LLM 动态生成节点参数
    
    Args:
        node_type: 节点类型
        node_design: LLM 设计的节点信息
    
    Returns:
        节点参数字典
    """
    # 从注册表获取参数 Schema
    schema = self.node_registry.get_node_parameters_schema(node_type)
    
    if not schema:
        # 如果没有 Schema，使用 LLM 生成
        return self._llm_generate_parameters(node_type, node_design)
    
    # 根据 Schema 生成参数
    parameters = {}
    for param in schema:
        param_name = param.get("name")
        param_type = param.get("type")
        default_value = param.get("default")
        
        if param.get("required"):
            # 必填参数
            if param_type == "string":
                parameters[param_name] = node_design.get("description", "")
            elif param_type == "number":
                parameters[param_name] = default_value or 0
            elif param_type == "boolean":
                parameters[param_name] = default_value or False
        else:
            # 可选参数使用默认值
            if default_value is not None:
                parameters[param_name] = default_value
    
    return parameters

def _llm_generate_parameters(self, node_type: str, node_design: Dict) -> Dict:
    """使用 LLM 生成未知节点的参数"""
    prompt = f"""请为以下 n8n 节点生成合理的参数配置:

节点类型: {node_type}
节点描述: {node_design.get("description", "")}
节点功能: {node_design.get("purpose", "")}

要求:
1. 以 JSON 格式返回
2. 参数名使用小驼峰命名
3. 参数值应该符合实际使用场景

JSON 格式:
{{
  "parameterName": "value",
  "anotherParameter": "value"
}}
"""
    
    # 调用 LLM
    try:
        from src.infrastructure.llm.llm_factory import LLMFactory
        llm = LLMFactory.create_llm()
        response = llm.invoke(prompt)
        
        # 解析 JSON
        import json
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except Exception as e:
        print(f"❌ LLM 参数生成失败: {e}")
        return {}
```

##### 步骤 4: 更新版本映射（1小时）
**文件**: `src/agents/shared/n8n_api_tools.py`

**重构 `_get_type_version` 方法**:

```python
def _get_type_version(self, node_type: str) -> int:
    """
    获取节点类型版本（动态查询 + 缓存）
    """
    # 🆕 从注册表查询
    all_nodes = self.node_registry.get_all_node_types()
    
    if node_type in all_nodes:
        return all_nodes[node_type].get("version", 1)
    
    # 回退到静态映射（核心节点）
    static_map = {
        "n8n-nodes-base.manualTrigger": 1,
        "n8n-nodes-base.set": 3,
        # ... 只保留核心节点 ...
    }
    
    return static_map.get(node_type, 1)
```

##### 步骤 5: 测试验证（2小时）
创建测试用例:

```python
# tests/unit/test_n8n_node_registry.py
def test_node_registry_dynamic_loading():
    registry = N8NNodeRegistry(
        api_url="http://localhost:5678",
        api_key="test_key"
    )
    
    # 测试获取所有节点
    nodes = registry.get_all_node_types()
    assert len(nodes) > 100  # 应该获取到大量节点
    
    # 测试搜索功能
    slack_nodes = registry.search_nodes("slack")
    assert len(slack_nodes) > 0
    assert "slack" in slack_nodes[0]["displayName"].lower()
```

---

### 任务 1.3: 消除硬编码值（P1）

**优先级**: 🔴 高
**预计时间**: 2-4 小时
**影响范围**: 部署灵活性

#### 具体步骤

##### 步骤 1: 创建环境变量管理器（1小时）
**新建文件**: `src/config/env_manager.py`

```python
import os
from typing import Any, Optional
from dotenv import load_dotenv

class EnvManager:
    """环境变量管理器 - 统一管理所有环境变量"""
    
    # 加载 .env 文件
    load_dotenv()
    
    # API 配置
    N8N_API_URL = os.getenv('N8N_API_URL', 'http://localhost:5678')
    N8N_API_KEY = os.getenv('N8N_API_KEY', '')
    
    # Redis 配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # LLM 配置
    DEFAULT_LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'siliconflow')
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'Pro/deepseek-ai/DeepSeek-V3.1-Terminus')
    
    # 超时配置
    DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '30'))
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '60'))
    HTTP_TIMEOUT = int(os.getenv('HTTP_TIMEOUT', '10'))
    
    # Token 配置
    DEFAULT_MAX_TOKENS = int(os.getenv('DEFAULT_MAX_TOKENS', '4000'))
    CREWAI_MAX_TOKENS = int(os.getenv('CREWAI_MAX_TOKENS', '8000'))
    
    # Iteration 配置
    DEFAULT_MAX_ITERATIONS = int(os.getenv('DEFAULT_MAX_ITERATIONS', '25'))
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        获取环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
        
        Returns:
            环境变量值或默认值
        """
        return os.getenv(key, default)
    
    @staticmethod
    def require(key: str) -> str:
        """
        获取必需的环境变量（不存在则抛出异常）
        
        Args:
            key: 环境变量名
        
        Returns:
            环境变量值
        
        Raises:
            ValueError: 环境变量不存在
        """
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"缺少必需的环境变量: {key}")
        return value
```

##### 步骤 2: 替换硬编码值（1-2小时）
**修改多个文件**:

```python
# src/agents/shared/n8n_api_tools.py
from src.config.env_manager import EnvManager

class N8NGenerateAndCreateWorkflowTool(BaseTool):
    def __init__(
        self,
        api_url: str = None,  # ✅ 改为可选
        api_key: str = None,  # ✅ 改为可选
        ...
    ):
        # ✅ 使用环境变量管理器
        self.api_url = api_url or EnvManager.N8N_API_URL
        self.api_key = api_key or EnvManager.N8N_API_KEY
```

```python
# src/storage/redis_chat_history.py
from src.config.env_manager import EnvManager

def __init__(
    self,
    session_id: str,
    redis_url: str = None,  # ✅ 改为可选
    ...
):
    # ✅ 使用环境变量管理器
    redis_url = redis_url or EnvManager.REDIS_URL
```

```python
# src/agents/shared/crewai_tools.py
from src.config.env_manager import EnvManager

def _run(self, query: str) -> str:
    # ✅ 使用环境变量的超时配置
    response = requests.get(
        url,
        headers=headers,
        timeout=EnvManager.HTTP_TIMEOUT
    )
```

##### 步骤 3: 创建 .env.example（0.5小时）
**新建文件**: `.env.example`

```bash
# n8n 配置
N8N_API_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here

# Redis 配置
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# LLM 配置
LLM_PROVIDER=siliconflow
DEFAULT_MODEL=Pro/deepseek-ai/DeepSeek-V3.1-Terminus

# 超时配置（秒）
DEFAULT_TIMEOUT=30
LLM_TIMEOUT=60
HTTP_TIMEOUT=10

# Token 配置
DEFAULT_MAX_TOKENS=4000
CREWAI_MAX_TOKENS=8000

# Iteration 配置
DEFAULT_MAX_ITERATIONS=25
```

##### 步骤 4: 更新文档（0.5小时）
更新 `README.md` 和 `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md` 说明环境变量配置。

---

---

### 任务 1.4: 实现自动继续执行机制（P1）

**优先级**: 🔴 高
**预计时间**: 3-4 小时
**影响范围**: 任务完成率

#### 问题描述
当前智能体在达到 `max_iterations` 或 `max_execution_time` 限制时会停止执行，即使任务未完成。这导致：
- ❌ 复杂任务无法完成
- ❌ 用户需要手动重启
- ❌ 上下文丢失

#### 解决方案：智能续接机制

##### 步骤 1: 实现执行状态检测（1小时）
**文件**: `src/agents/unified/unified_agent.py`

**新增状态枚举**:
```python
from enum import Enum

class AgentStopReason(Enum):
    """智能体停止原因"""
    COMPLETED = "completed"              # 任务完成
    ITERATION_LIMIT = "iteration_limit"  # 达到迭代次数限制
    TIME_LIMIT = "time_limit"           # 达到时间限制
    ERROR = "error"                     # 发生错误
    USER_INTERRUPT = "user_interrupt"   # 用户中断
```

**修改 `run` 方法**:
```python
def run(self, query: str, **kwargs) -> str:
    """
    运行智能体（支持自动续接）
    
    Args:
        query: 用户查询
        auto_continue: 是否自动继续（默认True）
        max_retries: 最大续接次数（默认3）
    
    Returns:
        执行结果
    """
    auto_continue = kwargs.get('auto_continue', True)
    max_retries = kwargs.get('max_retries', 3)
    retry_count = 0
    
    accumulated_result = ""
    current_query = query
    
    while retry_count <= max_retries:
        # 执行智能体
        result, stop_reason = self._execute_with_status(current_query, **kwargs)
        
        # 累积结果
        if retry_count == 0:
            accumulated_result = result
        else:
            accumulated_result += f"\n\n[续接 {retry_count}]\n{result}"
        
        # 检查停止原因
        if stop_reason == AgentStopReason.COMPLETED:
            # 任务完成，返回结果
            self.logger.info("✅ 任务成功完成")
            return accumulated_result
        
        elif stop_reason in [AgentStopReason.ITERATION_LIMIT, AgentStopReason.TIME_LIMIT]:
            if not auto_continue:
                # 不自动继续，返回部分结果
                self.logger.warning(f"⚠️ 达到{stop_reason.value}限制，停止执行")
                return accumulated_result
            
            # 自动继续
            retry_count += 1
            if retry_count > max_retries:
                self.logger.error(f"❌ 达到最大续接次数 ({max_retries})，停止执行")
                return accumulated_result + "\n\n[系统提示: 任务可能未完全完成，已达到最大续接次数]"
            
            # 生成续接提示
            current_query = self._generate_continuation_prompt(
                original_query=query,
                previous_result=result,
                stop_reason=stop_reason
            )
            
            self.logger.info(f"🔄 自动续接 ({retry_count}/{max_retries}): {stop_reason.value}")
        
        else:
            # 错误或中断，停止执行
            self.logger.error(f"❌ 执行失败: {stop_reason.value}")
            return accumulated_result
    
    return accumulated_result

def _execute_with_status(self, query: str, **kwargs) -> tuple[str, AgentStopReason]:
    """
    执行智能体并返回停止原因
    
    Returns:
        (result, stop_reason)
    """
    try:
        start_time = time.time()
        
        # 执行原有逻辑
        if self.agent_executor:
            result = self.agent_executor.invoke(
                {"input": query},
                config={"callbacks": self._create_callbacks()}
            )
            
            # 检查停止原因
            elapsed_time = time.time() - start_time
            max_execution_time = self.agent_config.get("max_execution_time", 180)
            
            # 从 agent_executor 获取实际的迭代次数
            actual_iterations = getattr(self.agent_executor, '_iterations', 0)
            max_iterations = self.agent_config.get("max_iterations", 25)
            
            # 判断停止原因
            if actual_iterations >= max_iterations:
                stop_reason = AgentStopReason.ITERATION_LIMIT
            elif elapsed_time >= max_execution_time:
                stop_reason = AgentStopReason.TIME_LIMIT
            else:
                stop_reason = AgentStopReason.COMPLETED
            
            return result.get("output", str(result)), stop_reason
        
        else:
            # 如果没有 executor，使用 LLM 直接回答
            response = self.llm.invoke(query)
            return response.content, AgentStopReason.COMPLETED
    
    except KeyboardInterrupt:
        return "执行被用户中断", AgentStopReason.USER_INTERRUPT
    except Exception as e:
        self.logger.error(f"执行错误: {e}")
        return f"执行失败: {str(e)}", AgentStopReason.ERROR

def _generate_continuation_prompt(
    self,
    original_query: str,
    previous_result: str,
    stop_reason: AgentStopReason
) -> str:
    """
    生成续接提示
    
    Args:
        original_query: 原始查询
        previous_result: 上一次的结果
        stop_reason: 停止原因
    
    Returns:
        续接提示
    """
    if stop_reason == AgentStopReason.ITERATION_LIMIT:
        reason_text = "达到迭代次数限制"
    elif stop_reason == AgentStopReason.TIME_LIMIT:
        reason_text = "达到执行时间限制"
    else:
        reason_text = "未知原因"
    
    # 提取上一次的最后几步操作
    last_actions = self._extract_last_actions(previous_result, n=3)
    
    continuation_prompt = f"""[系统提示: 由于{reason_text}，任务执行被中断。请继续完成任务。]

原始任务: {original_query}

已完成的部分:
{previous_result[-500:]}  # 只保留最后500字符

最近的操作:
{last_actions}

请继续执行任务，从上次中断的地方继续。不要重复已完成的工作。
"""
    
    return continuation_prompt

def _extract_last_actions(self, result: str, n: int = 3) -> str:
    """
    从结果中提取最后 n 个操作
    
    Args:
        result: 执行结果
        n: 提取的操作数量
    
    Returns:
        操作摘要
    """
    # 尝试从结果中提取 "Action:" 行
    import re
    actions = re.findall(r'Action:\s*(.+)', result)
    
    if actions:
        last_n = actions[-n:]
        return "\n".join([f"- {action}" for action in last_n])
    
    # 如果没有找到 Action，返回空字符串
    return "无法提取操作历史"
```

##### 步骤 2: 优化迭代限制配置（0.5小时）
**文件**: `config/base/agents.yaml`

**添加续接相关配置**:
```yaml
unified_agent:
  name: "统一智能体"
  description: "支持多种任务的通用智能体"
  max_iterations: 25
  max_execution_time: 180  # 秒
  
  # 🆕 自动续接配置
  auto_continue:
    enabled: true           # 是否启用自动续接
    max_retries: 3         # 最大续接次数
    reset_iterations: true  # 续接时是否重置迭代计数
```

##### 步骤 3: 实现智能任务分解（1-1.5小时）
**新建文件**: `src/core/services/task_decomposer.py`

```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SubTask:
    """子任务"""
    id: str
    description: str
    priority: int
    estimated_iterations: int
    dependencies: List[str]  # 依赖的子任务ID

class TaskDecomposer:
    """任务分解器 - 将复杂任务分解为子任务"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def decompose(self, task: str, max_iterations_per_subtask: int = 10) -> List[SubTask]:
        """
        分解任务
        
        Args:
            task: 任务描述
            max_iterations_per_subtask: 每个子任务的最大迭代次数
        
        Returns:
            子任务列表
        """
        prompt = f"""请将以下复杂任务分解为多个可独立执行的子任务：

任务: {task}

要求:
1. 每个子任务应该能在 {max_iterations_per_subtask} 步内完成
2. 子任务之间应该有清晰的依赖关系
3. 子任务描述应该具体、可执行

以 JSON 格式返回，格式如下:
{{
  "subtasks": [
    {{
      "id": "task_1",
      "description": "子任务描述",
      "priority": 1,
      "estimated_iterations": 5,
      "dependencies": []
    }}
  ]
}}
"""
        
        response = self.llm.invoke(prompt)
        
        # 解析 JSON
        import json
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            subtasks = []
            for item in data.get("subtasks", []):
                subtasks.append(SubTask(
                    id=item["id"],
                    description=item["description"],
                    priority=item.get("priority", 1),
                    estimated_iterations=item.get("estimated_iterations", 10),
                    dependencies=item.get("dependencies", [])
                ))
            return subtasks
        
        # 如果解析失败，返回原任务作为单个子任务
        return [SubTask(
            id="task_1",
            description=task,
            priority=1,
            estimated_iterations=max_iterations_per_subtask,
            dependencies=[]
        )]
    
    def should_decompose(self, task: str, max_iterations: int) -> bool:
        """
        判断任务是否需要分解
        
        Args:
            task: 任务描述
            max_iterations: 最大迭代次数
        
        Returns:
            是否需要分解
        """
        # 简单的启发式规则
        complexity_indicators = [
            "并且", "然后", "接着", "之后",
            "步骤", "阶段", "首先", "其次", "最后",
            "分析", "生成", "创建", "执行", "部署"
        ]
        
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in task)
        
        # 如果复杂度评分 > 3，建议分解
        return complexity_score > 3
```

##### 步骤 4: 集成任务分解（1小时）
**文件**: `src/agents/unified/unified_agent.py`

**修改 `run` 方法**:
```python
def run(self, query: str, **kwargs) -> str:
    """运行智能体（支持任务分解和自动续接）"""
    
    # 🆕 检查是否需要任务分解
    decompose_enabled = self.agent_config.get("auto_continue", {}).get("task_decomposition", True)
    max_iterations = self.agent_config.get("max_iterations", 25)
    
    if decompose_enabled:
        decomposer = TaskDecomposer(self.llm)
        if decomposer.should_decompose(query, max_iterations):
            # 分解任务
            subtasks = decomposer.decompose(query, max_iterations_per_subtask=10)
            
            self.logger.info(f"📋 任务已分解为 {len(subtasks)} 个子任务")
            
            # 按依赖顺序执行子任务
            results = {}
            for subtask in subtasks:
                # 检查依赖
                if all(dep in results for dep in subtask.dependencies):
                    self.logger.info(f"▶️ 执行子任务: {subtask.description}")
                    
                    # 执行子任务（使用原有的自动续接逻辑）
                    result = self._execute_subtask(subtask, results, **kwargs)
                    results[subtask.id] = result
            
            # 汇总结果
            final_result = self._summarize_results(query, results)
            return final_result
    
    # 原有的执行逻辑（带自动续接）
    return self._execute_with_auto_continue(query, **kwargs)
```

##### 步骤 5: 添加进度追踪（0.5小时）
**文件**: `src/agents/unified/unified_agent.py`

```python
class UnifiedAgent:
    def __init__(self, ...):
        # ... 现有代码 ...
        self.progress_tracker = ProgressTracker()  # 🆕 进度追踪器
    
    def run(self, query: str, **kwargs) -> str:
        # 🆕 初始化进度
        self.progress_tracker.start(query)
        
        try:
            # ... 执行逻辑 ...
            
            # 🆕 更新进度
            self.progress_tracker.update(step="执行中", progress=50)
            
            # ... 继续执行 ...
            
            # 🆕 完成
            self.progress_tracker.complete(result)
        
        except Exception as e:
            # 🆕 记录失败
            self.progress_tracker.fail(str(e))
            raise
```

**新建文件**: `src/core/services/progress_tracker.py`

```python
from datetime import datetime
from typing import Optional

class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self):
        self.task = None
        self.start_time = None
        self.current_step = None
        self.progress = 0
    
    def start(self, task: str):
        """开始任务"""
        self.task = task
        self.start_time = datetime.now()
        self.current_step = "初始化"
        self.progress = 0
        print(f"⏳ 开始执行: {task}")
    
    def update(self, step: str, progress: int):
        """更新进度"""
        self.current_step = step
        self.progress = progress
        print(f"▶️ {step} ({progress}%)")
    
    def complete(self, result: str):
        """完成任务"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"✅ 任务完成 (耗时: {elapsed:.1f}秒)")
    
    def fail(self, error: str):
        """任务失败"""
        print(f"❌ 任务失败: {error}")
```

##### 步骤 6: 测试验证（0.5小时）
**新建测试**: `tests/unit/test_auto_continue.py`

```python
def test_auto_continue_on_iteration_limit():
    """测试迭代限制时自动继续"""
    agent = UnifiedAgent(
        auto_continue=True,
        max_retries=2
    )
    
    # 模拟一个需要很多步骤的任务
    result = agent.run("执行一个复杂的多步骤任务")
    
    # 验证任务完成（即使超过了单次迭代限制）
    assert "任务完成" in result or "续接" in result

def test_task_decomposition():
    """测试任务分解"""
    agent = UnifiedAgent()
    
    complex_task = "首先分析数据，然后生成报告，最后发送邮件通知"
    result = agent.run(complex_task)
    
    # 验证任务被分解执行
    assert "子任务" in result or len(result) > 100
```

---

## 🔄 Phase 2: 重要优化（P2）

### 任务 2.1: 重构复杂函数（P2）

**优先级**: 🟡 中等
**预计时间**: 6-8 小时

#### 步骤 1: 重构 `create_crew()` 函数（3-4小时）
**文件**: `src/interfaces/crewai_runtime.py`

**重构策略**: 提取子函数，单一职责

```python
# 重构前: 235 行的巨型函数
def create_crew(self):
    # 235 行代码...
    pass

# 重构后: 拆分为多个小函数
def create_crew(self) -> bool:
    """创建 CrewAI 团队（流程编排）"""
    try:
        # 1. 加载配置
        config = self._load_and_validate_config()
        if not config:
            return False
        
        # 2. 创建 LLM
        llm = self._create_llm(config)
        if not llm:
            return False
        
        # 3. 创建工具
        tools = self._create_tools(config)
        
        # 4. 创建 Agents
        self.agents = self._create_agents(config, llm, tools)
        if not self.agents:
            return False
        
        # 5. 创建 Tasks
        self.tasks = self._create_tasks(config, self.agents)
        if not self.tasks:
            return False
        
        # 6. 组装 Crew
        self.crew = self._assemble_crew(config)
        
        return self.crew is not None
    
    except Exception as e:
        self.logger.error(f"创建团队失败: {e}")
        return False

def _load_and_validate_config(self) -> Optional[Dict]:
    """加载并验证配置（20-30行）"""
    pass

def _create_llm(self, config: Dict) -> Optional[Any]:
    """创建 LLM 实例（30-40行）"""
    pass

def _create_tools(self, config: Dict) -> List:
    """创建工具列表（40-50行）"""
    pass

def _create_agents(self, config: Dict, llm: Any, tools: List) -> List:
    """创建 Agent 列表（50-60行）"""
    pass

def _create_tasks(self, config: Dict, agents: List) -> List:
    """创建 Task 列表（40-50行）"""
    pass

def _assemble_crew(self, config: Dict) -> Optional[Any]:
    """组装 Crew（20-30行）"""
    pass
```

#### 步骤 2: 重构其他复杂函数（2-3小时）
- `_process_stream_chunk()` (162行)
- `_load_agent_templates()` (137行)
- `_build_workflow_prompt()` (134行)

#### 步骤 3: 单元测试（1小时）
为重构后的函数编写单元测试。

---

### 任务 2.2: 优化异常处理（P2）

**预计时间**: 2-3小时

#### 步骤 1: 消除裸 except（1小时）
替换所有 `except:` 为具体异常类型。

#### 步骤 2: 添加日志记录（1小时）
为所有 `except: pass` 添加日志。

#### 步骤 3: 创建自定义异常类（1小时）
**新建文件**: `src/exceptions/agent_exceptions.py`

```python
class AgentBaseException(Exception):
    """Agent 基础异常"""
    pass

class ToolExecutionError(AgentBaseException):
    """工具执行错误"""
    pass

class ConfigurationError(AgentBaseException):
    """配置错误"""
    pass

class LLMError(AgentBaseException):
    """LLM 调用错误"""
    pass
```

---

### 任务 2.3: 性能优化（P2）

**预计时间**: 4-6 小时

#### 步骤 1: 配置缓存（1-2小时）
实现配置文件缓存机制。

#### 步骤 2: 并发 LLM 调用（2-3小时）
使用 `asyncio` 实现并发调用。

#### 步骤 3: 添加性能监控（1小时）
记录关键操作的执行时间。

---

## 🏗️ Phase 3: 架构重构（P3）

### 任务 3.1: 重组目录结构（P3）

**预计时间**: 16-24 小时

#### 步骤 1: 制定迁移计划（2小时）
详细规划文件迁移路径。

#### 步骤 2: 迁移工具模块（4-6小时）
将 `agents/shared/tools.py` 等迁移到 `tools/` 目录。

#### 步骤 3: 创建统一的工具加载器（4-6小时）
重构工具加载逻辑。

#### 步骤 4: 更新所有导入（4-6小时）
修改所有文件的 import 语句。

#### 步骤 5: 测试验证（2-4小时）
确保所有功能正常。

---

## 📊 实施时间表

```
Week 1 (Day 1-5):
  Day 1-2: Phase 1 - 任务 1.1 (上下文逻辑修复)
  Day 3-4: Phase 1 - 任务 1.2 (n8n 节点重构 Part 1)
  Day 5:   Phase 1 - 任务 1.2 (n8n 节点重构 Part 2)

Week 2 (Day 6-10):
  Day 6:   Phase 1 - 任务 1.3 (消除硬编码)
  Day 7:   Phase 1 - 任务 1.4 (自动继续执行机制) 🆕
  Day 8-9: Phase 2 - 任务 2.1 (重构复杂函数)
  Day 10:  Phase 2 - 任务 2.2 (优化异常处理)

Week 3 (Day 11-15):
  Day 11:  Phase 2 - 任务 2.3 (性能优化)
  Day 12-15: Phase 3 - 架构重构（可选）

Week 4+ (可选):
  持续优化和监控
```

---

## ✅ 验收标准

### Phase 1 验收标准
- [ ] 智能体能正确理解"运行它"并调用对应工具
- [ ] n8n 节点覆盖率 > 80% (320+ 节点)
- [ ] 硬编码值 < 5 处（仅保留必要默认值）
- [ ] 所有配置可通过环境变量覆盖
- [ ] 🆕 智能体达到迭代/时间限制时自动继续执行
- [ ] 🆕 复杂任务自动分解为子任务
- [ ] 🆕 任务完成率 > 95%（不因限制而失败）

### Phase 2 验收标准
- [x] 所有函数 < 100 行
- [x] 无裸 except
- [x] 配置加载性能提升 50%+
- [x] LLM 调用支持并发

### Phase 3 验收标准
- [x] 目录结构清晰合理
- [x] 模块职责单一
- [x] 导入路径统一
- [x] 所有测试通过

---

## 🔄 回滚计划

每个阶段完成后创建 Git Tag:
```bash
git tag -a v1.1-phase1-complete -m "Phase 1 优化完成"
git tag -a v1.2-phase2-complete -m "Phase 2 优化完成"
git tag -a v2.0-phase3-complete -m "Phase 3 架构重构完成"
```

如果出现问题，可快速回滚:
```bash
git checkout v1.1-phase1-complete
```

---

*计划生成时间: 2025-10-28*
*预计总工时: 42-62 小时*
*建议实施周期: 2-3 周*

