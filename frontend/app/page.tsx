"use client"

import { useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { ToolPanel } from "@/components/tool-panel"
import { useAppStore } from "@/lib/store"
import { cn } from "@/lib/utils"

export default function Home() {
  const { darkMode, crewDrawerOpen } = useAppStore()

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [darkMode])

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar - Crew画布打开时收缩 */}
      <div className={cn(
        "transition-all duration-300",
        crewDrawerOpen ? "w-16" : "w-64"
      )}>
        <Sidebar collapsed={crewDrawerOpen} />
      </div>
      
      {/* ChatInterface - Crew画布打开时缩窄到60% */}
      <div className={cn(
        "flex-1 transition-all duration-300",
        crewDrawerOpen ? "max-w-[60%]" : "flex-1"
      )}>
        <ChatInterface />
      </div>
      
      {/* ToolPanel - 独立的面板 */}
      <ToolPanel />
    </div>
  )
}
