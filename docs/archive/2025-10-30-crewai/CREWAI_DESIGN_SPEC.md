# CrewAI 画布功能完整设计规范

## 📋 问题分析

### 当前问题
1. ❌ Crew画布按钮和右上角按钮叠加
2. ❌ Crew节点无法设置具体属性
3. ❌ 无法保存Crew配置到后端
4. ❌ 缺少完整的执行流程设计
5. ❌ 没有AI对话自动生成Crew的功能

---

## 🎯 完整功能设计

### 1. 用户交互流程

#### 流程A：AI对话生成Crew（智能模式）
```
用户输入 → AI理解需求 → 自动生成Crew配置 → 打开画布展示 → 用户编辑 → 保存 → 执行
```

**示例对话**:
```
用户: "帮我创建一个市场分析团队，包含数据分析师和报告撰写员"
AI: "好的，我为你生成了一个市场分析Crew，包含2个Agent和3个Task..."
[自动打开CrewAI画布，显示生成的配置]
```

**触发条件**:
- 用户消息包含关键词：创建团队、crew、多Agent、协作等
- AI工具调用：`crewai_generator` → 返回Crew配置 → 前端自动打开画布

#### 流程B：手动创建Crew（手动模式）
```
点击CrewAI按钮 → 创建新Crew → 手动添加节点 → 配置属性 → 保存 → 执行
```

---

### 2. 界面布局优化

#### 当前问题：按钮叠加
**原因**: CrewAI按钮在chat header右侧，可能与其他按钮冲突

**解决方案**:
```
┌─────────────────────────────────────────────────────┐
│  Chat Assistant                    [CrewAI] [⚙️]     │  ← Header
├─────────────────────────────────────────────────────┤
│                                                     │
│  消息内容区域                                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**调整**:
- 将CrewAI按钮移到header右侧固定位置
- 确保与设置按钮不冲突
- 添加tooltip提示

---

### 3. CrewAI抽屉详细设计

#### 布局结构
```
┌────────────┬───────────────────────────────────────┐
│  Crew列表  │        主内容区域                      │
│            │                                       │
│ [+ 新建]   │  Tabs: [画布] [配置] [执行] [结果]    │
│            │                                       │
│ Crew 1     │  ┌─────────────────────────────────┐ │
│ Crew 2     │  │                                 │ │
│ Crew 3     │  │      画布/配置内容               │ │
│            │  │                                 │ │
│            │  └─────────────────────────────────┘ │
│            │                                       │
│            │  [保存] [运行] [删除]                 │
└────────────┴───────────────────────────────────────┘
```

#### 标签页功能

**1. 画布 (Canvas)**
- 可视化编辑节点
- 拖拽添加Agent/Task
- 连接节点定义依赖关系
- 实时预览

**2. 配置 (Configuration)**
- Crew基本信息（名称、描述）
- Agent列表配置
- Task列表配置
- 执行参数（process、memory等）

**3. 执行 (Execution)**
- 输入参数表单
- 执行按钮
- 实时进度显示
- 日志输出

**4. 结果 (Results)**
- 执行历史
- 结果展示
- 导出功能

---

### 4. 节点属性配置

#### Agent节点配置面板
```typescript
interface AgentConfig {
  // 基本信息
  name: string              // Agent名称
  role: string              // 角色
  goal: string              // 目标
  backstory: string         // 背景故事
  
  // 工具配置
  tools: string[]           // 可用工具列表
  
  // LLM配置
  llm: string               // LLM模型
  temperature: number       // 温度
  maxTokens: number         // 最大token
  
  // 高级配置
  verbose: boolean          // 详细输出
  allowDelegation: boolean  // 允许委派
  maxIter: number          // 最大迭代
  maxRpm: number           // 请求速率限制
}
```

**配置UI**:
- 点击节点 → 右侧弹出配置面板
- 表单编辑所有属性
- 实时保存到节点data

#### Task节点配置面板
```typescript
interface TaskConfig {
  // 基本信息
  description: string       // 任务描述
  expectedOutput: string    // 期望输出
  
