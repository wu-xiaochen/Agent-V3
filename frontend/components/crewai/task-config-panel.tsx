"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface TaskConfig {
  id: string
  description: string
  expected_output: string
  agent?: string
  async_execution?: boolean
  context?: string[]
  tools?: string[]
}

interface TaskConfigPanelProps {
  task: TaskConfig
  availableAgents: Array<{ id: string; name: string; role: string }>
  onSave: (task: TaskConfig) => void
  onClose: () => void
}

export function TaskConfigPanel({ 
  task, 
  availableAgents,
  onSave, 
  onClose 
}: TaskConfigPanelProps) {
  const [formData, setFormData] = useState<TaskConfig>(task)

  useEffect(() => {
    setFormData(task)
  }, [task])

  const handleChange = (field: keyof TaskConfig, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSave = () => {
    onSave(formData)
    onClose()
  }

  return (
    <div className="fixed inset-y-0 right-0 w-[400px] bg-background border-l shadow-lg z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Task Configuration</h3>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="h-[calc(100vh-140px)]">
        <div className="p-4 space-y-4">
          {/* Basic Info */}
          <div className="space-y-3">
            <div>
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange("description", e.target.value)}
                placeholder="Describe what this task should accomplish..."
                rows={4}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Clear instructions for the agent to follow
              </p>
            </div>

            <div>
              <Label htmlFor="expected_output">Expected Output *</Label>
              <Textarea
                id="expected_output"
                value={formData.expected_output}
                onChange={(e) => handleChange("expected_output", e.target.value)}
                placeholder="What should the final output look like?"
                rows={3}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Define the expected result format
              </p>
            </div>
          </div>

          <Separator />

          {/* Agent Assignment */}
          <div className="space-y-3">
            <div>
              <Label htmlFor="agent">Assigned Agent *</Label>
              <Select
                value={formData.agent}
                onValueChange={(value) => handleChange("agent", value)}
              >
                <SelectTrigger id="agent">
                  <SelectValue placeholder="Select an agent..." />
                </SelectTrigger>
                <SelectContent>
                  {availableAgents.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground text-center">
                      No agents available
                    </div>
                  ) : (
                    availableAgents.map(agent => (
                      <SelectItem key={agent.id} value={agent.id}>
                        <div className="flex flex-col">
                          <span className="font-medium">{agent.name}</span>
                          <span className="text-xs text-muted-foreground">
                            {agent.role}
                          </span>
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              {availableAgents.length === 0 && (
                <p className="text-xs text-destructive mt-1">
                  Please create at least one agent first
                </p>
              )}
            </div>
          </div>

          <Separator />

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h4 className="font-semibold text-sm">Advanced Settings</h4>

            <div>
              <Label htmlFor="context">Context</Label>
              <Textarea
                id="context"
                value={formData.context?.join("\n") || ""}
                onChange={(e) => handleChange("context", e.target.value.split("\n").filter(Boolean))}
                placeholder="Additional context for this task (one per line)..."
                rows={3}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Background information or constraints
              </p>
            </div>

            <div>
              <Label htmlFor="tools">Tools</Label>
              <Input
                id="tools"
                value={formData.tools?.join(", ") || ""}
                onChange={(e) => handleChange("tools", e.target.value.split(",").map(t => t.trim()).filter(Boolean))}
                placeholder="tool1, tool2, tool3..."
              />
              <p className="text-xs text-muted-foreground mt-1">
                Specific tools for this task (comma-separated)
              </p>
            </div>
          </div>
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-background">
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="flex-1"
            disabled={!formData.description || !formData.expected_output || !formData.agent}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  )
}
