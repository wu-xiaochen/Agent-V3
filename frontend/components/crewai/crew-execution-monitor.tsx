"use client"

import { useState, useEffect, useRef } from "react"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Play, 
  Pause, 
  Square, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Users, 
  ListTodo,
  Clock,
  Download
} from "lucide-react"

interface ExecutionEvent {
  type: string
  timestamp: string
  [key: string]: any
}

interface ExecutionLog {
  timestamp: string
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
}

interface CrewExecutionMonitorProps {
  crewId: string
  inputs?: Record<string, any>
  onComplete?: (result: any) => void
  onError?: (error: any) => void
}

export function CrewExecutionMonitor({ 
  crewId, 
  inputs = {},
  onComplete,
  onError 
}: CrewExecutionMonitorProps) {
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [executionId, setExecutionId] = useState<string | null>(null)
  const [crewName, setCrewName] = useState<string>("")
  
  // 进度状态
  const [currentStep, setCurrentStep] = useState<string>("")
  const [progress, setProgress] = useState<number>(0)
  const [totalAgents, setTotalAgents] = useState<number>(0)
  const [totalTasks, setTotalTasks] = useState<number>(0)
  const [currentAgent, setCurrentAgent] = useState<string>("")
  const [currentTask, setCurrentTask] = useState<string>("")
  
  // 日志
  const [logs, setLogs] = useState<ExecutionLog[]>([])
  const [result, setResult] = useState<string | null>(null)
  const [duration, setDuration] = useState<number>(0)
  const [error, setError] = useState<string | null>(null)
  
  const eventSourceRef = useRef<EventSource | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  // 自动滚动到日志底部
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [logs])

  const addLog = (type: ExecutionLog['type'], message: string, timestamp?: string) => {
    setLogs(prev => [...prev, {
      timestamp: timestamp || new Date().toISOString(),
      type,
      message
    }])
  }

  const handleStart = async () => {
    try {
      setIsRunning(true)
      setError(null)
      setResult(null)
      setLogs([])
      setProgress(0)
      
      addLog('info', `开始执行Crew: ${crewId}`)
      
      // 创建EventSource连接
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const url = `${apiUrl}/api/crewai/crews/${crewId}/execute/stream`
      
      // 使用POST创建EventSource需要特殊处理
      // 这里我们使用fetch来模拟EventSource
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(inputs)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Failed to get response reader')
      }

      // 读取流式响应
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          setIsRunning(false)
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6)
            if (data.trim()) {
              try {
                const event: ExecutionEvent = JSON.parse(data)
                handleEvent(event)
              } catch (e) {
                console.error('Failed to parse event:', e)
              }
            }
          }
        }
      }
      
    } catch (error: any) {
      console.error('Execution error:', error)
      setError(error.message)
      setIsRunning(false)
      addLog('error', `执行失败: ${error.message}`)
      onError?.(error)
    }
  }

  const handleEvent = (event: ExecutionEvent) => {
    console.log('📨 Event received:', event)

    switch (event.type) {
      case 'start':
        setExecutionId(event.execution_id)
        setCrewName(event.crew_name || crewId)
        addLog('info', `Execution ID: ${event.execution_id}`, event.timestamp)
        break

      case 'status':
        setCurrentStep(event.message)
        addLog('info', event.message, event.timestamp)
        break

      case 'agent_start':
        setCurrentAgent(event.agent)
        setTotalAgents(event.total)
        addLog('info', `创建Agent [${event.index}/${event.total}]: ${event.agent}`, event.timestamp)
        break

      case 'task_start':
        setCurrentTask(event.task)
        setTotalTasks(event.total)
        addLog('info', `创建Task [${event.index}/${event.total}]: ${event.task}`, event.timestamp)
        break

      case 'progress':
        setProgress(event.percentage)
        setCurrentStep(event.step === 'agents' ? '创建Agents' : '创建Tasks')
        break

      case 'execution_start':
        setCurrentStep('执行中...')
        addLog('info', `开始执行 ${event.total_tasks} 个任务`, event.timestamp)
        break

      case 'result':
        setResult(event.output)
        setDuration(event.duration)
        setProgress(100)
        addLog('success', `✅ 执行完成！耗时: ${event.duration.toFixed(2)}秒`, event.timestamp)
        onComplete?.(event)
        break

      case 'error':
        setError(event.error)
        addLog('error', `❌ ${event.error}`, event.timestamp)
        setIsRunning(false)
        onError?.(event)
        break

      case 'done':
        setIsRunning(false)
        setCurrentStep(event.success !== false ? '完成' : '失败')
        break

      default:
        console.log('Unknown event type:', event.type)
    }
  }

  const handleStop = () => {
    eventSourceRef.current?.close()
    setIsRunning(false)
    setIsPaused(false)
    addLog('warning', '执行已停止')
  }

  const handleExport = () => {
    const exportData = {
      execution_id: executionId,
      crew_id: crewId,
      crew_name: crewName,
      duration,
      result,
      logs,
      timestamp: new Date().toISOString()
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `crew-execution-${executionId || 'unknown'}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Card className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">CrewAI Execution Monitor</h3>
          {crewName && (
            <p className="text-sm text-muted-foreground mt-1">{crewName}</p>
          )}
        </div>
        
        <div className="flex gap-2">
          {!isRunning ? (
            <Button onClick={handleStart} size="sm">
              <Play className="h-4 w-4 mr-2" />
              Start
            </Button>
          ) : (
            <Button onClick={handleStop} size="sm" variant="destructive">
              <Square className="h-4 w-4 mr-2" />
              Stop
            </Button>
          )}
          
          {result && (
            <Button onClick={handleExport} size="sm" variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Status */}
      {isRunning && (
        <div className="mb-6 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{currentStep}</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card className="p-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <div className="text-sm">
              <p className="text-muted-foreground">Agents</p>
              <p className="font-semibold">{totalAgents || '-'}</p>
            </div>
          </div>
        </Card>

        <Card className="p-3">
          <div className="flex items-center gap-2">
            <ListTodo className="h-4 w-4 text-muted-foreground" />
            <div className="text-sm">
              <p className="text-muted-foreground">Tasks</p>
              <p className="font-semibold">{totalTasks || '-'}</p>
            </div>
          </div>
        </Card>

        <Card className="p-3">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <div className="text-sm">
              <p className="text-muted-foreground">Duration</p>
              <p className="font-semibold">{duration > 0 ? `${duration.toFixed(2)}s` : '-'}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Logs */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold">Execution Logs</h4>
          <Badge variant="outline">{logs.length} entries</Badge>
        </div>

        <ScrollArea className="h-[300px] rounded-md border p-4">
          <div className="space-y-2">
            {logs.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No logs yet. Click Start to begin execution.
              </p>
            ) : (
              logs.map((log, index) => (
                <div
                  key={index}
                  className={`flex gap-2 text-sm ${
                    log.type === 'error' ? 'text-destructive' :
                    log.type === 'success' ? 'text-green-600' :
                    log.type === 'warning' ? 'text-yellow-600' :
                    'text-foreground'
                  }`}
                >
                  <span className="text-muted-foreground text-xs">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="flex-1">{log.message}</span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Result */}
      {result && (
        <div className="mt-6 space-y-2">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <h4 className="text-sm font-semibold">Execution Result</h4>
          </div>
          <Card className="p-4 bg-muted/50">
            <pre className="text-sm whitespace-pre-wrap">{result}</pre>
          </Card>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-6 space-y-2">
          <div className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-destructive" />
            <h4 className="text-sm font-semibold">Error</h4>
          </div>
          <Card className="p-4 bg-destructive/10 border-destructive/20">
            <pre className="text-sm text-destructive whitespace-pre-wrap">{error}</pre>
          </Card>
        </div>
      )}
    </Card>
  )
}

