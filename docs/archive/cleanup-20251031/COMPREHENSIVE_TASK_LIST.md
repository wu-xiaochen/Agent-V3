# 🎯 Agent-V3 综合任务清单

**创建日期**: 2025-10-30  
**版本**: v3.1  
**状态**: 进行中

---

## 📊 总体进度

```
总任务数: 22个
├── ✅ 已完成: 10个 (45%)
├── 🔄 进行中: 0个
└── ⏳ 待完成: 12个 (55%)

测试覆盖率:
├── 单元/集成测试: 31个 (100%通过)
├── E2E测试: 0个 Playwright测试
└── 测试覆盖率: 87%+ (后端), 0% (E2E)
```

---

## ✅ 已完成任务 (10个)

### Phase 1: 项目清理 ✅
1. ✅ 删除冗余文件(59个)
2. ✅ 整合文档结构
3. ✅ 更新README和路线图

### Phase 2: 紧急修复 ✅  
4. ✅ 主题切换功能
5. ✅ CrewAI JSON解析增强
6. ✅ 删除侧边栏设置链接

### Phase 3: 系统配置API ✅
7. ✅ 后端API实现(3个端点)
8. ✅ 单元测试(16个)
9. ✅ 集成测试(15个)

### Phase 4: 前端集成 ✅
10. ✅ 系统配置前端集成

### Phase 5: 优化增强 ✅ (刚完成)
11. ✅ **Markdown渲染优化**
    - 安装依赖(react-markdown, remark-gfm, react-syntax-highlighter)
    - 创建MarkdownContent组件(270行)
    - 集成到MessageBubble
    - 支持代码高亮、表格、列表等

12. ✅ **CrewAI配置生成优化**
    - 前端JSON提取增强
    - 配置验证和清洗(+73行)
    - 多重提取策略
    - 智能默认值

---

## 🔥 高优先级待办 (P0 - 核心功能)

### 1. ⏳ **建立Playwright测试框架** - 紧急
**预计时间**: 2小时  
**优先级**: P0  
**依赖**: 无

**任务清单**:
- [ ] 安装Playwright和依赖
- [ ] 创建playwright.config.ts
- [ ] 创建基础测试目录结构
- [ ] 编写第一个E2E测试(聊天功能)
- [ ] 配置CI/CD集成
- [ ] 编写测试脚本(npm test:e2e)

**交付物**:
- `playwright.config.ts`
- `tests/e2e/playwright/01-chat-basic.spec.ts`
- `tests/e2e/playwright/02-crewai-generation.spec.ts`
- `package.json` (添加测试脚本)

---

### 2. ⏳ **实现工具列表API** - 高优先级
**预计时间**: 2小时  
**优先级**: P0  
**依赖**: 无

**后端任务**:
- [ ] 创建GET `/api/tools/list`端点
- [ ] 返回所有可用工具列表
- [ ] 包含工具名称、描述、参数schema
- [ ] 编写单元测试
- [ ] 编写集成测试

**前端任务**:
- [ ] 创建`frontend/lib/api/tools.ts`
- [ ] 在Agent配置面板添加工具选择器
- [ ] 工具搜索和过滤功能
- [ ] 工具描述tooltip显示

**交付物**:
- 后端: `api_server.py` (新增端点)
- 前端: `frontend/lib/api/tools.ts`
- 前端: `frontend/components/crewai/agent-tools-selector.tsx`
- 测试: `tests/integration/test_tools_api.py`

---

### 3. ⏳ **CrewAI配置自动加载验证** - 测试
**预计时间**: 30分钟  
**优先级**: P0  
**依赖**: Playwright测试框架

**测试场景**:
1. 用户发送CrewAI生成请求
2. AI调用crewai_generator工具
3. 配置自动保存到data/crews/
4. 前端提取配置
5. 验证和清洗配置
6. CrewAI画布自动打开
7. 配置正确加载到画布

**验证点**:
- [ ] JSON正确解析
- [ ] 所有Agent字段完整
- [ ] 所有Task字段完整
- [ ] 默认值正确填充
- [ ] 画布自动打开
- [ ] 节点正确显示

---

### 4. ⏳ **CrewAI运行状态实时显示** - 功能增强
**预计时间**: 2小时  
**优先级**: P1  
**依赖**: 无

**功能需求**:
- [ ] 执行进度条(百分比显示)
- [ ] 实时日志流式更新(SSE)
- [ ] 当前执行的Agent高亮
- [ ] 当前执行的Task高亮
- [ ] 取消执行按钮
- [ ] 执行时长统计

