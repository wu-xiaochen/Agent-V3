"use client"

import { useState, useEffect } from "react"
import { MessageSquare, Plus, Database, Users, Settings, ChevronLeft, ChevronRight, Trash2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"

interface Session {
  session_id: string
  message_count: number
  last_message: string
  is_active: boolean
}

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { currentSession, setCurrentSession, clearMessages, setToolPanelOpen, setActiveTab } = useAppStore()

  // 加载会话列表
  const loadSessions = async () => {
    setIsLoading(true)
    try {
      const response = await api.chat.listSessions()
      if (response.success) {
        setSessions(response.sessions)
      }
    } catch (error) {
      console.error("加载会话列表失败:", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [])

  // 创建新会话
  const handleNewSession = () => {
    const newSessionId = `session-${Date.now()}`
    setCurrentSession(newSessionId)
    clearMessages()
    loadSessions()
  }

  // 切换会话
  const handleSelectSession = (sessionId: string) => {
    setCurrentSession(sessionId)
    clearMessages()
    // TODO: 加载该会话的历史消息
  }

  // 删除会话
  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (!confirm("确定要删除这个会话吗？")) {
      return
    }

    try {
      await api.chat.deleteSession(sessionId)
      
      // 如果删除的是当前会话，创建新会话
      if (sessionId === currentSession) {
        handleNewSession()
      }
      
      loadSessions()
    } catch (error) {
      console.error("删除会话失败:", error)
    }
  }

  return (
    <div
      className={cn(
        "h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-60",
      )}
    >
      <div className="p-4 border-b border-sidebar-border flex items-center justify-between">
        {!collapsed && <h1 className="text-lg font-semibold text-sidebar-foreground">AI Agent Hub</h1>}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="text-sidebar-foreground"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <div className="p-3">
        <Button
          onClick={handleNewSession}
          className="w-full bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
        >
          <Plus className="h-4 w-4" />
          {!collapsed && <span className="ml-2">New Chat</span>}
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1">
          <div className="flex items-center justify-between px-2 py-2">
            {!collapsed && <div className="text-xs font-medium text-sidebar-muted-foreground">Recent Chats</div>}
            {!collapsed && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={loadSessions}
                disabled={isLoading}
              >
                <RefreshCw className={cn("h-3 w-3", isLoading && "animate-spin")} />
              </Button>
            )}
          </div>
          {sessions.length === 0 ? (
            !collapsed && (
              <div className="text-xs text-sidebar-muted-foreground px-2 py-4 text-center">
                No conversations yet
              </div>
            )
          ) : (
            sessions.map((session) => (
              <div
                key={session.session_id}
                className={cn(
                  "group relative flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer transition-colors",
                  currentSession === session.session_id
                    ? "bg-sidebar-accent"
                    : "hover:bg-sidebar-accent/50"
                )}
                onClick={() => handleSelectSession(session.session_id)}
              >
                <MessageSquare className="h-4 w-4 shrink-0 text-sidebar-foreground" />
                {!collapsed && (
                  <>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-sidebar-foreground truncate">{session.last_message}</p>
                      <p className="text-xs text-sidebar-muted-foreground">
                        {session.message_count} messages
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => handleDeleteSession(session.session_id, e)}
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </Button>
                  </>
                )}
              </div>
            ))
          )}
        </div>

        {!collapsed && (
          <>
            <div className="text-xs font-medium text-sidebar-muted-foreground px-2 py-2 mt-6">Quick Access</div>
            <div className="space-y-1">
              <Button 
                variant="ghost" 
                className="w-full justify-start text-sidebar-foreground"
                onClick={() => {
                  setActiveTab("knowledge")
                  setToolPanelOpen(true)
                }}
              >
                <Database className="h-4 w-4" />
                <span className="ml-2 text-sm">Knowledge Bases</span>
              </Button>
              <Button 
                variant="ghost" 
                className="w-full justify-start text-sidebar-foreground"
                onClick={() => {
                  setActiveTab("crewai")
                  setToolPanelOpen(true)
                }}
              >
                <Users className="h-4 w-4" />
                <span className="ml-2 text-sm">CrewAI Teams</span>
              </Button>
            </div>
          </>
        )}
      </ScrollArea>

      <div className="p-3 border-t border-sidebar-border">
        <Button 
          variant="ghost" 
          className="w-full justify-start text-sidebar-foreground"
          onClick={() => {
            setActiveTab("tools")
            setToolPanelOpen(true)
          }}
        >
          <Settings className="h-4 w-4" />
          {!collapsed && <span className="ml-2 text-sm">Settings</span>}
        </Button>
      </div>
    </div>
  )
}
