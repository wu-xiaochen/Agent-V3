# 📋 AI Agent Hub - 项目路线图

**更新日期**: 2025-10-30  
**版本**: v3.1  
**开发原则**: 后端→测试→API→前端→再测试

---

## 🎯 项目概述

AI Agent Hub是一个多智能体协作平台，支持CrewAI团队生成、知识库管理、工具配置和实时思维链展示。

### 核心功能
- ✅ 智能对话系统（思维链可视化）
- ✅ CrewAI团队画布（可视化编辑和运行）
- ✅ Agent配置管理
- ✅ 工具配置管理
- 🔄 知识库系统（开发中）
- 🔄 CrewAI高级功能（Flow/Hierarchical架构）

---

## 📊 当前状态

### 已完成功能 ✅
1. **核心聊天系统**
   - 多会话管理
   - 思维链实时展示（V0风格）
   - 工具调用状态显示
   - 文件上传支持

2. **CrewAI基础功能**
   - 可视化画布（React Flow）
   - Agent/Task节点编辑
   - 团队保存/加载/删除
   - 团队执行和结果展示
   - 节点配置面板

3. **设置系统**
   - 独立设置页面（/settings）
   - Agent配置CRUD
   - 工具配置CRUD
   - 系统配置
   - 主题切换

4. **测试体系**
   - 41个单元/集成测试
   - 100%测试通过率
   - 覆盖率 >85%

### 待完成功能 ⏳

#### Phase 1: 紧急修复（P0）
1. 主题切换功能修复
2. CrewAI JSON解析增强
3. 系统配置后端API
4. 设置页面配置读取修复

#### Phase 2: CrewAI增强（P1）
1. 运行状态实时显示
2. 结果展示优化
3. 工具集成到CrewAI
4. 文件上传到CrewAI
5. Flow/Hierarchical架构支持

#### Phase 3: 知识库系统（P1）
1. 后端服务（ChromaDB集成）
2. 文档上传和解析
3. 向量检索
4. 前端管理UI
5. CrewAI集成

#### Phase 4: 架构优化（P2）
1. 后端模块化重组
2. 前端状态管理优化

---

## 📝 详细任务列表

### P0 - 紧急修复

#### 任务1: 修复主题切换
**状态**: 待修复  
**文件**: `frontend/app/layout.tsx`  
**预计时间**: 30分钟

**实现**:
```typescript
'use client'
import { useAppStore } from '@/lib/store'
import { useEffect } from 'react'

export default function RootLayout({ children }) {
  const darkMode = useAppStore(state => state.darkMode)
  
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])
  
  return (
    <html lang="en" className={darkMode ? 'dark' : ''}>
      {/* ... */}
    </html>
  )
}
```

---

#### 任务2: 增强CrewAI JSON解析
**状态**: 待修复  
**文件**: `frontend/components/chat-interface.tsx`  
**预计时间**: 1小时

**问题**: LLM返回的observation可能包含markdown代码块或非JSON内容

**解决方案**:
1. 支持提取```json代码块
2. Schema验证（agents/tasks必需字段）
3. 详细错误日志
4. 失败时不阻塞思维链显示

---

#### 任务3: 系统配置后端API
**状态**: 待开发  
**预计时间**: 3小时

**新文件**:
- `src/models/system_config.py`
- `src/services/system_config_service.py`
- `tests/unit/test_system_config.py`
- `tests/integration/test_system_config_api.py`

**API设计**:
```python
# GET /api/system/config
# 返回系统配置（API Key脱敏）

# PUT /api/system/config
# 更新系统配置
```

**数据模型**:
```python
class SystemConfig(BaseModel):
    id: str = "default"
    llm_provider: str = "siliconflow"
    api_key: str = ""  # 加密存储
    base_url: str
    default_model: str
    temperature: float = 0.7
    max_tokens: int = 2000
