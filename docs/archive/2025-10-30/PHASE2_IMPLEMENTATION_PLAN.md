# Phase 2 功能完善 - 实施计划

> **创建时间**: 2025-10-30  
> **状态**: 🚀 进行中  
> **预计完成**: 2-3 天

---

## 📋 Phase 2 目标概览

### 核心任务 (P0)
1. ✅ 会话滚动修复 (Phase 1 完成)
2. ✅ 停止功能 (Phase 1 完成)
3. ✅ 会话保存 (Phase 1 完成)
4. ✅ 文档上传解析 (Phase 1 完成)
5. 🔄 **工具调用真实数据集成** (当前任务)
6. 🔄 **CrewAI 后端集成**
7. 🔄 **知识库功能实现**

---

## 🎯 Task 1: 工具调用真实数据集成

### 问题分析
**当前状态**:
- ❌ 前端工具调用使用硬编码模拟数据
- ❌ 后端有 `record_tool_call` 但未被调用
- ❌ Agent 工具执行没有状态回调
- ❌ 工具调用历史无法持久化

**目标状态**:
- ✅ Agent 执行工具时实时推送状态
- ✅ 前端显示真实的工具调用信息
- ✅ 工具调用历史可查询
- ✅ 支持工具性能统计

### 实施步骤

#### Step 1.1: 增强 UnifiedAgent 工具调用回调

**文件**: `src/agents/unified/unified_agent.py`

**修改点**:
```python
1. 添加工具调用回调机制
2. 在工具执行前后触发回调
3. 记录工具名称、输入、输出、执行时间、状态
4. 支持异步回调
```

**代码结构**:
```python
class UnifiedAgent:
    def __init__(self, ..., tool_callback=None):
        self.tool_callback = tool_callback
    
    def _wrap_tool_with_callback(self, tool):
        """包装工具以支持回调"""
        original_run = tool._run
        
        def wrapped_run(*args, **kwargs):
            # 发送开始状态
            if self.tool_callback:
                self.tool_callback({
                    "tool": tool.name,
                    "status": "running",
                    "input": kwargs,
                    "timestamp": datetime.now()
                })
            
            start_time = time.time()
            try:
                result = original_run(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 发送成功状态
                if self.tool_callback:
                    self.tool_callback({
                        "tool": tool.name,
                        "status": "success",
                        "output": result,
                        "execution_time": execution_time,
                        "timestamp": datetime.now()
                    })
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                # 发送错误状态
                if self.tool_callback:
                    self.tool_callback({
                        "tool": tool.name,
                        "status": "error",
                        "error": str(e),
                        "execution_time": execution_time,
                        "timestamp": datetime.now()
                    })
                
                raise
        
        tool._run = wrapped_run
        return tool
```

#### Step 1.2: 后端 API 支持工具调用记录

**文件**: `api_server.py`

**修改点**:
```python
1. 为每个会话维护工具调用队列
2. 创建工具调用回调函数
3. 传递回调给 UnifiedAgent
4. 提供 API 获取会话的工具调用记录
```

**新增 API**:
```python
# 全局工具调用存储 (session_id -> [tool_calls])
session_tool_calls: Dict[str, List[Dict]] = {}

@app.get("/api/tools/history/{session_id}")
async def get_tool_call_history(session_id: str):
    """获取会话的工具调用历史"""
    return {
        "success": True,
        "session_id": session_id,
        "tool_calls": session_tool_calls.get(session_id, [])
    }

@app.post("/api/chat/message")
async def chat_message(request: ChatMessage):
    # ... 现有代码 ...
    
    # 创建工具调用回调
    def tool_callback(call_info):
        if session_id not in session_tool_calls:
            session_tool_calls[session_id] = []
        
        session_tool_calls[session_id].append({
            **call_info,
            "timestamp": call_info["timestamp"].isoformat()
        })
        
        # 记录到统计
        if call_info["status"] in ["success", "error"]:
            record_tool_call(
                call_info["tool"],
                call_info.get("execution_time", 0),
                call_info["status"] == "success"
            )
    
    # 传递回调给 Agent
    agent = UnifiedAgent(..., tool_callback=tool_callback)
```

