# CrewAI工具配置指南

## 概述

CrewAI工具系统允许CrewAI智能体调用各种功能工具。本指南详细说明了工具的配置位置、脚本位置以及如何添加新工具。

## 📁 文件结构

```
Agent-V3/
├── config/base/services.yaml          # ✅ 工具配置文件
├── src/
│   ├── agents/shared/
│   │   └── crewai_tools.py           # ✅ 工具实现脚本
│   └── interfaces/
│       └── crewai_runtime.py          # ✅ 工具加载和集成
└── docs/
    └── CREWAI_TOOLS_GUIDE.md         # 本文档
```

## 🔧 工具配置位置

### 1. 主配置文件

**文件**: `config/base/services.yaml`

**位置**: 第56-121行（crewai.tools部分）

```yaml
crewai:
  enabled: true
  llm:
    provider: "siliconflow"
    # ... LLM配置 ...
  
  # ✅ CrewAI工具配置
  tools:
    enabled: true                      # 是否启用工具
    
    # 默认工具列表（所有Agent都会获得）
    default_tools:
      - "time"                         # 时间查询
      - "search"                       # 网络搜索
      - "calculator"                   # 数学计算
    
    # 角色特定工具（根据Agent角色分配）
    role_tools:
      coder:                           # 代码生成Agent
        - "time"
        - "search"
        - "calculator"
        - "n8n_generate_workflow"      # N8N工作流生成
      
      analyst:                         # 数据分析Agent
        - "time"
        - "search"
        - "calculator"
      
      planner:                         # 规划Agent
        - "time"
        - "search"
        - "calculator"
      
      coordinator:                     # 协调Agent
        - "time"
        - "search"
      
      executor:                        # 执行Agent
        - "time"
        - "calculator"
      
      reviewer:                        # 审查Agent
        - "time"
        - "search"
    
    # 可用工具配置（工具的详细配置）
    available_tools:
      time:
        enabled: true
        description: "获取当前时间"
      
      search:
        enabled: true
        description: "网络搜索工具"
        max_results: 10                # 搜索结果数量
      
      calculator:
        enabled: true
        description: "数学计算工具"
      
      n8n_generate_workflow:
        enabled: true
        description: "n8n工作流生成工具"
        type: "mcp_stdio"
```

### 2. 工具优先级

CrewAI Agent获取工具的优先级：

1. **Agent配置中指定的工具** (最高优先级)
2. **角色特定工具** (`role_tools`)
3. **默认工具** (`default_tools`)

## 💻 工具实现脚本

### 1. 工具定义文件

**文件**: `src/agents/shared/crewai_tools.py`

这个文件包含所有CrewAI工具的实现：

```python
"""
CrewAI兼容的工具包
"""

from crewai.tools import BaseTool

# ✅ 1. 计算器工具
class CrewAICalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "执行数学计算"
    
    def _run(self, expression: str) -> str:
        # 工具逻辑
        ...

# ✅ 2. 时间工具
class CrewAITimeTool(BaseTool):
    name: str = "time"
    description: str = "获取当前时间"
    
    def _run(self, query: str = "") -> str:
        # 工具逻辑
        ...

# ✅ 3. 搜索工具
class CrewAISearchTool(BaseTool):
    name: str = "search"
    description: str = "搜索互联网信息"
    
    def _run(self, query: str) -> str:
        # 工具逻辑
        ...

# ✅ 4. N8N工作流生成工具
class CrewAIN8NGeneratorTool(BaseTool):
    name: str = "n8n_generate_workflow"
    description: str = "生成N8N工作流"
    
    def _run(self, workflow_description: str) -> str:
        # 工具逻辑
        ...

# ✅ 工具创建函数
def create_crewai_tools(tool_names: list = None) -> list:
    """创建CrewAI工具列表"""
    all_tools = {
        "calculator": CrewAICalculatorTool(),
        "time": CrewAITimeTool(),
        "search": CrewAISearchTool(),
        "n8n_generate_workflow": CrewAIN8NGeneratorTool()
    }
    
    if tool_names is None:
        return list(all_tools.values())
    
    tools = []
    for name in tool_names:
        if name in all_tools:
            tools.append(all_tools[name])
    
    return tools
```

