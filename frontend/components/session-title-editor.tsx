"use client"

import { useState, useEffect, useRef } from "react"
import { Check, X, Edit2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface SessionTitleEditorProps {
  sessionId: string
  title: string
  onSave: (sessionId: string, newTitle: string) => void
  className?: string
}

export function SessionTitleEditor({
  sessionId,
  title,
  onSave,
  className
}: SessionTitleEditorProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState(title)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isEditing])

  const handleSave = () => {
    if (editedTitle.trim() && editedTitle !== title) {
      onSave(sessionId, editedTitle.trim())
    }
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedTitle(title)
    setIsEditing(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSave()
    } else if (e.key === "Escape") {
      handleCancel()
    }
  }

  if (isEditing) {
    return (
      <div className={cn("flex items-center gap-1", className)}>
        <Input
          ref={inputRef}
          value={editedTitle}
          onChange={(e) => setEditedTitle(e.target.value)}
          onKeyDown={handleKeyDown}
          className="h-7 text-sm px-2"
          maxLength={50}
        />
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 shrink-0"
          onClick={handleSave}
        >
          <Check className="h-3 w-3 text-green-600" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 shrink-0"
          onClick={handleCancel}
        >
          <X className="h-3 w-3 text-red-600" />
        </Button>
      </div>
    )
  }

  return (
    <div className={cn("flex items-center gap-2 group/title", className)}>
      <p className="text-sm truncate flex-1">{title}</p>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0 opacity-0 group-hover/title:opacity-100 transition-opacity"
        onClick={(e) => {
          e.stopPropagation()
          setIsEditing(true)
        }}
      >
        <Edit2 className="h-3 w-3" />
      </Button>
    </div>
  )
}

