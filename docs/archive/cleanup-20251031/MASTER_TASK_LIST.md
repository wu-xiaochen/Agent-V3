# 🎯 Agent-V3 主任务清单

**创建日期**: 2025-10-30  
**项目版本**: v3.1  
**目标**: 完成所有核心功能、测试、优化

---

## 📊 当前进度总览

### ✅ 已完成 (Phase 1-3)
- [x] 项目清理和文档整合
- [x] 主题切换功能修复
- [x] CrewAI JSON解析增强
- [x] 系统配置后端API (3个端点)
- [x] 系统配置前端集成
- [x] 系统配置测试 (31/31通过)
- [x] CrewAI配置自动加载修复

**完成度**: 基础功能 100%

---

## 🔥 P0 - 紧急任务 (必须完成)

### 1. ⏳ E2E测试框架搭建 (使用Playwright MCP)
**优先级**: 🔴 最高  
**预计时间**: 4-6小时  
**负责人**: AI Agent  

#### 子任务
- [ ] 1.1 基础聊天功能E2E测试
  - [ ] 发送消息测试
  - [ ] 接收响应测试
  - [ ] 会话切换测试
  - [ ] 思维链显示测试
  - [ ] 工具调用测试
  
- [ ] 1.2 CrewAI功能E2E测试
  - [ ] 配置生成测试
  - [ ] 画布加载测试
  - [ ] Agent配置测试
  - [ ] Task配置测试
  - [ ] 执行流程测试
  - [ ] 结果展示测试

- [ ] 1.3 设置功能E2E测试
  - [ ] 系统配置读取测试
  - [ ] 系统配置保存测试
  - [ ] 主题切换测试
  - [ ] Agent配置CRUD测试
  - [ ] 工具配置CRUD测试

**测试脚本位置**: `tests/e2e/playwright/`

**验收标准**:
- [ ] 所有核心用户流程覆盖
- [ ] 测试通过率 100%
- [ ] 包含截图验证
- [ ] 包含性能测试

---

### 2. ⏳ CrewAI运行状态实时显示
**优先级**: 🔴 高  
**预计时间**: 3-4小时  
**文件**: `frontend/components/crewai/crew-drawer.tsx`

#### 需求
- [ ] 2.1 进度条组件
  - [ ] 显示当前执行进度 (X/Y tasks)
  - [ ] 显示当前执行的Agent
  - [ ] 显示执行耗时
  
- [ ] 2.2 实时日志流
  - [ ] WebSocket连接
  - [ ] 日志类型分类 (info/success/error/warning)
  - [ ] 日志时间戳
  - [ ] 自动滚动到底部
  
- [ ] 2.3 控制功能
  - [ ] 暂停执行按钮
  - [ ] 取消执行按钮
  - [ ] 重新执行按钮

**后端API**:
- [ ] GET /api/crewai/execution/{id}/status
- [ ] WebSocket /ws/crewai/execution/{id}

**测试**:
- [ ] 单元测试: 组件渲染
- [ ] 集成测试: API调用
- [ ] E2E测试: 完整流程

---

### 3. ⏳ CrewAI结果展示优化
**优先级**: 🟡 中  
**预计时间**: 2-3小时  
**文件**: `frontend/components/crewai/crew-drawer.tsx`

#### 需求
- [ ] 3.1 语法高亮
  - [ ] JSON结果高亮 (使用react-json-view)
  - [ ] 代码块高亮 (使用highlight.js)
  - [ ] Markdown渲染
  
- [ ] 3.2 日志增强
  - [ ] 按时间分组
  - [ ] 按Agent分组
  - [ ] 日志搜索/过滤
  - [ ] 日志级别过滤
  
- [ ] 3.3 导出功能
  - [ ] 导出为JSON
  - [ ] 导出为TXT
  - [ ] 导出为Markdown
  - [ ] 复制到剪贴板

**依赖安装**:
```bash
cd frontend
npm install react-json-view highlight.js
```

---

## 🚀 P1 - 高优先级任务

### 4. ⏳ 工具列表API和集成
**优先级**: 🟡 高  
**预计时间**: 4-5小时

