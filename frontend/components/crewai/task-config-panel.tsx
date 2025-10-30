"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import type { CrewTask, CrewAgent } from "@/lib/types/crewai"

interface TaskConfigPanelProps {
  task: CrewTask
  agents: CrewAgent[]
  onUpdate: (task: CrewTask) => void
  onClose: () => void
}

export function TaskConfigPanel({ task, agents, onUpdate, onClose }: TaskConfigPanelProps) {
  const [localTask, setLocalTask] = useState<CrewTask>(task)

  useEffect(() => {
    setLocalTask(task)
  }, [task])

  const handleChange = (field: keyof CrewTask, value: any) => {
    const updated = { ...localTask, [field]: value }
    setLocalTask(updated)
    onUpdate(updated)  // 实时更新
  }

  return (
    <Card className="absolute top-4 right-4 w-96 max-h-[80vh] bg-background/95 backdrop-blur shadow-lg border-2">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Task Configuration</h3>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="h-[calc(80vh-60px)]">
        <div className="p-4 space-y-4">
          {/* 基本信息 */}
          <div className="space-y-3">
            <div>
              <Label>Description *</Label>
              <Textarea
                value={localTask.description}
                onChange={(e) => handleChange("description", e.target.value)}
                placeholder="Describe what this task should accomplish"
                rows={4}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Clear and specific task description
              </p>
            </div>

            <div>
              <Label>Expected Output *</Label>
              <Textarea
                value={localTask.expectedOutput}
                onChange={(e) => handleChange("expectedOutput", e.target.value)}
                placeholder="What should the output look like?"
                rows={3}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Define the expected format and content
              </p>
            </div>
          </div>

          <Separator />

          {/* Agent分配 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Agent Assignment</h4>

            <div>
              <Label>Assigned Agent *</Label>
              <Select
                value={localTask.agent}
                onValueChange={(value) => handleChange("agent", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select an agent" />
                </SelectTrigger>
                <SelectContent>
                  {agents.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No agents available
                    </SelectItem>
                  ) : (
                    agents.map((agent) => (
                      <SelectItem key={agent.id} value={agent.id}>
                        {agent.name} ({agent.role})
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                Which agent will execute this task
              </p>
            </div>
          </div>

          <Separator />

          {/* 依赖关系 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Dependencies</h4>
            <div className="text-sm text-muted-foreground">
              {localTask.dependencies.length > 0
                ? `Depends on: ${localTask.dependencies.join(", ")}`
                : "No dependencies"}
            </div>
            <p className="text-xs text-muted-foreground">
              Connect tasks in the canvas to define dependencies
            </p>
          </div>

          <Separator />

          {/* 工具配置 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Task-Specific Tools</h4>
            <div className="text-sm text-muted-foreground">
              {localTask.tools && localTask.tools.length > 0
                ? `Tools: ${localTask.tools.join(", ")}`
                : "Using agent's default tools"}
            </div>
            <p className="text-xs text-muted-foreground">
              Optional: Override agent's tools for this specific task
            </p>
          </div>

          <Separator />

          {/* 高级设置 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Advanced Settings</h4>

            <div className="flex items-center justify-between">
              <div>
                <Label>Async Execution</Label>
                <p className="text-xs text-muted-foreground">Run task asynchronously</p>
              </div>
              <Switch
                checked={localTask.async || false}
                onCheckedChange={(checked) => handleChange("async", checked)}
              />
            </div>
          </div>

          {/* ID显示 */}
          <div className="pt-4 border-t text-xs text-muted-foreground">
            <div>ID: {localTask.id}</div>
          </div>
        </div>
      </ScrollArea>
    </Card>
  )
}

