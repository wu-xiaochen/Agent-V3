"use client"

import { useState, useEffect } from "react"
import { Settings, Zap, CheckCircle2, XCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { api } from "@/lib/api"

interface Tool {
  name: string
  display_name: string
  type: string
  enabled: boolean
  description: string
}

export function ToolsSettings() {
  const [tools, setTools] = useState<Record<string, Tool>>({})
  const [isLoading, setIsLoading] = useState(false)

  // 加载工具列表
  const loadTools = async () => {
    setIsLoading(true)
    try {
      const response = await api.tools.listTools()
      if (response.success) {
        setTools(response.tools)
      }
    } catch (error) {
      console.error("加载工具列表失败:", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadTools()
  }, [])

  // 切换工具启用状态
  const handleToggleTool = async (toolName: string) => {
    // TODO: 调用后端API更新工具状态
    setTools({
      ...tools,
      [toolName]: {
        ...tools[toolName],
        enabled: !tools[toolName].enabled
      }
    })
  }

  const toolsList = Object.entries(tools)

  return (
    <div className="space-y-4">
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold text-foreground">Tools Configuration</h3>
          <p className="text-sm text-muted-foreground">
            Manage and configure available tools
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadTools} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="p-3">
          <div className="text-xs text-muted-foreground">Total Tools</div>
          <div className="text-2xl font-bold text-foreground">{toolsList.length}</div>
        </Card>
        <Card className="p-3">
          <div className="text-xs text-muted-foreground">Enabled</div>
          <div className="text-2xl font-bold text-green-600">
            {toolsList.filter(([_, tool]) => tool.enabled).length}
          </div>
        </Card>
        <Card className="p-3">
          <div className="text-xs text-muted-foreground">Disabled</div>
          <div className="text-2xl font-bold text-gray-400">
            {toolsList.filter(([_, tool]) => !tool.enabled).length}
          </div>
        </Card>
      </div>

      {/* 工具列表 */}
      <ScrollArea className="h-[calc(100vh-350px)]">
        <div className="space-y-3">
          {isLoading ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              Loading tools...
            </div>
          ) : toolsList.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              No tools configured
            </div>
          ) : (
            toolsList.map(([name, tool]) => (
              <Card key={name} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-2">
                        {tool.enabled ? (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-gray-400" />
                        )}
                        <h4 className="font-medium text-sm text-foreground">
                          {tool.display_name}
                        </h4>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {tool.type}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {tool.description}
                    </p>
                    <div className="text-xs text-muted-foreground font-mono">
                      {name}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <Label htmlFor={`tool-${name}`} className="text-xs">
                      {tool.enabled ? "Enabled" : "Disabled"}
                    </Label>
                    <Switch
                      id={`tool-${name}`}
                      checked={tool.enabled}
                      onCheckedChange={() => handleToggleTool(name)}
                    />
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      {/* 底部说明 */}
      <div className="p-3 bg-muted/50 rounded-lg">
        <div className="flex items-start gap-2">
          <Settings className="h-4 w-4 mt-0.5 text-muted-foreground" />
          <div className="space-y-1">
            <p className="text-xs font-medium text-foreground">Configuration Note</p>
            <p className="text-xs text-muted-foreground">
              Tool configurations are loaded from <code className="px-1 py-0.5 bg-muted rounded">config/tools/unified_tools.yaml</code>.
              Changes will take effect after restarting the agent.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