**技术方案**:
```typescript
// frontend/components/crewai/crew-execution-monitor.tsx
- 使用SSE监听执行进度
- 实时更新UI状态
- 显示每个步骤的详细日志
```

**交付物**:
- `frontend/components/crewai/crew-execution-monitor.tsx`
- `frontend/components/crewai/execution-progress-bar.tsx`
- 修改: `frontend/components/crewai/crew-drawer.tsx`

---

### 5. ⏳ **CrewAI结果展示优化** - UI增强
**预计时间**: 1.5小时  
**优先级**: P1  
**依赖**: Markdown渲染优化(已完成✅)

**优化项**:
- [ ] JSON输出语法高亮(使用react-syntax-highlighter)
- [ ] 日志按时间戳分组
- [ ] 日志类型过滤(info/success/error/warning)
- [ ] 导出为TXT格式
- [ ] 导出为Markdown格式
- [ ] 导出为JSON格式
- [ ] 一键复制结果

**技术方案**:
```typescript
// 复用MarkdownContent组件进行渲染
import { MarkdownContent } from '@/components/markdown-content'

// JSON高亮显示
<SyntaxHighlighter language="json" style={darkMode ? oneDark : vscDarkPlus}>
  {JSON.stringify(result, null, 2)}
</SyntaxHighlighter>
```

**交付物**:
- `frontend/components/crewai/result-viewer.tsx`
- `frontend/components/crewai/log-viewer.tsx`
- `frontend/utils/export-helpers.ts`

---

## 📋 中优先级待办 (P1 - 重要功能)

### 6. ⏳ **Agent配置面板工具选择**
**预计时间**: 1.5小时  
**依赖**: 工具列表API(任务2)

- [ ] 在Agent配置对话框添加工具选择器
- [ ] 多选checkbox支持
- [ ] 工具分类显示
- [ ] 工具描述和参数展示

---

### 7. ⏳ **文件上传到CrewAI**
**预计时间**: 3小时  
**依赖**: 无

**后端**:
- [ ] POST `/api/files/upload` 端点
- [ ] PDF/DOCX/TXT文件解析
- [ ] 文件内容提取
- [ ] 返回文件ID和摘要

**前端**:
- [ ] Task节点支持附加文件
- [ ] 文件上传UI组件
- [ ] 文件列表显示
- [ ] 文件作为context传递给Task

---

### 8. ⏳ **Flow/Hierarchical架构支持**
**预计时间**: 6小时  
**依赖**: 无
**参考**: https://docs.crewai.com/

- [ ] 后端支持Hierarchical流程
- [ ] Manager Agent配置
- [ ] 前端画布支持条件分支
- [ ] Flow架构可视化
- [ ] 执行顺序动态调整

---

### 9. ⏳ **知识库后端服务**
**预计时间**: 6小时  
**依赖**: 无

- [ ] ChromaDB集成
- [ ] 文档分块和Embedding
- [ ] 向量检索API
- [ ] 知识库CRUD API
- [ ] 单元测试(8个)
- [ ] 集成测试(10个)

---

### 10. ⏳ **知识库前端UI**
**预计时间**: 4小时  
**依赖**: 知识库后端(任务9)

- [ ] 知识库列表页面
- [ ] 创建知识库对话框
- [ ] 文档上传组件
- [ ] 文档列表和管理
- [ ] 语义搜索测试UI

---

### 11. ⏳ **知识库CrewAI集成**
**预计时间**: 2小时  
**依赖**: 知识库后端+前端

- [ ] Agent配置关联知识库
- [ ] 知识库作为工具使用
- [ ] 自动检索相关文档
- [ ] 文档内容注入Task context

---

### 12. ⏳ **E2E测试完整覆盖**
**预计时间**: 12小时  
**依赖**: Playwright框架(任务1)

**测试模块**:
- [ ] 模块1: 基础聊天(40个测试项)
- [ ] 模块2: CrewAI团队(30个测试项)
- [ ] 模块3: 知识库(20个测试项)
- [ ] 模块4: 系统设置(15个测试项)
- [ ] 模块5: 工具管理(10个测试项)
- [ ] 模块6-8: UI/性能/错误(15个测试项)

**目标覆盖率**: 70%+ (Beta版本要求)

---

## 🔄 可选优化项 (P2 - 辅助功能)

### 13. 后端模块化重组
- 拆分api_server.py为多个路由模块
- 服务层独立管理
- 预计: 6小时

### 14. 前端架构优化
- 模块化API客户端
- 自定义Hooks
- 预计: 4小时

---

## 📊 任务优先级矩阵

