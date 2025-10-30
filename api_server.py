"""
Agent-V3 API Server
提供 RESTful API 和 WebSocket 接口
"""

import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict, Any
from pathlib import Path
import uvicorn
import asyncio
import json

# 导入项目模块 - 延迟导入 UnifiedAgent 以避免循环导入
# from src.agents.unified.unified_agent import UnifiedAgent  # 移至函数内部
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
session_tool_calls = {}  # 🆕 session_id -> [tool_calls] - 存储每个会话的工具调用历史
session_thinking_chains = {}  # 🆕 session_id -> [thinking_chain_steps] - 存储完整思维链


# ==================== Pydantic 模型 ====================

class FileAttachment(BaseModel):
    """文件附件"""
    id: str
    name: str
    type: str
    url: str
    size: int
    parsed_content: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    """聊天消息"""
    session_id: str
    message: str
    provider: Optional[str] = "siliconflow"
    model_name: Optional[str] = None
    memory: bool = True
    streaming: bool = False
    attachments: List[FileAttachment] = []  # ✅ 新增：支持附件


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
    parsed_content: Optional[Dict[str, Any]] = None  # 🆕 添加解析内容字段


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
        
        # 🆕 创建工具调用回调函数
        def tool_callback(call_info: Dict[str, Any]):
            """工具调用回调，记录工具执行状态"""
            # 初始化会话的工具调用列表
            if session_id not in session_tool_calls:
                session_tool_calls[session_id] = []
            
            # 转换datetime为字符串
            call_data = {**call_info}
            if 'timestamp' in call_data:
                call_data['timestamp'] = call_data['timestamp'].isoformat()
            
            # 添加到会话历史
            session_tool_calls[session_id].append(call_data)
            logger.info(f"🔧 工具调用记录: {call_data.get('tool')} - {call_data.get('status')}")
            
            # 🆕 同时添加到思维链（如果是完成状态）
            if call_info.get("status") in ["success", "error"]:
                # 初始化思维链
                if session_id not in session_thinking_chains:
                    session_thinking_chains[session_id] = []
                
                # 查找最新的action步骤号
                action_steps = [s for s in session_thinking_chains[session_id] if s.get("type") == "action"]
                step_number = action_steps[-1]["step"] if action_steps else 1
                
                # 添加observation
                observation_data = {
                    "type": "observation",
                    "step": step_number,
                    "content": call_info.get("output", call_info.get("error", "")),
                    "execution_time": call_info.get("execution_time", 0),
                    "status": call_info["status"],
                    "session_id": session_id,
                    "timestamp": call_data['timestamp']
                }
                
                if call_info.get("error"):
                    observation_data["error"] = call_info["error"]
                
                # 🔥 尝试解析output为JSON对象并添加到metadata
                output_str = call_info.get("output", "")
                if output_str and isinstance(output_str, str):
                    try:
                        import json
                        parsed_output = json.loads(output_str)
                        if isinstance(parsed_output, dict):
                            observation_data["metadata"] = {"observation": parsed_output}
                            logger.info("✅ 成功将observation对象添加到metadata")
                    except (json.JSONDecodeError, ValueError):
                        pass  # 不是JSON格式，保持原样
                
                session_thinking_chains[session_id].append(observation_data)
                logger.debug(f"🧠 添加observation到思维链: Step {step_number}")
            
            # 记录到统计（仅在完成时）
            if call_info.get("status") in ["success", "error"]:
                record_tool_call(
                    call_info["tool"],
                    call_info.get("execution_time", 0),
                    call_info["status"] == "success"
                )
        
        # 🆕 创建思维链更新回调函数
        def thinking_chain_callback(step_data: Dict[str, Any]):
            """思维链更新回调，记录完整的思考过程"""
            # 初始化会话的思维链列表
            if session_id not in session_thinking_chains:
                session_thinking_chains[session_id] = []
            
            # 添加到思维链历史
            session_thinking_chains[session_id].append(step_data)
            logger.debug(f"🧠 思维链记录: {step_data.get('type')} - Step {step_data.get('step', 0)}")
        
        # 获取或创建 agent
        if session_id not in agent_instances:
            # 🆕 延迟导入 UnifiedAgent 和 ThinkingChainHandler
            from src.agents.unified.unified_agent import UnifiedAgent
            from src.agents.shared.thinking_chain_handler import ThinkingChainHandler
            
            # 创建思维链处理器
            thinking_handler = ThinkingChainHandler(
                session_id=session_id,
                on_update=thinking_chain_callback
            )
            
            logger.info(f"📝 创建新的 Agent 会话: {session_id}")
            agent = UnifiedAgent(
                provider=request.provider,
                model_name=request.model_name,
                memory=request.memory,
                session_id=session_id,
                streaming_style="none",  # API 模式不使用流式输出
                tool_callback=tool_callback,  # 🆕 传递工具回调
                thinking_handler=thinking_handler  # 🆕 传递思维链处理器
            )
            agent_instances[session_id] = agent
        else:
            agent = agent_instances[session_id]
            # 🆕 更新已存在的 agent 的回调
            agent.tool_callback = tool_callback
            # 如果已有thinking_handler，更新它的回调
            if hasattr(agent, 'thinking_handler') and agent.thinking_handler:
                agent.thinking_handler.on_update = thinking_chain_callback
        
        # ✅ 修复：处理附件并构建增强的prompt
        enhanced_message = request.message
        
        if request.attachments:
            logger.info(f"📎 检测到 {len(request.attachments)} 个附件")
            
            # 将文档内容添加到消息中
            context_parts = [request.message]
            
            for attachment in request.attachments:
                if attachment.parsed_content:
                    doc_context = f"\n\n[文档: {attachment.name}]"
                    doc_context += f"\n文件类型: {attachment.parsed_content.get('type', 'unknown')}"
                    doc_context += f"\n\n内容摘要:\n{attachment.parsed_content.get('summary', '')}"
                    
                    # 获取完整文本（限制长度以避免上下文过长）
                    full_text = attachment.parsed_content.get('full_text', '')
                    if full_text:
                        # 限制文档内容长度为8000字符
                        doc_context += f"\n\n完整内容:\n{full_text[:8000]}"
                        if len(full_text) > 8000:
                            doc_context += "\n...(内容已截断)"
                    
                    context_parts.append(doc_context)
                    logger.info(f"📄 已添加文档上下文: {attachment.name} ({len(full_text)} 字符)")
            
            enhanced_message = "\n".join(context_parts)
            logger.info(f"✅ 增强消息长度: {len(enhanced_message)} 字符")
        
        # 处理消息
        logger.info(f"💬 处理消息: {request.message[:50]}...")
        
        # 记录工具调用开始时间
        import time
        start_time = time.time()
        
        response = agent.run(enhanced_message)  # ✅ 使用增强的消息
        
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


