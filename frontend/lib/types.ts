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
}

export interface ChatSession {
  id: string
  title: string
  createdAt: Date
  lastMessageAt: Date
}

export interface KnowledgeBase {
  id: string
  name: string
  documentCount: number
  tags: string[]
  createdAt: Date
}

export interface Document {
  id: string
  name: string
  type: string
  size: number
  uploadedAt: Date
  tags: string[]
}

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