### 2. 运行时集成

**文件**: `src/interfaces/crewai_runtime.py`

**位置**: 第299-337行

这个文件负责在创建CrewAI Agent时加载和分配工具：

```python
# 获取工具配置
if tools_enabled:
    # 确定工具列表
    if agent_config.get("tools"):
        tool_names = agent_config["tools"]
    elif agent_role_type in role_tools_mapping:
        tool_names = role_tools_mapping[agent_role_type]
    else:
        tool_names = default_tools
    
    # ✅ 创建CrewAI工具
    from src.agents.shared.crewai_tools import create_crewai_tools
    agent_tools = create_crewai_tools(tool_names)
    
# ✅ 创建Agent并传递工具
agent = Agent(
    role=agent_role,
    goal=agent_config["goal"],
    backstory=agent_config["backstory"],
    llm=agent_llm,
    tools=agent_tools  # 传递工具
)
```

## 🆕 如何添加新工具

### 步骤1: 在`crewai_tools.py`中实现工具

```python
# src/agents/shared/crewai_tools.py

class CrewAIYourNewTool(BaseTool):
    """你的新工具"""
    
    name: str = "your_new_tool"
    description: str = "工具描述，告诉AI这个工具是做什么的"
    
    def _run(self, input_param: str) -> str:
        """
        工具执行逻辑
        
        Args:
            input_param: 输入参数
            
        Returns:
            工具执行结果
        """
        try:
            # 你的工具逻辑
            result = do_something(input_param)
            return f"成功: {result}"
        except Exception as e:
            return f"错误: {str(e)}"
```

### 步骤2: 将工具添加到工具映射

在`create_crewai_tools`函数中添加：

```python
def create_crewai_tools(tool_names: list = None) -> list:
    all_tools = {
        "calculator": CrewAICalculatorTool(),
        "time": CrewAITimeTool(),
        "search": CrewAISearchTool(),
        "n8n_generate_workflow": CrewAIN8NGeneratorTool(),
        "your_new_tool": CrewAIYourNewTool(),  # ✅ 添加新工具
    }
    # ...
```

### 步骤3: 在配置文件中声明工具

编辑`config/base/services.yaml`：

```yaml
crewai:
  tools:
    # 添加到默认工具
    default_tools:
      - "time"
      - "search"
      - "calculator"
      - "your_new_tool"  # ✅ 添加到默认工具
    
    # 或添加到特定角色
    role_tools:
      your_role:
        - "time"
        - "your_new_tool"  # ✅ 只给特定角色
    
    # 在available_tools中配置
    available_tools:
      your_new_tool:
        enabled: true
        description: "你的新工具描述"
        # 其他配置参数
        custom_param: "value"
```

### 步骤4: 测试新工具

```python
# 测试工具
from src.agents.shared.crewai_tools import CrewAIYourNewTool

tool = CrewAIYourNewTool()
result = tool._run("test input")
print(result)
```

## 📊 现有工具列表

### 1. Calculator (计算器)
- **名称**: `calculator`
- **描述**: 执行数学计算
- **输入**: 数学表达式 (如 "10 + 20 * 3")
- **输出**: 计算结果
- **配置**: `config/base/services.yaml:115-117`

### 2. Time (时间)
- **名称**: `time`
- **描述**: 获取当前日期和时间
- **输入**: 无需参数
- **输出**: 当前时间字符串
- **配置**: `config/base/services.yaml:108-110`

### 3. Search (搜索)
- **名称**: `search`
- **描述**: 搜索互联网信息
- **输入**: 搜索查询字符串
- **输出**: 搜索结果列表
- **配置**: `config/base/services.yaml:111-114`
- **参数**: `max_results: 10`

### 4. N8N Workflow Generator (N8N工作流生成)
- **名称**: `n8n_generate_workflow`
- **描述**: 生成N8N工作流配置
- **输入**: 工作流描述
- **输出**: N8N工作流JSON
- **配置**: `config/base/services.yaml:118-121`

## 🎯 角色工具分配

