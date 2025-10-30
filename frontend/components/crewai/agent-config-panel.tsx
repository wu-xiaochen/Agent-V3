"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"

interface AgentConfig {
  id: string
  name: string
  role: string
  goal: string
  backstory: string
  verbose?: boolean
  allow_delegation?: boolean
  max_iter?: number
  memory?: boolean
  tools?: string[]
}

interface AgentConfigPanelProps {
  agent: AgentConfig
  onSave: (agent: AgentConfig) => void
  onClose: () => void
}

export function AgentConfigPanel({ agent, onSave, onClose }: AgentConfigPanelProps) {
  const [formData, setFormData] = useState<AgentConfig>(agent)
  const [newTool, setNewTool] = useState("")

  useEffect(() => {
    setFormData(agent)
  }, [agent])

  const handleChange = (field: keyof AgentConfig, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleAddTool = () => {
    if (newTool.trim() && !formData.tools?.includes(newTool.trim())) {
      setFormData(prev => ({
        ...prev,
        tools: [...(prev.tools || []), newTool.trim()]
      }))
      setNewTool("")
    }
  }

  const handleRemoveTool = (tool: string) => {
    setFormData(prev => ({
      ...prev,
      tools: (prev.tools || []).filter(t => t !== tool)
    }))
  }

  const handleSave = () => {
    onSave(formData)
    onClose()
  }

  return (
    <div className="fixed inset-y-0 right-0 w-[400px] bg-background border-l shadow-lg z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Agent Configuration</h3>
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
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                placeholder="Agent Name"
              />
            </div>

            <div>
              <Label htmlFor="role">Role *</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => handleChange("role", e.target.value)}
                placeholder="e.g. Senior Data Analyst"
                required
              />
            </div>

            <div>
              <Label htmlFor="goal">Goal *</Label>
              <Textarea
                id="goal"
                value={formData.goal}
                onChange={(e) => handleChange("goal", e.target.value)}
                placeholder="What is this agent's objective?"
                rows={3}
                required
              />
            </div>

            <div>
              <Label htmlFor="backstory">Backstory *</Label>
              <Textarea
                id="backstory"
                value={formData.backstory}
                onChange={(e) => handleChange("backstory", e.target.value)}
                placeholder="Agent's background and expertise"
                rows={4}
                required
              />
            </div>
          </div>

          <Separator />

          {/* Tools */}
          <div className="space-y-3">
            <Label>Tools</Label>
            <div className="flex gap-2">
              <Input
                value={newTool}
                onChange={(e) => setNewTool(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddTool()}
                placeholder="Add tool name..."
              />
              <Button onClick={handleAddTool} size="sm">
                Add
              </Button>
            </div>
            {formData.tools && formData.tools.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tools.map(tool => (
                  <Badge
                    key={tool}
                    variant="secondary"
                    className="cursor-pointer"
                    onClick={() => handleRemoveTool(tool)}
                  >
                    {tool}
                    <X className="ml-1 h-3 w-3" />
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <Separator />

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h4 className="font-semibold text-sm">Advanced Settings</h4>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Verbose Mode</Label>
                <p className="text-xs text-muted-foreground">
                  Show detailed execution logs
                </p>
              </div>
              <Switch
                checked={formData.verbose ?? false}
                onCheckedChange={(checked) => handleChange("verbose", checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Allow Delegation</Label>
                <p className="text-xs text-muted-foreground">
                  Can delegate tasks to other agents
                </p>
              </div>
              <Switch
                checked={formData.allow_delegation ?? false}
                onCheckedChange={(checked) => handleChange("allow_delegation", checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Memory</Label>
                <p className="text-xs text-muted-foreground">
                  Remember conversation history
                </p>
              </div>
              <Switch
                checked={formData.memory ?? true}
                onCheckedChange={(checked) => handleChange("memory", checked)}
              />
            </div>

            <div>
              <Label htmlFor="max_iter">Max Iterations</Label>
              <Input
                id="max_iter"
                type="number"
                value={formData.max_iter ?? 15}
                onChange={(e) => handleChange("max_iter", parseInt(e.target.value))}
                min={1}
                max={100}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum number of iterations before stopping (1-100)
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
            disabled={!formData.role || !formData.goal || !formData.backstory}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  )
}
