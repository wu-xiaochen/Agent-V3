# Agent-V3 功能升级计划

## 📅 版本：V3.1.0
## 🎯 目标：增强工具系统、知识库、多模态、前端界面

---

## 🚀 新功能需求

### 1. 工具系统灵活配置 ⭐⭐⭐
**需求描述**：
- 移除硬编码的工具定义
- 支持通过配置文件灵活配置工具
- 支持 MCP 和 API 两种模式
- 智能体自动读取和适配

**技术方案**：
```yaml
# config/tools/unified_tools.yaml
tools:
  - name: "search"
    type: "builtin"
    enabled: true
    
  - name: "n8n_workflow"
    type: "mcp"
    mode: "stdio"  # 或 "http"
    config_ref: "n8n_mcp_generator"
    enabled: true
    
  - name: "crewai_generator"
    type: "api"
    module: "src.tools.crewai_generator"
    class: "CrewAIGeneratorTool"
    enabled: true
```

**实现步骤**：
1. 创建统一的工具配置 Schema
2. 实现工具注册器（Tool Registry）
3. 实现工具工厂模式（支持动态加载）
4. 更新 UnifiedAgent 使用新的工具系统

---

### 2. 文档自动下载链接 ⭐⭐
**需求描述**：
- Agent 生成文档后，自动提供下载链接
- 不要总结，直接返回文件路径和下载 URL

**技术方案**：
```python
# src/interfaces/file_manager.py
class FileManager:
    def save_document(self, content, filename) -> dict:
        """保存文档并返回下载信息"""
        return {
            "filename": filename,
            "path": "/outputs/documents/xxx.md",
            "download_url": "http://localhost:8000/api/files/download/xxx",
            "size": "2.5KB",
            "created_at": "2025-10-29 10:00:00"
        }
```

**实现步骤**：
1. 创建 FileManager 服务
2. 实现文件存储和访问接口
3. 在 Agent 工具中集成文件管理
4. 返回格式化的下载信息

---

### 3. 知识库功能 ⭐⭐⭐⭐
**需求描述**：
- 创建和管理知识库
- 支持挂载到 Agent
- 支持 CrewAI 知识库
- 支持向量检索和语义搜索

**技术方案**：
```python
# 知识库架构
KnowledgeBase:
  - id: kb_001
  - name: "产品文档库"
  - type: "vector"  # vector, sql, file
  - storage: "chromadb"
  - embedding_model: "text-embedding-3-small"
  - agents: ["unified_agent", "crew_001"]
  
# 使用方式
agent.attach_knowledge_base(kb_id="kb_001")
crew.add_knowledge_source(kb_id="kb_001")
```

**实现步骤**：
1. 设计知识库数据模型
2. 实现知识库 CRUD 接口
3. 集成向量数据库（ChromaDB/FAISS）
4. 实现知识库挂载机制
5. 支持 CrewAI 知识库集成

---

### 4. 文件附件和多模态 ⭐⭐⭐⭐
**需求描述**：
- 支持文件上传和读取
- 支持图片、PDF、Word、Excel 等格式
- 支持多模态模型（GPT-4V, Claude 3 等）
- 文件自动解析和分析

**技术方案**：
```python
# src/infrastructure/multimodal/
class MultimodalProcessor:
    def process_file(self, file_path) -> dict:
        """处理各类文件"""
        - 图片 → Vision Model 分析
        - PDF → 文本提取 + 结构化
        - Excel → 数据表格解析
        - Word → 文档内容提取
        
    def analyze_with_vision(self, image_path, query):
        """使用视觉模型分析"""
```

**实现步骤**：
1. 实现文件上传接口
2. 创建多模态处理器
3. 集成 Vision API
4. 实现文件解析器（PDF, Excel, Word）
5. 在 Agent 中集成多模态能力

---

### 5. API 接口层和前端 ⭐⭐⭐⭐⭐
**需求描述**：
- 实现完整的 REST API
- 设计现代化前端界面
- 支持实时通信（WebSocket）
- 工具运行可视化

**API 设计**：
```yaml
# RESTful API 端点
POST   /api/chat/message          # 发送消息
GET    /api/chat/history          # 获取历史
WS     /api/chat/stream           # 实时流式输出

POST   /api/knowledge/create      # 创建知识库
POST   /api/knowledge/upload      # 上传文档
GET    /api/knowledge/list        # 列出知识库

POST   /api/crew/create           # 创建 CrewAI
POST   /api/crew/run              # 运行 CrewAI
GET    /api/crew/status           # 获取状态

POST   /api/files/upload          # 上传文件
GET    /api/files/download/:id    # 下载文件
POST   /api/files/analyze         # 分析文件
```

**前端设计**：
```
主界面布局：
┌─────────────────────────────────────────┐
│  Logo    [知识库] [工具] [设置]         │
├──────────┬──────────────────────────────┤
│          │  💬 Chat Interface           │
│  侧边栏  │  ─────────────────────      │
│          │  User: 帮我分析这个文档       │
│  - 对话  │  AI: 正在分析...             │
│  - 知识库│                               │
│  - Crew  │  [输入框]              [发送] │
│  - 文件  ├──────────────────────────────┤
│          │  🔧 Tool Panel (滑出)       │
│          │  CrewAI 配置可视化           │
│          │  ├ Agents: [列表]            │
│          │  ├ Tasks: [流程图]           │
│          │  └ Status: Running...        │
└──────────┴──────────────────────────────┘
```

