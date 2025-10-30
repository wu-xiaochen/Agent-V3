# 📋 完整实施计划

**创建日期**: 2025-10-30  
**版本**: v2.0（按新工作流重新规划）  
**开发原则**: 后端→测试→API→前端→再测试

---

## 🎯 总体目标

完成所有未实现功能，确保系统完整性和稳定性

---

## 📊 任务优先级

### P0 - 紧急（立即执行）
1. ✅ 修复主题切换功能
2. 🔄 实现工具配置持久化
3. 🔄 实现Agent配置持久化

### P1 - 高优先级（本周完成）
4. ⏳ 实现知识库功能
5. ⏳ 系统配置持久化

### P2 - 中优先级（下周完成）
6. ⏳ 后端架构重组
7. ⏳ 前端架构优化

---

## 📝 详细任务列表

### 任务1: 修复主题切换功能 ✅

**状态**: 已修复  
**优先级**: P0  
**预计时间**: 30分钟

**完成项**:
- [x] 添加`setDarkMode`方法到store
- [x] 主题切换功能正常
- [x] 需要添加持久化（下一步）

---

### 任务2: 工具配置持久化 🔄

**状态**: 进行中  
**优先级**: P0  
**预计时间**: 4小时

#### 2.1 后端开发（2小时）

**文件创建**:
```bash
# 数据模型
src/models/tool_config.py

# API路由
src/api/routers/tools.py  # 或在api_server.py中添加

# 测试文件
tests/unit/test_tool_config.py
tests/integration/test_tool_api.py
```

**API设计**:
```python
# GET /api/tools/configs
# 获取所有工具配置

# POST /api/tools/configs
# 批量更新工具配置

# GET /api/tools/{tool_id}/config
# 获取单个工具配置

# PUT /api/tools/{tool_id}/config
# 更新单个工具配置
```

**数据模型**:
```python
class ToolConfig(BaseModel):
    tool_id: str
    enabled: bool
    mode: Literal["API", "MCP"]
    config: Dict[str, Any]
    updated_at: datetime
```

**存储方案**:
- 方案1: JSON文件 `data/tool_configs.json`
- 方案2: SQLite `data/tool_configs.db`
- **推荐**: 方案1（简单快速）

#### 2.2 后端测试（1小时）

**单元测试**:
```python
def test_get_tool_configs():
    """测试获取工具配置"""
    
def test_update_tool_config():
    """测试更新工具配置"""
    
def test_invalid_tool_id():
    """测试无效工具ID"""
```

**集成测试**:
```python
def test_tool_config_api():
    """测试工具配置API端点"""
```

#### 2.3 前端集成（1小时）

**文件修改**:
```typescript
// frontend/lib/api.ts
export const toolsApi = {
  async getConfigs() {...},
  async updateConfig(toolId: string, config: ToolConfig) {...}
}

// frontend/components/settings/tool-settings.tsx
// 连接到API，移除localStorage
```

---

### 任务3: Agent配置持久化 🔄

**状态**: 待开始  
**优先级**: P0  
**预计时间**: 4小时

#### 3.1 后端开发（2小时）

**API设计**:
```python
# GET /api/agents
# 获取所有Agent配置

# POST /api/agents
# 创建新Agent

# PUT /api/agents/{agent_id}
# 更新Agent

# DELETE /api/agents/{agent_id}
# 删除Agent
```

**数据模型**:
```python
class AgentConfig(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    model: str
    created_at: datetime
    updated_at: datetime
```

**存储方案**:
- JSON文件 `data/agent_configs.json`

#### 3.2 后端测试（1小时）

**测试用例**:
- CRUD操作
- 并发更新
- 数据验证

#### 3.3 前端集成（1小时）

**修改组件**:
- `agent-settings.tsx` - 连接API
- 移除localStorage逻辑

---

### 任务4: 系统配置持久化 🔄

**状态**: 待开始  
**优先级**: P1  
**预计时间**: 3小时

#### 4.1 后端开发（1.5小时）

**API设计**:
```python
# GET /api/system/config
# 获取系统配置

# PUT /api/system/config
# 更新系统配置
```

**配置项**:
```python
class SystemConfig(BaseModel):
    llm_provider: str
    api_key: str  # 加密存储
    base_url: str
    default_model: str
    temperature: float
    max_tokens: int
```

**安全要求**:
- API Key必须加密存储
- 使用环境变量或密钥管理

#### 4.2 后端测试（1小时）

**测试重点**:
- API Key加密/解密
- 配置验证
- 默认值处理

#### 4.3 前端集成（0.5小时）

---

### 任务5: 主题切换持久化 ✅

**状态**: 待实现  
**优先级**: P0  
**预计时间**: 30分钟

**实现方式**: LocalStorage（纯前端）

**代码**:
```typescript
// frontend/lib/store.ts
// 从localStorage加载初始值
darkMode: localStorage.getItem('theme') === 'dark',

// 保存时写入localStorage
setDarkMode: (dark) => {
  localStorage.setItem('theme', dark ? 'dark' : 'light')
  set({ darkMode: dark })
}
```

---

### 任务6: 知识库功能 ⏳

**状态**: 待开始  
**优先级**: P1  
**预计时间**: 8小时

