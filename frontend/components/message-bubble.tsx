"use client"

import type { Message } from "@/lib/types"
import { cn } from "@/lib/utils"
import { User, Bot } from "lucide-react"
import { Card } from "@/components/ui/card"

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
          <Bot className="h-4 w-4 text-primary-foreground" />
        </div>
      )}
      <Card
        className={cn(
          "max-w-[80%] p-4",
          isUser ? "bg-primary text-primary-foreground" : "bg-card text-card-foreground",
        )}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </div>
        {message.files && message.files.length > 0 && (
          <div className="mt-2 space-y-2">
            {message.files.map((file) => (
              <div key={file.id} className="text-xs bg-background/10 rounded p-2">
                {file.name}
              </div>
            ))}
          </div>
        )}
        <div className="text-xs opacity-70 mt-2">{message.timestamp.toLocaleTimeString()}</div>
      </Card>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
          <User className="h-4 w-4 text-secondary-foreground" />
        </div>
      )}
    </div>
  )
}