```

---

#### 任务4: 删除侧边栏设置链接
**状态**: 待修改  
**文件**: `frontend/components/sidebar.tsx` (line 420-428)  
**预计时间**: 10分钟

删除Settings按钮，只保留顶部设置入口。

---

### P1 - CrewAI增强

#### 任务5: 运行状态实时显示
**状态**: 待开发  
**文件**: `frontend/components/crewai/crew-drawer.tsx`  
**预计时间**: 2小时

**功能**:
1. 进度条显示执行进度
2. 流式日志实时更新
3. 显示当前执行的Agent和Task
4. 取消执行按钮

---

#### 任务6: 结果展示优化
**状态**: 待优化  
**预计时间**: 1.5小时

**改进**:
1. 语法高亮显示JSON输出
2. 日志按时间戳分组
3. 导出支持多种格式（JSON/TXT/MD）

---

#### 任务7: 工具集成
**状态**: 待开发  
**预计时间**: 4小时

**后端**:
- GET `/api/tools/list` - 所有可用工具
- GET `/api/tools/{tool_id}` - 工具详细信息

**前端**:
- AgentConfigPanel添加工具多选框
- 工具搜索和过滤
- 工具描述和参数展示

---

#### 任务8: 文件上传到CrewAI
**状态**: 待开发  
**预计时间**: 3小时

**后端**:
- POST `/api/files/upload` - 上传文件
- 文件解析（PDF/DOCX/TXT）
- 返回文件ID和摘要

**前端**:
- Task节点支持附加文件
- 文件作为context传递

---

#### 任务9: Flow/Hierarchical架构
**状态**: 待开发  
**参考**: https://docs.crewai.com/  
**预计时间**: 6小时

**实现**:
1. Sequential（默认）
2. Hierarchical（需manager agent）
3. Flow（条件分支）

**后端**: 执行逻辑支持不同架构  
**前端**: 画布支持不同连接规则

---

### P1 - 知识库系统

#### 任务10: 后端知识库服务
**状态**: 待开发  
**预计时间**: 6小时

**新文件**:
- `src/services/knowledge_base_service.py`
- `tests/unit/test_knowledge_base_service.py`
- `tests/integration/test_knowledge_base_api.py`

**功能**:
- 创建知识库
- 上传文档（PDF/DOCX/TXT/MD）
- 文档分块和Embedding
- 向量存储（ChromaDB）
- 语义检索

**API端点**:
```python
POST /api/knowledge-bases           # 创建知识库
GET  /api/knowledge-bases           # 列出知识库
POST /api/knowledge-bases/{kb_id}/documents  # 上传文档
POST /api/knowledge-bases/{kb_id}/query      # 查询
DELETE /api/knowledge-bases/{kb_id}          # 删除
```

---

#### 任务11: 前端知识库UI
**状态**: 待开发  
**文件**: `frontend/components/settings/knowledge-base-settings.tsx`  
**预计时间**: 4小时

**功能**:
- 知识库列表
- 创建新知识库
- 拖拽上传文档
- 文档列表和删除
- 测试查询功能

---

#### 任务12: CrewAI集成知识库
**状态**: 待开发  
**预计时间**: 2小时

**功能**:
- Agent配置中选择知识库
- 知识库作为工具挂载
- 自动检索相关文档

---

### P2 - 架构优化

#### 任务13: 后端架构重组
**状态**: 可选  
**预计时间**: 6小时

**目标**: 拆分`api_server.py`（1166行）为模块化结构

**新结构**:
```
src/api/
├── main.py              # FastAPI app
├── dependencies.py      # 依赖注入
├── routers/
│   ├── chat.py
│   ├── thinking.py
│   ├── crewai.py
│   ├── tools.py
│   ├── agents.py
│   ├── knowledge.py
│   └── system.py
├── services/
│   ├── chat_service.py
│   ├── crewai_service.py
│   └── knowledge_service.py
└── models/
    ├── chat.py
    ├── tool.py
    └── agent.py
```

**注意**: 仅重组结构，不修改业务逻辑

---

#### 任务14: 前端架构优化
**状态**: 可选  
**预计时间**: 4小时

**目标**: 模块化API和状态管理

**新结构**:
```
frontend/
├── lib/
│   ├── api/
│   │   ├── chat.ts
│   │   ├── crewai.ts
│   │   ├── tools.ts
│   │   └── knowledge.ts
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useThinkingChain.ts
│   │   └── useCrewCanvas.ts
│   └── store/
│       ├── chatStore.ts
│       ├── crewStore.ts
│       └── configStore.ts
└── types/
    ├── chat.ts
    ├── crewai.ts
    └── tools.ts
```

---

## 📅 时间计划

### 第1周: 紧急修复
- [x] 主题切换（30分钟）
- [ ] CrewAI JSON解析（1小时）
- [ ] 系统配置API（3小时）
- [ ] 删除侧边栏设置（10分钟）

**预计完成**: 2025-10-31

### 第2周: CrewAI增强
- [ ] 运行状态显示（2小时）
- [ ] 结果展示优化（1.5小时）
- [ ] 工具集成（4小时）
- [ ] 文件上传（3小时）
- [ ] Flow架构（6小时）

**预计完成**: 2025-11-07

### 第3周: 知识库系统
- [ ] 后端服务（6小时）
- [ ] 前端UI（4小时）
- [ ] CrewAI集成（2小时）
- [ ] 完整测试（4小时）

**预计完成**: 2025-11-14

### 第4周: 架构优化（可选）
- [ ] 后端重组（6小时）
- [ ] 前端优化（4小时）
- [ ] 回归测试（4小时）

**预计完成**: 2025-11-21

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
3. ✅ 核心功能100%
4. ✅ 所有测试通过
5. ✅ 文档完整
6. ✅ 代码质量优秀

---

## 🚀 开发规范

### 必须遵守
1. **不改变原有功能** - 最高优先级
2. **后端优先** - 先开发后端和测试
3. **测试驱动** - 每个功能都有测试
4. **文档同步** - 代码和文档同步更新

### 开发流程
```
1. 后端服务开发
2. 后端单元测试
3. 后端集成测试
4. API接口文档
5. 前端开发
6. 前端集成测试
7. E2E测试
8. 用户验收
```

详见: `DEVELOPMENT_WORKFLOW.md`

---

## 📊 项目统计

| 指标 | 数值 |
|------|-----|
| 代码行数 | ~12,000行 |
| 测试用例 | 41个 |
| 测试通过率 | 100% |
| 代码覆盖率 | >85% |
| API端点 | 25个 |
| 前端组件 | 45个 |

---

## 📚 相关文档

- `README.md` - 项目介绍和快速开始
- `DEVELOPMENT_WORKFLOW.md` - 开发工作流规范
- `CHANGELOG.md` - 版本变更历史
- `docs/DOCUMENTATION_INDEX.md` - 完整文档索引

---

**维护者**: AI Development Team  
**最后更新**: 2025-10-30  
**下一步**: Phase 1 - 紧急修复

