"""
API增强功能
支持流式工具调用状态、会话管理优化等
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v2", tags=["Enhanced API"])


# ==================== 数据模型 ====================

class ToolCallStatus(BaseModel):
    """工具调用状态"""
    tool_name: str
    status: str  # running, success, error
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime
    execution_time: Optional[float] = None


class StreamChatMessage(BaseModel):
    """流式聊天消息"""
    session_id: str
    message: str
    provider: str = "siliconflow"
    model_name: Optional[str] = None
    memory: bool = True
    stream_tool_calls: bool = True  # 是否流式返回工具调用状态


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    title: str
    message_count: int
    last_message: str
    created_at: datetime
    last_active: datetime
    is_active: bool


class SessionUpdateRequest(BaseModel):
    """会话更新请求"""
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ==================== 会话管理增强 ====================

# 会话存储（应该用数据库，这里简化为内存）
sessions_store: Dict[str, SessionInfo] = {}


@router.post("/chat/sessions/{session_id}/update")
async def update_session(session_id: str, update: SessionUpdateRequest):
    """
    更新会话信息
    
    支持：
    - 修改会话标题
    - 添加元数据
    """
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions_store[session_id]
    
    if update.title:
        session.title = update.title
        logger.info(f"📝 更新会话标题: {session_id} -> {update.title}")
    
    if update.metadata:
        # 这里可以添加元数据存储逻辑
        logger.info(f"📋 更新会话元数据: {session_id}")
    
    session.last_active = datetime.now()
    
    return {
        "success": True,
        "session": session
    }


@router.get("/chat/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 50, offset: int = 0):
    """
    获取会话历史消息
    
    Args:
        session_id: 会话ID
        limit: 返回消息数量
        offset: 偏移量
    """
    # 这里应该从数据库读取，现在返回模拟数据
    return {
        "success": True,
        "session_id": session_id,
        "messages": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


# ==================== 流式聊天增强 ====================

async def stream_agent_response(
    agent: Any,
    message: str,
    session_id: str,
    stream_tool_calls: bool = True
) -> AsyncGenerator[str, None]:
    """
    流式返回Agent响应
    
    发送格式：
    - data: {type: "tool_call", data: {...}}
    - data: {type: "thought", data: "..."}
    - data: {type: "response", data: "..."}
    - data: {type: "done"}
    """
    try:
        # 发送开始信号
        yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
        
        # 模拟工具调用（实际应该从agent获取）
        if stream_tool_calls and ("crew" in message.lower() or "crewai" in message.lower()):
            # 发送工具调用状态
            tool_call = {
                "type": "tool_call",
                "data": {
                    "tool_name": "CrewAI Runtime",
                    "status": "running",
                    "input_data": {"task": message},
                    "timestamp": datetime.now().isoformat()
                }
            }
            yield f"data: {json.dumps(tool_call)}\n\n"
            
            # 模拟工具执行
            await asyncio.sleep(0.5)
            
            # 发送工具完成状态
            tool_complete = {
                "type": "tool_call",
                "data": {
                    "tool_name": "CrewAI Runtime",
                    "status": "success",
                    "output_data": "CrewAI团队分析完成",
                    "execution_time": 0.5,
                    "timestamp": datetime.now().isoformat()
                }
            }
            yield f"data: {json.dumps(tool_complete)}\n\n"
        
        # 执行Agent
        response = agent.run(message)
        
        # 确保response是字符串
        if isinstance(response, dict):
            response_text = response.get('response', str(response))
        else:
            response_text = str(response)
        
        # 分块发送响应（模拟流式输出）
        words = response_text.split()
        current_chunk = ""
        
        for word in words:
            current_chunk += word + " "
            if len(current_chunk) > 50:  # 每50个字符发送一次
                yield f"data: {json.dumps({'type': 'response', 'data': current_chunk})}\n\n"
                current_chunk = ""
                await asyncio.sleep(0.05)  # 模拟延迟
        
        # 发送剩余内容
        if current_chunk:
            yield f"data: {json.dumps({'type': 'response', 'data': current_chunk})}\n\n"
        
        # 发送完成信号
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        logger.error(f"❌ 流式响应错误: {e}")
        error_data = {
            "type": "error",
            "data": str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/chat/stream")
async def stream_chat(request: StreamChatMessage, agent_instances: Dict = None):
    """
    流式聊天接口
    
    使用 Server-Sent Events (SSE) 实时推送：
    - 工具调用状态
    - Agent思考过程
    - 最终响应
    """
    if agent_instances is None:
        raise HTTPException(status_code=500, detail="Agent instances not available")
    
    session_id = request.session_id
    
    # 获取或创建agent
    if session_id not in agent_instances:
        from src.agents.unified.unified_agent import UnifiedAgent
        
        logger.info(f"📝 创建新的 Agent 会话: {session_id}")
        agent = UnifiedAgent(
            provider=request.provider,
            model_name=request.model_name,
            memory=request.memory,
            session_id=session_id,
            streaming_style="none"
        )
        agent_instances[session_id] = agent
    else:
        agent = agent_instances[session_id]
    
    # 返回流式响应
    return StreamingResponse(
        stream_agent_response(
            agent,
            request.message,
            session_id,
            request.stream_tool_calls
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx优化
        }
    )


# ==================== 工具调用统计 ====================

class ToolCallStats(BaseModel):
    """工具调用统计"""
    tool_name: str
    total_calls: int
    success_count: int
    error_count: int
    avg_execution_time: float
    last_called: datetime


# 工具调用统计存储
tool_stats: Dict[str, ToolCallStats] = {}


@router.get("/tools/stats")
async def get_tool_stats():
    """
    获取工具调用统计
    """
    return {
        "success": True,
        "stats": list(tool_stats.values())
    }


@router.get("/tools/stats/{tool_name}")
async def get_tool_stat(tool_name: str):
    """
    获取指定工具的统计
    """
    if tool_name not in tool_stats:
        return {
            "success": False,
            "error": "Tool not found"
        }
    
    return {
        "success": True,
        "stat": tool_stats[tool_name]
    }


def record_tool_call(tool_name: str, execution_time: float, success: bool):
    """
    记录工具调用
    """
    if tool_name not in tool_stats:
        tool_stats[tool_name] = ToolCallStats(
            tool_name=tool_name,
            total_calls=0,
            success_count=0,
            error_count=0,
            avg_execution_time=0.0,
            last_called=datetime.now()
        )
    
    stat = tool_stats[tool_name]
    stat.total_calls += 1
    
    if success:
        stat.success_count += 1
    else:
        stat.error_count += 1
    
    # 更新平均执行时间
    stat.avg_execution_time = (
        (stat.avg_execution_time * (stat.total_calls - 1) + execution_time) 
        / stat.total_calls
    )
    
    stat.last_called = datetime.now()


# ==================== 导出路由 ====================

def get_enhanced_router():
    """获取增强路由器"""
    return router