@app.get("/api/tools/history/{session_id}")
async def get_tool_call_history(session_id: str):
    """
    获取会话的工具调用历史
    
    Args:
        session_id: 会话ID
        
    Returns:
        工具调用历史列表
    """
    try:
        tool_calls = session_tool_calls.get(session_id, [])
        logger.info(f"📊 获取工具调用历史: {session_id} - {len(tool_calls)} 条记录")
        
        return {
            "success": True,
            "session_id": session_id,
            "tool_calls": tool_calls,
            "count": len(tool_calls)
        }
    except Exception as e:
        logger.error(f"❌ 获取工具调用历史失败: {e}")
        return {
            "success": False,
            "session_id": session_id,
            "tool_calls": [],
            "count": 0,
            "error": str(e)
        }


@app.delete("/api/tools/history/{session_id}")
async def clear_tool_call_history(session_id: str):
    """
    清空会话的工具调用历史
    
    Args:
        session_id: 会话ID
        
    Returns:
        成功消息
    """
    try:
        if session_id in session_tool_calls:
            count = len(session_tool_calls[session_id])
            session_tool_calls[session_id] = []
            logger.info(f"🗑️ 清空工具调用历史: {session_id} - {count} 条记录")
            return {
                "success": True,
                "session_id": session_id,
                "message": f"已清空 {count} 条工具调用记录"
            }
        else:
            return {
                "success": True,
                "session_id": session_id,
                "message": "没有需要清空的记录"
            }
    except Exception as e:
        logger.error(f"❌ 清空工具调用历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 🆕 思维链API ====================

@app.get("/api/thinking/history/{session_id}")
async def get_thinking_chain_history(session_id: str):
    """
    获取会话的完整思维链历史
    
    Args:
        session_id: 会话ID
        
    Returns:
        完整的思维链历史，包括：
        - thought: 思考过程
        - planning: 规划步骤
        - action: 工具调用
        - observation: 执行结果
        - final_thought: 最终分析
    """
    try:
        chain = session_thinking_chains.get(session_id, [])
        logger.info(f"🧠 获取思维链历史: {session_id} - {len(chain)} 个步骤")
        
        return {
            "success": True,
            "session_id": session_id,
            "thinking_chain": chain,
            "count": len(chain)
        }
    except Exception as e:
        logger.error(f"❌ 获取思维链历史失败: {e}")
        return {
            "success": False,
            "session_id": session_id,
            "thinking_chain": [],
            "count": 0,
            "error": str(e)
        }


@app.delete("/api/thinking/history/{session_id}")
async def clear_thinking_chain_history(session_id: str):
    """
    清空会话的思维链历史
    
    Args:
        session_id: 会话ID
        
    Returns:
        成功消息
    """
    try:
        if session_id in session_thinking_chains:
            count = len(session_thinking_chains[session_id])
            session_thinking_chains[session_id] = []
            logger.info(f"🗑️ 清空思维链历史: {session_id} - {count} 个步骤")
            return {
                "success": True,
                "session_id": session_id,
                "message": f"已清空 {count} 个思维链步骤"
            }
        else:
            return {
                "success": True,
                "session_id": session_id,
                "message": "没有需要清空的记录"
            }
    except Exception as e:
        logger.error(f"❌ 清空思维链历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 系统配置API ====================

from src.models.system_config import SystemConfig, SystemConfigUpdate, SystemConfigResponse
from src.services.system_config_service import SystemConfigService

# 创建系统配置服务实例
system_config_service = SystemConfigService()

# 🆕 知识库服务
from src.models.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    DocumentUploadRequest,
    SearchRequest
)
from src.services.knowledge_base_service import KnowledgeBaseService

knowledge_base_service = KnowledgeBaseService()


@app.get("/api/system/config", response_model=Dict[str, Any])
async def get_system_config():
    """
    获取系统配置（API Key脱敏）
    
    Returns:
        系统配置对象（API Key已脱敏）
    """
    try:
        config = system_config_service.get_config()
        response = SystemConfigResponse.from_system_config(config)
        
        return {
            "success": True,
            "config": response.model_dump(mode='json')
        }
    except Exception as e:
        logger.error(f"❌ 获取系统配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/system/config", response_model=Dict[str, Any])
async def update_system_config(update: Dict[str, Any]):
    """
    更新系统配置
    
    Args:
        update: 配置更新数据
        
    Returns:
        更新后的配置对象（API Key已脱敏）
    """
    try:
        # 创建更新对象
        config_update = SystemConfigUpdate(**update)
        
        # 更新配置
        updated_config = system_config_service.update_config(config_update)
        response = SystemConfigResponse.from_system_config(updated_config)
        
        logger.info(f"✅ 系统配置已更新: {update.keys()}")
        
        return {
            "success": True,
            "config": response.model_dump(mode='json'),
            "message": "配置已更新"
        }
    except ValidationError as e:
        logger.error(f"❌ 配置验证失败: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 更新系统配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/system/config/reset", response_model=Dict[str, Any])
async def reset_system_config():
    """
    重置系统配置为默认值
    
    Returns:
        默认配置对象（API Key已脱敏）
    """
    try:
        default_config = system_config_service.reset_to_default()
        response = SystemConfigResponse.from_system_config(default_config)
        
        logger.info("✅ 系统配置已重置为默认值")
        
        return {
            "success": True,
            "config": response.model_dump(mode='json'),
            "message": "配置已重置为默认值"
        }
    except Exception as e:
        logger.error(f"❌ 重置系统配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 工具列表API ====================

from src.infrastructure.tools.tool_registry import get_tool_registry, get_tool_factory


@app.get("/api/tools/available", response_model=Dict[str, Any])
async def get_available_tools():
    """
    获取所有可用工具列表（用于CrewAI工具选择）
    
    Returns:
        {
            "success": bool,
            "tools": [
                {
                    "name": str,
                    "display_name": str,
                    "type": str,  # builtin, mcp, api
                    "enabled": bool,
                    "description": str,
                    "parameters": dict  # 工具参数schema（可选）
                },
                ...
            ],
            "total": int,
            "groups": dict  # 工具组信息
        }
    """
    try:
        registry = get_tool_registry()
        
        # 确保工具已加载
        if not registry._tools:
            success = registry.load_from_config()
            if not success:
                logger.warning("⚠️  工具注册器加载失败，返回空列表")
                return {
                    "success": False,
                    "tools": [],
                    "total": 0,
                    "groups": {},
                    "message": "工具配置加载失败"
                }
        
        # 获取所有工具信息
        all_tools = []
        for name, tool_def in registry._tools.items():
            tool_info = {
                "name": name,
                "display_name": tool_def.display_name,
                "type": tool_def.type,
                "enabled": tool_def.enabled,
                "description": tool_def.description or f"{tool_def.display_name}工具",
                "module": tool_def.module,
            }
            
            # 添加参数信息（如果有）
            if tool_def.parameters:
                tool_info["parameters"] = tool_def.parameters
            
            # 添加配置信息（用于MCP等）
            if tool_def.config:
                tool_info["config"] = tool_def.config
            
            all_tools.append(tool_info)
        
        # 获取工具组信息
        tool_groups = registry._tool_groups
        
        logger.info(f"✅ 返回 {len(all_tools)} 个可用工具")
        
        return {
            "success": True,
            "tools": all_tools,
            "total": len(all_tools),
            "groups": tool_groups,
            "enabled_count": len([t for t in all_tools if t["enabled"]])
        }
        
    except Exception as e:
        logger.error(f"❌ 获取工具列表失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {
            "success": False,
            "tools": [],
            "total": 0,
            "groups": {},
            "message": f"获取工具列表失败: {str(e)}"
        }


@app.get("/api/tools/enabled", response_model=Dict[str, Any])
async def get_enabled_tools():
    """
    仅获取启用的工具列表
    
    Returns:
        {
            "success": bool,
            "tools": [...],  # 只包含enabled=True的工具
            "total": int
        }
    """
    try:
        registry = get_tool_registry()
        
        if not registry._tools:
            registry.load_from_config()
        
        # 只获取启用的工具
        enabled_tool_names = registry.get_enabled_tools()
        enabled_tools = []
        
        for name in enabled_tool_names:
            tool_def = registry.get_tool_definition(name)
            if tool_def:
                enabled_tools.append({
                    "name": name,
                    "display_name": tool_def.display_name,
                    "type": tool_def.type,
                    "description": tool_def.description or f"{tool_def.display_name}工具",
                })
        
        logger.info(f"✅ 返回 {len(enabled_tools)} 个启用的工具")
        
        return {
            "success": True,
            "tools": enabled_tools,
            "total": len(enabled_tools)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取启用工具列表失败: {e}")
        return {
            "success": False,
            "tools": [],
            "total": 0,
            "message": str(e)
        }


@app.get("/api/tools/groups/{group_name}", response_model=Dict[str, Any])
async def get_tools_by_group(group_name: str):
    """
    获取指定工具组的工具列表
    
    Args:
        group_name: 工具组名称（如 basic, advanced, mcp等）
    
    Returns:
        {
            "success": bool,
            "group_name": str,
            "tools": [...],
            "total": int
        }
    """
    try:
        registry = get_tool_registry()
        
        if not registry._tools:
            registry.load_from_config()
        
        # 获取工具组中的工具名称
        tool_names = registry.get_tools_by_group(group_name)
        
        if not tool_names:
            return {
                "success": False,
                "group_name": group_name,
                "tools": [],
                "total": 0,
                "message": f"工具组 '{group_name}' 不存在或为空"
            }
        
        # 获取工具详细信息
        tools = []
        for name in tool_names:
            tool_def = registry.get_tool_definition(name)
            if tool_def:
                tools.append({
                    "name": name,
                    "display_name": tool_def.display_name,
                    "type": tool_def.type,
                    "enabled": tool_def.enabled,
                    "description": tool_def.description,
                })
        
        logger.info(f"✅ 返回工具组 '{group_name}' 的 {len(tools)} 个工具")
        
        return {
            "success": True,
            "group_name": group_name,
            "tools": tools,
            "total": len(tools)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取工具组失败: {e}")
        return {
            "success": False,
            "group_name": group_name,
            "tools": [],
            "total": 0,
            "message": str(e)
        }


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
                # 🆕 延迟导入 UnifiedAgent
                from src.agents.unified.unified_agent import UnifiedAgent
                
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
    上传文件并解析内容
    
    Args:
        file: 上传的文件
        file_type: 文件类型 (image, data, temp)
        tags: 标签（逗号分隔）
        
    Returns:
        文件信息和解析结果
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
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "文件上传失败"))
        
        # 尝试解析文档内容
        parsed_content = None
        file_path = result.get("path")
        
        logger.info(f"🔍 开始解析文档: file_path={file_path}, exists={Path(file_path).exists() if file_path else False}")
        
        if file_path and Path(file_path).exists():
            try:
                from src.infrastructure.multimodal.document_parser import parse_document
                
                # 解析文档
                parse_result = parse_document(file_path)
                logger.info(f"🔍 解析结果: {parse_result}")
                
                if parse_result.get("success"):
                    # 🆕 统一字段名称：content -> full_text
                    content = parse_result.get("full_text") or parse_result.get("content", "")
                    parsed_content = {
                        "type": parse_result.get("type"),
                        "summary": parse_result.get("summary") or content[:500],  # 前500字符作为摘要
                        "full_text": content,
                        "metadata": parse_result.get("metadata", {})
                    }
                    logger.info(f"📄 文档解析成功: {file.filename}, 内容长度: {len(content)} 字符")
                else:
                    logger.warning(f"⚠️  文档解析失败: {parse_result.get('error')}")
                    
            except Exception as e:
                logger.warning(f"⚠️  文档解析失败: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        
        response_data = {
            "success": True,
            "file_id": result["file_id"],
            "filename": result["filename"],
            "download_url": result["download_url"],
            "size": result["size"],
            "message": "文件上传成功"
        }
        
        # 添加解析内容到响应
        if parsed_content:
            response_data["parsed_content"] = parsed_content
            response_data["message"] = "文件上传并解析成功"
            logger.info(f"✅ 响应中包含 parsed_content: {bool(parsed_content)}")
        else:
            logger.warning(f"⚠️  响应中不包含 parsed_content")
        
        logger.info(f"🔍 返回响应: {list(response_data.keys())}")
        return response_data
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 文件上传失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
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


# ==================== CrewAI API ====================

# CrewAI数据存储目录
CREWS_DIR = "data/crews"
Path(CREWS_DIR).mkdir(parents=True, exist_ok=True)

def _get_crew_file(crew_id: str) -> Path:
    return Path(CREWS_DIR) / f"{crew_id}.json"

def _load_crew(crew_id: str) -> Optional[dict]:
    file_path = _get_crew_file(crew_id)
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def _save_crew(crew: dict):
    file_path = _get_crew_file(crew["id"])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(crew, f, indent=2, ensure_ascii=False)

@app.post("/api/crewai/crews")
async def create_crew(crew: dict):
    """创建新的Crew配置"""
    try:
        from datetime import datetime
        crew["createdAt"] = datetime.now().isoformat()
        crew["updatedAt"] = datetime.now().isoformat()
        
        _save_crew(crew)
        
        return {
            "success": True,
            "crew_id": crew["id"],
            "message": "Crew created successfully"
        }
    except Exception as e:
        logger.error(f"❌ 创建Crew失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create crew: {str(e)}")

@app.get("/api/crewai/crews")
async def list_crews():
    """获取所有Crew列表"""
    try:
        crews = []
        crews_path = Path(CREWS_DIR)
        if crews_path.exists():
            for file_path in crews_path.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    crew = json.load(f)
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
        logger.error(f"❌ 列出Crew失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list crews: {str(e)}")

@app.get("/api/crewai/crews/{crew_id}")
async def get_crew(crew_id: str):
    """获取Crew详情"""
    crew = _load_crew(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    return {
        "success": True,
        "crew": crew
    }

@app.put("/api/crewai/crews/{crew_id}")
async def update_crew(crew_id: str, crew: dict):
    """更新Crew配置"""
    existing_crew = _load_crew(crew_id)
    if not existing_crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        from datetime import datetime
        crew["createdAt"] = existing_crew.get("createdAt", datetime.now().isoformat())
        crew["updatedAt"] = datetime.now().isoformat()
        
        _save_crew(crew)
        
        return {
            "success": True,
            "message": "Crew updated successfully"
        }
    except Exception as e:
        logger.error(f"❌ 更新Crew失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update crew: {str(e)}")

@app.delete("/api/crewai/crews/{crew_id}")
async def delete_crew(crew_id: str):
    """删除Crew"""
    file_path = _get_crew_file(crew_id)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        file_path.unlink()
        return {
            "success": True,
            "message": "Crew deleted successfully"
        }
    except Exception as e:
        logger.error(f"❌ 删除Crew失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete crew: {str(e)}")

@app.post("/api/crewai/crews/{crew_id}/execute")
async def execute_crew(crew_id: str, inputs: dict = {}):
    """
    执行Crew
    
    Args:
        crew_id: Crew ID
        inputs: 执行输入参数
    
    Returns:
        {
            success: bool,
            execution_id: str,
            output: str,  # 执行结果
            logs: List[str],  # 执行日志
            duration: float  # 执行时间(秒)
        }
    """
    crew_config = _load_crew(crew_id)
    if not crew_config:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    try:
        from datetime import datetime
        import time
        from crewai import Crew, Agent, Task, Process
        
        execution_id = f"exec_{crew_id}_{int(datetime.now().timestamp())}"
        start_time = time.time()
        logs = []
        
        logger.info(f"🚀 开始执行Crew: {crew_id}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 开始执行Crew: {crew_config.get('name', crew_id)}")
        
        # 1. 创建Agents
        agents = []
        for agent_config in crew_config.get("agents", []):
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 👤 创建Agent: {agent_config.get('role', 'Unknown')}")
            agent = Agent(
                role=agent_config.get("role", "Agent"),
                goal=agent_config.get("goal", "Complete the task"),
                backstory=agent_config.get("backstory", "I am a helpful assistant"),
                verbose=True,
                allow_delegation=agent_config.get("allow_delegation", False),
                max_iter=agent_config.get("max_iter", 15),
                memory=agent_config.get("memory", True)
            )
            agents.append(agent)
        
        # 2. 创建Tasks
        tasks = []
        for i, task_config in enumerate(crew_config.get("tasks", [])):
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 创建Task: {task_config.get('description', 'Unknown')[:50]}...")
            
            # 分配agent
            agent_role = task_config.get("agent", "")
            assigned_agent = agents[0]  # 默认第一个agent
            for agent in agents:
                if agent.role == agent_role:
                    assigned_agent = agent
                    break
            
            task = Task(
                description=task_config.get("description", "Complete this task"),
                expected_output=task_config.get("expected_output", "Task completed"),
                agent=assigned_agent
            )
            tasks.append(task)
        
        # 3. 创建Crew并执行
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 创建Crew实例...")
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True
        )
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ▶️ 开始执行任务...")
        
        # 执行（同步）
        result = crew.kickoff(inputs=inputs)
        
        duration = time.time() - start_time
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 执行完成！耗时: {duration:.2f}秒")
        
        logger.info(f"✅ Crew执行成功: {execution_id}, 耗时: {duration:.2f}s")
        
        return {
            "success": True,
            "execution_id": execution_id,
            "output": str(result) if result else "No output",
            "logs": logs,
            "duration": duration
        }
        
    except Exception as e:
        logger.error(f"❌ 执行Crew失败: {e}")
        import traceback
        error_trace = traceback.format_exc()
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 执行失败: {str(e)}")
        
        return {
            "success": False,
            "execution_id": execution_id if 'execution_id' in locals() else "unknown",
            "output": "",
            "logs": logs,
            "error": str(e),
            "traceback": error_trace
        }


class CrewExecutionRequest(BaseModel):
    """CrewAI执行请求"""
    inputs: Dict[str, Any] = {}
    files: List[str] = []  # 文件ID列表
    
    
@app.post("/api/crewai/crews/{crew_id}/execute/stream")
async def execute_crew_stream(crew_id: str, request: CrewExecutionRequest = CrewExecutionRequest()):
    """
    流式执行Crew，实时返回执行状态
    
    使用Server-Sent Events (SSE)格式返回：
    - data: {type: "status", message: "...", timestamp: "..."}
    - data: {type: "agent_start", agent: "...", timestamp: "..."}
    - data: {type: "task_start", task: "...", timestamp: "..."}
    - data: {type: "log", message: "...", timestamp: "..."}
    - data: {type: "progress", current: X, total: Y, percentage: Z}
    - data: {type: "result", output: "...", duration: X}
    - data: {type: "error", error: "...", traceback: "..."}
    - data: {type: "done"}
    
    Args:
        crew_id: Crew ID
        request: 执行请求（包含inputs和files）
    
    Returns:
        StreamingResponse (SSE格式)
    """
    inputs = request.inputs
    file_ids = request.files
    crew_config = _load_crew(crew_id)
    if not crew_config:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    async def event_generator():
        """生成SSE事件流"""
        try:
            from datetime import datetime
            import time
            import asyncio
            from crewai import Crew, Agent, Task, Process
            
            execution_id = f"exec_{crew_id}_{int(datetime.now().timestamp())}"
            start_time = time.time()
            
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'execution_id': execution_id, 'crew_name': crew_config.get('name', crew_id), 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"🚀 开始流式执行Crew: {crew_id}")
            
            # 🆕 处理文件输入
            file_contents = {}
            if file_ids:
                yield f"data: {json.dumps({'type': 'status', 'message': f'加载 {len(file_ids)} 个文件...', 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.1)
                
                for file_id in file_ids:
                    try:
                        # 从文件管理器获取文件信息
                        file_info = file_manager.get_file_info(file_id)
                        if file_info and file_info.get("success"):
                            file_path = file_info.get("path")
                            if file_path and Path(file_path).exists():
                                # 解析文件内容
                                from src.infrastructure.multimodal.document_parser import parse_document
                                parse_result = parse_document(file_path)
                                
                                if parse_result.get("success"):
                                    content = parse_result.get("full_text") or parse_result.get("content", "")
                                    file_contents[file_id] = {
                                        "filename": file_info.get("filename", file_id),
                                        "type": parse_result.get("type", "unknown"),
                                        "content": content
                                    }
                                    filename = file_info.get("filename")
                                    log_msg = f'✅ 已加载文件: {filename} ({len(content)} 字符)'
                                    yield f"data: {json.dumps({'type': 'log', 'message': log_msg, 'log_type': 'success', 'timestamp': datetime.now().isoformat()})}\n\n"
                                else:
                                    filename = file_info.get("filename")
                                    log_msg = f'⚠️ 文件解析失败: {filename}'
                                    yield f"data: {json.dumps({'type': 'log', 'message': log_msg, 'log_type': 'warning', 'timestamp': datetime.now().isoformat()})}\n\n"
                    except Exception as e:
                        logger.warning(f"文件加载失败 {file_id}: {e}")
                        log_msg = f'❌ 文件加载错误: {str(e)}'
                        yield f"data: {json.dumps({'type': 'log', 'message': log_msg, 'log_type': 'error', 'timestamp': datetime.now().isoformat()})}\n\n"
                
                # 将文件内容添加到inputs中
                if file_contents:
                    inputs["__files__"] = file_contents
                    logger.info(f"📁 已加载 {len(file_contents)} 个文件到执行上下文")
            
            # 1. 创建Agents
            agents = []
            agent_configs = crew_config.get("agents", [])
            total_agents = len(agent_configs)
            
            yield f"data: {json.dumps({'type': 'status', 'message': f'创建 {total_agents} 个Agent...', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
            
            for idx, agent_config in enumerate(agent_configs):
                agent_role = agent_config.get('role', 'Unknown Agent')
                
                # 发送Agent创建事件
                yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent_role, 'index': idx + 1, 'total': total_agents, 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.05)
                
                agent = Agent(
                    role=agent_config.get("role", "Agent"),
                    goal=agent_config.get("goal", "Complete the task"),
                    backstory=agent_config.get("backstory", "I am a helpful assistant"),
                    verbose=True,
                    allow_delegation=agent_config.get("allow_delegation", False),
                    max_iter=agent_config.get("max_iter", 15),
                    memory=agent_config.get("memory", True)
                )
                agents.append(agent)
                
                # 发送进度更新
                yield f"data: {json.dumps({'type': 'progress', 'step': 'agents', 'current': idx + 1, 'total': total_agents, 'percentage': int((idx + 1) / total_agents * 100), 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.05)
            
            # 2. 创建Tasks
            tasks = []
            task_configs = crew_config.get("tasks", [])
            total_tasks = len(task_configs)
            
            yield f"data: {json.dumps({'type': 'status', 'message': f'创建 {total_tasks} 个Task...', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
            
            for idx, task_config in enumerate(task_configs):
                task_desc = task_config.get('description', 'Unknown Task')[:50]
                
                # 发送Task创建事件
                yield f"data: {json.dumps({'type': 'task_start', 'task': task_desc, 'index': idx + 1, 'total': total_tasks, 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.05)
                
                # 分配agent
                agent_role = task_config.get("agent", "")
                assigned_agent = agents[0]  # 默认第一个agent
                for agent in agents:
                    if agent.role == agent_role:
                        assigned_agent = agent
                        break
                
                task = Task(
                    description=task_config.get("description", "Complete this task"),
                    expected_output=task_config.get("expected_output", "Task completed"),
                    agent=assigned_agent
                )
                tasks.append(task)
                
                # 发送进度更新
                yield f"data: {json.dumps({'type': 'progress', 'step': 'tasks', 'current': idx + 1, 'total': total_tasks, 'percentage': int((idx + 1) / total_tasks * 100), 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.05)
            
            # 3. 创建并执行Crew
            yield f"data: {json.dumps({'type': 'status', 'message': '创建Crew实例...', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
            
            # 🆕 支持不同的Process类型
            process_type = crew_config.get("process", "sequential").lower()
            process_mapping = {
                "sequential": Process.sequential,
                "hierarchical": Process.hierarchical
            }
            process = process_mapping.get(process_type, Process.sequential)
            
            # 🆕 Hierarchical需要Manager配置
            manager_llm = None
            if process_type == "hierarchical":
                # 使用系统配置的LLM作为Manager
                from src.services.system_config_service import SystemConfigService
                sys_config_service = SystemConfigService()
                sys_config = sys_config_service.load_config()
                
                from langchain_openai import ChatOpenAI
                manager_llm = ChatOpenAI(
                    model=sys_config.default_model,
                    api_key=sys_config.api_key,
                    base_url=sys_config.base_url,
                    temperature=sys_config.temperature
                )
                
                yield f"data: {json.dumps({'type': 'log', 'message': '🎯 使用Hierarchical模式，Manager LLM已配置', 'log_type': 'info', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=process,
                manager_llm=manager_llm,  # 🆕 仅Hierarchical需要
                verbose=True
            )
            
            yield f"data: {json.dumps({'type': 'status', 'message': '开始执行任务...', 'timestamp': datetime.now().isoformat()})}\n\n"
            yield f"data: {json.dumps({'type': 'execution_start', 'total_tasks': total_tasks, 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
            
            # 执行Crew（这里是同步的，CrewAI暂不支持真正的异步流式）
            # 在实际执行过程中，我们可以通过回调或日志捕获来发送更新
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
            
            duration = time.time() - start_time
            
            # 发送完成事件
            yield f"data: {json.dumps({'type': 'result', 'output': str(result) if result else 'No output', 'duration': duration, 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.1)
            
            yield f"data: {json.dumps({'type': 'done', 'execution_id': execution_id, 'duration': duration, 'timestamp': datetime.now().isoformat()})}\n\n"
            
            logger.info(f"✅ Crew流式执行成功: {execution_id}, 耗时: {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ 流式执行Crew失败: {e}")
            import traceback
            error_trace = traceback.format_exc()
            
            # 发送错误事件
            yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'traceback': error_trace, 'timestamp': datetime.now().isoformat()})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'success': False, 'timestamp': datetime.now().isoformat()})}\n\n"
    
    from starlette.responses import StreamingResponse
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用nginx缓冲
        }
    )


