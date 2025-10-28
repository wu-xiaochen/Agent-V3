# N8N API 完整集成设置指南

## 当前状态

✅ **已实现**: 完整的 N8N API 工具包  
⚠️ **需要**: 配置有效的 N8N API 密钥

## 新实现的功能

### 完整的 N8N API 工具（`src/agents/shared/n8n_api_tools.py`）

我已经为您实现了完整的 N8N API 集成，包括以下工具：

1. **`n8n_generate_and_create_workflow`** ⭐ 推荐
   - 根据描述智能生成工作流
   - **直接创建到 n8n 实例**
   - 返回工作流 ID 和访问 URL
   
2. **`n8n_create_workflow`**
   - 根据 JSON 配置创建工作流
   - 支持完整的工作流定义
   
3. **`n8n_list_workflows`**
   - 列出所有工作流
   - 支持按激活状态筛选
   
4. **`n8n_execute_workflow`**
   - 执行指定工作流
   - 支持传递执行数据
   
5. **`n8n_delete_workflow`**
   - 删除指定工作流

### 对比：简化版 vs API 完整版

| 功能 | 简化版 (已废弃) | API 完整版 (新) |
|------|----------------|----------------|
| 生成工作流 JSON | ✅ | ✅ |
| **直接创建到 n8n** | ❌ | ✅ **已实现** |
| 列出工作流 | ❌ | ✅ |
| 执行工作流 | ❌ | ✅ |
| 删除工作流 | ❌ | ✅ |
| 依赖 | 无 | N8N API Key |

## 设置步骤

### 1. 在 n8n 中生成 API 密钥

#### 方法 1: 通过 n8n Web 界面

1. 打开 n8n: http://localhost:5678
2. 点击右上角的用户图标 → **Settings**
3. 进入 **API Keys** 页面
4. 点击 **Create API Key**
5. 给密钥命名（如 "Agent-V3"）
6. 复制生成的 API Key

#### 方法 2: 使用 n8n CLI

```bash
# 在 n8n 容器中创建 API Key
docker exec -it n8n n8n user:create-api-key <user-email>
```

### 2. 更新配置文件

#### 选项 A: 更新 `config/tools/tools_config.json`

找到 `n8n_mcp_generator` 配置并更新 API Key:

```json
{
  "type": "mcp_stdio",
  "name": "n8n_mcp_generator",
  "description": "N8N工作流生成工具",
  "enabled": true,
  "env": {
    "N8N_API_URL": "http://localhost:5678",
    "N8N_API_KEY": "你的新API密钥"  // ⚠️ 在这里更新
  }
}
```

#### 选项 B: 使用环境变量（推荐）

在项目根目录创建 `.env` 文件：

```bash
# .env
N8N_API_URL=http://localhost:5678
N8N_API_KEY=你的新API密钥
```

然后在 Python 中加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. 验证配置

运行测试脚本验证 API 连接：

```bash
python -c "
from src.agents.shared.n8n_api_tools import N8NAPIClient

client = N8NAPIClient()
try:
    workflows = client.list_workflows()
    print(f'✅ API 连接成功! 工作流数量: {len(workflows)}')
except Exception as e:
    print(f'❌ API 连接失败: {e}')
"
```

## 使用示例

### 1. 通过 UnifiedAgent 使用

```bash
# 智能生成并直接创建到 n8n
python main.py --query "帮我在n8n上创建一个定时任务，每小时发送邮件"
```

Agent 会：
1. 调用 `n8n_generate_and_create_workflow` 工具
2. 生成工作流配置
3. **直接创建到您的 n8n 实例** ✅
4. 返回工作流 ID 和访问链接

### 2. 直接使用工具

```python
from src.agents.shared.n8n_api_tools import N8NGenerateAndCreateWorkflowTool

# 创建工具实例
tool = N8NGenerateAndCreateWorkflowTool()

# 生成并创建工作流
result = tool._run(workflow_description="创建一个简单的HTTP请求工作流")

# 解析结果
import json
data = json.loads(result)
if data['success']:
    print(f"工作流已创建!")
    print(f"ID: {data['workflow_id']}")
    print(f"访问链接: {data['url']}")
```

