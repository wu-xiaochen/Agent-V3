"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Settings, Bot, Wrench, Database, Palette, ArrowLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

const settingsNav = [
  {
    title: "系统设置",
    href: "/settings/system",
    icon: Settings,
    description: "LLM配置、API设置、主题等"
  },
  {
    title: "Agent配置",
    href: "/settings/agents",
    icon: Bot,
    description: "管理Agent、编辑提示词"
  },
  {
    title: "工具配置",
    href: "/settings/tools",
    icon: Wrench,
    description: "启用/禁用工具、参数配置"
  },
  {
    title: "知识库",
    href: "/settings/knowledge",
    icon: Database,
    description: "管理知识库、文档上传"
  }
]

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div className="flex h-screen bg-background">
      {/* 左侧导航栏 */}
      <aside className="w-64 border-r bg-muted/10">
        <div className="flex h-full flex-col">
          {/* 头部 */}
          <div className="flex items-center justify-between p-6">
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              <h2 className="text-lg font-semibold">设置</h2>
            </div>
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          <Separator />

          {/* 导航列表 */}
          <ScrollArea className="flex-1 px-3">
            <div className="space-y-1 py-4">
              {settingsNav.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon

                return (
                  <Link key={item.href} href={item.href}>
                    <div
                      className={cn(
                        "flex items-start gap-3 rounded-lg px-3 py-3 transition-all hover:bg-accent",
                        isActive && "bg-accent"
                      )}
                    >
                      <Icon className={cn(
                        "h-5 w-5 mt-0.5 flex-shrink-0",
                        isActive ? "text-primary" : "text-muted-foreground"
                      )} />
                      <div className="flex flex-col gap-0.5">
                        <span className={cn(
                          "text-sm font-medium",
                          isActive && "text-primary"
                        )}>
                          {item.title}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {item.description}
                        </span>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          </ScrollArea>

          {/* 底部信息 */}
          <div className="border-t p-4">
            <div className="text-xs text-muted-foreground space-y-1">
              <div className="flex items-center justify-between">
                <span>版本</span>
                <span className="font-mono">v3.1.0</span>
              </div>
              <div className="flex items-center justify-between">
                <span>环境</span>
                <span className="font-mono">Development</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* 右侧内容区域 */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  )
}

