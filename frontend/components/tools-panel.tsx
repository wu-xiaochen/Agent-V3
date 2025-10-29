"use client"

import { Wrench, CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Tool {
  id: string
  name: string
  status: "idle" | "running" | "completed" | "error"
  lastRun?: Date
}

export function ToolsPanel() {
  const tools: Tool[] = [
    { id: "tool-1", name: "Web Search", status: "idle" },
    { id: "tool-2", name: "Document Parser", status: "completed", lastRun: new Date() },
    { id: "tool-3", name: "Code Analyzer", status: "idle" },
    { id: "tool-4", name: "Image Generator", status: "idle" },
  ]

  const getStatusIcon = (status: Tool["status"]) => {
    switch (status) {
      case "idle":
        return <Wrench className="h-4 w-4 text-muted-foreground" />
      case "running":
        return <Loader2 className="h-4 w-4 text-primary animate-spin" />
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case "error":
        return <XCircle className="h-4 w-4 text-destructive" />
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-card-foreground">Available Tools</h3>

      <div className="space-y-2">
        {tools.map((tool) => (
          <Card key={tool.id} className="p-3 hover:bg-accent/50 transition-colors cursor-pointer">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getStatusIcon(tool.status)}
                <div>
                  <h4 className="font-medium text-sm text-card-foreground">{tool.name}</h4>
                  {tool.lastRun && (
                    <p className="text-xs text-muted-foreground">Last run: {tool.lastRun.toLocaleTimeString()}</p>
                  )}
                </div>
              </div>
              <Badge variant="outline" className="text-xs">
                {tool.status}
              </Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