#### 后端开发
**文件**: `api_server.py` 或新建 `src/api/routers/tools.py`

- [ ] 4.1 API端点
  - [ ] GET /api/tools - 获取所有工具
  - [ ] GET /api/tools/{tool_id} - 获取工具详情
  - [ ] GET /api/tools/categories - 获取工具分类
  
- [ ] 4.2 工具数据模型
  ```python
  class Tool(BaseModel):
      id: str
      name: str
      display_name: str
      description: str
      category: str
      parameters: List[ToolParameter]
      enabled: bool
  ```

- [ ] 4.3 测试
  - [ ] 单元测试: `tests/unit/test_tools_api.py`
  - [ ] 集成测试: `tests/integration/test_tools_api.py`

#### 前端开发
**文件**: `frontend/components/crewai/agent-config-panel.tsx`

- [ ] 4.4 工具选择器
  - [ ] 多选下拉框
  - [ ] 工具搜索
  - [ ] 按分类过滤
  - [ ] 工具描述展示
  - [ ] 已选工具标签

- [ ] 4.5 API集成
  - [ ] `frontend/lib/api/tools.ts` 已存在，验证功能
  - [ ] 组件调用API

---

### 5. ⏳ 文件上传到CrewAI
**优先级**: 🟡 高  
**预计时间**: 3-4小时

#### 后端开发
- [ ] 5.1 文件处理服务
  - [ ] PDF解析 (PyPDF2)
  - [ ] DOCX解析 (python-docx)
  - [ ] TXT/MD解析
  - [ ] 文件摘要生成
  
- [ ] 5.2 API端点
  - [ ] POST /api/files/upload
  - [ ] GET /api/files/{file_id}
  - [ ] DELETE /api/files/{file_id}

#### 前端开发
- [ ] 5.3 文件上传组件
  - [ ] Task节点支持附加文件
  - [ ] 拖拽上传
  - [ ] 进度条显示
  - [ ] 文件列表管理
  
- [ ] 5.4 Context传递
  - [ ] 文件内容作为Task context
  - [ ] 文件摘要展示

---

### 6. ⏳ 知识库系统 (完整实现)
**优先级**: 🟡 高  
**预计时间**: 8-10小时

#### 后端开发 (6小时)
**新文件**: 
- `src/services/knowledge_base_service.py`
- `tests/unit/test_knowledge_base_service.py`
- `tests/integration/test_knowledge_base_api.py`

- [ ] 6.1 ChromaDB集成
  - [ ] 知识库创建/删除
  - [ ] 文档上传
  - [ ] 文档分块 (LangChain)
  - [ ] Embedding生成
  - [ ] 向量存储
  
- [ ] 6.2 检索功能
  - [ ] 语义搜索
  - [ ] Top-K结果
  - [ ] 相似度阈值
  - [ ] 结果排序
  
- [ ] 6.3 API端点
  - [ ] POST /api/knowledge-bases - 创建知识库
  - [ ] GET /api/knowledge-bases - 列出知识库
  - [ ] POST /api/knowledge-bases/{kb_id}/documents - 上传文档
  - [ ] POST /api/knowledge-bases/{kb_id}/query - 查询
  - [ ] DELETE /api/knowledge-bases/{kb_id} - 删除
  
- [ ] 6.4 测试
  - [ ] 单元测试 (15个用例)
  - [ ] 集成测试 (10个用例)

#### 前端开发 (4小时)
**文件**: `frontend/components/settings/knowledge-base-settings.tsx`

- [ ] 6.5 知识库管理UI
  - [ ] 知识库列表（卡片视图）
  - [ ] 创建知识库对话框
  - [ ] 文档上传（拖拽）
  - [ ] 文档列表
  - [ ] 删除确认
  
- [ ] 6.6 测试查询
  - [ ] 查询输入框
  - [ ] 结果列表
  - [ ] 相似度显示
  - [ ] 来源文档链接

#### CrewAI集成
- [ ] 6.7 知识库工具
  - [ ] Agent配置选择知识库
  - [ ] 知识库作为Tool挂载
  - [ ] 自动检索相关文档

---

## 📋 P2 - 中优先级任务