  // 关联配置
  agent: string            // 执行Agent的ID
  context: string[]        // 上下文Task IDs
  
  // 工具和执行
  tools: string[]          // 任务特定工具
  async: boolean           // 异步执行
  
  // 输出配置
  outputFile?: string      // 输出文件
  outputJson?: boolean     // JSON输出
  outputPydantic?: string  // Pydantic模型
}
```

---

### 5. Crew保存机制

#### 后端API设计

```python
# 1. 保存Crew配置
POST /api/crewai/crews
Body: {
  "name": "市场分析团队",
  "description": "分析市场趋势",
  "agents": [...],
  "tasks": [...],
  "process": "sequential",
  "config": {...}
}
Response: {
  "success": true,
  "crew_id": "crew_123",
  "message": "Crew saved successfully"
}

# 2. 获取Crew列表
GET /api/crewai/crews
Response: {
  "success": true,
  "crews": [...]
}

# 3. 获取Crew详情
GET /api/crewai/crews/{crew_id}
Response: {
  "success": true,
  "crew": {...}
}

# 4. 更新Crew
PUT /api/crewai/crews/{crew_id}
Body: {...}

# 5. 删除Crew
DELETE /api/crewai/crews/{crew_id}

# 6. 执行Crew
POST /api/crewai/crews/{crew_id}/execute
Body: {
  "inputs": {...}  // 输入参数
}
Response: {
  "success": true,
  "execution_id": "exec_456"
}

# 7. 获取执行状态
GET /api/crewai/executions/{execution_id}
Response: {
  "status": "running",
  "progress": 50,
  "current_task": "task_1",
  "result": null
}

# 8. AI生成Crew
POST /api/crewai/generate
Body: {
  "prompt": "创建市场分析团队",
  "session_id": "session_1"
}
Response: {
  "success": true,
  "crew": {...},  // 生成的配置
  "crew_id": "crew_789"
}
```

#### 前端保存流程
```typescript
// 1. 画布保存
const handleSaveCanvas = async () => {
  const crewConfig = {
    id: currentCrew.id,
    name: currentCrew.name,
    description: currentCrew.description,
    agents: convertNodesToAgents(nodes),
    tasks: convertNodesToTasks(nodes, edges),
    process: currentCrew.process,
    config: currentCrew.config
  }
  
  const result = await api.crewai.saveCrew(crewConfig)
  if (result.success) {
    toast.success("Crew saved successfully")
  }
}

// 2. 自动保存
useEffect(() => {
  const autoSave = setTimeout(() => {
    if (hasUnsavedChanges) {
      handleSaveCanvas()
    }
  }, 5000)  // 5秒自动保存
  
  return () => clearTimeout(autoSave)
}, [nodes, edges])
```

---

### 6. Crew执行流程

#### 执行步骤
```
1. 用户点击"Run Crew"
2. 显示输入参数对话框（如果需要）
3. 提交执行请求到后端
4. 后端创建CrewAI实例
5. 执行Crew任务
6. 实时更新执行状态（WebSocket/轮询）
7. 显示执行结果
```

#### 前端执行UI
```typescript
const handleRunCrew = async () => {
  // 1. 检查是否需要输入参数
  if (crew.requiresInput) {
    const inputs = await showInputDialog()
    if (!inputs) return
  }
  
  // 2. 开始执行
  setExecutionStatus("running")
  const result = await api.crewai.executeCrew(crew.id, inputs)
  
  // 3. 轮询状态
  const pollInterval = setInterval(async () => {
    const status = await api.crewai.getExecutionStatus(result.execution_id)
    setExecutionProgress(status.progress)
    setCurrentTask(status.current_task)
    
    if (status.status === "completed") {
      clearInterval(pollInterval)
      setExecutionResult(status.result)
      setExecutionStatus("completed")
    }
  }, 1000)
}
```

---

### 7. AI自动生成Crew

#### 后端实现
```python
# src/tools/crewai_generator_v2.py
class CrewAIGeneratorV2(BaseTool):
    name = "crewai_generator_v2"
    description = "Generate a complete CrewAI configuration from natural language description"
    
    def _run(self, prompt: str, session_id: str) -> dict:
        # 1. 使用LLM分析需求
        analysis = self.llm.invoke(f"""
        分析以下需求，生成CrewAI配置：
        {prompt}
        
        返回JSON格式：
        {{
          "name": "Crew名称",
          "description": "描述",
          "agents": [...],
          "tasks": [...]
        }}
        """)
        
        # 2. 解析LLM输出
        crew_config = json.loads(analysis)
        
        # 3. 保存到数据库
        crew_id = self.save_crew(crew_config)
        
        # 4. 返回结果（包含打开画布的指令）
        return {
            "success": True,
            "crew_id": crew_id,
            "crew_config": crew_config,
            "action": "open_canvas",  # 前端识别此字段
            "message": f"已生成Crew: {crew_config['name']}"
        }
