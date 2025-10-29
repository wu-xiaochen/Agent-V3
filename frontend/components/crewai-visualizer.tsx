"use client"

import { useState } from "react"
import { Play, Square, RotateCcw, Plus, Trash2, Edit, Save, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"

interface Agent {
  id: string
  role: string
  goal: string
  tools: string[]
  status: "idle" | "running" | "completed" | "error"
}

export function CrewAIVisualizer() {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: "agent-1",
      role: "Research Analyst",
      goal: "Gather and analyze information from various sources",
      tools: ["Web Search", "Document Reader"],
      status: "idle",
    },
    {
      id: "agent-2",
      role: "Content Writer",
      goal: "Create engaging content based on research",
      tools: ["Text Generator", "Grammar Check"],
      status: "idle",
    },
  ])

  const [isRunning, setIsRunning] = useState(false)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [editingAgentId, setEditingAgentId] = useState<string | null>(null)
  const [newAgentData, setNewAgentData] = useState({ role: "", goal: "", tools: "" })
  const [runParams, setRunParams] = useState({ maxIterations: 5, temperature: 0.7, userInput: "" })
  const [executionLogs, setExecutionLogs] = useState<string[]>([])

  const handleRun = () => {
    if (!runParams.userInput.trim()) {
      alert("请输入执行任务描述")
      return
    }
    
    setIsRunning(true)
    setExecutionLogs([])
    setAgents((prev) => prev.map((agent) => ({ ...agent, status: "running" as const })))

    // 模拟执行过程
    let logIndex = 0
    const logs = [
      `🚀 开始执行任务: ${runParams.userInput}`,
      `📝 参数: 最大迭代=${runParams.maxIterations}, 温度=${runParams.temperature}`,
      `🤖 激活 Agent 1: ${agents[0]?.role}`,
      `🔍 ${agents[0]?.role} 开始执行任务...`,
      `✅ ${agents[0]?.role} 完成任务`,
    ]
    
    if (agents[1]) {
      logs.push(`🤖 激活 Agent 2: ${agents[1].role}`)
      logs.push(`📝 ${agents[1].role} 开始执行任务...`)
      logs.push(`✅ ${agents[1].role} 完成任务`)
    }
    
    logs.push(`🎉 所有任务执行完成！`)

    const logInterval = setInterval(() => {
      if (logIndex < logs.length) {
        setExecutionLogs((prev) => [...prev, logs[logIndex]])
        logIndex++
      } else {
        clearInterval(logInterval)
        setAgents((prev) => prev.map((agent) => ({ ...agent, status: "completed" as const })))
        setIsRunning(false)
      }
    }, 800)
  }

  const handleStop = () => {
    setIsRunning(false)
    setAgents((prev) => prev.map((agent) => ({ ...agent, status: "idle" as const })))
    setExecutionLogs((prev) => [...prev, "⚠️ 执行已停止"])
  }

  const handleReset = () => {
    setAgents((prev) => prev.map((agent) => ({ ...agent, status: "idle" as const })))
    setExecutionLogs([])
    setRunParams({ ...runParams, userInput: "" })
  }

  const handleAddAgent = () => {
    if (!newAgentData.role || !newAgentData.goal) {
      alert("请填写 Agent 角色和目标")
      return
    }
    
    const newAgent: Agent = {
      id: `agent-${Date.now()}`,
      role: newAgentData.role,
      goal: newAgentData.goal,
      tools: newAgentData.tools.split(",").map((t) => t.trim()).filter(Boolean),
      status: "idle",
    }
    
    setAgents([...agents, newAgent])
    setIsAddDialogOpen(false)
    setNewAgentData({ role: "", goal: "", tools: "" })
  }

  const handleDeleteAgent = (agentId: string) => {
    if (confirm("确定要删除这个 Agent 吗？")) {
      setAgents(agents.filter((a) => a.id !== agentId))
    }
  }

  const handleEditAgent = (agentId: string) => {
    const agent = agents.find((a) => a.id === agentId)
    if (agent) {
      setEditingAgentId(agentId)
      setNewAgentData({
        role: agent.role,
        goal: agent.goal,
        tools: agent.tools.join(", "),
      })
    }
  }

  const handleSaveEdit = () => {
    if (editingAgentId) {
      setAgents(
        agents.map((a) =>
          a.id === editingAgentId
            ? {
                ...a,
                role: newAgentData.role,
                goal: newAgentData.goal,
                tools: newAgentData.tools.split(",").map((t) => t.trim()).filter(Boolean),
              }
            : a
        )
      )
      setEditingAgentId(null)
      setNewAgentData({ role: "", goal: "", tools: "" })
    }
  }

  const handleCancelEdit = () => {
    setEditingAgentId(null)
    setNewAgentData({ role: "", goal: "", tools: "" })
  }

  const getStatusColor = (status: Agent["status"]) => {
    switch (status) {
      case "idle":
        return "bg-muted text-muted-foreground"
      case "running":
        return "bg-primary text-primary-foreground animate-pulse"
      case "completed":
        return "bg-green-500 text-white"
      case "error":
        return "bg-destructive text-destructive-foreground"
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-card-foreground">CrewAI Teams</h3>
        <div className="flex gap-2">
          {!isRunning ? (
            <Button size="sm" onClick={handleRun} className="bg-primary text-primary-foreground" disabled={agents.length === 0}>
              <Play className="h-3 w-3 mr-1" />
              Run
            </Button>
          ) : (
            <Button size="sm" variant="destructive" onClick={handleStop}>
              <Square className="h-3 w-3 mr-1" />
              Stop
            </Button>
          )}
          <Button size="sm" variant="outline" onClick={handleReset} disabled={isRunning}>
            <RotateCcw className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* 执行任务输入 */}
      <div className="space-y-2">
        <Label htmlFor="task-input" className="text-sm font-medium">
          任务描述
        </Label>
        <Textarea
          id="task-input"
          placeholder="描述您希望 CrewAI 团队完成的任务..."
          value={runParams.userInput}
          onChange={(e) => setRunParams({ ...runParams, userInput: e.target.value })}
          className="min-h-[60px]"
          disabled={isRunning}
        />
      </div>

      {/* Agent列表 */}
      <ScrollArea className="max-h-[300px]">
        <div className="space-y-3 pr-3">
          {agents.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm py-6">
              暂无 Agent，点击下方添加按钮创建
            </div>
          ) : (
            agents.map((agent, index) => (
              <Card key={agent.id} className="p-4 space-y-3">
                {editingAgentId === agent.id ? (
                  // 编辑模式
                  <div className="space-y-3">
                    <div>
                      <Label className="text-xs">角色</Label>
                      <Input
                        value={newAgentData.role}
                        onChange={(e) => setNewAgentData({ ...newAgentData, role: e.target.value })}
                        className="h-8 mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-xs">目标</Label>
                      <Textarea
                        value={newAgentData.goal}
                        onChange={(e) => setNewAgentData({ ...newAgentData, goal: e.target.value })}
                        className="min-h-[60px] mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-xs">工具 (逗号分隔)</Label>
                      <Input
                        value={newAgentData.tools}
                        onChange={(e) => setNewAgentData({ ...newAgentData, tools: e.target.value })}
                        className="h-8 mt-1"
                        placeholder="Tool1, Tool2, Tool3"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={handleSaveEdit} className="flex-1">
                        <Save className="h-3 w-3 mr-1" />
                        保存
                      </Button>
                      <Button size="sm" variant="outline" onClick={handleCancelEdit} className="flex-1">
                        <X className="h-3 w-3 mr-1" />
                        取消
                      </Button>
                    </div>
                  </div>
                ) : (
                  // 显示模式
                  <>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-sm text-card-foreground">{agent.role}</h4>
                          <Badge className={getStatusColor(agent.status)}>{agent.status}</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">{agent.goal}</p>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => handleEditAgent(agent.id)}
                          disabled={isRunning}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => handleDeleteAgent(agent.id)}
                          disabled={isRunning}
                        >
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-xs text-muted-foreground">工具</Label>
                      <div className="flex flex-wrap gap-1">
                        {agent.tools.length > 0 ? (
                          agent.tools.map((tool) => (
                            <Badge key={tool} variant="outline" className="text-xs">
                              {tool}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-xs text-muted-foreground">暂无工具</span>
                        )}
                      </div>
                    </div>

                    {index < agents.length - 1 && (
                      <div className="flex justify-center pt-2">
                        <div className="w-px h-4 bg-border" />
                      </div>
                    )}
                  </>
                )}
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      {/* 添加Agent按钮和对话框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <Button 
          variant="outline" 
          className="w-full bg-transparent" 
          size="sm"
          onClick={() => setIsAddDialogOpen(true)}
          disabled={isRunning}
        >
          <Plus className="h-3 w-3 mr-1" />
          添加 Agent
        </Button>
        
        <DialogContent>
          <DialogHeader>
            <DialogTitle>添加新 Agent</DialogTitle>
            <DialogDescription>
              配置新的 Agent 角色、目标和工具
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="new-role">角色</Label>
              <Input
                id="new-role"
                placeholder="例如: Research Analyst"
                value={newAgentData.role}
                onChange={(e) => setNewAgentData({ ...newAgentData, role: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-goal">目标</Label>
              <Textarea
                id="new-goal"
                placeholder="描述这个 Agent 的主要目标..."
                value={newAgentData.goal}
                onChange={(e) => setNewAgentData({ ...newAgentData, goal: e.target.value })}
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-tools">工具 (逗号分隔)</Label>
              <Input
                id="new-tools"
                placeholder="Web Search, Document Reader, Calculator"
                value={newAgentData.tools}
                onChange={(e) => setNewAgentData({ ...newAgentData, tools: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleAddAgent}>
              <Plus className="h-4 w-4 mr-2" />
              添加
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 执行参数 */}
      <div className="space-y-3 pt-4 border-t border-border">
        <h4 className="font-medium text-sm text-card-foreground">执行参数</h4>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="max-iterations" className="text-xs">
              最大迭代次数
            </Label>
            <Input
              id="max-iterations"
              type="number"
              value={runParams.maxIterations}
              onChange={(e) => setRunParams({ ...runParams, maxIterations: parseInt(e.target.value) })}
              className="h-8 mt-1"
              disabled={isRunning}
            />
          </div>
          <div>
            <Label htmlFor="temperature" className="text-xs">
              Temperature
            </Label>
            <Input
              id="temperature"
              type="number"
              step="0.1"
              value={runParams.temperature}
              onChange={(e) => setRunParams({ ...runParams, temperature: parseFloat(e.target.value) })}
              className="h-8 mt-1"
              disabled={isRunning}
            />
          </div>
        </div>
      </div>

      {/* 执行日志 */}
      {executionLogs.length > 0 && (
        <div className="space-y-2 pt-4 border-t border-border">
          <h4 className="font-medium text-sm text-card-foreground">执行日志</h4>
          <ScrollArea className="h-[150px] w-full rounded-md border border-border p-3">
            <div className="space-y-1">
              {executionLogs.map((log, index) => (
                <div key={index} className="text-xs font-mono text-muted-foreground">
                  {log}
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      )}
    </div>
  )
}