# ==================== 工具配置管理 API ====================

@app.get("/api/tools/configs")
async def get_tool_configs():
    """
    获取所有工具配置
    
    Returns:
        工具配置列表
    """
    try:
        from src.services.tool_config_service import get_tool_config_service
        
        service = get_tool_config_service()
        configs = service.get_all_configs()
        
        return {
            "success": True,
            "tools": [config.model_dump(mode='json') for config in configs],
            "total": len(configs)
        }
    except Exception as e:
        logger.error(f"Failed to get tool configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/{tool_id}/config")
async def get_tool_config(tool_id: str):
    """
    获取单个工具配置
    
    Args:
        tool_id: 工具ID
        
    Returns:
        工具配置
    """
    try:
        from src.services.tool_config_service import get_tool_config_service
        
        service = get_tool_config_service()
        config = service.get_config(tool_id)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
        
        return {
            "success": True,
            "tool": config.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tools/{tool_id}/config")
async def update_tool_config(tool_id: str, update: Dict[str, Any]):
    """
    更新单个工具配置
    
    Args:
        tool_id: 工具ID
        update: 更新数据
        
    Returns:
        更新后的工具配置
    """
    try:
        from src.services.tool_config_service import get_tool_config_service
        from src.models.tool_config import ToolConfigUpdate
        
        service = get_tool_config_service()
        
        # 验证工具是否存在
        if not service.get_config(tool_id):
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
        
        # 创建更新对象
        config_update = ToolConfigUpdate(**update)
        
        # 更新配置
        updated_config = service.update_config(tool_id, config_update)
        
        if not updated_config:
            raise HTTPException(status_code=500, detail="Failed to update tool config")
        
        logger.info(f"Updated tool config for {tool_id}")
        
        return {
            "success": True,
            "message": f"Tool {tool_id} config updated successfully",
            "tool": updated_config.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tool config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/configs/batch")
async def batch_update_tool_configs(configs: List[Dict[str, Any]]):
    """
    批量更新工具配置
    
    Args:
        configs: 工具配置列表
        
    Returns:
        更新后的所有工具配置
    """
    try:
        from src.services.tool_config_service import get_tool_config_service
        from src.models.tool_config import ToolConfig
        
        service = get_tool_config_service()
        
        # 解析配置
        tool_configs = [ToolConfig(**config) for config in configs]
        
        # 批量更新
        updated_configs = service.update_all_configs(tool_configs)
        
        logger.info(f"Batch updated {len(updated_configs)} tool configs")
        
        return {
            "success": True,
            "message": f"Updated {len(updated_configs)} tool configs",
            "tools": [config.model_dump(mode='json') for config in updated_configs],
            "total": len(updated_configs)
        }
    except Exception as e:
        logger.error(f"Failed to batch update tool configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/configs/reset")
async def reset_tool_configs():
    """
    重置工具配置为默认值
    
    Returns:
        默认工具配置列表
    """
    try:
        from src.services.tool_config_service import get_tool_config_service
        
        service = get_tool_config_service()
        configs = service.reset_to_default()
        
        logger.info("Reset tool configs to default")
        
        return {
            "success": True,
            "message": "Tool configs reset to default",
            "tools": [config.model_dump(mode='json') for config in configs],
            "total": len(configs)
        }
    except Exception as e:
        logger.error(f"Failed to reset tool configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Agent配置管理 API ====================

@app.get("/api/agents")
async def get_agent_configs():
    """
    获取所有Agent配置
    
    Returns:
        Agent配置列表
    """
    try:
        from src.services.agent_config_service import get_agent_config_service
        
        service = get_agent_config_service()
        configs = service.get_all_configs()
        
        return {
            "success": True,
            "agents": [config.model_dump(mode='json') for config in configs],
            "total": len(configs)
        }
    except Exception as e:
        logger.error(f"Failed to get agent configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}")
async def get_agent_config(agent_id: str):
    """
    获取单个Agent配置
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Agent配置
    """
    try:
        from src.services.agent_config_service import get_agent_config_service
        
        service = get_agent_config_service()
        config = service.get_config(agent_id)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "success": True,
            "agent": config.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents")
async def create_agent_config(create_data: Dict[str, Any]):
    """
    创建Agent配置
    
    Args:
        create_data: Agent创建数据
        
    Returns:
        创建的Agent配置
    """
    try:
        from src.services.agent_config_service import get_agent_config_service
        from src.models.agent_config import AgentConfigCreate
        
        service = get_agent_config_service()
        
        # 创建配置对象
        config_create = AgentConfigCreate(**create_data)
        
        # 创建Agent
        new_config = service.create_config(config_create)
        
        logger.info(f"Created agent: {new_config.id}")
        
        return {
            "success": True,
            "message": f"Agent {new_config.name} created successfully",
            "agent": new_config.model_dump(mode='json')
        }
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/agents/{agent_id}")
async def update_agent_config(agent_id: str, update_data: Dict[str, Any]):
    """
    更新Agent配置
    
    Args:
        agent_id: Agent ID
        update_data: 更新数据
        
    Returns:
        更新后的Agent配置
    """
    try:
        from src.services.agent_config_service import get_agent_config_service
        from src.models.agent_config import AgentConfigUpdate
        
        service = get_agent_config_service()
        
        # 验证Agent是否存在
        if not service.get_config(agent_id):
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # 创建更新对象
        config_update = AgentConfigUpdate(**update_data)
        
        # 更新配置
        updated_config = service.update_config(agent_id, config_update)
        
        if not updated_config:
            raise HTTPException(status_code=500, detail="Failed to update agent config")
        
        logger.info(f"Updated agent: {agent_id}")
        
        return {
            "success": True,
            "message": f"Agent {agent_id} updated successfully",
            "agent": updated_config.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/agents/{agent_id}")
async def delete_agent_config(agent_id: str):
    """
    删除Agent配置
    
    Args:
        agent_id: Agent ID
        
    Returns:
        删除结果
    """
    try:
        from src.services.agent_config_service import get_agent_config_service
        
        service = get_agent_config_service()
        
        # 删除配置
        success = service.delete_config(agent_id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete agent (not found or last agent)"
            )
        
        logger.info(f"Deleted agent: {agent_id}")
        
        return {
            "success": True,
            "message": f"Agent {agent_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/reset")
async def reset_agent_configs():
    """
    重置Agent配置为默认值
    
    Returns:
        默认Agent配置列表
    """
    try:
        from src.services.agent_config_service import get_agent_config_service
        
        service = get_agent_config_service()
        configs = service.reset_to_default()
        
        logger.info("Reset agent configs to default")
        
        return {
            "success": True,
            "message": "Agent configs reset to default",
            "agents": [config.model_dump(mode='json') for config in configs],
            "total": len(configs)
        }
    except Exception as e:
        logger.error(f"Failed to reset agent configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 主入口 ====================

# ==================== 知识库API ====================

@app.post("/api/knowledge-bases", response_model=Dict[str, Any])
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """创建知识库"""
    try:
        kb = knowledge_base_service.create_knowledge_base(request)
        return {
            "success": True,
            "knowledge_base": kb.model_dump(),
            "message": "知识库创建成功"
        }
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases", response_model=Dict[str, Any])
async def list_knowledge_bases():
    """列出所有知识库"""
    try:
        kbs = knowledge_base_service.list_knowledge_bases()
        return {
            "success": True,
            "knowledge_bases": [kb.model_dump() for kb in kbs],
            "total": len(kbs)
        }
    except Exception as e:
        logger.error(f"列出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases/{kb_id}", response_model=Dict[str, Any])
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    try:
        kb = knowledge_base_service.get_knowledge_base(kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        return {
            "success": True,
            "knowledge_base": kb.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/knowledge-bases/{kb_id}", response_model=Dict[str, Any])
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdate):
    """更新知识库"""
    try:
        kb = knowledge_base_service.update_knowledge_base(kb_id, request)
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        return {
            "success": True,
            "knowledge_base": kb.model_dump(),
            "message": "知识库更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge-bases/{kb_id}", response_model=Dict[str, Any])
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    try:
        success = knowledge_base_service.delete_knowledge_base(kb_id)
        if not success:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        return {
            "success": True,
            "message": "知识库删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases/{kb_id}/documents", response_model=Dict[str, Any])
async def upload_document(kb_id: str, request: DocumentUploadRequest):
    """上传文档到知识库"""
    try:
        # 从文件管理器获取文件信息
        file_info = file_manager.get_file_info(request.file_id)
        if not file_info or not file_info.get("success"):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_path = file_info.get("path")
        if not file_path or not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="文件路径无效")
        
        # 添加到知识库
        doc = knowledge_base_service.add_document(
            kb_id=kb_id,
            file_path=file_path,
            filename=file_info.get("filename", ""),
            file_type=file_info.get("type", ""),
            file_size=file_info.get("size", 0),
            metadata=request.metadata
        )
        
        if not doc:
            raise HTTPException(status_code=500, detail="文档处理失败")
        
        return {
            "success": True,
            "document": doc.model_dump(),
            "message": "文档上传成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases/{kb_id}/search", response_model=Dict[str, Any])
async def search_knowledge_base(kb_id: str, request: SearchRequest):
    """检索知识库"""
    try:
        # 确保request中的kb_id与路径参数一致
        request.kb_id = kb_id
        
        response = knowledge_base_service.search(request)
        return response.model_dump()
    except Exception as e:
        logger.error(f"检索知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

