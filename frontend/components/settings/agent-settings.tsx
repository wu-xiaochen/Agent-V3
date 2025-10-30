"use client"

import { useState, useEffect } from "react"
import { Plus, Edit, Trash2, Save, X, RefreshCw } from "lucide-react"
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
import { agentsApi, type AgentConfig, type AgentConfigCreate, type AgentConfigUpdate } from "@/lib/api/agents"

export function AgentSettings() {
  const [agents, setAgents] = useState<AgentConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [editingAgent, setEditingAgent] = useState<AgentConfig | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const { toast } = useToast()

  // 加载Agent配置
  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      setLoading(true)
      const configs = await agentsApi.getAllConfigs()
      setAgents(configs)
    } catch (error) {
      console.error('Failed to load agents:', error)
      toast({
        title: "Error",
        description: "Failed to load agent configurations",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (agent: AgentConfig | AgentConfigCreate) => {
    try {
      if (isCreating) {
        // 创建新Agent
        const created = await agentsApi.create(agent as AgentConfigCreate)
        setAgents([...agents, created])
        toast({ title: "Agent created", description: created.name })
      } else if (editingAgent) {
        // 更新现有Agent
        const updated = await agentsApi.update(editingAgent.id, agent as AgentConfigUpdate)
        setAgents(agents.map(a => a.id === updated.id ? updated : a))
        toast({ title: "Agent updated", description: updated.name })
      }
      
      setIsDialogOpen(false)
      setEditingAgent(null)
      setIsCreating(false)
    } catch (error) {
      console.error('Failed to save agent:', error)
      toast({
        title: "Error",
        description: "Failed to save agent configuration",
        variant: "destructive"
      })
    }
  }

  const handleDelete = async (id: string) => {
    if (agents.length <= 1) {
      toast({ 
        title: "Cannot delete", 
        description: "At least one agent must exist",
        variant: "destructive" 
      })
      return
    }

    try {
      await agentsApi.delete(id)
      setAgents(agents.filter(a => a.id !== id))
      toast({ title: "Agent deleted" })
    } catch (error) {
      console.error('Failed to delete agent:', error)
      toast({
        title: "Error",
        description: "Failed to delete agent",
        variant: "destructive"
      })
    }
  }

  const handleReset = async () => {
    try {
      const configs = await agentsApi.resetToDefault()
      setAgents(configs)
      toast({
        title: "Reset successful",
        description: "Agent configurations reset to default"
      })
    } catch (error) {
      console.error('Failed to reset:', error)
      toast({
        title: "Error",
        description: "Failed to reset configurations",
        variant: "destructive"
      })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Loading agent configurations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          Manage AI agents and their system prompts
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset to Default
          </Button>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setIsCreating(true)
                setEditingAgent(null)
              }}>
                <Plus className="mr-2 h-4 w-4" />
                New Agent
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <AgentForm
                agent={editingAgent}
                isCreating={isCreating}
                onSave={handleSave}
                onCancel={() => {
                  setIsDialogOpen(false)
                  setEditingAgent(null)
                  setIsCreating(false)
                }}
              />
            </DialogContent>
          </Dialog>
        </div>
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
                    {agent.system_prompt}
                  </p>
                </div>
                <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                  <span>Model: {agent.model}</span>
                  <span>Temp: {agent.temperature}</span>
                  <span>Tokens: {agent.max_tokens}</span>
                  {agent.tools && agent.tools.length > 0 && (
                    <span>Tools: {agent.tools.length}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    setEditingAgent(agent)
                    setIsCreating(false)
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
  isCreating,
  onSave, 
  onCancel 
}: { 
  agent: AgentConfig | null
  isCreating: boolean
  onSave: (agent: AgentConfig | AgentConfigCreate) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState<AgentConfigCreate>(agent || {
    name: "",
    description: "",
    system_prompt: "",
    model: "gpt-4",
    temperature: 0.7,
    max_tokens: 2000,
    tools: []
  })

  return (
    <>
      <DialogHeader>
        <DialogTitle>{isCreating ? "Create New Agent" : "Edit Agent"}</DialogTitle>
        <DialogDescription>
          Configure the agent's name, description, and system prompt
        </DialogDescription>
      </DialogHeader>
      
      <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
        <div>
          <Label htmlFor="name">Name *</Label>
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

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="temperature">Temperature</Label>
            <Input
              id="temperature"
              type="number"
              min="0"
              max="2"
              step="0.1"
              value={formData.temperature}
              onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
            />
          </div>
          <div>
            <Label htmlFor="max_tokens">Max Tokens</Label>
            <Input
              id="max_tokens"
              type="number"
              min="1"
              value={formData.max_tokens}
              onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
            />
          </div>
        </div>

        <div>
          <Label htmlFor="systemPrompt">System Prompt *</Label>
          <Textarea
            id="systemPrompt"
            value={formData.system_prompt}
            onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
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
          disabled={!formData.name || !formData.system_prompt}
        >
          <Save className="mr-2 h-4 w-4" />
          {isCreating ? "Create" : "Save"}
        </Button>
      </DialogFooter>
    </>
  )
}
