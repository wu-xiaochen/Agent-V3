"use client"

import { memo } from "react"
import { Handle, Position, NodeProps } from "reactflow"
import { CheckSquare } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

export const TaskNode = memo(({ data, selected }: NodeProps) => {
  const task = data.task

  return (
    <Card className={`min-w-[200px] ${selected ? "ring-2 ring-primary" : ""}`}>
      <Handle type="target" position={Position.Top} />
      
      <CardHeader className="p-3 pb-2">
        <div className="flex items-center gap-2">
          <CheckSquare className="h-4 w-4 text-green-600" />
          <span className="font-semibold text-sm">{data.label}</span>
        </div>
      </CardHeader>
      
      <CardContent className="p-3 pt-0">
        {task?.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">
            {task.description}
          </p>
        )}
      </CardContent>
      
      <Handle type="source" position={Position.Bottom} />
    </Card>
  )
})

TaskNode.displayName = "TaskNode"

