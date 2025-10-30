"use client"

import type { Message } from "@/lib/types"
import { cn } from "@/lib/utils"
import { User, Bot } from "lucide-react"
import { MarkdownContent } from "./markdown-content"

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-3 items-start", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
          <Bot className="h-4 w-4 text-primary-foreground" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[80%] px-3 py-2 rounded-lg",
          isUser ? "bg-primary text-primary-foreground" : "bg-card text-card-foreground border border-border",
        )}
      >
        {/* 用户消息: 简单文本 | AI消息: Markdown渲染 */}
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed m-0">{message.content}</p>
        ) : (
          <MarkdownContent content={message.content} className="text-sm" />
        )}
        {message.files && message.files.length > 0 && (
          <div className="mt-2 space-y-2">
            {message.files.map((file) => (
              <div key={file.id} className="text-xs bg-background/10 rounded p-2">
                {file.name}
              </div>
            ))}
          </div>
        )}
        <div className="text-xs opacity-60 mt-1.5">{message.timestamp.toLocaleTimeString()}</div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
          <User className="h-4 w-4 text-secondary-foreground" />
        </div>
      )}
    </div>
  )
}
