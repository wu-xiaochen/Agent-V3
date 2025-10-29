/**
 * API 客户端 - 与后端 FastAPI 服务通信
 */

import axios, { AxiosInstance, AxiosError } from "axios"
import type { Message, FileAttachment, KnowledgeBase, Document } from "./types"

// API 基础配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds
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
    }
  ): Promise<ChatMessageResponse> {
    const response = await apiClient.post<ChatMessageResponse>("/api/chat/message", {
      session_id: sessionId,
      message,
      provider: options?.provider || "siliconflow",
      model_name: options?.modelName,
      memory: options?.memory !== false,
      streaming: false,
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
   * 创建 CrewAI 配置 (TODO: 需要后端实现)
   */
  async createCrew(config: any): Promise<any> {
    throw new Error("Not implemented yet")
  },

  /**
   * 运行 CrewAI (TODO: 需要后端实现)
   */
  async runCrew(crewId: string, query: string): Promise<any> {
    throw new Error("Not implemented yet")
  },

  /**
   * 获取 CrewAI 状态 (TODO: 需要后端实现)
   */
  async getStatus(crewId: string): Promise<any> {
    throw new Error("Not implemented yet")
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
export const api = {
  chat: chatAPI,
  files: filesAPI,
  tools: toolsAPI,
  knowledge: knowledgeAPI,
  crewai: crewaiAPI,
  health: healthAPI,
}

export default api