#### 6.1 后端开发（4小时）

**组件选型**:
- 向量数据库: ChromaDB（已安装）
- 文档解析: pypdfium2, python-docx
- Embedding: HuggingFace模型

**API设计**:
```python
# POST /api/knowledge-bases
# 创建知识库

# POST /api/knowledge-bases/{kb_id}/documents
# 上传文档

# POST /api/knowledge-bases/{kb_id}/query
# 查询知识库

# GET /api/knowledge-bases
# 列出所有知识库
```

**数据流程**:
```
文档上传 → 文本提取 → 分块 → Embedding → 存储到ChromaDB
查询 → Embedding → 向量检索 → 返回相关文档
```

#### 6.2 后端测试（2小时）

**测试场景**:
- 文档上传和解析
- 向量检索准确性
- 多知识库隔离

#### 6.3 前端开发（2小时）

**组件**:
- 知识库列表
- 文档上传UI
- 查询界面

---

### 任务7: 后端架构重组 ⏳

**状态**: 待开始  
**优先级**: P2  
**预计时间**: 6小时

**目标**: 将`api_server.py`（1166行）拆分为模块化结构

**新结构**:
```
src/api/
├── __init__.py
├── main.py              # FastAPI app
├── dependencies.py      # 依赖注入
├── routers/
│   ├── __init__.py
│   ├── chat.py          # 聊天相关
│   ├── thinking.py      # 思维链
│   ├── crewai.py        # CrewAI
│   ├── tools.py         # 工具配置
│   ├── agents.py        # Agent配置
│   ├── knowledge.py     # 知识库
│   └── system.py        # 系统配置
├── services/
│   ├── __init__.py
│   ├── chat_service.py
│   ├── crewai_service.py
│   └── knowledge_service.py
└── models/
    ├── __init__.py
    ├── chat.py
    ├── tool.py
    └── agent.py
```

**迁移步骤**:
1. 创建新目录结构
2. 逐个路由迁移（不修改逻辑）
3. 更新测试
4. 验证所有功能正常
5. 删除旧文件

**重要**: 不修改任何业务逻辑，仅重组结构

---

### 任务8: 前端架构优化 ⏳

**状态**: 待开始  
**优先级**: P2  
**预计时间**: 4小时

**目标**: 模块化API和状态管理

**新结构**:
```
frontend/
├── lib/
│   ├── api/
│   │   ├── index.ts
│   │   ├── chat.ts
│   │   ├── crewai.ts
│   │   ├── tools.ts
│   │   ├── agents.ts
│   │   └── knowledge.ts
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useThinkingChain.ts
│   │   ├── useCrewCanvas.ts
│   │   └── useToolConfig.ts
│   └── store/
│       ├── index.ts
│       ├── chatStore.ts
│       ├── crewStore.ts
│       └── configStore.ts
└── types/
    ├── index.ts
    ├── chat.ts
    ├── crewai.ts
    └── tools.ts
```

**迁移步骤**:
1. 创建新文件结构
2. 逐个模块迁移
3. 更新导入路径
4. 测试所有功能
5. 删除旧代码

---

## 📅 时间计划

### 第1阶段：紧急修复（1天）
- [x] 主题切换修复（30分钟）
- [ ] 主题持久化（30分钟）
- [ ] 工具配置持久化（4小时）
- [ ] Agent配置持久化（4小时）

**预计完成**: 2025-10-31

### 第2阶段：核心功能（3天）
- [ ] 系统配置持久化（3小时）
- [ ] 知识库功能（8小时）
- [ ] 完整测试（4小时）

**预计完成**: 2025-11-03

### 第3阶段：架构优化（2天）
- [ ] 后端架构重组（6小时）
- [ ] 前端架构优化（4小时）
- [ ] 回归测试（4小时）

**预计完成**: 2025-11-05

---

## ✅ 验收标准

### 每个任务完成标准
1. ✅ 后端单元测试通过
2. ✅ 后端集成测试通过
3. ✅ 前端功能正常
4. ✅ E2E测试通过
5. ✅ API文档完成
6. ✅ 无linter错误
7. ✅ 代码覆盖率 >85%
8. ✅ 用户验收测试通过

### 整体完成标准
1. ✅ 所有P0任务完成
2. ✅ 所有P1任务完成
3. ✅ 核心功能97% → 100%
4. ✅ 所有测试通过
5. ✅ 文档完整
6. ✅ 代码质量优秀

---

## 🚀 立即开始

### 当前任务：工具配置持久化

#### 步骤1: 创建后端API（现在开始）
```bash
# 1. 创建数据模型
# 文件: src/models/tool_config.py

# 2. 在api_server.py添加路由

# 3. 创建测试
# 文件: tests/unit/test_tool_config.py
```

#### 步骤2: 运行测试
```bash
pytest tests/unit/test_tool_config.py -v
```

#### 步骤3: 前端集成
```bash
# 修改: frontend/components/settings/tool-settings.tsx
```

#### 步骤4: 验证
```bash
# 手动测试所有功能
```

---

**注意**: 严格遵守`DEVELOPMENT_WORKFLOW.md`中的开发流程！

---

**维护者**: AI Assistant  
**最后更新**: 2025-10-30  
**下一步**: 立即开始工具配置持久化

