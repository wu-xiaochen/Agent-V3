# CrewAI 标准化配置系统

本系统提供了标准化的CrewAI配置生成、验证和加载功能，用于创建和管理供应链优化团队。

## 功能特点

- 标准化配置结构定义
- 自动生成团队配置
- 配置验证和格式检查
- 支持JSON和YAML格式
- 配置文件加载和团队创建

## 主要组件

### 1. 配置模板 (`src/interfaces/crewai_config_template.py`)

定义了标准化的配置数据结构：
- `AgentConfig`: 智能体配置
- `TaskConfig`: 任务配置
- `CrewAIConfig`: 团队配置
- `CrewAIStandardConfig`: 标准化配置

### 2. 配置生成器 (`src/tools/crewai_generator.py`)

提供配置生成功能：
- 根据业务流程自动生成团队配置
- 支持自定义智能体和任务
- 导出为JSON或YAML格式

### 3. 运行时系统 (`src/interfaces/crewai_runtime.py`)

提供配置加载和团队运行功能：
- 从配置文件加载团队
- 创建和运行CrewAI团队
- 处理执行结果

## 使用方法

### 1. 生成配置

```python
from src.tools.crewai_generator import CrewAIGeneratorTool

# 创建生成器工具
generator = CrewAIGeneratorTool()

# 定义业务流程
business_process = "为生物质锅炉项目设计智能寻源供应链，包括供应商筛选、价格谈判和质量控制"

# 生成配置
config = generator._run(
    business_process=business_process,
    crew_name="生物质锅炉智能寻源团队",
    output_file="biomass_boiler_crew_config.json"
)
```

### 2. 加载配置并创建团队

```python
from src.interfaces.crewai_runtime import CrewAIRuntime
import json

# 创建运行时
runtime = CrewAIRuntime()

# 加载配置文件
with open("biomass_boiler_crew_config.json", "r") as f:
    config_data = json.load(f)

# 从配置创建团队
success = runtime.load_crew_from_config(config_data)

if success:
    # 运行团队
    result = runtime.run_crew()
    print(f"团队执行结果: {result}")
```

### 3. 直接使用配置类

```python
from src.interfaces.crewai_config_template import (
    CrewAIStandardConfig, 
    AgentConfig, 
    TaskConfig, 
    CrewAIConfig
)

# 创建智能体配置
agents = [
    AgentConfig(
        name="供应链规划师",
        role="负责制定供应链战略和规划",
        goal="根据业务需求制定最优的供应链规划和策略",
        backstory="你是一位经验丰富的供应链规划专家..."
    )
]

# 创建任务配置
tasks = [
    TaskConfig(
        name="供应链分析",
        description="分析当前供应链状况，识别关键问题和机会",
        agent="供应链规划师",
        expected_output="详细的供应链分析报告"
    )
]

# 创建团队配置
crewai_config = CrewAIConfig(
    name="供应链优化团队",
    description="负责供应链优化和分析",
    agents=agents,
    tasks=tasks,
    process="sequential"
)

# 创建标准化配置
standard_config = CrewAIStandardConfig(
    business_process="供应链优化",
    crewai_config=crewai_config
)

# 保存配置
standard_config.save_to_file("custom_crew_config.json")
```

## 环境要求

- Python 3.8+
- CrewAI
- LangChain
- Pydantic
- PyYAML
- 硅基流动API密钥

## 运行测试

```bash
# 运行标准化配置系统测试
python test_standard_crew_config.py
```

## 注意事项

1. 运行团队需要设置硅基流动API密钥：
   ```bash
   export SILICONFLOW_API_KEY="your-siliconflow-api-key-here"
   ```

2. 配置文件支持JSON和YAML格式，根据文件扩展名自动识别。

3. 智能体和任务的配置必须包含所有必需字段，否则验证将失败。

4. 系统默认使用硅基流动API作为LLM提供商。

## 扩展开发

如需扩展系统功能，可以：

1. 在`AgentRole`枚举中添加新的角色类型
2. 在`_load_agent_templates`方法中添加新的角色模板
3. 在`_load_task_templates`方法中添加新的任务模板
4. 扩展配置数据结构以支持更多字段

## 故障排除

1. 如果遇到导入错误，检查Python路径是否正确设置
2. 如果团队创建失败，确认硅基流动API密钥已设置
3. 如果配置验证失败，检查所有必需字段是否已填写
4. 如果API调用失败，检查网络连接和API密钥有效性