import { create } from "zustand"
import type { Message, ChatSession, ToolType } from "./types"

interface AppState {
  currentSession: string | null
  messages: Message[]
  sessions: ChatSession[]
  toolPanelOpen: boolean
  currentTool: ToolType | null
  darkMode: boolean

  setCurrentSession: (sessionId: string) => void
  addMessage: (message: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void
  setToolPanelOpen: (open: boolean) => void
  setCurrentTool: (tool: ToolType | null) => void
  toggleDarkMode: () => void
  createNewSession: () => void
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
  darkMode: true,

  setCurrentSession: (sessionId) => set({ currentSession: sessionId }),

  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),

  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg)),
    })),

  clearMessages: () => set({ messages: [] }),

  setToolPanelOpen: (open) => set({ toolPanelOpen: open }),

  setCurrentTool: (tool) => set({ currentTool: tool }),

  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),

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
      }
    }),
}))
