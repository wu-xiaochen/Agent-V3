"use client"

import { useState } from "react"
import { Plus, Save, Trash2, Edit2, Bot } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface Agent {
  id: string
  name: string
  description: string
  prompt: string
  model: string
  temperature: number
  tools: string[]
  enabled: boolean
  createdAt: string
}

const defaultAgents: Agent[] = [
  {
    id: "unified",
    name: "统一智能体",
    description: "通用的多功能智能体，支持所有工具",
    prompt: "你是一个专业的AI助手，擅长使用各种工具帮助用户解决问题。",
    model: "deepseek-chat",
    temperature: 0.7,
    tools: ["time", "search", "calculator", "document_generator", "crewai"],
    enabled: true,
    createdAt: "2025-10-30"
  },
  {
    id: "supply_chain",
    name: "供应链智能体",
    description: "专注于供应链管理和优化的专业智能体",
    prompt: "你是一位供应链管理专家，精通库存管理、物流优化和需求预测。",
    model: "deepseek-chat",
    temperature: 0.5,
    tools: ["time", "calculator", "document_generator", "n8n"],
    enabled: true,
    createdAt: "2025-10-20"
  }
]

export function AgentEditor() {
  const [agents, setAgents] = useState<Agent[]>(defaultAgents)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null)

  const handleSave = () => {
    if (selectedAgent) {
      setAgents(agents.map(a => a.id === selectedAgent.id ? selectedAgent : a))
      setIsEditing(false)
      // TODO: API call to save agent
    }
  }

  const handleDelete = () => {
    if (agentToDelete) {
      setAgents(agents.filter(a => a.id !== agentToDelete))
      setDeleteDialogOpen(false)
      setAgentToDelete(null)
      if (selectedAgent?.id === agentToDelete) {
        setSelectedAgent(null)
      }
      // TODO: API call to delete agent
    }
  }

  const handleCreateNew = () => {
    const newAgent: Agent = {
      id: `agent_${Date.now()}`,
      name: "新建智能体",
      description: "描述你的智能体",
      prompt: "你是一个...",
      model: "deepseek-chat",
      temperature: 0.7,
      tools: [],
      enabled: true,
      createdAt: new Date().toISOString().split('T')[0]
    }
    setAgents([...agents, newAgent])
    setSelectedAgent(newAgent)
    setIsEditing(true)
  }

  return (
    <div className="flex h-full">
      {/* 左侧列表 */}
      <div className="w-80 border-r bg-muted/10">
        <div className="p-4 border-b">
          <Dialog>
            <DialogTrigger asChild>
              <Button className="w-full" onClick={handleCreateNew}>
                <Plus className="mr-2 h-4 w-4" />
                新建 Agent
              </Button>
            </DialogTrigger>
          </Dialog>
        </div>

        <ScrollArea className="h-[calc(100%-73px)]">
          <div className="p-4 space-y-2">
            {agents.map((agent) => (
              <Card
                key={agent.id}
                className={`cursor-pointer transition-all hover:border-primary ${
                  selectedAgent?.id === agent.id ? "border-primary" : ""
                }`}
                onClick={() => {
                  setSelectedAgent(agent)
                  setIsEditing(false)
                }}
              >
                <CardHeader className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4" />
                      <CardTitle className="text-sm">{agent.name}</CardTitle>
                    </div>
                    <Badge variant={agent.enabled ? "default" : "secondary"}>
                      {agent.enabled ? "启用" : "禁用"}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">
                    {agent.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* 右侧详情 */}
      <div className="flex-1">
        {selectedAgent ? (
          <ScrollArea className="h-full">
            <div className="p-6 space-y-6">
              {/* 头部操作 */}
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold">
                  {isEditing ? "编辑 Agent" : "Agent 详情"}
                </h3>
                <div className="flex gap-2">
                  {isEditing ? (
                    <>
                      <Button variant="outline" onClick={() => setIsEditing(false)}>
                        取消
                      </Button>
                      <Button onClick={handleSave}>
                        <Save className="mr-2 h-4 w-4" />
                        保存
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button variant="outline" onClick={() => setIsEditing(true)}>
                        <Edit2 className="mr-2 h-4 w-4" />
                        编辑
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={() => {
                          setAgentToDelete(selectedAgent.id)
                          setDeleteDialogOpen(true)
                        }}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        删除
                      </Button>
                    </>
                  )}
                </div>
              </div>

              <Separator />

              {/* 基本信息 */}
              <div className="space-y-4">
                <div>
                  <Label>Agent 名称</Label>
                  <Input
                    value={selectedAgent.name}
                    disabled={!isEditing}
                    onChange={(e) =>
                      setSelectedAgent({ ...selectedAgent, name: e.target.value })
                    }
                  />
                </div>

                <div>
                  <Label>描述</Label>
                  <Textarea
                    value={selectedAgent.description}
                    disabled={!isEditing}
                    onChange={(e) =>
                      setSelectedAgent({ ...selectedAgent, description: e.target.value })
                    }
                    rows={2}
                  />
                </div>

                <div>
                  <Label>系统提示词</Label>
                  <Textarea
                    value={selectedAgent.prompt}
                    disabled={!isEditing}
                    onChange={(e) =>
                      setSelectedAgent({ ...selectedAgent, prompt: e.target.value })
                    }
                    rows={8}
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    定义 Agent 的角色、能力和行为方式
                  </p>
                </div>
              </div>

              <Separator />

              {/* 模型配置 */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold">模型配置</h4>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>LLM 模型</Label>
                    <Select
                      value={selectedAgent.model}
                      disabled={!isEditing}
                      onValueChange={(value) =>
                        setSelectedAgent({ ...selectedAgent, model: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="deepseek-chat">DeepSeek Chat</SelectItem>
                        <SelectItem value="gpt-4">GPT-4</SelectItem>
                        <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                        <SelectItem value="claude-3">Claude 3</SelectItem>
                        <SelectItem value="qwen-max">Qwen Max</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Temperature</Label>
                    <Input
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      value={selectedAgent.temperature}
                      disabled={!isEditing}
                      onChange={(e) =>
                        setSelectedAgent({
                          ...selectedAgent,
                          temperature: parseFloat(e.target.value)
                        })
                      }
                    />
                  </div>
                </div>
              </div>

              <Separator />

              {/* 工具配置 */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold">可用工具</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAgent.tools.map((tool) => (
                    <Badge key={tool} variant="secondary">
                      {tool}
                    </Badge>
                  ))}
                  {selectedAgent.tools.length === 0 && (
                    <p className="text-sm text-muted-foreground">未配置工具</p>
                  )}
                </div>
              </div>

              {/* 元数据 */}
              <Separator />
              <div className="text-xs text-muted-foreground space-y-1">
                <div>Agent ID: {selectedAgent.id}</div>
                <div>创建时间: {selectedAgent.createdAt}</div>
              </div>
            </div>
          </ScrollArea>
        ) : (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>选择一个 Agent 或创建新的 Agent</p>
            </div>
          </div>
        )}
      </div>

      {/* 删除确认对话框 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除这个 Agent 吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive">
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

