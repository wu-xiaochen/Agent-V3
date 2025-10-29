"use client"

import { useState } from "react"
import { MessageSquare, Plus, Database, Users, Settings, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { cn } from "@/lib/utils"

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { sessions, currentSession, setCurrentSession, createNewSession } = useAppStore()

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
          onClick={createNewSession}
          className="w-full bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
        >
          <Plus className="h-4 w-4" />
          {!collapsed && <span className="ml-2">New Chat</span>}
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1">
          <div className="text-xs font-medium text-sidebar-muted-foreground px-2 py-2">
            {!collapsed && "Recent Chats"}
          </div>
          {sessions.map((session) => (
            <Button
              key={session.id}
              variant={currentSession === session.id ? "secondary" : "ghost"}
              className={cn(
                "w-full justify-start text-sidebar-foreground",
                currentSession === session.id && "bg-sidebar-accent",
              )}
              onClick={() => setCurrentSession(session.id)}
            >
              <MessageSquare className="h-4 w-4 shrink-0" />
              {!collapsed && <span className="ml-2 truncate text-sm">{session.title}</span>}
            </Button>
          ))}
        </div>

        {!collapsed && (
          <>
            <div className="text-xs font-medium text-sidebar-muted-foreground px-2 py-2 mt-6">Quick Access</div>
            <div className="space-y-1">
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground">
                <Database className="h-4 w-4" />
                <span className="ml-2 text-sm">Knowledge Bases</span>
              </Button>
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground">
                <Users className="h-4 w-4" />
                <span className="ml-2 text-sm">CrewAI Teams</span>
              </Button>
            </div>
          </>
        )}
      </ScrollArea>

      <div className="p-3 border-t border-sidebar-border">
        <Button variant="ghost" className="w-full justify-start text-sidebar-foreground">
          <Settings className="h-4 w-4" />
          {!collapsed && <span className="ml-2 text-sm">Settings</span>}
        </Button>
      </div>
    </div>
  )
}
