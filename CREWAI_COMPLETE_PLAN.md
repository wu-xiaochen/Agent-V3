# CrewAI 完整优化与实施计划

## 📋 问题清单

### 🔴 P0 - 关键问题（必须立即修复）

1. **UI布局冲突**
   - ❌ 右上角ToolPanel按钮（fixed right-4 top-4）与CrewAI按钮位置冲突
   - ❌ 多个功能入口重复（ToolPanel有CrewAI标签，Header也有CrewAI按钮）
   - ❌ 布局不统一，用户体验混乱

2. **功能缺失**
   - ❌ 无法保存Crew到后端
   - ❌ 无法加载已保存的Crew
   - ❌ 节点配置无法持久化

3. **AI自动生成缺失**
   - ❌ 对话中无法自动生成Crew
   - ❌ 没有crewai_generator工具集成
   - ❌ 生成后无法自动打开画布

---

## 🎯 完整解决方案

### Phase 1: UI重构和布局优化 (1小时)

#### 1.1 移除重复入口
**问题**: ToolPanel和Header都有CrewAI功能，造成冗余

**解决方案**:
- 保留Header的CrewAI按钮（主入口）
- ToolPanel中移除CrewAI标签
- 统一使用CrewDrawer作为唯一入口

**实施步骤**:
```typescript
// tool-panel.tsx
// 移除: <TabsTrigger value="crewai">CrewAI</TabsTrigger>
// 调整grid: grid-cols-5 → grid-cols-4
```

#### 1.2 修复按钮冲突
**问题**: ToolPanel的Menu按钮（fixed right-4 top-4）和CrewAI按钮重叠

**解决方案A** (推荐):
- 移除ToolPanel的独立Menu按钮
- 在Sidebar底部添加ToolPanel打开按钮
- 统一侧边栏交互模式

**解决方案B**:
- 调整CrewAI按钮位置到header右侧
- 调整ToolPanel Menu按钮到top-20，避开header

**推荐**: 方案A，更统一的交互体验

#### 1.3 优化Header布局
```typescript
// chat-interface.tsx header部分
<div className="border-b p-4 flex items-center justify-between">
  <div className="flex-1">
    <h2>Chat Assistant</h2>
    <p>Ask me anything</p>
  </div>
  <div className="flex items-center gap-3">
    <CrewDrawer />
    {/* 其他按钮 */}
  </div>
</div>
```

---

### Phase 2: Crew保存和加载功能 (1.5小时)

#### 2.1 前端API客户端
**文件**: `frontend/lib/api/crewai.ts`

```typescript
export const crewaiAPI = {
  // 创建Crew
  async saveCrew(crew: CrewConfig): Promise<{ success: boolean; crew_id: string }> {
    const response = await apiClient.post('/api/crewai/crews', crew)
    return response.data
  },
  
  // 获取Crew列表
  async listCrews(): Promise<{ success: boolean; crews: CrewConfig[] }> {
    const response = await apiClient.get('/api/crewai/crews')
    return response.data
  },
  
  // 获取Crew详情
  async getCrew(crewId: string): Promise<{ success: boolean; crew: CrewConfig }> {
    const response = await apiClient.get(`/api/crewai/crews/${crewId}`)
    return response.data
  },
  
  // 更新Crew
  async updateCrew(crewId: string, crew: CrewConfig) {
    const response = await apiClient.put(`/api/crewai/crews/${crewId}`, crew)
    return response.data
  },
  
  // 删除Crew
  async deleteCrew(crewId: string) {
    const response = await apiClient.delete(`/api/crewai/crews/${crewId}`)
    return response.data
  },
  
  // 执行Crew
  async executeCrew(crewId: string, inputs: any = {}) {
    const response = await apiClient.post(`/api/crewai/crews/${crewId}/execute`, { inputs })
    return response.data
  }
}
```

#### 2.2 CrewDrawer集成API
**更新**: `frontend/components/crewai/crew-drawer.tsx`

```typescript
// 加载Crew列表
useEffect(() => {
  const loadCrews = async () => {
    const result = await api.crewai.listCrews()
    if (result.success) {
      setCrews(result.crews)
    }
  }
  loadCrews()
}, [open])

// 保存Crew
const handleSave = async () => {
  if (!selectedCrew) return
  
  const crewData = convertCanvasToCrewConfig(nodes, edges)
  const result = await api.crewai.saveCrew(crewData)
  
  if (result.success) {
    toast.success("Crew saved successfully")
    // 刷新列表
    loadCrews()
  }
}

// 加载Crew到画布
const handleLoadCrew = async (crewId: string) => {
  const result = await api.crewai.getCrew(crewId)
  if (result.success) {
    setSelectedCrew(result.crew)
    const { nodes, edges } = convertCrewConfigToCanvas(result.crew)
    setInitialNodes(nodes)
    setInitialEdges(edges)
  }
}
```