### Coder (代码生成)
```yaml
role_tools:
  coder:
    - "time"
    - "search"
    - "calculator"
    - "n8n_generate_workflow"  # 特有工具
```
**用途**: 生成代码、工作流等

### Analyst (数据分析)
```yaml
role_tools:
  analyst:
    - "time"
    - "search"
    - "calculator"
```
**用途**: 数据分析、计算统计

### Planner (规划)
```yaml
role_tools:
  planner:
    - "time"
    - "search"
    - "calculator"
```
**用途**: 制定计划、时间规划

### Coordinator (协调)
```yaml
role_tools:
  coordinator:
    - "time"
    - "search"
```
**用途**: 协调任务、查找信息

### Executor (执行)
```yaml
role_tools:
  executor:
    - "time"
    - "calculator"
```
**用途**: 执行任务、计算

### Reviewer (审查)
```yaml
role_tools:
  reviewer:
    - "time"
    - "search"
```
**用途**: 审查内容、查找参考

## 🧪 测试工具

### 测试单个工具
```bash
# 测试计算器
python -c "
from src.agents.shared.crewai_tools import CrewAICalculatorTool
tool = CrewAICalculatorTool()
print(tool._run('10 + 20'))
"
```

### 测试工具创建
```bash
# 测试工具列表创建
python -c "
from src.agents.shared.crewai_tools import create_crewai_tools
tools = create_crewai_tools(['calculator', 'time'])
print(f'Created {len(tools)} tools')
for tool in tools:
    print(f'  - {tool.name}')
"
```

### 测试CrewAI集成
```bash
# 测试完整的CrewAI工具流程
python main.py --query "生成一个数据分析团队" --streaming-style simple
```

## 🔍 调试工具问题

### 1. 查看工具加载日志

在`crewai_runtime.py`中，工具加载会输出日志：

```
INFO - 智能体 coder (coder) 配置了工具: ['time', 'search', 'calculator', 'n8n_generate_workflow']
INFO - 已为智能体创建 4 个CrewAI工具
```

### 2. 检查工具是否正确创建

```python
from src.agents.shared.crewai_tools import create_crewai_tools

# 测试工具创建
tools = create_crewai_tools(['calculator'])
print(f"Tool name: {tools[0].name}")
print(f"Tool type: {type(tools[0])}")
print(f"Is BaseTool: {isinstance(tools[0], BaseTool)}")
```

### 3. 启用详细日志

在`main.py`中设置：

```bash
python main.py --debug --query "你的查询"
```

## 💡 最佳实践

### 1. 工具命名
- 使用小写字母和下划线
- 清晰描述工具功能
- 示例: `search`, `calculator`, `n8n_generate_workflow`

### 2. 工具描述
- 简洁明了，告诉AI工具的用途
- 说明输入格式和输出格式
- 提供使用示例

### 3. 错误处理
- 总是使用try-except捕获异常
- 返回友好的错误信息
- 记录详细的错误日志

### 4. 工具性能
- 避免耗时操作
- 设置超时限制
- 考虑缓存结果

## 📚 相关文档

- [N8N工具修复总结](../N8N_TOOL_FIX_SUMMARY.md)
- [工具和CrewAI完整修复报告](../TOOLS_AND_CREWAI_FIX_COMPLETE.md)
- [工具状态报告](../TOOLS_STATUS_REPORT.md)
- [CrewAI官方文档](https://docs.crewai.com/core-concepts/Tools/)

## ❓ 常见问题

### Q: 为什么CrewAI需要单独的工具实现？
**A**: CrewAI使用`crewai.tools.BaseTool`，与LangChain的`langchain.tools.BaseTool`类型不兼容。

### Q: 如何让某个Agent不使用工具？
**A**: 在配置中不指定工具，或者设置`tools: []`空列表。

### Q: 可以在运行时动态添加工具吗？
**A**: 目前不支持。需要在配置文件中声明并重启。

### Q: 工具调用失败怎么办？
**A**: 
1. 查看日志确认工具是否正确加载
2. 测试工具单独运行是否正常
3. 检查工具描述是否清晰
4. 确认输入参数格式正确

---

**版本**: 1.0  
**更新时间**: 2025-10-28  
**维护者**: Agent-V3 Team

