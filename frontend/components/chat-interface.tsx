"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { MessageBubble } from "./message-bubble"

export function ChatInterface() {
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const { messages, addMessage } = useAppStore()

  // 自动滚动到底部
  useEffect(() => {
    // 使用 requestAnimationFrame 确保 DOM 更新后再滚动
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
    
    // 双重延迟确保滚动
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        scrollToBottom()
      })
    })
    
    const timer = setTimeout(scrollToBottom, 100)
    return () => clearTimeout(timer)
  }, [messages])

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

    try {
      // 调用实际的 API
      const { api } = await import("@/lib/api")
      const response = await api.chat.sendMessage(
        useAppStore.getState().currentSession || "default",
        messageContent,
        {
          provider: "siliconflow",
          memory: true,
        }
      )

      if (response.success) {
        const aiMessage = {
          id: `msg-${Date.now()}-ai`,
          role: "assistant" as const,
          content: response.response,
          timestamp: new Date(),
        }
        addMessage(aiMessage)
      } else {
        // 错误处理
        const errorMessage = {
          id: `msg-${Date.now()}-error`,
          role: "assistant" as const,
          content: "抱歉，处理您的请求时出错了。请稍后重试。",
          timestamp: new Date(),
        }
        addMessage(errorMessage)
      }
    } catch (error) {
      console.error("发送消息失败:", error)
      const errorMessage = {
        id: `msg-${Date.now()}-error`,
        role: "assistant" as const,
        content: "❌ 无法连接到服务器，请确保后端服务正在运行。",
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
            messages.map((message) => <MessageBubble key={message.id} message={message} />)
          )}
          {isLoading && (
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

                  // 添加系统消息通知用户
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
