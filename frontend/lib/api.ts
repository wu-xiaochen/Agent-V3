/**
 * API 客户端 - 与后端 FastAPI 服务通信
 */

import type { Message, FileAttachment } from "./types"

// 从api-client导入以避免循环依赖
import { apiClient } from "./api-client"

// 导出apiClient供其他模块使用
export { apiClient }

// ==================== 类型定义 ====================

interface ChatMessageRequest {
  session_id: string
  message: string
  provider?: string
  model_name?: string
  memory?: boolean
  streaming?: boolean
}

interface ChatMessageResponse {
  success: boolean
  session_id: string
  response: string
  metadata?: Record<string, any>
}

interface ChatHistoryResponse {
  success: boolean
  session_id: string
  messages: Array<{
    type: string
    content: string
    timestamp?: string
  }>
}

interface FileUploadResponse {
  success: boolean
  file_id: string
  filename: string
  download_url: string
  size: number
  message: string
}

interface FileListResponse {
  success: boolean
  count: number
  files: Array<{
    file_id: string
    filename: string
    download_url: string
    size: number
    size_human: string
    created_at: string
    mime_type: string
    tags: string[]
  }>
}

interface ToolListResponse {
  success: boolean
  count: number
  tools: Record<
    string,
    {
      display_name: string
      type: string
      enabled: boolean
      description: string
    }
  >
}

// ==================== Chat API ====================

export const chatAPI = {
  /**
   * 发送聊天消息
   */
  async sendMessage(
    sessionId: string,
    message: string,
    options?: {
      provider?: string
      modelName?: string
      memory?: boolean
      attachments?: FileAttachment[]  // ✅ 新增：支持附件
    }
  ): Promise<ChatMessageResponse> {
    const response = await apiClient.post<ChatMessageResponse>("/api/chat/message", {
      session_id: sessionId,
      message,
      provider: options?.provider || "siliconflow",
      model_name: options?.modelName,
      memory: options?.memory !== false,
      streaming: false,
      attachments: options?.attachments || []  // ✅ 传递附件
    })
    return response.data
  },

  /**
   * 获取聊天历史
   */
  async getHistory(sessionId: string, limit: number = 50): Promise<ChatHistoryResponse> {
    const response = await apiClient.get<ChatHistoryResponse>(`/api/chat/history/${sessionId}`, {
      params: { limit },
    })
    return response.data
  },

  /**
   * 创建 WebSocket 连接进行流式对话
   */
  createStreamConnection(
    sessionId: string,
    onMessage: (data: any) => void,
    onError: (error: any) => void
  ): WebSocket {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    const wsUrl = baseUrl.replace("http", "ws") + "/api/chat/stream"
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log("WebSocket connected")
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error)
      }
    }

    ws.onerror = (error) => {
      console.error("WebSocket error:", error)
      onError(error)
    }

    ws.onclose = () => {
      console.log("WebSocket disconnected")
    }

    return ws
  },

  /**
   * 发送流式消息
   */
  sendStreamMessage(
    ws: WebSocket,
    sessionId: string,
    message: string,
    options?: {
      provider?: string
      modelName?: string
    }
  ): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(
        JSON.stringify({
          session_id: sessionId,
          message,
          provider: options?.provider || "siliconflow",
          model_name: options?.modelName,
        })
      )
    } else {
      console.error("WebSocket is not connected")
    }
  },

  /**
   * 列出所有会话
   */
  async listSessions(): Promise<{
    success: boolean
    count: number
    sessions: Array<{
      session_id: string
      message_count: number
      last_message: string
      is_active: boolean
    }>
  }> {
    const response = await apiClient.get("/api/chat/sessions")
    return response.data
  },

  /**
   * 删除会话
   */
  async deleteSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/api/chat/sessions/${sessionId}`)
    return response.data
  },

  /**
   * 清空所有会话
   */
  async clearAllSessions(): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete("/api/chat/sessions")
    return response.data
  },
}

// ==================== Files API ====================

export const filesAPI = {
  /**
   * 上传文件
   */
  async uploadFile(
    file: File,
    options?: {
      fileType?: string
      tags?: string
    }
  ): Promise<FileUploadResponse> {
    const formData = new FormData()
    formData.append("file", file)
    if (options?.fileType) {
      formData.append("file_type", options.fileType)
    }
    if (options?.tags) {
      formData.append("tags", options.tags)
    }

    const response = await apiClient.post<FileUploadResponse>("/api/files/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    return response.data
  },

  /**
   * 列出文件
   */
  async listFiles(options?: { tags?: string; limit?: number }): Promise<FileListResponse> {
    const response = await apiClient.get<FileListResponse>("/api/files/list", {
      params: options,
    })
    return response.data
  },

  /**
   * 删除文件
   */
  async deleteFile(fileId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/api/files/${fileId}`)
    return response.data
  },

  /**
   * 获取下载链接
   */
  getDownloadUrl(fileId: string): string {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    return `${baseUrl}/api/files/download/${fileId}`
  },
}