### 7. ⏳ Flow/Hierarchical架构支持
**优先级**: 🟢 中  
**预计时间**: 6-8小时

- [ ] 7.1 后端执行逻辑
  - [ ] Sequential (默认，已实现)
  - [ ] Hierarchical (Manager Agent)
  - [ ] Flow (条件分支)
  
- [ ] 7.2 前端画布支持
  - [ ] 不同连接规则
  - [ ] Manager Agent配置
  - [ ] 条件分支UI
  
- [ ] 7.3 测试
  - [ ] 各架构执行测试
  - [ ] E2E测试

---

### 8. ⏳ 性能优化
**优先级**: 🟢 中  
**预计时间**: 4-6小时

#### 后端优化
- [ ] 8.1 数据库查询优化
  - [ ] 添加索引
  - [ ] 查询缓存
  - [ ] 批量操作
  
- [ ] 8.2 API响应优化
  - [ ] 响应压缩
  - [ ] 分页支持
  - [ ] 字段选择

#### 前端优化
- [ ] 8.3 React性能优化
  - [ ] useMemo/useCallback
  - [ ] 虚拟滚动 (react-window)
  - [ ] 代码分割
  - [ ] 懒加载
  
- [ ] 8.4 状态管理优化
  - [ ] Zustand持久化优化
  - [ ] 选择器优化
  - [ ] 避免不必要的重渲染

---

### 9. ⏳ 错误处理和用户体验优化
**优先级**: 🟢 中  
**预计时间**: 3-4小时

- [ ] 9.1 全局错误边界
  - [ ] React Error Boundary
  - [ ] 友好错误页面
  - [ ] 错误日志收集
  
- [ ] 9.2 加载状态优化
  - [ ] Skeleton加载
  - [ ] 进度指示器
  - [ ] 乐观更新
  
- [ ] 9.3 Toast通知优化
  - [ ] 统一通知样式
  - [ ] 操作撤销
  - [ ] 通知队列管理

---

## 🧪 测试完整性检查清单

### 单元测试 (Unit Tests)
- [x] 系统配置模型和服务 (16/16)
- [ ] 知识库服务 (0/15)
- [ ] 工具管理服务 (0/10)
- [ ] CrewAI执行服务 (0/12)
- [ ] 文件处理服务 (0/8)

**目标**: 60+个单元测试，覆盖率 >85%

### 集成测试 (Integration Tests)
- [x] 系统配置API (15/15)
- [ ] 知识库API (0/10)
- [ ] 工具API (0/8)
- [ ] CrewAI API (0/12)
- [ ] 文件上传API (0/6)

**目标**: 50+个集成测试，覆盖率 >80%

### E2E测试 (End-to-End Tests with Playwright)
- [ ] 基础聊天流程 (0/6)
- [ ] CrewAI完整流程 (0/8)
- [ ] 设置功能 (0/5)
- [ ] 知识库管理 (0/6)
- [ ] 跨功能集成 (0/4)

**目标**: 30+个E2E测试，核心流程100%覆盖

---

## 📦 依赖和工具安装

### Python后端依赖
```bash
# 知识库相关
pip install chromadb langchain pypdf2 python-docx

# 测试相关
pip install pytest pytest-asyncio pytest-cov

# 性能分析
pip install py-spy memory-profiler
```

### Node.js前端依赖
```bash
cd frontend

# UI增强
npm install react-json-view highlight.js react-syntax-highlighter

# 性能优化
npm install react-window @tanstack/react-virtual

# 测试工具
npm install -D @playwright/test
```

---

## 🎯 Sprint计划

### Sprint 1: E2E测试和CrewAI增强 (3-4天)
**目标**: 完成E2E测试框架 + CrewAI实时显示和结果优化

- Day 1: E2E测试框架搭建
  - [ ] Playwright配置
  - [ ] 基础聊天测试 (4小时)
  
- Day 2: CrewAI E2E测试 + 实时显示
  - [ ] CrewAI测试用例 (3小时)
  - [ ] 实时状态显示 (4小时)
  
