"use client"

import { useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { ToolPanel } from "@/components/tool-panel"
import { useAppStore } from "@/lib/store"

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
      {/* Sidebar - 画布打开时收缩 */}
      <div className={`transition-all duration-300 ${crewDrawerOpen ? 'w-16' : 'w-64'}`}>
        <Sidebar collapsed={crewDrawerOpen} />
      </div>
      
      {/* Chat Interface - 画布打开时缩窄 */}
      <div className={`flex-1 transition-all duration-300 ${crewDrawerOpen ? 'max-w-[40%]' : 'max-w-full'}`}>
        <ChatInterface />
      </div>
      
      {/* Tool Panel - 不受影响 */}
      <ToolPanel />
    </div>
  )
}