| 任务ID | 任务名称 | 优先级 | 预计时间 | 依赖 | 状态 |
|--------|----------|--------|----------|------|------|
| 1 | Playwright测试框架 | P0 | 2h | 无 | ⏳ 待开始 |
| 2 | 工具列表API | P0 | 2h | 无 | ⏳ 待开始 |
| 3 | CrewAI自动加载验证 | P0 | 0.5h | #1 | ⏳ 待开始 |
| 4 | CrewAI运行状态显示 | P1 | 2h | 无 | ⏳ 待开始 |
| 5 | CrewAI结果展示优化 | P1 | 1.5h | 无 | ⏳ 待开始 |
| 6 | Agent工具选择 | P1 | 1.5h | #2 | ⏳ 待开始 |
| 7 | 文件上传到CrewAI | P1 | 3h | 无 | ⏳ 待开始 |
| 8 | Flow/Hierarchical | P1 | 6h | 无 | ⏳ 待开始 |
| 9 | 知识库后端 | P1 | 6h | 无 | ⏳ 待开始 |
| 10 | 知识库前端 | P1 | 4h | #9 | ⏳ 待开始 |
| 11 | 知识库集成 | P1 | 2h | #10 | ⏳ 待开始 |
| 12 | E2E测试完整覆盖 | P0 | 12h | #1 | ⏳ 待开始 |

---

## 🎯 执行计划

### 阶段1: 测试基础设施 (立即执行)
**时间**: 2-3小时

```
任务1: Playwright测试框架 ⏰ 2h
  ↓
任务3: CrewAI自动加载验证 ⏰ 0.5h
  ↓
任务12: 开始E2E测试编写 ⏰ 开始
```

### 阶段2: 核心API完善 (今天完成)
**时间**: 3-4小时

```
任务2: 工具列表API ⏰ 2h
  ↓
任务6: Agent工具选择 ⏰ 1.5h
```

### 阶段3: UI增强 (明天)
**时间**: 3.5小时

```
任务4: CrewAI运行状态 ⏰ 2h
  ∥
任务5: CrewAI结果展示 ⏰ 1.5h
```

### 阶段4: 高级功能 (本周)
**时间**: 15小时

```
任务7: 文件上传 ⏰ 3h
  ∥
任务8: Flow架构 ⏰ 6h
  ∥
任务9-11: 知识库系统 ⏰ 12h
```

### 阶段5: 完善测试 (下周)
**时间**: 12小时

```
任务12: E2E测试完整覆盖 ⏰ 12h
  ↓
测试报告和优化 ⏰ 2h
```

---

## 📈 里程碑

### M1: 测试就绪 (今天)
- ✅ Playwright框架建立
- ✅ 核心功能测试通过
- ✅ 工具API完成

### M2: 功能完善 (3天内)
- ✅ CrewAI UI增强完成
- ✅ 文件上传功能
- ✅ P0测试覆盖率70%+

### M3: Beta就绪 (1周内)
- ✅ 知识库系统完成
- ✅ Flow架构支持
- ✅ 测试覆盖率85%+

### M4: Production就绪 (2周内)
- ✅ 所有功能完成
- ✅ 测试覆盖率95%+
- ✅ 性能优化完成
- ✅ 文档完整

---

## 🚀 立即行动

### 现在开始 (接下来2小时)

**任务1: 建立Playwright测试框架**

```bash
# 1. 安装依赖
cd frontend
pnpm add -D @playwright/test
npx playwright install

# 2. 创建配置文件
# playwright.config.ts

# 3. 创建第一个测试
# tests/e2e/playwright/01-chat-basic.spec.ts

# 4. 运行测试
pnpm test:e2e
```

**预期产出**:
- ✅ Playwright环境配置完成
- ✅ 至少2个E2E测试通过
- ✅ 测试截图和报告生成

---

## 📝 备注

### 团队协作建议
1. **智能体1**(我): 专注于测试框架和E2E测试
2. **智能体2**: 专注于工具API和前端集成
3. **智能体3**: 专注于CrewAI UI增强

### 质量标准
- ✅ 所有代码无Linter错误
- ✅ 所有新功能有测试覆盖
- ✅ 所有API有文档说明
- ✅ 所有UI有截图演示

### 成功标准
- Beta版本: 测试覆盖率 >70%, 所有P0功能完成
- Production: 测试覆盖率 >95%, 所有功能完成

---

**文档版本**: v1.0  
**创建时间**: 2025-10-30  
**下次更新**: 任务完成后

**当前最紧急任务**: #1 建立Playwright测试框架 ⚡