- Day 3: CrewAI结果优化 + 设置测试
  - [ ] 结果展示优化 (3小时)
  - [ ] 设置功能测试 (3小时)
  
- Day 4: 工具集成
  - [ ] 工具列表API (4小时)
  - [ ] 前端工具选择器 (3小时)

**验收**: E2E测试 >20个，CrewAI功能完善

---

### Sprint 2: 知识库系统 (4-5天)
**目标**: 完整实现知识库功能

- Day 1-2: 后端开发
  - [ ] ChromaDB集成 (4小时)
  - [ ] API端点 (3小时)
  - [ ] 单元测试 (2小时)
  
- Day 3: 前端UI
  - [ ] 知识库管理界面 (4小时)
  - [ ] 文档上传 (2小时)
  
- Day 4: CrewAI集成
  - [ ] 知识库工具 (3小时)
  - [ ] Agent配置 (2小时)
  
- Day 5: 测试和优化
  - [ ] 集成测试 (2小时)
  - [ ] E2E测试 (2小时)
  - [ ] 性能优化 (2小时)

**验收**: 知识库完全可用，测试通过

---

### Sprint 3: 优化和完善 (2-3天)
**目标**: 性能优化、错误处理、文档完善

- Day 1: 性能优化
  - [ ] 后端优化 (3小时)
  - [ ] 前端优化 (3小时)
  
- Day 2: 错误处理和UX
  - [ ] 全局错误处理 (2小时)
  - [ ] 加载状态优化 (2小时)
  - [ ] Toast优化 (2小时)
  
- Day 3: 文档和部署
  - [ ] API文档更新 (2小时)
  - [ ] 用户文档 (2小时)
  - [ ] 部署指南 (2小时)

**验收**: 系统稳定，文档完整

---

## 📈 质量门禁

### 代码质量要求
- [ ] Linter零错误
- [ ] TypeScript类型覆盖 >95%
- [ ] 代码复杂度 <10
- [ ] 重复代码率 <3%

### 测试覆盖要求
- [ ] 单元测试覆盖率 >85%
- [ ] 集成测试覆盖率 >80%
- [ ] E2E测试核心流程 100%
- [ ] 所有测试通过率 100%

### 性能要求
- [ ] 首屏加载 <3秒
- [ ] API响应 <500ms (p95)
- [ ] E2E测试执行 <5分钟
- [ ] 内存占用 <500MB

### 安全要求
- [ ] API Key加密存储
- [ ] CORS配置正确
- [ ] XSS防护
- [ ] SQL注入防护

---

## 🎊 最终验收标准

### 功能完整性
- [ ] 所有P0任务完成
- [ ] 所有P1任务完成 >80%
- [ ] 核心功能100%可用
- [ ] 无阻塞性Bug

### 测试完整性
- [ ] 单元测试 >60个
- [ ] 集成测试 >50个
- [ ] E2E测试 >30个
- [ ] 所有测试通过

### 文档完整性
- [ ] API文档完整
- [ ] 用户指南完整
- [ ] 开发文档完整
- [ ] 部署文档完整

### 代码质量
- [ ] 无Linter错误
- [ ] 代码review通过
- [ ] 性能测试通过
- [ ] 安全审计通过

---

## 📝 协作分工建议

### AI Agent 1 (后端专家)
- 系统配置服务 ✅
- 知识库服务 ⏳
- 工具API ⏳
- CrewAI执行优化 ⏳
- 后端测试 ⏳

### AI Agent 2 (前端专家)
- UI组件优化 ⏳
- CrewAI画布增强 ⏳
- 知识库UI ⏳
- 性能优化 ⏳
- 用户体验优化 ⏳

### AI Agent 3 (测试专家)
- E2E测试框架 ⏳
- Playwright测试用例 ⏳
- 性能测试 ⏳
- 测试报告 ⏳

### AI Agent 4 (DevOps)
- CI/CD配置 ⏳
- 部署自动化 ⏳
- 监控告警 ⏳
- 文档生成 ⏳

---

**创建时间**: 2025-10-30  
**预计完成**: 2025-11-15  
**当前进度**: 约30%完成

**下一步**: 开始Sprint 1 - E2E测试框架搭建

