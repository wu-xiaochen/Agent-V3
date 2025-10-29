"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, Loader2, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { MessageBubble } from "./message-bubble"
import { Card } from "@/components/ui/card"

// 工具调用状态组件
function ToolCallStatus({ toolCalls, isThinking }: { toolCalls: any[]; isThinking: boolean }) {
  const [isExpanded, setIsExpanded] = useState(true)

  if (toolCalls.length === 0 && !isThinking) return null

  return (
    <Card className="p-3 my-2 bg-muted/50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {isThinking && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
          <span className="text-sm font-medium text-muted-foreground">
            {isThinking ? "AI正在思考..." : "工具调用完成"}
          </span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </Button>
      </div>

      {isExpanded && (
        <div className="space-y-2 text-xs">
          {toolCalls.map((call, index) => (
            <div key={index} className="flex items-start gap-2 p-2 bg-background rounded">
              <div className={`mt-0.5 h-2 w-2 rounded-full ${
                call.status === "success" ? "bg-green-500" :
                call.status === "error" ? "bg-red-500" :
                "bg-yellow-500 animate-pulse"
              }`} />
              <div className="flex-1">
                <p className="font-medium">{call.tool}</p>
                {call.input && <p className="text-muted-foreground">输入: {JSON.stringify(call.input)}</p>}
                {call.output && <p className="text-muted-foreground mt-1">输出: {call.output}</p>}
                {call.error && <p className="text-red-500 mt-1">错误: {call.error}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

export function ChatInterface() {
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [toolCalls, setToolCalls] = useState<any[]>([])
  const [isThinking, setIsThinking] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const { messages, addMessage, currentSession } = useAppStore()

  // 自动滚动到底部
  useEffect(() => {
    const scrollToBottom = () => {
      if (scrollRef.current) {
        const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]')
        if (scrollElement) {
          scrollElement.scrollTo({
            top: scrollElement.scrollHeight,
            behavior: 'smooth'
          })
        }
      }
    }
    
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        scrollToBottom()
      })
    })
    
    const timer = setTimeout(scrollToBottom, 100)
    return () => clearTimeout(timer)
  }, [messages, toolCalls])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: "user" as const,
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    const messageContent = input
    setInput("")
    setIsLoading(true)
    setIsThinking(true)
    setToolCalls([])

    try {
      const { api } = await import("@/lib/api")
      
      // 调用API
      console.log("🚀 Sending message:", {
        session: currentSession,
        message: messageContent
      })
      
      const response = await api.chat.sendMessage(
        currentSession || "default",
        messageContent,
        {
          provider: "siliconflow",
          memory: true,
        }
      )

      console.log("📥 Response received:", response)

      if (response.success) {
        // 解析响应中的工具调用信息（如果有）
        const responseText = response.response
        
        // TODO: 这里应该从后端获取真实的工具调用信息
        // 现在先模拟一下
        if (responseText.includes("CrewAI") || responseText.includes("crew")) {
          setToolCalls([
            { tool: "CrewAI Runtime", status: "running", input: { task: messageContent } },
          ])
          
          // 模拟工具调用过程
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          setToolCalls(prev => prev.map(call => ({
            ...call,
            status: "success",
            output: "CrewAI任务执行成功"
          })))
        }

        setIsThinking(false)
        
        const aiMessage = {
          id: `msg-${Date.now()}-ai`,
          role: "assistant" as const,
          content: responseText,
          timestamp: new Date(),
        }
        addMessage(aiMessage)
      } else {
        setIsThinking(false)
        const errorMessage = {
          id: `msg-${Date.now()}-error`,
          role: "assistant" as const,
          content: "抱歉，处理您的请求时出错了。请稍后重试。",
          timestamp: new Date(),
        }
        addMessage(errorMessage)
      }
    } catch (error: any) {
      console.error("❌ 发送消息失败:", error)
      console.error("Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      
      setIsThinking(false)
      setToolCalls([])
      
      const errorMessage = {
        id: `msg-${Date.now()}-error`,
        role: "assistant" as const,
        content: `❌ 无法连接到服务器。\n错误详情: ${error.message}\n请确保后端服务正在运行 (http://localhost:8000)`,
        timestamp: new Date(),
      }
      addMessage(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex flex-col h-screen">
      <div className="border-b border-border p-4 bg-card">
        <h2 className="text-lg font-semibold text-card-foreground">Chat Assistant</h2>
        <p className="text-sm text-muted-foreground">Ask me anything about your AI agents</p>
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-foreground">Welcome to AI Agent Hub</h3>
                <p className="text-muted-foreground">Start a conversation to interact with your AI agents</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => <MessageBubble key={message.id} message={message} />)}
              
              {/* 工具调用状态 */}
              {(toolCalls.length > 0 || isThinking) && (
                <ToolCallStatus toolCalls={toolCalls} isThinking={isThinking} />
              )}
            </>
          )}
          
          {isLoading && toolCalls.length === 0 && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">AI is thinking...</span>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4 bg-card">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end gap-2">
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              multiple
              onChange={async (e) => {
                const files = e.target.files
                if (!files || files.length === 0) return

                setIsLoading(true)
                try {
                  const { api } = await import("@/lib/api")
                  const uploadPromises = Array.from(files).map((file) =>
                    api.files.uploadFile(file, {
                      fileType: file.type.startsWith("image/") ? "image" : "data",
                    })
                  )

                  const results = await Promise.all(uploadPromises)
                  const successCount = results.filter((r) => r.success).length

                  const systemMessage = {
                    id: `msg-${Date.now()}-system`,
                    role: "assistant" as const,
                    content: `✅ 成功上传 ${successCount} 个文件。\n\n${results
                      .filter((r) => r.success)
                      .map((r) => `📄 ${r.filename} (${(r.size / 1024).toFixed(1)} KB)\n下载链接: ${r.download_url}`)
                      .join("\n\n")}`,
                    timestamp: new Date(),
                  }
                  addMessage(systemMessage)
                } catch (error) {
                  console.error("文件上传失败:", error)
                  const errorMessage = {
                    id: `msg-${Date.now()}-error`,
                    role: "assistant" as const,
                    content: "❌ 文件上传失败，请稍后重试。",
                    timestamp: new Date(),
                  }
                  addMessage(errorMessage)
                } finally {
                  setIsLoading(false)
                  if (fileInputRef.current) {
                    fileInputRef.current.value = ""
                  }
                }
              }}
            />
            <Button variant="outline" size="icon" onClick={() => fileInputRef.current?.click()} className="shrink-0">
              <Paperclip className="h-4 w-4" />
            </Button>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="min-h-[44px] max-h-[120px] resize-none"
              rows={1}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="shrink-0 bg-primary text-primary-foreground hover:bg-primary/90"
              size="icon"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