// ==================== Tools API ====================

export const toolsAPI = {
  /**
   * 列出所有工具
   */
  async listTools(): Promise<ToolListResponse> {
    const response = await apiClient.get<ToolListResponse>("/api/tools/list")
    return response.data
  },

  /**
   * 获取工具调用历史
   */
  async getToolCallHistory(sessionId: string): Promise<{
    success: boolean
    session_id: string
    tool_calls: Array<{
      tool: string
      status: string
      input?: any
      output?: string
      error?: string
      execution_time?: number
      timestamp: string
    }>
    count: number
  }> {
    const response = await apiClient.get(`/api/tools/history/${sessionId}`)
    return response.data
  },

  /**
   * 清空工具调用历史
   */
  async clearToolCallHistory(sessionId: string): Promise<{
    success: boolean
    session_id: string
    message: string
  }> {
    const response = await apiClient.delete(`/api/tools/history/${sessionId}`)
    return response.data
  },
}

// ==================== 🆕 Thinking Chain API ====================

export const thinkingAPI = {
  /**
   * 获取思维链历史
   */
  async getThinkingChain(sessionId: string): Promise<{
    success: boolean
    session_id: string
    thinking_chain: Array<{
      type: string  // chain_start, thinking, thought, planning, action, observation, final_thought, chain_end
      step: number
      content: string
      tool?: string
      tool_input?: any
      output?: string
      error?: string
      execution_time?: number
      timestamp: string
      status: string
    }>
    count: number
  }> {
    const response = await apiClient.get(`/api/thinking/history/${sessionId}`)
    return response.data
  },

  /**
   * 清空思维链历史
   */
  async clearThinkingChain(sessionId: string): Promise<{
    success: boolean
    session_id: string
    message: string
  }> {
    const response = await apiClient.delete(`/api/thinking/history/${sessionId}`)
    return response.data
  },
}

// ==================== Knowledge Base API ====================

import { knowledgeBaseApi, type KnowledgeBase, type Document, type CreateKnowledgeBaseRequest, type UpdateKnowledgeBaseRequest, type UploadDocumentRequest, type SearchRequest, type SearchResponse } from './api/knowledge-base'

export const knowledgeAPI = {
  /**
   * 列出所有知识库
   */
  async listKnowledgeBases(): Promise<KnowledgeBase[]> {
    const response = await knowledgeBaseApi.list()
    if (response.success) {
      return response.knowledge_bases
    }
    return []
  },

  /**
   * 创建知识库
   */
  async createKnowledgeBase(request: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    const response = await knowledgeBaseApi.create(request)
    if (response.success) {
      return response.knowledge_base
    }
    throw new Error(response.message || "创建知识库失败")
  },

  /**
   * 获取知识库详情
   */
  async getKnowledgeBase(kbId: string): Promise<KnowledgeBase> {
    const response = await knowledgeBaseApi.get(kbId)
    if (response.success) {
      return response.knowledge_base
    }
    throw new Error("获取知识库失败")
  },

  /**
   * 更新知识库
   */
  async updateKnowledgeBase(kbId: string, request: UpdateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    const response = await knowledgeBaseApi.update(kbId, request)
    if (response.success) {
      return response.knowledge_base
    }
    throw new Error(response.message || "更新知识库失败")
  },

  /**
   * 删除知识库
   */
  async deleteKnowledgeBase(kbId: string): Promise<void> {
    const response = await knowledgeBaseApi.delete(kbId)
    if (!response.success) {
      throw new Error(response.message || "删除知识库失败")
    }
  },

  /**
   * 上传文档到知识库
   */
  async uploadDocument(kbId: string, request: UploadDocumentRequest): Promise<Document> {
    const response = await knowledgeBaseApi.uploadDocument(kbId, request)
    if (response.success) {
      return response.document
    }
    throw new Error(response.message || "上传文档失败")
  },

  /**
   * 列出知识库中的所有文档
   */
  async listDocuments(kbId: string): Promise<Document[]> {
    const response = await knowledgeBaseApi.listDocuments(kbId)
    if (response.success) {
      return response.documents
    }
    return []
  },

  /**
   * 删除文档
   */
  async deleteDocument(kbId: string, docId: string): Promise<void> {
    const response = await knowledgeBaseApi.deleteDocument(kbId, docId)
    if (!response.success) {
      throw new Error(response.message || "删除文档失败")
    }
  },

  /**
   * 检索知识库
   */
  async searchKnowledgeBase(kbId: string, request: SearchRequest): Promise<SearchResponse> {
    return await knowledgeBaseApi.search(kbId, request)
  },
}

