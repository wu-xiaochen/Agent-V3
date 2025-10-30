"use client"

import { memo } from "react"
import { Handle, Position, NodeProps } from "reactflow"
import { Bot } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export const AgentNode = memo(({ data, selected }: NodeProps) => {
  const agent = data.agent

  return (
    <Card className={`min-w-[200px] ${selected ? "ring-2 ring-primary" : ""}`}>
      <Handle type="target" position={Position.Top} />
      
      <CardHeader className="p-3 pb-2">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-primary" />
          <span className="font-semibold text-sm">{agent?.name || data.label}</span>
        </div>
      </CardHeader>
      
      <CardContent className="p-3 pt-0 space-y-2">
        {agent?.role && (
          <div className="text-xs">
            <span className="text-muted-foreground">Role:</span> {agent.role}
          </div>
        )}
        {agent?.tools && agent.tools.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {agent.tools.slice(0, 3).map((tool) => (
              <Badge key={tool} variant="secondary" className="text-xs">
                {tool}
              </Badge>
            ))}
            {agent.tools.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{agent.tools.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
      
      <Handle type="source" position={Position.Bottom} />
    </Card>
  )
})

AgentNode.displayName = "AgentNode"