### 3. 列出现有工作流

```python
from src.agents.shared.n8n_api_tools import N8NListWorkflowsTool

tool = N8NListWorkflowsTool()
result = tool._run()

data = json.loads(result)
for workflow in data['workflows']:
    print(f"- {workflow['name']} (ID: {workflow['id']})")
```

### 4. 执行工作流

```python
from src.agents.shared.n8n_api_tools import N8NExecuteWorkflowTool

tool = N8NExecuteWorkflowTool()
result = tool._run(
    workflow_id="your-workflow-id",
    data='{"input": "test data"}'
)
```

## 工具配置

### 当前配置（`config/base/agents.yaml`）

```yaml
unified_agent:
  tools:
    - "calculator"
    - "search"
    - "time"
    - "crewai_generator"
    - "crewai_runtime"
    - "n8n_mcp_generator"  # ✅ 自动加载所有 N8N API 工具
```

当 `n8n_mcp_generator` 被加载时，会展开为 5 个工具：
- n8n_generate_and_create_workflow
- n8n_create_workflow
- n8n_list_workflows
- n8n_execute_workflow
- n8n_delete_workflow

## 故障排查

### 问题 1: "unauthorized" 错误

**原因**: API Key 无效或未配置

**解决**:
1. 在 n8n 中重新生成 API Key
2. 更新配置文件中的 API Key
3. 重启 Agent

### 问题 2: "Connection refused"

**原因**: n8n 服务未运行

**解决**:
```bash
# 检查 n8n 是否运行
docker ps | grep n8n

# 启动 n8n
docker start n8n
```

### 问题 3: API 响应 401

**原因**: API Key 格式错误或权限不足

**解决**:
1. 确认 API Key 格式正确（JWT 格式）
2. 确认用户有足够权限
3. 在 n8n 设置中检查 API 是否启用

### 问题 4: 工作流创建失败

**原因**: 工作流配置无效

**解决**:
- 检查节点配置是否完整
- 确认节点类型存在
- 查看 n8n 日志获取详细错误

```bash
docker logs n8n
```

## 测试工具加载

验证工具是否正确加载：

```bash
python -c "
from src.agents.shared.tools import get_tools_for_agent

tools = get_tools_for_agent('unified_agent')
n8n_tools = [t for t in tools if 'n8n' in t.name]

print(f'N8N 工具数量: {len(n8n_tools)}')
for tool in n8n_tools:
    print(f'  - {tool.name}')
"
```

期望输出：
```
N8N 工具数量: 5
  - n8n_generate_and_create_workflow
  - n8n_create_workflow
  - n8n_list_workflows
  - n8n_execute_workflow
  - n8n_delete_workflow
```

## 完整工作流示例

### 示例 1: 智能创建工作流

```bash
python main.py --query "在n8n上创建一个工作流：
1. 每天早上9点触发
2. 发送HTTP请求获取天气
3. 将结果发送到Slack频道"
```

### 示例 2: 手动创建工作流

```python
from src.agents.shared.n8n_api_tools import N8NCreateWorkflowTool
import json

tool = N8NCreateWorkflowTool()

workflow = {
    "name": "测试工作流",
    "nodes": [
        {
            "parameters": {},
            "name": "Start",
            "type": "n8n-nodes-base.start",
            "typeVersion": 1,
            "position": [250, 300]
        }
    ],
    "connections": {},
    "active": False
}

result = tool._run(workflow_json=json.dumps(workflow))
print(result)
```

## 下一步

完成 API Key 配置后：

1. ✅ 测试 API 连接
2. ✅ 运行示例查询
3. ✅ 验证工作流创建
4. ✅ 在 n8n Web 界面查看创建的工作流

## 参考资源

- [n8n API 文档](https://docs.n8n.io/api/)
- [n8n-mcp GitHub](https://github.com/czlonkowski/n8n-mcp)
- [工具实现代码](../src/agents/shared/n8n_api_tools.py)

---

**状态**: ✅ 工具已实现，等待 API Key 配置  
**最后更新**: 2025-10-28  
**维护者**: Agent-V3 Team

