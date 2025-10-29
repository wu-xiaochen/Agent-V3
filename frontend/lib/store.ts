import { create } from "zustand"
import type { Message, ChatSession, ToolType } from "./types"

interface AppState {
  currentSession: string | null
  messages: Message[]
  sessions: ChatSession[]
  toolPanelOpen: boolean
  currentTool: ToolType | null
  activeTab: string
  darkMode: boolean
  sessionTitleGenerated: boolean  // 标记会话标题是否已生成

  setCurrentSession: (sessionId: string) => void
  addMessage: (message: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void
  setToolPanelOpen: (open: boolean) => void
  setCurrentTool: (tool: ToolType | null) => void
  setActiveTab: (tab: string) => void
  toggleDarkMode: () => void
  createNewSession: () => void
  setSessionTitleGenerated: (generated: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  currentSession: "session-1",
  messages: [],
  sessions: [
    {
      id: "session-1",
      title: "New Chat",
      createdAt: new Date(),
      lastMessageAt: new Date(),
    },
  ],
  toolPanelOpen: false,
  currentTool: null,
  activeTab: "crewai",
  darkMode: true,
  sessionTitleGenerated: false,

  setCurrentSession: (sessionId) => set((state) => {
    // 在切换会话前，可以在这里保存当前会话的消息到localStorage
    if (state.currentSession && state.messages.length > 0) {
      const sessionData = {
        sessionId: state.currentSession,
        messages: state.messages,
        timestamp: new Date().toISOString()
      }
      localStorage.setItem(`session_${state.currentSession}`, JSON.stringify(sessionData))
      console.log(`💾 Saved session ${state.currentSession} with ${state.messages.length} messages`)
    }
    
    // 尝试加载新会话的消息
    const savedData = localStorage.getItem(`session_${sessionId}`)
    let loadedMessages = []
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        loadedMessages = parsed.messages || []
        console.log(`📥 Loaded session ${sessionId} with ${loadedMessages.length} messages`)
      } catch (e) {
        console.error("Failed to load session:", e)
      }
    }
    
    return { 
      currentSession: sessionId, 
      sessionTitleGenerated: false,
      messages: loadedMessages
    }
  }),

  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),

  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg)),
    })),

  clearMessages: () => set({ messages: [], sessionTitleGenerated: false }),

  setToolPanelOpen: (open) => set({ toolPanelOpen: open }),

  setCurrentTool: (tool) => set({ currentTool: tool }),

  setActiveTab: (tab) => set({ activeTab: tab }),

  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),

  setSessionTitleGenerated: (generated) => set({ sessionTitleGenerated: generated }),

  createNewSession: () =>
    set((state) => {
      const newSession: ChatSession = {
        id: `session-${Date.now()}`,
        title: "New Chat",
        createdAt: new Date(),
        lastMessageAt: new Date(),
      }
      return {
        sessions: [...state.sessions, newSession],
        currentSession: newSession.id,
        messages: [],
        sessionTitleGenerated: false,
      }
    }),
}))
