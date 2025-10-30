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
import type { CrewAgent } from "@/lib/types/crewai"

interface AgentConfigPanelProps {
  agent: CrewAgent
  onUpdate: (agent: CrewAgent) => void
  onClose: () => void
}

export function AgentConfigPanel({ agent, onUpdate, onClose }: AgentConfigPanelProps) {
  const [localAgent, setLocalAgent] = useState<CrewAgent>(agent)

  useEffect(() => {
    setLocalAgent(agent)
  }, [agent])

  const handleChange = (field: keyof CrewAgent, value: any) => {
    const updated = { ...localAgent, [field]: value }
    setLocalAgent(updated)
    onUpdate(updated)  // 实时更新
  }

  return (
    <Card className="absolute top-4 right-4 w-96 max-h-[80vh] bg-background/95 backdrop-blur shadow-lg border-2">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Agent Configuration</h3>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="h-[calc(80vh-60px)]">
        <div className="p-4 space-y-4">
          {/* 基本信息 */}
          <div className="space-y-3">
            <div>
              <Label>Name *</Label>
              <Input
                value={localAgent.name}
                onChange={(e) => handleChange("name", e.target.value)}
                placeholder="Agent name"
              />
            </div>

            <div>
              <Label>Role *</Label>
              <Input
                value={localAgent.role}
                onChange={(e) => handleChange("role", e.target.value)}
                placeholder="e.g., Data Analyst"
              />
              <p className="text-xs text-muted-foreground mt-1">
                The role of the agent in the crew
              </p>
            </div>

            <div>
              <Label>Goal *</Label>
              <Textarea
                value={localAgent.goal}
                onChange={(e) => handleChange("goal", e.target.value)}
                placeholder="What is the agent's goal?"
                rows={3}
              />
            </div>

            <div>
              <Label>Backstory</Label>
              <Textarea
                value={localAgent.backstory}
                onChange={(e) => handleChange("backstory", e.target.value)}
                placeholder="Agent's background and expertise"
                rows={4}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Provide context and personality
              </p>
            </div>
          </div>

          <Separator />

          {/* LLM配置 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">LLM Configuration</h4>

            <div>
              <Label>Model</Label>
              <Select
                value={localAgent.llm || "default"}
                onValueChange={(value) => handleChange("llm", value === "default" ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Use Crew Default</SelectItem>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="deepseek-chat">DeepSeek Chat</SelectItem>
                  <SelectItem value="claude-3">Claude 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator />

          {/* 工具配置 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Tools</h4>
            <div className="text-sm text-muted-foreground">
              Tools: {localAgent.tools.join(", ") || "None"}
            </div>
            <p className="text-xs text-muted-foreground">
              Configure tools in the Crew settings
            </p>
          </div>

          <Separator />

          {/* 高级设置 */}
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Advanced Settings</h4>

            <div className="flex items-center justify-between">
              <div>
                <Label>Verbose</Label>
                <p className="text-xs text-muted-foreground">Enable detailed logging</p>
              </div>
              <Switch
                checked={localAgent.verbose || false}
                onCheckedChange={(checked) => handleChange("verbose", checked)}
              />
            </div>

            <div>
              <Label>Max Iterations</Label>
              <Input
                type="number"
                value={localAgent.maxIter || 20}
                onChange={(e) => handleChange("maxIter", parseInt(e.target.value))}
                min={1}
                max={100}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum number of iterations
              </p>
            </div>

            <div>
              <Label>Max RPM</Label>
              <Input
                type="number"
                value={localAgent.maxRpm || 10}
                onChange={(e) => handleChange("maxRpm", parseInt(e.target.value))}
                min={1}
                max={100}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Requests per minute limit
              </p>
            </div>
          </div>

          {/* ID显示 */}
          <div className="pt-4 border-t text-xs text-muted-foreground">
            <div>ID: {localAgent.id}</div>
          </div>
        </div>
      </ScrollArea>
    </Card>
  )
}

