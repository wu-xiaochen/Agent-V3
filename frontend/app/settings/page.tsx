"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function SettingsPage() {
  const router = useRouter()

  useEffect(() => {
    // 默认重定向到系统设置
    router.replace("/settings/system")
  }, [router])

  return null
}

