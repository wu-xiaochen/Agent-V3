"""
CrewAI API路由
提供Crew配置的CRUD操作和执行功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

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
    """执行Crew"""
    crew = _load_crew(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        # TODO: 实现实际的CrewAI执行逻辑
        # 这里需要将配置转换为CrewAI对象并执行
        
        return {
            "success": True,
            "execution_id": f"exec_{crew_id}_{datetime.now().timestamp()}",
            "message": "Crew execution started (implementation pending)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute crew: {str(e)}")

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

