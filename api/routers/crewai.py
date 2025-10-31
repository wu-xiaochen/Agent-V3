"""
CrewAI API路由
提供Crew配置的CRUD操作和执行功能
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import os
import asyncio
from datetime import datetime
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.interfaces.crewai_runtime import CrewAIRuntime

router = APIRouter(prefix="/api/crewai", tags=["crewai"])

# 数据模型
class AgentConfig(BaseModel):
    id: str
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = []
    llm: Optional[str] = None
    maxIter: Optional[int] = 20
    maxRpm: Optional[int] = 10
    verbose: Optional[bool] = False

class TaskConfig(BaseModel):
    id: str
    description: str
    expectedOutput: str
    agent: str
    dependencies: List[str] = []
    context: Optional[List[str]] = []
    tools: Optional[List[str]] = []
    async_execution: Optional[bool] = False

class CrewConfig(BaseModel):
    id: str
    name: str
    description: str
    agents: List[AgentConfig]
    tasks: List[TaskConfig]
    process: str = "sequential"
    verbose: Optional[bool] = False
    memory: Optional[bool] = False
    cache: Optional[bool] = False
    maxRpm: Optional[int] = None
    createdAt: str
    updatedAt: str

class CrewExecutionRequest(BaseModel):
    inputs: Dict[str, Any] = {}
    files: Optional[List[str]] = []  # 文件ID列表

# 简单的文件存储（后续可替换为数据库）
CREWS_DIR = "data/crews"
os.makedirs(CREWS_DIR, exist_ok=True)

def _get_crew_file(crew_id: str) -> str:
    return os.path.join(CREWS_DIR, f"{crew_id}.json")

def _load_crew(crew_id: str) -> Optional[dict]:
    file_path = _get_crew_file(crew_id)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def _save_crew(crew: dict):
    file_path = _get_crew_file(crew["id"])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(crew, f, indent=2, ensure_ascii=False)

# API端点

@router.post("/crews")
async def create_crew(crew: CrewConfig):
    """创建新的Crew配置"""
    try:
        crew_dict = crew.model_dump()
        crew_dict["createdAt"] = datetime.now().isoformat()
        crew_dict["updatedAt"] = datetime.now().isoformat()
        
        _save_crew(crew_dict)
        
        return {
            "success": True,
            "crew_id": crew.id,
            "message": "Crew created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create crew: {str(e)}")

@router.get("/crews")
async def list_crews():
    """获取所有Crew列表"""
    try:
        crews = []
        if os.path.exists(CREWS_DIR):
            for filename in os.listdir(CREWS_DIR):
                if filename.endswith(".json"):
                    with open(os.path.join(CREWS_DIR, filename), "r", encoding="utf-8") as f:
                        crew = json.load(f)
                        # 只返回基本信息
                        crews.append({
                            "id": crew["id"],
                            "name": crew["name"],
                            "description": crew["description"],
                            "agentCount": len(crew.get("agents", [])),
                            "taskCount": len(crew.get("tasks", [])),
                            "createdAt": crew.get("createdAt"),
                            "updatedAt": crew.get("updatedAt")
                        })
        
        return {
            "success": True,
            "crews": crews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list crews: {str(e)}")

@router.get("/crews/{crew_id}")
async def get_crew(crew_id: str):
    """获取Crew详情"""
    crew = _load_crew(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    return {
        "success": True,
        "crew": crew
    }

@router.put("/crews/{crew_id}")
async def update_crew(crew_id: str, crew: CrewConfig):
    """更新Crew配置"""
    existing_crew = _load_crew(crew_id)
    if not existing_crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        crew_dict = crew.model_dump()
        crew_dict["createdAt"] = existing_crew.get("createdAt", datetime.now().isoformat())
        crew_dict["updatedAt"] = datetime.now().isoformat()
        
        _save_crew(crew_dict)
        
        return {
            "success": True,
            "message": "Crew updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update crew: {str(e)}")

@router.delete("/crews/{crew_id}")
async def delete_crew(crew_id: str):
    """删除Crew"""
    file_path = _get_crew_file(crew_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        os.remove(file_path)
        return {
            "success": True,
            "message": "Crew deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete crew: {str(e)}")

@router.post("/crews/{crew_id}/execute")
async def execute_crew(crew_id: str, request: CrewExecutionRequest):
    """执行Crew（同步版本，保留向后兼容）"""
    crew = _load_crew(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        # 使用流式执行端点
        execution_id = f"exec_{crew_id}_{datetime.now().timestamp()}"
        runtime = CrewAIRuntime()
        
        # 转换配置格式
        runtime.load_config_from_dict(crew)
        if not runtime.create_crew():
            raise HTTPException(status_code=500, detail="Failed to create crew")
        
        # 获取查询输入
        query = request.inputs.get("query", "执行任务")
        
        # 执行（同步方式）
        result = runtime.run_crew(query=query, save_result=True)
        
        return {
            "success": True,
            "execution_id": execution_id,
            "result": str(result) if result else None,
            "message": "Crew execution completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute crew: {str(e)}")


async def _stream_crew_execution(crew_id: str, request: CrewExecutionRequest) -> AsyncGenerator[str, None]:
    """
    流式执行CrewAI团队，发送SSE事件
    
    Args:
        crew_id: Crew配置ID
        request: 执行请求（包含inputs和files）
        
    Yields:
        SSE格式的JSON事件
    """
    execution_id = f"exec_{crew_id}_{int(datetime.now().timestamp() * 1000)}"
    start_time = datetime.now()
    
    try:
        # 加载Crew配置
        crew = _load_crew(crew_id)
        if not crew:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Crew not found', 'timestamp': datetime.now().isoformat()})}\n\n"
            return
        
        crew_name = crew.get("name", crew_id)
        
        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'execution_id': execution_id, 'crew_name': crew_name, 'crew_id': crew_id, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 发送状态：加载配置
        yield f"data: {json.dumps({'type': 'status', 'message': 'Loading CrewAI configuration...', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 初始化Runtime
        runtime = CrewAIRuntime()
        runtime.load_config_from_dict(crew)
        
        # 发送状态：创建Agents
        agents = crew.get("agents", [])
        total_agents = len(agents)
        
        yield f"data: {json.dumps({'type': 'progress', 'percentage': 10, 'step': 'agents', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        for idx, agent in enumerate(agents):
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent.get('name', agent.get('role', 'Unknown')), 'index': idx + 1, 'total': total_agents, 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)  # 小延迟以展示进度
        
        # 发送状态：创建Tasks
        tasks = crew.get("tasks", [])
        total_tasks = len(tasks)
        
        yield f"data: {json.dumps({'type': 'progress', 'percentage': 30, 'step': 'tasks', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        for idx, task in enumerate(tasks):
            yield f"data: {json.dumps({'type': 'task_start', 'task': task.get('description', 'Unknown')[:50], 'index': idx + 1, 'total': total_tasks, 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
        
        # 创建Crew
        yield f"data: {json.dumps({'type': 'status', 'message': 'Creating CrewAI team...', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        if not runtime.create_crew():
            yield f"data: {json.dumps({'type': 'error', 'error': 'Failed to create crew', 'timestamp': datetime.now().isoformat()})}\n\n"
            return
        
        yield f"data: {json.dumps({'type': 'progress', 'percentage': 50, 'step': 'crew_created', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 获取查询输入
        query = request.inputs.get("query", "执行任务")
        
        # 发送执行开始事件
        yield f"data: {json.dumps({'type': 'execution_start', 'query': query, 'total_tasks': total_tasks, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        yield f"data: {json.dumps({'type': 'progress', 'percentage': 60, 'step': 'executing', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 在后台线程中执行（因为CrewAI的kickoff可能是同步的）
        loop = asyncio.get_event_loop()
        
        def run_crew_sync():
            """在后台线程中同步执行CrewAI"""
            try:
                inputs = {"query": query}
                result = runtime.run_crew(query=query, save_result=True)
                return result
            except Exception as e:
                return {"error": str(e)}
        
        # 执行并等待结果
        result = await loop.run_in_executor(None, run_crew_sync)
        
        # 计算执行时间
        duration = (datetime.now() - start_time).total_seconds()
        
        yield f"data: {json.dumps({'type': 'progress', 'percentage': 90, 'step': 'processing_result', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 检查是否有错误
        if isinstance(result, dict) and "error" in result:
            yield f"data: {json.dumps({'type': 'error', 'error': result['error'], 'timestamp': datetime.now().isoformat()})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'success': False, 'timestamp': datetime.now().isoformat()})}\n\n"
            return
        
        # 发送结果
        result_str = str(result) if result else "执行完成，但未返回结果"
        yield f"data: {json.dumps({'type': 'result', 'output': result_str, 'duration': duration, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        yield f"data: {json.dumps({'type': 'progress', 'percentage': 100, 'step': 'complete', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 发送完成事件
        yield f"data: {json.dumps({'type': 'done', 'success': True, 'execution_id': execution_id, 'duration': duration, 'timestamp': datetime.now().isoformat()})}\n\n"
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        yield f"data: {json.dumps({'type': 'error', 'error': error_msg, 'trace': error_trace, 'timestamp': datetime.now().isoformat()})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'success': False, 'timestamp': datetime.now().isoformat()})}\n\n"


@router.post("/crews/{crew_id}/execute/stream")
async def execute_crew_stream(crew_id: str, request: CrewExecutionRequest):
    """
    流式执行Crew（Server-Sent Events）
    返回实时执行状态和结果
    """
    return StreamingResponse(
        _stream_crew_execution(crew_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/generate")
async def generate_crew(prompt: str, session_id: str):
    """AI生成Crew配置"""
    try:
        # TODO: 使用LLM生成Crew配置
        # 这里需要调用LLM分析prompt并生成配置
        
        return {
            "success": True,
            "crew_id": f"generated_{datetime.now().timestamp()}",
            "message": "Crew generation (implementation pending)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate crew: {str(e)}")

