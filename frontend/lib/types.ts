export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  files?: FileAttachment[]
  streaming?: boolean
}

export interface FileAttachment {
  id: string
  name: string
  type: string
  url: string
  size: number
  parsed_content?: {
    type: string
    summary: string
    full_text: string
  }
}

export interface ChatSession {
  id: string
  title: string
  createdAt: Date
  lastMessageAt: Date
}

// KnowledgeBase 和 Document 类型已移至 frontend/lib/api/knowledge-base.ts
// 如需使用，请从该文件导入

export interface Agent {
  id: string
  role: string
  goal: string
  tools: string[]
  status: "idle" | "running" | "completed" | "error"
}

export interface Task {
  id: string
  description: string
  agentId: string
  status: "pending" | "running" | "completed" | "error"
  dependencies: string[]
}

export interface CrewConfig {
  id: string
  name: string
  agents: Agent[]
  tasks: Task[]
}

export type ToolType = "crewai" | "n8n" | "knowledge" | "tools"

export interface ToolStatus {
  type: ToolType
  status: "idle" | "running" | "completed" | "error"
  output?: any
}
