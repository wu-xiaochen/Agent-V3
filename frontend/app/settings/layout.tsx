"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/lib/store"

/**
 * Settings Layout - 重定向到主页面并打开Tool Panel的Settings标签
 * 根据用户反馈，移除独立的侧边栏版本，统一使用tool-panel中的Settings
 */
export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { setToolPanelOpen, setActiveTab } = useAppStore()

  useEffect(() => {
    // 重定向到主页面并自动打开Settings标签
    setToolPanelOpen(true)
    setActiveTab("settings")
    router.push("/")
  }, [router, setToolPanelOpen, setActiveTab])

  // 在重定向期间显示加载状态
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="text-center">
        <p className="text-muted-foreground">正在跳转到设置...</p>
      </div>
    </div>
  )
}