#### Step 1.3: 前端实时获取工具调用状态

**文件**: `frontend/lib/api.ts`

**新增方法**:
```typescript
// 获取工具调用历史
async getToolCallHistory(sessionId: string): Promise<{
  success: boolean
  session_id: string
  tool_calls: ToolCall[]
}> {
  const response = await apiClient.get(`/api/tools/history/${sessionId}`)
  return response.data
}

// 轮询工具调用状态（用于非流式场景）
async pollToolCallStatus(
  sessionId: string,
  interval: number = 500
): Promise<EventSource> {
  // 实现轮询逻辑
}
```

**文件**: `frontend/components/chat-interface.tsx`

**修改点**:
```typescript
1. 移除硬编码的工具调用模拟
2. 在发送消息时启动工具调用状态轮询
3. 从 API 获取真实工具调用记录
4. 更新 toolCalls 状态
```

**修改代码**:
```typescript
const handleSend = async () => {
  // ... 现有代码 ...
  
  // 启动工具调用状态轮询
  const pollInterval = setInterval(async () => {
    try {
      const { api } = await import("@/lib/api")
      const history = await api.tools.getToolCallHistory(currentSession || "default")
      
      if (history.success) {
        setToolCalls(history.tool_calls)
        
        // 检查是否所有工具都已完成
        const allCompleted = history.tool_calls.every(
          call => call.status === "success" || call.status === "error"
        )
        
        if (allCompleted && !isThinking) {
          clearInterval(pollInterval)
        }
      }
    } catch (error) {
      console.error("Failed to poll tool calls:", error)
    }
  }, 500)
  
  // 在finally中清理轮询
  try {
    // ... API调用 ...
  } finally {
    clearInterval(pollInterval)
    setIsLoading(false)
  }
}
```

### 验收标准
- [ ] Agent 执行工具时能看到实时状态更新
- [ ] 工具调用历史可以通过 API 查询
- [ ] 前端正确显示工具执行状态（运行中/成功/失败）
- [ ] 工具性能统计准确记录
- [ ] 多工具调用正确展示

---

## 🎯 Task 2: CrewAI 后端集成

### 问题分析
**当前状态**:
- ❌ 前端 CrewAI 可视化器使用模拟数据
- ❌ Agent 配置无法保存到后端
- ❌ CrewAI 任务无法真实执行
- ❌ 执行日志是模拟的

**目标状态**:
- ✅ CrewAI 配置持久化存储
- ✅ Agent 配置 CRUD 操作
- ✅ 真实执行 CrewAI 任务
- ✅ 实时显示执行日志

### 实施步骤

#### Step 2.1: 后端 CrewAI 配置管理 API

**新建文件**: `src/services/crewai_service.py`

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import os
from datetime import datetime

class AgentConfig(BaseModel):
    """Agent配置"""
    id: str
    role: str
    goal: str
    tools: List[str]
    backstory: Optional[str] = None