**实现步骤**：
1. 创建 FastAPI 应用
2. 实现所有 API 端点
3. 添加 WebSocket 支持
4. 设计前端组件
5. 实现工具可视化面板

---

### 6. 工具可视化面板 ⭐⭐⭐⭐
**需求描述**：
- 右侧滑出窗口显示工具运行
- CrewAI 配置可视化
- 支持用户输入参数
- 支持多轮对话和 Flow 形式

**技术方案**：
```typescript
// 工具面板状态管理
interface ToolPanelState {
  visible: boolean;
  currentTool: 'crewai' | 'n8n' | 'knowledge' | null;
  crewConfig?: CrewAIConfig;
  toolStatus: 'idle' | 'running' | 'completed' | 'error';
  output?: any;
}

// CrewAI 可视化组件
<CrewAIVisualizer
  config={crewConfig}
  onParamChange={updateParams}
  onRun={runCrew}
  mode="conversation" // 或 "flow"
/>
```

**实现步骤**：
1. 设计工具面板组件
2. 实现 CrewAI 配置编辑器
3. 实现流程图可视化
4. 添加参数输入表单
5. 实现实时状态更新

---

## 📋 实现优先级

### Phase 1: 核心功能（2-3天）
1. ✅ 工具系统灵活配置
2. ✅ 文档下载链接
3. ✅ API 接口层基础

### Phase 2: 知识库和多模态（3-4天）
4. ✅ 知识库功能
5. ✅ 文件附件和多模态

### Phase 3: 前端和可视化（3-4天）
6. ✅ 前端界面开发
7. ✅ 工具可视化面板
8. ✅ CrewAI Flow 支持

---

## 🎨 V0 前端提示词

```markdown
Create a modern AI agent chat interface with the following requirements:

### Layout
- Clean, modern design with sidebar navigation
- Main chat area in the center
- Slide-out tool panel on the right side
- Top header with logo and navigation

### Components Needed

1. **Sidebar (Left)**
   - Chat history list
   - Knowledge base manager
   - CrewAI teams list
   - File uploads section
   - Settings

2. **Main Chat Area (Center)**
   - Message list with user/AI messages
   - Streaming text support
   - Code block rendering with syntax highlighting
   - File preview (images, documents)
   - Message input with file attachment button
   - Send button

3. **Tool Panel (Right, Slide-out)**
   - Toggle button to show/hide
   - Tabs for different tools:
     * CrewAI Configurator
     * N8N Workflow Viewer
     * Knowledge Base Browser
   - Real-time status indicators
   - Parameter input forms
   - Visual flow diagram for CrewAI

### CrewAI Visualizer Features
- Agent cards with roles and capabilities
- Task flow diagram (nodes and edges)
- Parameter input fields
- Run/Stop controls
- Status: idle/running/completed/error
- Output display area
- Support for conversation mode and flow mode

### Styling
- Use Tailwind CSS or shadcn/ui
- Dark mode support
- Smooth animations for panel slide-in/out
- Professional color scheme (primary: blue, accent: purple)
- Icons from lucide-react or heroicons

### Technical Requirements
- Built with React + TypeScript
- State management with Zustand or Context API
- WebSocket support for real-time updates
- File upload with drag-and-drop
- Responsive design (desktop first)
- Code splitting and lazy loading

### API Integration Points
- POST /api/chat/message - Send message
- WS /api/chat/stream - Real-time streaming
- POST /api/crew/create - Create CrewAI
- POST /api/crew/run - Run CrewAI
- POST /api/files/upload - Upload files
- GET /api/knowledge/list - List knowledge bases

### Special Features
1. **Streaming Support**: Display AI responses character by character
2. **Tool Visualization**: Show tool execution in real-time
3. **CrewAI Editor**: Drag-and-drop agent/task configuration
4. **File Analysis**: Show file analysis results inline
5. **Multi-turn Conversation**: Support context-aware chat

Please create a fully functional, production-ready interface with clean code structure.
```

---

## 🔧 技术栈

### 后端
- **FastAPI**: API 框架
- **WebSocket**: 实时通信
- **ChromaDB**: 向量数据库
- **Redis**: 缓存和会话
- **SQLite/PostgreSQL**: 数据持久化

### 前端
- **React 18**: UI 框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式
- **shadcn/ui**: 组件库
- **React Flow**: 流程图
- **Zustand**: 状态管理
- **Socket.io**: WebSocket 客户端

### 多模态
- **OpenAI GPT-4V**: 视觉分析
- **PyMuPDF**: PDF 解析
- **python-docx**: Word 解析
- **openpyxl**: Excel 解析
- **Pillow**: 图片处理

---

## ⚠️ 兼容性保证

### 不影响现有功能
- ✅ 保留所有现有 Agent 功能
- ✅ 保留 CrewAI 集成
- ✅ 保留 N8N 集成
- ✅ 保留记忆系统
- ✅ 向后兼容配置文件

### 渐进式升级
1. 新功能作为独立模块
2. 通过配置开关启用
3. 不修改核心 Agent 逻辑
4. API 层作为新增接口

---

## 📝 下一步行动

1. **Phase 1 启动**：实现工具配置系统
2. **创建分支**：`feature/v3.1-upgrade`
3. **逐步开发**：按优先级实施
4. **持续测试**：确保不影响现有功能
5. **文档同步**：更新所有相关文档

准备好开始了吗？我们从 Phase 1 开始！

