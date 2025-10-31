"use client"

import { useState, useEffect, useRef } from "react"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useAppStore } from "@/lib/store"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
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
  files?: string[]  // 文件ID列表
  onComplete?: (result: any) => void
  onError?: (error: any) => void
}

export function CrewExecutionMonitor({ 
  crewId, 
  inputs = {},
  files = [],
  onComplete,
  onError
}: CrewExecutionMonitorProps) {
  const darkMode = useAppStore(state => state.darkMode)
  const { toast } = useToast()
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
  
  // 日志过滤
  const [logFilter, setLogFilter] = useState<'all' | 'info' | 'success' | 'error' | 'warning'>('all')
  const filteredLogs = logFilter === 'all' 
    ? logs 
    : logs.filter(log => log.type === logFilter)
  
  // 🆕 日志按时间戳分组（按分钟分组）
  const groupedLogs = (() => {
    const groups: Record<string, ExecutionLog[]> = {}
    filteredLogs.forEach(log => {
      const date = new Date(log.timestamp)
      const groupKey = `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
      if (!groups[groupKey]) {
        groups[groupKey] = []
      }
      groups[groupKey].push(log)
    })
    return Object.entries(groups).map(([time, logs]) => ({ time, logs }))
  })()
  
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
        body: JSON.stringify({
          inputs,
          files  // 🆕 传递文件ID列表
        })
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

  const handleStop = async () => {
    if (executionId) {
      try {
        await api.crewai.cancelExecution(executionId)
        addLog('warning', '执行已取消')
      } catch (error: any) {
        console.error('取消执行失败:', error)
        addLog('error', `取消失败: ${error.message}`)
      }
    }
    eventSourceRef.current?.close()
    setIsRunning(false)
    setIsPaused(false)
  }
  
  const handlePause = async () => {
    if (!executionId) return
    
    try {
      const result = await api.crewai.pauseExecution(executionId)
      if (result.success) {
        setIsPaused(true)
        addLog('info', '执行已暂停')
      }
    } catch (error: any) {
      console.error('暂停执行失败:', error)
      addLog('error', `暂停失败: ${error.message}`)
    }
  }
  
  const handleResume = async () => {
    if (!executionId) return
    
    try {
      const result = await api.crewai.resumeExecution(executionId)
      if (result.success) {
        setIsPaused(false)
        addLog('info', '执行已恢复')
      }
    } catch (error: any) {
      console.error('恢复执行失败:', error)
      addLog('error', `恢复失败: ${error.message}`)
    }
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
            <>
              {!isPaused ? (
                <Button onClick={handlePause} size="sm" variant="outline">
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </Button>
              ) : (
                <Button onClick={handleResume} size="sm" variant="outline">
                  <Play className="h-4 w-4 mr-2" />
                  Resume
                </Button>
              )}
              <Button onClick={handleStop} size="sm" variant="destructive">
                <Square className="h-4 w-4 mr-2" />
                Stop
              </Button>
            </>
          )}
          
          {result && (
            <Button onClick={handleExport} size="sm" variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export JSON
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
          <div className="flex items-center gap-2">
            {/* 日志过滤器 */}
            <div className="flex gap-1">
              <Button
                size="sm"
                variant={logFilter === 'all' ? 'default' : 'outline'}
                onClick={() => setLogFilter('all')}
                className="h-7 px-2 text-xs"
              >
                All ({logs.length})
              </Button>
              <Button
                size="sm"
                variant={logFilter === 'info' ? 'default' : 'outline'}
                onClick={() => setLogFilter('info')}
                className="h-7 px-2 text-xs"
              >
                Info ({logs.filter(l => l.type === 'info').length})
              </Button>
              <Button
                size="sm"
                variant={logFilter === 'success' ? 'default' : 'outline'}
                onClick={() => setLogFilter('success')}
                className="h-7 px-2 text-xs"
              >
                Success ({logs.filter(l => l.type === 'success').length})
              </Button>
              <Button
                size="sm"
                variant={logFilter === 'error' ? 'default' : 'outline'}
                onClick={() => setLogFilter('error')}
                className="h-7 px-2 text-xs"
              >
                Error ({logs.filter(l => l.type === 'error').length})
              </Button>
            </div>
          </div>
        </div>

        <ScrollArea className="h-[300px] rounded-md border p-4">
          <div className="space-y-4">
            {groupedLogs.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                {logs.length === 0 
                  ? "No logs yet. Click Start to begin execution."
                  : `No ${logFilter} logs found.`
                }
              </p>
            ) : (
              groupedLogs.map((group, groupIndex) => (
                <div key={groupIndex} className="space-y-2 mb-4">
                  {/* 🆕 时间分组标题 */}
                  <div className="sticky top-0 bg-background/95 backdrop-blur-sm py-1 z-10">
                    <div className="text-xs font-semibold text-muted-foreground border-b pb-1">
                      {group.time}
                    </div>
                  </div>
                  
                  {/* 该时间段的日志 */}
                  <div className="space-y-1 pl-2">
                    {group.logs.map((log, index) => (
                      <div
                        key={`${groupIndex}-${index}`}
                        className={`flex gap-2 text-sm p-2 rounded hover:bg-muted/50 transition-colors ${
                          log.type === 'error' ? 'text-destructive' :
                          log.type === 'success' ? 'text-green-600' :
                          log.type === 'warning' ? 'text-yellow-600' :
                          'text-foreground'
                        }`}
                      >
                        <span className="text-muted-foreground text-xs font-mono shrink-0 w-16">
                          {new Date(log.timestamp).toLocaleTimeString('en-US', { 
                            hour12: false, 
                            hour: '2-digit', 
                            minute: '2-digit', 
                            second: '2-digit' 
                          })}
                        </span>
                        <Badge variant="outline" className="shrink-0 h-5 text-xs">
                          {log.type}
                        </Badge>
                        <span className="flex-1">{log.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Result */}
      {result && (
        <div className="mt-6 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <h4 className="text-sm font-semibold">Execution Result</h4>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  navigator.clipboard.writeText(result)
                  toast({ title: "已复制到剪贴板", duration: 2000 })
                }}
              >
                Copy
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  // 下载为JSON文件（包含完整执行信息）
                  const exportData = {
                    execution_id: executionId,
                    crew_id: crewId,
                    crew_name: crewName,
                    duration,
                    timestamp: new Date().toISOString(),
                    result,
                    logs
                  }
                  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `crew-result-${executionId || 'unknown'}.json`
                  document.body.appendChild(a)
                  a.click()
                  document.body.removeChild(a)
                  URL.revokeObjectURL(url)
                }}
              >
                Export JSON
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  // 下载为文本文件
                  const blob = new Blob([result], { type: 'text/plain' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `crew-result-${executionId || 'unknown'}.txt`
                  document.body.appendChild(a)
                  a.click()
                  document.body.removeChild(a)
                  URL.revokeObjectURL(url)
                }}
              >
                Download TXT
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  // 下载为Markdown文件
                  const markdown = `# CrewAI Execution Result\n\n**Execution ID**: ${executionId}\n**Crew Name**: ${crewName}\n**Duration**: ${duration.toFixed(2)}s\n**Timestamp**: ${new Date().toISOString()}\n\n## Result\n\n\`\`\`\n${result}\n\`\`\`\n\n## Execution Logs\n\n${logs.map(log => `- [${new Date(log.timestamp).toLocaleTimeString()}] **${log.type}**: ${log.message}`).join('\n')}`
                  const blob = new Blob([markdown], { type: 'text/markdown' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `crew-result-${executionId || 'unknown'}.md`
                  document.body.appendChild(a)
                  a.click()
                  document.body.removeChild(a)
                  URL.revokeObjectURL(url)
                }}
              >
                Download MD
              </Button>
            </div>
          </div>
          <Card className="p-4 bg-muted/50">
            <div className="space-y-3">
              {/* 尝试检测JSON并格式化 */}
              {(() => {
                try {
                  // 尝试解析为JSON - 使用语法高亮
                  const jsonMatch = result.match(/\{[\s\S]*\}|\[[\s\S]*\]/)
                  if (jsonMatch) {
                    try {
                      const parsed = JSON.parse(jsonMatch[0])
                      const jsonString = JSON.stringify(parsed, null, 2)
                      return (
                        <div className="space-y-2">
                          <div className="text-xs text-muted-foreground">Formatted JSON:</div>
                          <SyntaxHighlighter
                            language="json"
                            style={darkMode ? oneDark : vscDarkPlus}
                            customStyle={{
                              borderRadius: '0.5rem',
                              fontSize: '0.875rem',
                              margin: 0,
                            }}
                            PreTag="div"
                          >
                            {jsonString}
                          </SyntaxHighlighter>
                        </div>
                      )
                    } catch (e) {
                      // JSON解析失败，继续其他格式化
                    }
                  }
                } catch (e) {
                  // 不是JSON，继续
                }
                
                // 检测代码块 - 使用语法高亮
                const codeBlockMatch = result.match(/```(\w+)?\n([\s\S]*?)```/)
                if (codeBlockMatch) {
                  const language = codeBlockMatch[1] || 'text'
                  const code = codeBlockMatch[2].trim()
                  return (
                    <div className="space-y-2">
                      <div className="text-xs text-muted-foreground">Code Block ({language}):</div>
                      <SyntaxHighlighter
                        language={language}
                        style={darkMode ? oneDark : vscDarkPlus}
                        customStyle={{
                          borderRadius: '0.5rem',
                          fontSize: '0.875rem',
                          margin: 0,
                        }}
                        PreTag="div"
                      >
                        {code}
                      </SyntaxHighlighter>
                    </div>
                  )
                }
                
                // 普通文本，检测段落
                const paragraphs = result.split(/\n\n+/)
                if (paragraphs.length > 1) {
                  return (
                    <div className="space-y-3">
                      {paragraphs.map((para, idx) => (
                        <div key={idx} className="text-sm leading-relaxed">
                          {para.split('\n').map((line, lineIdx) => (
                            <div key={lineIdx}>{line || '\u00A0'}</div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )
                }
                
                // 单段文本
                return <pre className="text-sm whitespace-pre-wrap leading-relaxed">{result}</pre>
              })()}
            </div>
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

