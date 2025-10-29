"use client"

import { useState, useEffect } from "react"
import { Clock, CheckCircle, XCircle, Loader2, ChevronDown, ChevronUp } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ToolCall {
  id: string
  tool_name: string
  status: "running" | "success" | "error"
  input: any
  output?: string
  error?: string
  execution_time?: number
  timestamp: Date
}

interface ToolCallHistoryProps {
  sessionId?: string
  maxItems?: number
}

export function ToolCallHistory({ sessionId, maxItems = 10 }: ToolCallHistoryProps) {
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([])
  const [isExpanded, setIsExpanded] = useState(false)
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

  // 模拟数据（实际应该从API获取）
  useEffect(() => {
    // TODO: 从API获取工具调用历史
    // const fetchHistory = async () => {
    //   const response = await api.tools.getHistory(sessionId)
    //   setToolCalls(response.data)
    // }
    // fetchHistory()
  }, [sessionId])

  const toggleItem = (id: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      running: "bg-yellow-500",
      success: "bg-green-500",
      error: "bg-red-500"
    }
    return (
      <Badge className={cn("text-xs", variants[status as keyof typeof variants] || "bg-gray-500")}>
        {status}
      </Badge>
    )
  }

  if (toolCalls.length === 0) {
    return (
      <Card className="p-4">
        <p className="text-sm text-muted-foreground text-center">暂无工具调用记录</p>
      </Card>
    )
  }

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">工具调用历史</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </Button>
      </div>

      {isExpanded && (
        <ScrollArea className="max-h-[400px]">
          <div className="space-y-2">
            {toolCalls.slice(0, maxItems).map((call) => (
              <Card
                key={call.id}
                className="p-3 cursor-pointer hover:bg-accent/50 transition-colors"
                onClick={() => toggleItem(call.id)}
              >
                <div className="flex items-start gap-2">
                  {getStatusIcon(call.status)}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm truncate">{call.tool_name}</p>
                      {getStatusBadge(call.status)}
                    </div>
                    
                    <p className="text-xs text-muted-foreground">
                      {call.timestamp.toLocaleString()}
                      {call.execution_time && ` • ${call.execution_time.toFixed(2)}s`}
                    </p>

                    {expandedItems.has(call.id) && (
                      <div className="mt-2 space-y-2 text-xs">
                        <div>
                          <p className="font-medium text-muted-foreground mb-1">输入:</p>
                          <pre className="bg-muted p-2 rounded overflow-x-auto">
                            {JSON.stringify(call.input, null, 2)}
                          </pre>
                        </div>
                        
                        {call.output && (
                          <div>
                            <p className="font-medium text-muted-foreground mb-1">输出:</p>
                            <pre className="bg-muted p-2 rounded overflow-x-auto">
                              {call.output}
                            </pre>
                          </div>
                        )}
                        
                        {call.error && (
                          <div>
                            <p className="font-medium text-destructive mb-1">错误:</p>
                            <pre className="bg-destructive/10 p-2 rounded overflow-x-auto text-destructive">
                              {call.error}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </ScrollArea>
      )}

      {!isExpanded && (
        <p className="text-xs text-muted-foreground">
          共 {toolCalls.length} 条记录，点击展开查看
        </p>
      )}
    </Card>
  )
}

