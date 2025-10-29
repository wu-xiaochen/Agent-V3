"""
Agent-V3 API Server
提供 RESTful API 和 WebSocket 接口
"""

import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import uvicorn
import asyncio
import json

# 导入项目模块
from src.agents.unified.unified_agent import UnifiedAgent
from src.interfaces.file_manager import get_file_manager
from src.infrastructure.tools import get_tool_registry
from src.config.config_loader import config_loader
from api_enhancements import get_enhanced_router, record_tool_call

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Agent-V3 API",
    description="智能 Agent API 服务，支持对话、工具调用、知识库、文件处理等功能",
    version="3.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
outputs_dir = Path("outputs")
outputs_dir.mkdir(exist_ok=True)
# app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# 注册增强路由
enhanced_router = get_enhanced_router()
app.include_router(enhanced_router)

# 全局变量
file_manager = None
agent_instances = {}  # session_id -> agent
websocket_connections = {}  # session_id -> websocket


# ==================== Pydantic 模型 ====================

class ChatMessage(BaseModel):
    """聊天消息"""
    session_id: str
    message: str
    provider: Optional[str] = "siliconflow"
    model_name: Optional[str] = None
    memory: bool = True
    streaming: bool = False


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    session_id: str
    response: str
    metadata: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    file_id: str
    filename: str
    download_url: str
    size: int
    message: str


# ==================== 启动和关闭事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global file_manager
    
    logger.info("🚀 Agent-V3 API 服务启动中...")
    
    # 初始化文件管理器
    file_manager = get_file_manager()
    logger.info("✅ 文件管理器已初始化")
    
    # 初始化工具注册器
    registry = get_tool_registry()
    registry.load_from_config()
    logger.info("✅ 工具注册器已初始化")
    
    # 清理过期文件
    cleaned_count = file_manager.cleanup_expired_files()
    if cleaned_count > 0:
        logger.info(f"🗑️  已清理 {cleaned_count} 个过期文件")
    
    logger.info("✅ Agent-V3 API 服务已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("🛑 Agent-V3 API 服务关闭中...")
    
    # 关闭所有 WebSocket 连接
    for session_id, ws in websocket_connections.items():
        try:
            await ws.close()
        except Exception as e:
            logger.error(f"❌ 关闭 WebSocket 失败: {e}")
    
    logger.info("✅ Agent-V3 API 服务已关闭")


# ==================== 基础接口 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Agent-V3 API",
        "version": "3.1.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "chat": "/api/chat/message",
            "files": "/api/files/*",
            "knowledge": "/api/knowledge/*",
            "tools": "/api/tools/*"
        }
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "file_manager": "ok" if file_manager else "not_initialized",
        "active_sessions": len(agent_instances),
        "active_websockets": len(websocket_connections)
    }


# ==================== 聊天接口 ====================