#### 2.3 数据转换函数
```typescript
// Canvas数据 → CrewConfig
function convertCanvasToCrewConfig(nodes: Node[], edges: Edge[]): CrewConfig {
  const agents = nodes
    .filter(n => n.type === 'agent')
    .map(n => n.data.agent)
  
  const tasks = nodes
    .filter(n => n.type === 'task')
    .map(n => {
      // 从edges找出依赖关系
      const dependencies = edges
        .filter(e => e.target === n.id)
        .map(e => e.source)
      
      return {
        ...n.data.task,
        dependencies
      }
    })
  
  return {
    id: crypto.randomUUID(),
    name: "...",
    agents,
    tasks,
    // ...
  }
}

// CrewConfig → Canvas数据
function convertCrewConfigToCanvas(crew: CrewConfig): { nodes: Node[], edges: Edge[] } {
  const nodes: Node[] = [
    // Agents
    ...crew.agents.map((agent, i) => ({
      id: agent.id,
      type: 'agent',
      position: { x: 100, y: 100 + i * 150 },
      data: { agent, label: agent.name }
    })),
    // Tasks
    ...crew.tasks.map((task, i) => ({
      id: task.id,
      type: 'task',
      position: { x: 400, y: 100 + i * 150 },
      data: { task, label: task.description.slice(0, 20) }
    }))
  ]
  
  const edges: Edge[] = crew.tasks.flatMap(task =>
    task.dependencies.map(dep => ({
      id: `${dep}-${task.id}`,
      source: dep,
      target: task.id
    }))
  )
  
  return { nodes, edges }
}
```

---

### Phase 3: AI自动生成Crew (2小时)

#### 3.1 增强crewai_generator工具
**文件**: `src/tools/crewai_generator.py`

**新增功能**:
```python
def _run(self, query: str, session_id: str = "") -> dict:
    """
    使用LLM分析query，生成完整的Crew配置
    """
    # 1. 使用LLM分析需求
    analysis_prompt = f"""
    分析以下需求，生成一个CrewAI团队配置。
    
    需求: {query}
    
    请生成JSON格式的配置，包含：
    1. Crew名称和描述
    2. 至少2个Agent（角色、目标、背景）
    3. 至少2个Task（描述、期望输出、负责Agent）
    4. Task之间的依赖关系
    
    返回格式:
    {{
      "name": "团队名称",
      "description": "团队描述",
      "agents": [
        {{
          "id": "agent1",
          "name": "Agent名称",
          "role": "角色",
          "goal": "目标",
          "backstory": "背景故事",
          "tools": ["tool1", "tool2"]
        }}
      ],
      "tasks": [
        {{
          "id": "task1",
          "description": "任务描述",
          "expectedOutput": "期望输出",
          "agent": "agent1",
          "dependencies": []
        }}
      ]
    }}
    """
    
    # 2. 调用LLM
    response = self.llm.invoke(analysis_prompt)
    
    # 3. 解析JSON
    try:
        crew_config = json.loads(response.content)
    except:
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        crew_config = json.loads(json_match.group())
    
    # 4. 补充完整信息
    crew_config["id"] = f"crew_{int(time.time())}"
    crew_config["createdAt"] = datetime.now().isoformat()
    crew_config["updatedAt"] = datetime.now().isoformat()
    crew_config["process"] = "sequential"
    
    # 5. 保存到数据库/文件
    self._save_crew(crew_config)
    
    # 6. 返回特殊标记，让前端打开画布
    return {
        "success": True,
        "crew_id": crew_config["id"],
        "crew_config": crew_config,
        "action": "open_canvas",  # ← 前端识别此标记
        "message": f"✅ 已生成Crew团队: {crew_config['name']}\n包含 {len(crew_config['agents'])} 个Agent和 {len(crew_config['tasks'])} 个Task\n\n点击右上角CrewAI按钮查看详情"
    }

def _save_crew(self, crew_config: dict):
    """保存Crew配置到文件"""
    import os
    os.makedirs("data/crews", exist_ok=True)
    file_path = f"data/crews/{crew_config['id']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(crew_config, f, indent=2, ensure_ascii=False)
```

#### 3.2 前端自动打开画布
**文件**: `frontend/components/chat-interface.tsx`

```typescript
// 在handleSend的响应处理中添加
useEffect(() => {
  const checkCrewGeneration = async () => {
    // 检查最新消息的metadata
    const latestMessage = messages[messages.length - 1]
    if (latestMessage?.role === 'assistant' && latestMessage.metadata) {
      const { action, crew_id, crew_config } = latestMessage.metadata
      
      if (action === 'open_canvas' && crew_config) {
        // 自动打开CrewAI画布
        setCrewDrawerOpen(true)
        
        // 加载生成的Crew配置
        const { nodes, edges } = convertCrewConfigToCanvas(crew_config)
        setCrewCanvasData({ nodes, edges, crewId: crew_id })
        
        // 提示用户
        toast.success("Crew已生成，画布已打开")
      }
    }
  }
  
  checkCrewGeneration()
}, [messages])
```

#### 3.3 更新UnifiedAgent的工具列表
确保`crewai_generator`在工具列表中：

```yaml
# config/base/agents.yaml
agents:
  unified_agent:
    tools:
      - time
      - calculator
      - search
      - document_generator
      - crewai_generator  # ← 确保包含
```

---

### Phase 4: 完整测试方案 (1小时)

