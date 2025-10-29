"use client"

import { useState, useEffect } from "react"
import { MessageSquare, Plus, Database, Users, Settings, ChevronLeft, ChevronRight, Trash2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"
import { SessionTitleEditor } from "./session-title-editor"

interface Session {
  session_id: string
  message_count: number
  last_message: string
  is_active: boolean
  is_local: boolean  // 标记是否为本地创建（未同步到后端）
}

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { currentSession, setCurrentSession, clearMessages, setToolPanelOpen, setActiveTab, messages, sessionTitleGenerated, setSessionTitleGenerated } = useAppStore()

  console.log("🔄 Sidebar Render - currentSession:", currentSession)

  // 从后端加载会话列表
  const loadSessionsFromBackend = async () => {
    setIsLoading(true)
    try {
      const response = await api.chat.listSessions()
      console.log("📥 Loaded sessions from backend:", response)
      
      if (response.success) {
        // 合并后端会话和本地会话
        setSessions(prev => {
          const localSessions = prev.filter(s => s.is_local)
          const backendSessions = response.sessions.map(s => ({
            ...s,
            is_local: false,
            is_active: s.session_id === currentSession
          }))
          return [...localSessions, ...backendSessions]
        })
      }
    } catch (error) {
      console.error("❌ 加载会话列表失败:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // 初始化加载
  useEffect(() => {
    loadSessionsFromBackend()
  }, [])

  // 监听 currentSession 变化，更新激活状态
  useEffect(() => {
    console.log("👁️ currentSession changed to:", currentSession)
    setSessions(prev => prev.map(s => ({
      ...s,
      is_active: s.session_id === currentSession
    })))
  }, [currentSession])

  // 监听消息变化，自动生成会话标题（基于第一条用户消息）
  useEffect(() => {
    if (messages.length > 0 && !sessionTitleGenerated && currentSession) {
      const firstUserMessage = messages.find(m => m.role === "user")
      if (firstUserMessage) {
        // 生成标题：截取第一条消息的前20个字符
        const title = firstUserMessage.content.slice(0, 20) + (firstUserMessage.content.length > 20 ? "..." : "")
        console.log("📝 Auto-generating session title:", title)
        
        // 更新本地会话标题
        setSessions(prev => prev.map(s => 
          s.session_id === currentSession 
            ? { ...s, last_message: title }
            : s
        ))
        
        setSessionTitleGenerated(true)
      }
    }
  }, [messages, sessionTitleGenerated, currentSession, setSessionTitleGenerated])

  // 创建新会话
  const handleNewSession = () => {
    const newSessionId = `session-${Date.now()}`
    console.log("✨ Creating new session:", newSessionId)
    
    // 1. 更新全局状态
    setCurrentSession(newSessionId)
    clearMessages()
    
    // 2. 添加到本地会话列表（标记为本地）
    const newSession: Session = {
      session_id: newSessionId,
      message_count: 0,
      last_message: "New conversation",
      is_active: true,
      is_local: true  // 标记为本地会话
    }
    
    setSessions(prev => [
      newSession,
      ...prev.map(s => ({ ...s, is_active: false }))
    ])
    
    console.log("✅ New session created")
  }

  // 切换会话
  const handleSelectSession = (sessionId: string) => {
    console.log("🔀 Switching to session:", sessionId, "from:", currentSession)
    
    // 如果已经是当前会话，不做任何操作
    if (sessionId === currentSession) {
      console.log("⚠️  Already on this session, skip")
      return
    }
    
    // 更新全局状态
    setCurrentSession(sessionId)
    clearMessages()
    
    // 激活状态会通过 useEffect 自动更新
    console.log("✅ Session switched")
  }

  // 删除会话
  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation() // 阻止事件冒泡到父元素
    
    console.log("🗑️  Deleting session:", sessionId)
    
    if (!confirm("确定要删除这个会话吗？")) {
      return
    }

    try {
      // 查找会话
      const session = sessions.find(s => s.session_id === sessionId)
      
      if (!session) {
        console.error("❌ Session not found:", sessionId)
        return
      }

      // 如果是本地会话（未同步到后端），直接删除
      if (session.is_local) {
        console.log("📌 Deleting local session (not calling backend)")
        
        // 从列表中移除
        setSessions(prev => prev.filter(s => s.session_id !== sessionId))
        
        // 如果删除的是当前会话，创建新会话
        if (sessionId === currentSession) {
          console.log("🔄 Deleted current session, creating new one")
          handleNewSession()
        }
      } else {
        // 如果是后端会话，调用API删除
        console.log("🌐 Deleting backend session (calling API)")
        await api.chat.deleteSession(sessionId)
        
        // 从列表中移除
        setSessions(prev => prev.filter(s => s.session_id !== sessionId))
        
        // 如果删除的是当前会话，创建新会话
        if (sessionId === currentSession) {
          console.log("🔄 Deleted current session, creating new one")
          handleNewSession()
        } else {
          // 重新加载会话列表以确保同步
          await loadSessionsFromBackend()
        }
      }
      
      console.log("✅ Session deleted successfully")
    } catch (error) {
      console.error("❌ 删除会话失败:", error)
      alert("删除会话失败，请重试")
    }
  }

  // 刷新会话列表
  const handleRefresh = () => {
    console.log("🔄 Refreshing sessions...")
    loadSessionsFromBackend()
  }

  // 保存会话标题
  const handleSaveTitle = async (sessionId: string, newTitle: string) => {
    console.log("💾 Saving session title:", sessionId, newTitle)
    
    try {
      // TODO: 调用后端API保存标题
      // await api.chat.updateSession(sessionId, { title: newTitle })
      
      // 更新本地状态
      setSessions(prev => prev.map(s => 
        s.session_id === sessionId 
          ? { ...s, last_message: newTitle }
          : s
      ))
      
      console.log("✅ Session title saved")
    } catch (error) {
      console.error("❌ Failed to save session title:", error)
      alert("保存会话标题失败，请重试")
    }
  }

  return (
    <div
      className={cn(
        "h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-60",
      )}
    >
      {/* 头部 */}
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

      {/* New Chat 按钮 */}
      <div className="p-3">
        <Button
          onClick={handleNewSession}
          className="w-full bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
        >
          <Plus className="h-4 w-4" />
          {!collapsed && <span className="ml-2">New Chat</span>}
        </Button>
      </div>

      {/* 会话列表 */}
      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1">
          <div className="flex items-center justify-between px-2 py-2">
            {!collapsed && <div className="text-xs font-medium text-sidebar-muted-foreground">Recent Chats</div>}
            {!collapsed && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={handleRefresh}
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
                  session.is_active
                    ? "bg-sidebar-accent ring-2 ring-primary/20"
                    : "hover:bg-sidebar-accent/50"
                )}
                onClick={() => handleSelectSession(session.session_id)}
              >
                <MessageSquare className={cn(
                  "h-4 w-4 shrink-0",
                  session.is_active ? "text-primary" : "text-sidebar-foreground"
                )} />
                {!collapsed && (
                  <>
                    <div className="flex-1 min-w-0 mr-8">
                      <SessionTitleEditor
                        sessionId={session.session_id}
                        title={session.last_message + (session.is_local ? " (新建)" : "")}
                        onSave={handleSaveTitle}
                        className={cn(
                          session.is_active ? "text-primary font-medium" : "text-sidebar-foreground"
                        )}
                      />
                      <p className="text-xs text-sidebar-muted-foreground">
                        {session.message_count} messages
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 shrink-0 absolute right-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/10"
                      onClick={(e) => handleDeleteSession(session.session_id, e)}
                    >
                      <Trash2 className="h-3.5 w-3.5 text-destructive" />
                    </Button>
                  </>
                )}
              </div>
            ))
          )}
        </div>

        {/* Quick Access */}
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

      {/* 底部设置按钮 */}
      <div className="p-3 border-t border-sidebar-border">
        <Button 
          variant="ghost" 
          className="w-full justify-start text-sidebar-foreground"
          onClick={() => {
            setActiveTab("settings")
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