```

#### 前端响应
```typescript
// 在AI回复中检测特殊标记
useEffect(() => {
  if (latestMessage.metadata?.action === "open_canvas") {
    const crewId = latestMessage.metadata.crew_id
    const crewConfig = latestMessage.metadata.crew_config
    
    // 自动打开CrewAI画布
    setCrewDrawerOpen(true)
    setSelectedCrew(crewConfig)
    setCrewCanvasMode("view")  // 查看模式，可编辑
  }
}, [messages])
```

---

## 🛠️ 实施计划

### Phase 1: 修复当前问题 (2小时)
1. ✅ 修复按钮叠加问题
2. ✅ 实现节点属性配置面板
3. ✅ 实现Crew保存功能（前端+后端）

### Phase 2: 完善执行流程 (2小时)
4. ✅ 实现输入参数对话框
5. ✅ 实现执行状态显示
6. ✅ 实现结果展示

### Phase 3: AI自动生成 (2小时)
7. ✅ 后端CrewAI生成工具增强
8. ✅ 前端自动打开画布
9. ✅ 画布和对话联动

### Phase 4: 优化和测试 (1小时)
10. ✅ 自动保存功能
11. ✅ 错误处理和提示
12. ✅ 完整功能测试

---

## 📋 详细任务分解

### Task 1: 修复UI布局
- [ ] 调整CrewAI按钮位置
- [ ] 添加tooltip
- [ ] 确保响应式布局

### Task 2: 节点配置面板
- [ ] 创建AgentConfigPanel组件
- [ ] 创建TaskConfigPanel组件
- [ ] 实现点击节点打开配置
- [ ] 实时更新节点数据

### Task 3: 后端API
- [ ] 创建`api/routers/crewai.py`
- [ ] 实现CRUD端点
- [ ] 实现执行端点
- [ ] 实现生成端点

### Task 4: 前端API集成
- [ ] 添加`lib/api/crewai.ts`
- [ ] 实现保存/加载功能
- [ ] 实现执行功能

### Task 5: 执行流程
- [ ] 输入参数对话框
- [ ] 执行状态显示
- [ ] 进度条和日志
- [ ] 结果展示

### Task 6: AI生成集成
- [ ] 增强`crewai_generator`工具
- [ ] 前端识别特殊响应
- [ ] 自动打开画布
- [ ] 显示生成的配置

---

## 🎯 预期效果

### 用户体验
1. **智能生成**: 对话中自动生成Crew，画布自动打开
2. **可视化编辑**: 直观的节点编辑，拖拽连接
3. **属性配置**: 点击节点即可配置所有属性
4. **实时保存**: 自动保存，不丢失配置
5. **执行跟踪**: 实时查看执行进度和结果

### 技术实现
- 前后端完整API对接
- WebSocket实时通信（可选）
- 数据持久化
- 错误处理和回滚

---

**开始时间**: 2025-10-30 14:00
**预计完成**: 2025-10-30 21:00 (7小时)
**当前状态**: 📋 设计完成，待实施

