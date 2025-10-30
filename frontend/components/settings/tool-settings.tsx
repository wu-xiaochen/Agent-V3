"use client"

import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export function ToolSettings() {
  const tools = [
    { id: "time", name: "Time Tool", enabled: true, mode: "API" },
    { id: "calculator", name: "Calculator", enabled: true, mode: "API" },
    { id: "search", name: "Web Search", enabled: false, mode: "API" },
    { id: "document_generator", name: "Document Generator", enabled: true, mode: "API" },
    { id: "crewai_generator", name: "CrewAI Generator", enabled: true, mode: "API" },
  ]

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Enable/disable tools and configure their parameters
      </p>
      
      {tools.map(tool => (
        <div key={tool.id} className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <Label className="font-semibold">{tool.name}</Label>
              <Badge variant="secondary" className="text-xs">
                {tool.mode}
              </Badge>
            </div>
          </div>
          <Switch checked={tool.enabled} />
        </div>
      ))}
    </div>
  )
}