// ==================== CrewAI API (待实现) ====================

export const crewaiAPI = {
  /**
   * 创建或保存Crew配置
   */
  async saveCrew(crew: any): Promise<{ success: boolean; crew_id: string; message: string }> {
    const response = await apiClient.post("/api/crewai/crews", crew)
    return response.data
  },

  /**
   * 获取所有Crew列表
   */
  async listCrews(): Promise<{ 
    success: boolean
    crews: Array<{
      id: string
      name: string
      description: string
      agentCount: number
      taskCount: number
      createdAt: string
      updatedAt: string
    }>
  }> {
    const response = await apiClient.get("/api/crewai/crews")
    return response.data
  },

  /**
   * 获取单个Crew的详细信息
   */
  async getCrew(crewId: string): Promise<{ success: boolean; crew: any }> {
    const response = await apiClient.get(`/api/crewai/crews/${crewId}`)
    return response.data
  },

  /**
   * 更新Crew配置
   */
  async updateCrew(crewId: string, crew: any): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.put(`/api/crewai/crews/${crewId}`, crew)
    return response.data
  },

  /**
   * 删除Crew
   */
  async deleteCrew(crewId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/api/crewai/crews/${crewId}`)
    return response.data
  },

  /**
   * 执行Crew
   */
  async executeCrew(crewId: string, inputs: Record<string, any> = {}): Promise<{ 
    success: boolean
    execution_id: string
    message: string
  }> {
    const response = await apiClient.post(`/api/crewai/crews/${crewId}/execute`, { inputs })
    return response.data
  },
  
  /**
   * 获取执行状态
   */
  async getExecutionStatus(executionId: string): Promise<{
    success: boolean
    status: any
  }> {
    const response = await apiClient.get(`/api/crewai/execution/${executionId}/status`)
    return response.data
  },
  
  /**
   * 暂停执行
   */
  async pauseExecution(executionId: string): Promise<{
    success: boolean
    message: string
  }> {
    const response = await apiClient.post(`/api/crewai/execution/${executionId}/pause`)
    return response.data
  },
  
  /**
   * 恢复执行
   */
  async resumeExecution(executionId: string): Promise<{
    success: boolean
    message: string
  }> {
    const response = await apiClient.post(`/api/crewai/execution/${executionId}/resume`)
    return response.data
  },
  
  /**
   * 取消执行
   */
  async cancelExecution(executionId: string): Promise<{
    success: boolean
    message: string
  }> {
    const response = await apiClient.post(`/api/crewai/execution/${executionId}/cancel`)
    return response.data
  },
  
  /**
   * 获取执行日志
   */
  async getExecutionLogs(executionId: string, limit: number = 100): Promise<{
    success: boolean
    logs: any[]
    count: number
  }> {
    const response = await apiClient.get(`/api/crewai/execution/${executionId}/logs?limit=${limit}`)
    return response.data
  },
}

// ==================== Health Check ====================

export const healthAPI = {
  /**
   * 检查 API 服务健康状态
   */
  async check(): Promise<{
    status: string
    file_manager: string
    active_sessions: number
    active_websockets: number
  }> {
    const response = await apiClient.get("/api/health")
    return response.data
  },
}

// 导出所有 API
// 导入系统配置API
import { systemApi } from './api/system'
// 导入工具列表API (用于CrewAI工具选择)
import { toolsListApi } from './api/tools'
// 导入知识库API (如果存在)
// import { knowledgeBaseApi } from './api/knowledge-base'

export const api = {
  chat: chatAPI,
  files: filesAPI,
  tools: toolsAPI,
  thinking: thinkingAPI,  // 🆕 思维链API
  knowledge: knowledgeAPI,
  crewai: crewaiAPI,
  health: healthAPI,
  system: systemApi,  // 🆕 系统配置API
  toolsList: toolsListApi,  // 🆕 工具列表API（用于CrewAI）
  // knowledgeBase: knowledgeBaseApi,  // ⏳ 知识库API (待实现)
}

export default api
