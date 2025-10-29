"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, Loader2, ChevronDown, ChevronUp, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { MessageBubble } from "./message-bubble"
import { Card } from "@/components/ui/card"

// ✅ 修复：工具调用状态组件 - 正确的折叠逻辑
function ToolCallStatus({ toolCalls, isThinking }: { toolCalls: any[]; isThinking: boolean }) {
  const [isExpanded, setIsExpanded] = useState(true)

  // ✅ 修复：正确的条件判断 - 只有在没有内容时才隐藏
  if (!isThinking && toolCalls.length === 0) return null

  return (
    <Card className="p-3 my-2 bg-muted/50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {isThinking && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
          <span className="text-sm font-medium text-muted-foreground">
            {isThinking ? "🤔 AI正在思考..." : "✅ 工具调用完成"}
          </span>
        </div>
        {/* ✅ 修复：只在有工具调用时显示折叠按钮 */}
        {toolCalls.length > 0 && (
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </Button>
        )}
      </div>

      {/* ✅ 修复：只在展开且有工具调用时显示内容 */}
      {isExpanded && toolCalls.length > 0 && (
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
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, addMessage, currentSession } = useAppStore()

  // ✅ 修复：使用 scrollIntoView 确保滚动生效
  useEffect(() => {
    // 使用 requestAnimationFrame 确保 DOM 已完成渲染
    requestAnimationFrame(() => {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ 
          behavior: 'smooth',
          block: 'end'
        })
      }
    })
  }, [messages, toolCalls, isThinking])

  const handleStop = () => {
    if (abortController) {
      console.log("🛑 Stopping AI execution...")
      abortController.abort()
      setAbortController(null)
      setIsLoading(false)
      setIsThinking(false)
      setToolCalls([])
      
      const stopMessage = {
        id: `msg-${Date.now()}-stop`,
        role: "assistant" as const,
        content: "⚠️ 任务已被用户停止",
        timestamp: new Date(),
      }
      addMessage(stopMessage)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    // ✅ 修复：构建包含文档附件的消息
    const attachments = uploadedFiles
      .filter(f => f.status === 'success')
      .map(f => ({
        id: f.id,
        name: f.file.name,
        type: f.type,
        url: f.url || '',
        size: f.file.size,
        parsed_content: f.parsed
      }))

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: "user" as const,
      content: input,
      timestamp: new Date(),
      files: attachments.length > 0 ? attachments : undefined
    }

    addMessage(userMessage)
    const messageContent = input
    setInput("")
    setIsLoading(true)
    setIsThinking(true)
    setToolCalls([])
    
    // ✅ 清空已上传的文件（发送后）
    setUploadedFiles([])

    // 创建新的 AbortController
    const controller = new AbortController()
    setAbortController(controller)

    try {
      const { api } = await import("@/lib/api")
      
      // ✅ 修复：调用API时携带附件信息
      console.log("🚀 Sending message:", {
        session: currentSession,
        message: messageContent,
        attachments: attachments.length
      })
      
      const response = await api.chat.sendMessage(
        currentSession || "default",
        messageContent,
        {
          provider: "siliconflow",
          memory: true,
          attachments: attachments  // ✅ 传递附件给后端
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
      setAbortController(null)
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

      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
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
          
          {/* ✅ 滚动锚点 - 确保自动滚动到最底部 */}
          <div ref={messagesEndRef} className="h-1" />
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4 bg-card">
        <div className="max-w-4xl mx-auto space-y-2">
          {/* 文件附件预览 - 类似 Cursor 的简洁设计 */}
          {uploadedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 pb-2">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="inline-flex items-center gap-2 px-2.5 py-1.5 bg-muted rounded-md text-sm"
                >
                  {file.type === 'image' && file.preview ? (
                    <img src={file.preview} alt="" className="w-5 h-5 rounded object-cover" />
                  ) : (
                    <Paperclip className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  <span className="text-xs font-medium truncate max-w-[150px]">{file.file.name}</span>
                  {file.status === 'uploading' && <Loader2 className="h-3 w-3 animate-spin" />}
                  {file.status === 'success' && <span className="text-green-500 text-xs">✓</span>}
                  {file.status === 'error' && <span className="text-red-500 text-xs">✗</span>}
                  <button
                    onClick={() => {
                      const newFiles = uploadedFiles.filter(f => f.id !== file.id)
                      setUploadedFiles(newFiles)
                    }}
                    className="hover:bg-background rounded p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <div className="flex items-end gap-2">
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              multiple
              accept="image/*,.pdf,.doc,.docx,.txt,.md"
              onChange={async (e) => {
                const files = Array.from(e.target.files || [])
                if (files.length === 0) return

                // 添加到待上传列表
                const newFiles = files.map(file => ({
                  id: `file-${Date.now()}-${Math.random()}`,
                  file,
                  type: file.type.startsWith('image/') ? 'image' as const : 'document' as const,
                  status: 'uploading' as const,
                  preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
                }))
                
                setUploadedFiles(prev => [...prev, ...newFiles])

                // 上传文件
                try {
                  const { api } = await import("@/lib/api")
                  
                  for (const uploadFile of newFiles) {
                    try {
                      const result = await api.files.uploadFile(uploadFile.file, {
                        fileType: uploadFile.type
                      })

                      if (result.success) {
                        setUploadedFiles(prev =>
                          prev.map(f =>
                            f.id === uploadFile.id
                              ? { 
                                  ...f, 
                                  status: 'success' as const, 
                                  url: result.download_url,
                                  parsed: result.parsed_content
                                }
                              : f
                          )
                        )
                        
                        // 如果文档解析成功，显示解析结果
                        if (result.parsed_content) {
                          const parsedMessage = {
                            id: `msg-${Date.now()}-parsed`,
                            role: "assistant" as const,
                            content: `📄 **${result.filename}** 解析成功！\n\n` +
                                   `**类型**: ${result.parsed_content.type}\n\n` +
                                   `**内容摘要**:\n${result.parsed_content.summary}\n\n` +
                                   `💡 您可以在对话中引用这个文档的内容。`,
                            timestamp: new Date(),
                          }
                          addMessage(parsedMessage)
                        }
                      } else {
                        throw new Error(result.error || 'Upload failed')
                      }
                    } catch (error) {
                      console.error("文件上传失败:", error)
                      setUploadedFiles(prev =>
                        prev.map(f =>
                          f.id === uploadFile.id ? { ...f, status: 'error' as const } : f
                        )
                      )
                    }
                  }
                } finally {
                  if (fileInputRef.current) {
                    fileInputRef.current.value = ""
                  }
                }
              }}
            />
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => fileInputRef.current?.click()} 
              className="shrink-0"
              title="上传文件"
            >
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
            {isLoading ? (
              <Button
                onClick={handleStop}
                className="shrink-0 bg-destructive text-destructive-foreground hover:bg-destructive/90"
                size="icon"
                title="停止执行"
              >
                <X className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleSend}
                disabled={!input.trim()}
                className="shrink-0 bg-primary text-primary-foreground hover:bg-primary/90"
                size="icon"
                title="发送消息"
              >
                <Send className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