@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatMessage):
    """
    发送聊天消息
    
    Args:
        request: 聊天请求
        
    Returns:
        聊天响应
    """
    try:
        session_id = request.session_id
        
        # 获取或创建 agent
        if session_id not in agent_instances:
            logger.info(f"📝 创建新的 Agent 会话: {session_id}")
            agent = UnifiedAgent(
                provider=request.provider,
                model_name=request.model_name,
                memory=request.memory,
                session_id=session_id,
                streaming_style="none"  # API 模式不使用流式输出
            )
            agent_instances[session_id] = agent
        else:
            agent = agent_instances[session_id]
        
        # 处理消息
        logger.info(f"💬 处理消息: {request.message[:50]}...")
        
        # 记录工具调用开始时间
        import time
        start_time = time.time()
        
        response = agent.run(request.message)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        logger.info(f"⏱️  执行时间: {execution_time:.2f}s")
        
        # 确保 response 是字符串
        if isinstance(response, dict):
            # 如果是字典，提取 response 字段或转换为字符串
            response_text = response.get('response', str(response))
        else:
            response_text = str(response)
        
        return ChatResponse(
            success=True,
            session_id=session_id,
            response=response_text,
            metadata={"provider": request.provider, "model": request.model_name}
        )
        
    except Exception as e:
        logger.error(f"❌ 处理聊天消息失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return ChatResponse(
            success=False,
            session_id=request.session_id,
            response=f"处理消息时出错: {str(e)}",
            metadata={"error": str(e)}
        )


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """
    获取聊天历史
    
    Args:
        session_id: 会话ID
        limit: 返回的最大消息数
        
    Returns:
        聊天历史
    """
    try:
        if session_id not in agent_instances:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        agent = agent_instances[session_id]
        
        # 获取历史记录
        if hasattr(agent.memory, "messages"):
            messages = agent.memory.messages[-limit:]
            return {
                "success": True,
                "session_id": session_id,
                "messages": [
                    {
                        "type": msg.type,
                        "content": msg.content,
                        "timestamp": getattr(msg, "timestamp", None)
                    }
                    for msg in messages
                ]
            }
        else:
            return {
                "success": True,
                "session_id": session_id,
                "messages": [],
                "note": "此会话未启用记忆功能"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取聊天历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/sessions")
async def list_sessions():
    """
    列出所有会话
    
    Returns:
        会话列表
    """
    try:
        sessions = []
        for session_id, agent in agent_instances.items():
            # 获取最后一条消息
            last_message = None
            message_count = 0
            
            if hasattr(agent.memory, "messages") and agent.memory.messages:
                messages = agent.memory.messages
                message_count = len(messages)
                # 获取最后一条用户消息
                for msg in reversed(messages):
                    if msg.type == "human":
                        last_message = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                        break
            
            sessions.append({
                "session_id": session_id,
                "message_count": message_count,
                "last_message": last_message or "新对话",
                "is_active": session_id in websocket_connections
            })
        
        return {
            "success": True,
            "count": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"❌ 列出会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        删除结果
    """
    try:
        if session_id not in agent_instances:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 删除 agent 实例
        del agent_instances[session_id]
        
        # 如果有 WebSocket 连接，也删除
        if session_id in websocket_connections:
            del websocket_connections[session_id]
        
        logger.info(f"🗑️ 已删除会话: {session_id}")
        
        return {
            "success": True,
            "message": f"会话 {session_id} 已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/sessions")
async def clear_all_sessions():
    """
    清空所有会话
    
    Returns:
        清空结果
    """
    try:
        count = len(agent_instances)
        agent_instances.clear()
        websocket_connections.clear()
        
        logger.info(f"🗑️ 已清空所有会话，共 {count} 个")
        
        return {
            "success": True,
            "message": f"已清空 {count} 个会话"
        }
        
    except Exception as e:
        logger.error(f"❌ 清空会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/chat/stream")
async def chat_stream(websocket: WebSocket):
    """
    WebSocket 流式聊天接口
    
    客户端发送格式:
    {
        "session_id": "xxx",
        "message": "用户消息",
        "provider": "siliconflow",
        "model_name": "qwen-max"
    }
    
    服务器响应格式:
    {
        "type": "token" | "complete" | "error",
        "content": "...",
        "metadata": {}
    }
    """
    await websocket.accept()
    session_id = None
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            session_id = request_data.get("session_id")
            message = request_data.get("message")
            provider = request_data.get("provider", "siliconflow")
            model_name = request_data.get("model_name")
            
            if not session_id or not message:
                await websocket.send_json({
                    "type": "error",
                    "content": "缺少 session_id 或 message 参数"
                })
                continue
            
            # 保存 WebSocket 连接
            websocket_connections[session_id] = websocket
            
            # 获取或创建 agent
            if session_id not in agent_instances:
                agent = UnifiedAgent(
                    provider=provider,
                    model_name=model_name,
                    memory=True,
                    session_id=session_id,
                    streaming_style="simple"
                )
                agent_instances[session_id] = agent
            else:
                agent = agent_instances[session_id]
            
            # 处理消息（流式输出会通过回调发送到客户端）
            try:
                response = agent.run(message)
                
                # 发送完成信号
                await websocket.send_json({
                    "type": "complete",
                    "content": response,
                    "metadata": {"session_id": session_id}
                })
                
            except Exception as e:
                logger.error(f"❌ 处理流式消息失败: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": f"处理消息时出错: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket 连接断开: {session_id}")
        if session_id in websocket_connections:
            del websocket_connections[session_id]
    except Exception as e:
        logger.error(f"❌ WebSocket 错误: {e}")
        if session_id in websocket_connections:
            del websocket_connections[session_id]


# ==================== 文件接口 ====================

@app.post("/api/files/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form("data"),
    tags: Optional[str] = Form(None)
):
    """
    上传文件
    
    Args:
        file: 上传的文件
        file_type: 文件类型 (image, data, temp)
        tags: 标签（逗号分隔）
        
    Returns:
        文件信息
    """
    try:
        # 读取文件内容
        content = await file.read()
        
        # 处理标签
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # 保存文件
        result = file_manager.save_binary_file(
            data=content,
            filename=file.filename,
            file_type=file_type,
            tags=tag_list
        )
        
        if result["success"]:
            return FileUploadResponse(
                success=True,
                file_id=result["file_id"],
                filename=result["filename"],
                download_url=result["download_url"],
                size=result["size"],
                message="文件上传成功"
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "文件上传失败"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/download/{file_id}")
async def download_file(file_id: str):
    """
    下载文件
    
    Args:
        file_id: 文件ID
        
    Returns:
        文件内容
    """
    try:
        file_info = file_manager.get_file(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        filepath = file_info["full_path"]
        filename = file_info["filename"]
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=file_info["mime_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 文件下载失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/list")
async def list_files(tags: Optional[str] = None, limit: int = 100):
    """
    列出文件
    
    Args:
        tags: 标签过滤（逗号分隔）
        limit: 最大返回数量
        
    Returns:
        文件列表
    """
    try:
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        files = file_manager.list_files(tags=tag_list, limit=limit)
        
        return {
            "success": True,
            "count": len(files),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"❌ 列出文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """
    删除文件
    
    Args:
        file_id: 文件ID
        
    Returns:
        删除结果
    """
    try:
        success = file_manager.delete_file(file_id)
        if success:
            return {"success": True, "message": "文件已删除"}
        else:
            raise HTTPException(status_code=404, detail="文件不存在或删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 工具接口 ====================

@app.get("/api/tools/list")
async def list_tools():
    """
    列出所有可用工具
    
    Returns:
        工具列表
    """
    try:
        registry = get_tool_registry()
        tools = registry.list_all_tools()
        
        return {
            "success": True,
            "count": len(tools),
            "tools": tools
        }
        
    except Exception as e:
        logger.error(f"❌ 列出工具失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 主入口 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent-V3 API Server")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

