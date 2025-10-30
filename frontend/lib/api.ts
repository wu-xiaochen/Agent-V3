/**
 * API 客户端 - 与后端 FastAPI 服务通信
 */

import axios, { AxiosInstance, AxiosError } from "axios"
import type { Message, FileAttachment, KnowledgeBase, Document } from "./types"

// API 基础配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// 创建 axios 实例并导出
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 🆕 5分钟超时（CrewAI和复杂任务需要更长时间）
  headers: {
    "Content-Type": "application/json",
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token
    // const token = localStorage.getItem("token")
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)

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
    const wsUrl = API_BASE_URL.replace("http", "ws") + "/api/chat/stream"
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
    return `${API_BASE_URL}/api/files/download/${fileId}`
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

// ==================== Knowledge Base API (待实现) ====================

export const knowledgeAPI = {
  /**
   * 列出知识库 (TODO: 需要后端实现)
   */
  async listKnowledgeBases(): Promise<KnowledgeBase[]> {
    // 暂时返回模拟数据
    return []
  },

  /**
   * 创建知识库 (TODO: 需要后端实现)
   */
  async createKnowledgeBase(name: string, description: string): Promise<KnowledgeBase> {
    throw new Error("Not implemented yet")
  },

  /**
   * 上传文档到知识库 (TODO: 需要后端实现)
   */
  async uploadDocument(kbId: string, file: File): Promise<Document> {
    throw new Error("Not implemented yet")
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
// 导入工具列表API
import { toolsListApi } from './api/tools'
// 导入知识库API
import { knowledgeBaseApi } from './api/knowledge-base'

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
  knowledgeBase: knowledgeBaseApi,  // 🆕 知识库API
}

export default api
