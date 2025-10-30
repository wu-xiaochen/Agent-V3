"use client"

import { useState } from "react"
import { Plus, Edit, Trash2, Save, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"

interface Agent {
  id: string
  name: string
  description: string
  systemPrompt: string
  model: string
}

const DEFAULT_AGENTS: Agent[] = [
  {
    id: "unified_agent",
    name: "Unified Agent",
    description: "通用智能助手，可以处理各种任务",
    systemPrompt: "你是一个智能助手，可以帮助用户完成各种任务。你拥有多个工具，可以查询时间、进行计算、生成文档等。",
    model: "gpt-4"
  }
]

export function AgentSettings() {
  const [agents, setAgents] = useState<Agent[]>(DEFAULT_AGENTS)
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const { toast } = useToast()

  const handleSave = (agent: Agent) => {
    if (editingAgent?.id) {
      // Update existing
      setAgents(agents.map(a => a.id === agent.id ? agent : a))
      toast({ title: "Agent updated successfully" })
    } else {
      // Create new
      setAgents([...agents, { ...agent, id: `agent_${Date.now()}` }])
      toast({ title: "Agent created successfully" })
    }
    setIsDialogOpen(false)
    setEditingAgent(null)
  }

  const handleDelete = (id: string) => {
    if (agents.length <= 1) {
      toast({ 
        title: "Cannot delete", 
        description: "At least one agent must exist",
        variant: "destructive" 
      })
      return
    }
    setAgents(agents.filter(a => a.id !== id))
    toast({ title: "Agent deleted" })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          Manage AI agents and their system prompts
        </p>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingAgent(null)}>
              <Plus className="mr-2 h-4 w-4" />
              New Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <AgentForm
              agent={editingAgent}
              onSave={handleSave}
              onCancel={() => {
                setIsDialogOpen(false)
                setEditingAgent(null)
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4">
        {agents.map(agent => (
          <Card key={agent.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold">{agent.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {agent.description}
                </p>
                <div className="mt-3 p-3 bg-muted rounded-md">
                  <p className="text-xs font-mono text-muted-foreground line-clamp-3">
                    {agent.systemPrompt}
                  </p>
                </div>
                <div className="mt-2 flex gap-2 text-xs text-muted-foreground">
                  <span>Model: {agent.model}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    setEditingAgent(agent)
                    setIsDialogOpen(true)
                  }}
                >
                  <Edit className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(agent.id)}
                  disabled={agents.length <= 1}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

function AgentForm({ 
  agent, 
  onSave, 
  onCancel 
}: { 
  agent: Agent | null
  onSave: (agent: Agent) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState<Agent>(agent || {
    id: "",
    name: "",
    description: "",
    systemPrompt: "",
    model: "gpt-4"
  })

  return (
    <>
      <DialogHeader>
        <DialogTitle>{agent ? "Edit Agent" : "Create New Agent"}</DialogTitle>
        <DialogDescription>
          Configure the agent's name, description, and system prompt
        </DialogDescription>
      </DialogHeader>
      
      <div className="space-y-4 py-4">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g. Research Assistant"
          />
        </div>

        <div>
          <Label htmlFor="description">Description</Label>
          <Input
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Brief description of the agent's purpose"
          />
        </div>

        <div>
          <Label htmlFor="model">Model</Label>
          <Input
            id="model"
            value={formData.model}
            onChange={(e) => setFormData({ ...formData, model: e.target.value })}
            placeholder="e.g. gpt-4, gpt-3.5-turbo"
          />
        </div>

        <div>
          <Label htmlFor="systemPrompt">System Prompt</Label>
          <Textarea
            id="systemPrompt"
            value={formData.systemPrompt}
            onChange={(e) => setFormData({ ...formData, systemPrompt: e.target.value })}
            placeholder="Define the agent's behavior, personality, and capabilities..."
            rows={8}
            className="font-mono text-sm"
          />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button 
          onClick={() => onSave(formData)}
          disabled={!formData.name || !formData.systemPrompt}
        >
          <Save className="mr-2 h-4 w-4" />
          Save
        </Button>
      </DialogFooter>
    </>
  )
}