class CrewConfig(BaseModel):
    """Crew配置"""
    id: str
    name: str
    description: str
    agents: List[AgentConfig]
    tasks: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class CrewAIService:
    """CrewAI 服务"""
    
    def __init__(self, config_dir: str = "config/crewai"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
    
    def list_crews(self) -> List[CrewConfig]:
        """列出所有Crew配置"""
        pass
    
    def get_crew(self, crew_id: str) -> Optional[CrewConfig]:
        """获取指定Crew配置"""
        pass
    
    def create_crew(self, config: CrewConfig) -> CrewConfig:
        """创建Crew配置"""
        pass
    
    def update_crew(self, crew_id: str, config: CrewConfig) -> CrewConfig:
        """更新Crew配置"""
        pass
    
    def delete_crew(self, crew_id: str) -> bool:
        """删除Crew配置"""
        pass
    
    def execute_crew(
        self,
        crew_id: str,
        task_description: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行Crew任务"""
        pass
```

**新建文件**: `api_crewai.py`

```python
from fastapi import APIRouter, HTTPException
from src.services.crewai_service import CrewAIService, CrewConfig, AgentConfig

router = APIRouter(prefix="/api/crewai", tags=["CrewAI"])
crewai_service = CrewAIService()

@router.get("/crews")
async def list_crews():
    """列出所有Crew"""
    crews = crewai_service.list_crews()
    return {"success": True, "crews": crews}

@router.get("/crews/{crew_id}")
async def get_crew(crew_id: str):
    """获取Crew详情"""
    crew = crewai_service.get_crew(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return {"success": True, "crew": crew}

@router.post("/crews")
async def create_crew(config: CrewConfig):
    """创建Crew"""
    crew = crewai_service.create_crew(config)
    return {"success": True, "crew": crew}

@router.put("/crews/{crew_id}")
async def update_crew(crew_id: str, config: CrewConfig):
    """更新Crew"""
    crew = crewai_service.update_crew(crew_id, config)
    return {"success": True, "crew": crew}

@router.delete("/crews/{crew_id}")
async def delete_crew(crew_id: str):
    """删除Crew"""
    success = crewai_service.delete_crew(crew_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crew not found")
    return {"success": True, "message": "Crew deleted"}

@router.post("/crews/{crew_id}/execute")
async def execute_crew(
    crew_id: str,
    task_description: str,
    parameters: Dict[str, Any] = {}
):
    """执行Crew任务"""
    result = crewai_service.execute_crew(crew_id, task_description, parameters)
    return {"success": True, "result": result}
```

**修改**: `api_server.py`

```python
from api_crewai import router as crewai_router

app.include_router(crewai_router)
```

#### Step 2.2: 前端 CrewAI API 集成

**文件**: `frontend/lib/api.ts`

**新增**:
```typescript
export const crewaiAPI = {
  async listCrews(): Promise<{ success: boolean; crews: CrewConfig[] }> {
    const response = await apiClient.get("/api/crewai/crews")
    return response.data
  },

  async getCrew(crewId: string): Promise<{ success: boolean; crew: CrewConfig }> {
    const response = await apiClient.get(`/api/crewai/crews/${crewId}`)
    return response.data
  },

  async createCrew(config: CrewConfig): Promise<{ success: boolean; crew: CrewConfig }> {
    const response = await apiClient.post("/api/crewai/crews", config)
    return response.data
  },

  async updateCrew(crewId: string, config: CrewConfig): Promise<{ success: boolean; crew: CrewConfig }> {
    const response = await apiClient.put(`/api/crewai/crews/${crewId}`, config)
    return response.data
  },

  async deleteCrew(crewId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/api/crewai/crews/${crewId}`)
    return response.data
  },

  async executeCrew(
    crewId: string,
    taskDescription: string,
    parameters: Record<string, any> = {}
  ): Promise<{ success: boolean; result: any }> {
    const response = await apiClient.post(`/api/crewai/crews/${crewId}/execute`, {
      task_description: taskDescription,
      parameters,
    })
    return response.data
  },
}
```

#### Step 2.3: 前端 CrewAI 可视化器连接真实 API

**文件**: `frontend/components/crewai-visualizer.tsx`

**修改点**:
```typescript
1. 移除模拟数据
2. 从 API 加载 Crew 配置
3. Agent CRUD 操作调用真实 API
4. 执行任务调用真实 API
5. 显示真实执行日志
```

### 验收标准
- [ ] CrewAI 配置可以保存到后端
- [ ] Agent 可以添加/编辑/删除
- [ ] CrewAI 任务可以真实执行
- [ ] 执行日志实时显示
- [ ] 支持用户输入参数

---

## 🎯 Task 3: 知识库功能实现

### 问题分析
**当前状态**:
- ✅ 已有 `KnowledgeBaseManager` 和 `VectorStoreManager`
- ❌ ChromaDB 未初始化
- ❌ 文档上传后未自动索引
- ❌ 前端 UI 使用模拟数据

**目标状态**:
- ✅ ChromaDB 正确初始化和配置
- ✅ 文档上传自动索引到向量数据库
- ✅ 支持语义搜索
- ✅ 前端完整的知识库管理界面

### 实施步骤

#### Step 3.1: 初始化 ChromaDB

**新建文件**: `src/infrastructure/knowledge/chroma_setup.py`

```python
import chromadb
from chromadb.config import Settings
import os

def initialize_chroma():
    """初始化ChromaDB"""
    chroma_path = os.path.join(os.getcwd(), "data", "chroma")
    os.makedirs(chroma_path, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    return client

# 全局实例
chroma_client = initialize_chroma()
```

#### Step 3.2: 知识库 CRUD API

**新建文件**: `api_knowledge.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.infrastructure.knowledge.knowledge_base import KnowledgeBaseManager
from src.infrastructure.knowledge.vector_store import VectorStoreManager
from src.infrastructure.multimodal.document_parser import parse_document

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

kb_manager = KnowledgeBaseManager()
vector_store = VectorStoreManager()

@router.post("/bases")
async def create_knowledge_base(name: str, description: str = ""):
    """创建知识库"""
    kb = kb_manager.create_knowledge_base(name, description)
    return {"success": True, "knowledge_base": kb}

@router.get("/bases")
async def list_knowledge_bases():
    """列出所有知识库"""
    bases = kb_manager.list_knowledge_bases()
    return {"success": True, "knowledge_bases": bases}

@router.post("/bases/{kb_id}/documents")
async def upload_document(kb_id: str, file: UploadFile = File(...)):
    """上传文档到知识库"""
    # 保存文件
    file_path = f"data/knowledge/{kb_id}/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 解析文档
    parsed = parse_document(file_path)
    
    if not parsed.get("success"):
        raise HTTPException(status_code=400, detail="Failed to parse document")
    
    # 添加到知识库
    doc = kb_manager.add_document(
        kb_id=kb_id,
        title=file.filename,
        content=parsed["full_text"],
        metadata={"type": parsed["type"], "path": file_path}
    )
    
    # 索引到向量数据库
    vector_store.add_documents(kb_id, [doc])
    
    return {"success": True, "document": doc}

@router.post("/bases/{kb_id}/search")
async def search_knowledge_base(kb_id: str, query: str, top_k: int = 5):
    """语义搜索"""
    results = vector_store.search(kb_id, query, top_k)
    return {"success": True, "results": results}
```

#### Step 3.3: 前端知识库管理界面

**文件**: `frontend/components/knowledge-browser.tsx`

**修改点**:
```typescript
1. 移除模拟数据
2. 从 API 加载知识库列表
3. 实现创建知识库
4. 实现文档上传
5. 实现搜索功能
```

### 验收标准
- [ ] ChromaDB 正确初始化
- [ ] 可以创建/列出知识库
- [ ] 文档上传自动解析和索引
- [ ] 语义搜索返回正确结果
- [ ] 前端界面完整可用

---

## 📊 进度跟踪

### Task 1: 工具调用真实数据 ✅
- [x] Step 1.1: UnifiedAgent 回调机制
- [x] Step 1.2: 后端 API 集成
- [x] Step 1.3: 前端实时更新
- [ ] 测试验证

### Task 2: CrewAI 后端集成 ⏳
- [ ] Step 2.1: 后端服务和 API
- [ ] Step 2.2: 前端 API 客户端
- [ ] Step 2.3: 前端 UI 集成
- [ ] 测试验证

### Task 3: 知识库功能 ⏳
- [ ] Step 3.1: ChromaDB 初始化
- [ ] Step 3.2: 后端 API
- [ ] Step 3.3: 前端 UI
- [ ] 测试验证

---

## 🎯 今日目标 (Day 1)

1. ✅ 完成 Task 1: 工具调用真实数据集成
2. 🔄 开始 Task 2: CrewAI 后端集成

---

## 📝 注意事项

1. **测试驱动**: 每个功能完成后立即测试
2. **增量提交**: 每个小步骤完成后提交 Git
3. **文档同步**: 更新相关文档
4. **错误处理**: 完善的错误提示和日志
5. **性能考虑**: 注意 API 调用频率和缓存策略

---

**下一步**: 立即开始 Task 1.1 - UnifiedAgent 工具调用回调机制

