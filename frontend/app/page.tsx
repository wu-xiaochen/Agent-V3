"use client"

import { useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { SessionsSidebar } from "@/components/sessions-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { ToolPanel } from "@/components/tool-panel"
import { useAppStore } from "@/lib/store"

export default function Home() {
  const { darkMode } = useAppStore()

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [darkMode])

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <SessionsSidebar />
      <ChatInterface />
      <ToolPanel />
    </div>
  )
}