#### 测试用例清单

##### 4.1 UI布局测试
- [ ] ToolPanel Menu按钮不遮挡CrewAI按钮
- [ ] Header右侧按钮布局合理
- [ ] Sidebar底部有ToolPanel入口
- [ ] 响应式布局正常

##### 4.2 CrewAI基础功能测试
- [ ] 点击CrewAI按钮打开抽屉
- [ ] 创建新Crew
- [ ] 添加Agent节点
- [ ] 点击Agent节点打开配置面板
- [ ] 编辑Agent属性（名称、角色等）
- [ ] 关闭配置面板
- [ ] 验证节点标签更新
- [ ] 添加Task节点
- [ ] 点击Task节点打开配置
- [ ] 选择Agent分配给Task
- [ ] 拖拽连接节点

##### 4.3 保存和加载测试
- [ ] 点击Save按钮保存Crew
- [ ] 验证后端文件生成（data/crews/）
- [ ] 关闭抽屉
- [ ] 重新打开CrewAI
- [ ] 验证Crew列表显示
- [ ] 点击Crew加载到画布
- [ ] 验证节点和连线正确

##### 4.4 AI生成测试
- [ ] 在聊天中输入："创建一个数据分析团队"
- [ ] 验证AI调用crewai_generator工具
- [ ] 验证生成Crew配置
- [ ] 验证画布自动打开
- [ ] 验证节点已加载
- [ ] 验证可以编辑生成的配置
- [ ] 保存并验证

##### 4.5 执行流程测试（Phase 5）
- [ ] 点击Run Crew按钮
- [ ] 如需输入参数，显示对话框
- [ ] 提交执行
- [ ] 显示执行状态
- [ ] 显示执行结果

##### 4.6 端到端测试
- [ ] 完整流程：对话 → 生成 → 编辑 → 保存 → 重新加载 → 执行
- [ ] 多个Crew管理
- [ ] 删除Crew
- [ ] 错误处理（网络错误、保存失败等）

---

## 📅 实施时间表

### Day 1 (今天)

**14:00-15:00**: Phase 1 - UI重构
- 移除ToolPanel的CrewAI标签
- 修复Menu按钮冲突
- 优化Header布局
- 测试布局

**15:00-16:30**: Phase 2 - 保存加载功能
- 创建crewai API客户端
- 实现数据转换函数
- 集成到CrewDrawer
- 测试保存加载

**16:30-18:30**: Phase 3 - AI自动生成
- 增强crewai_generator工具
- 实现前端自动打开画布
- 测试对话生成流程

**18:30-19:30**: Phase 4 - 完整测试
- 执行所有测试用例
- 修复发现的bug
- 优化用户体验

---

## 🎯 完成标准

### 功能完整性
- ✅ 所有UI冲突已解决
- ✅ Crew可以保存和加载
- ✅ 对话可以生成Crew
- ✅ 画布自动打开
- ✅ 所有测试用例通过

### 用户体验
- ✅ 布局合理，无遮挡
- ✅ 操作流畅，无卡顿
- ✅ 提示清晰，易理解
- ✅ 错误处理友好

### 代码质量
- ✅ 无Lint错误
- ✅ 代码有注释
- ✅ 类型定义完整
- ✅ 错误处理完善

---

## 📋 任务分解

### Task 1: 移除UI冲突 ⏱️ 30分钟
- [ ] 修改tool-panel.tsx，移除CrewAI标签
- [ ] 调整grid-cols-5 → grid-cols-4
- [ ] 移除固定Menu按钮或调整位置
- [ ] 在Sidebar添加ToolPanel入口
- [ ] 测试验证

### Task 2: 创建API客户端 ⏱️ 30分钟
- [ ] 创建lib/api/crewai.ts
- [ ] 实现6个API方法
- [ ] 导出到lib/api.ts
- [ ] 添加类型定义

### Task 3: 数据转换 ⏱️ 30分钟
- [ ] 实现convertCanvasToCrewConfig
- [ ] 实现convertCrewConfigToCanvas
- [ ] 处理边界情况
- [ ] 添加单元测试

### Task 4: CrewDrawer集成 ⏱️ 30分钟
- [ ] useEffect加载Crew列表
- [ ] handleSave实现
- [ ] handleLoad实现
- [ ] 错误处理和toast提示

### Task 5: AI生成工具 ⏱️ 1小时
- [ ] 增强src/tools/crewai_generator.py
- [ ] 实现LLM分析prompt
- [ ] 实现JSON解析
- [ ] 实现保存逻辑
- [ ] 返回特殊标记

### Task 6: 前端自动打开 ⏱️ 30分钟
- [ ] 监听消息metadata
- [ ] 识别action: "open_canvas"
- [ ] 自动打开画布
- [ ] 加载Crew数据

### Task 7: 完整测试 ⏱️ 1小时
- [ ] 执行所有测试用例
- [ ] 记录问题
- [ ] 修复bug
- [ ] 再次验证

---

**开始时间**: 2025-10-30 15:30
**预计完成**: 2025-10-30 20:00
**当前状态**: 📋 计划完成，准备执行

