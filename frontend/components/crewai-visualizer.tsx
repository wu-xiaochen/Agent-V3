"use client"

import { useState } from "react"
import { Play, Square, RotateCcw, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

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

  const handleRun = () => {
    setIsRunning(true)
    setAgents((prev) => prev.map((agent) => ({ ...agent, status: "running" as const })))

    // Simulate completion
    setTimeout(() => {
      setAgents((prev) => prev.map((agent) => ({ ...agent, status: "completed" as const })))
      setIsRunning(false)
    }, 3000)
  }

  const handleStop = () => {
    setIsRunning(false)
    setAgents((prev) => prev.map((agent) => ({ ...agent, status: "idle" as const })))
  }

  const handleReset = () => {
    setAgents((prev) => prev.map((agent) => ({ ...agent, status: "idle" as const })))
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
        <h3 className="font-semibold text-card-foreground">Agent Crew</h3>
        <div className="flex gap-2">
          {!isRunning ? (
            <Button size="sm" onClick={handleRun} className="bg-primary text-primary-foreground">
              <Play className="h-3 w-3 mr-1" />
              Run
            </Button>
          ) : (
            <Button size="sm" variant="destructive" onClick={handleStop}>
              <Square className="h-3 w-3 mr-1" />
              Stop
            </Button>
          )}
          <Button size="sm" variant="outline" onClick={handleReset}>
            <RotateCcw className="h-3 w-3" />
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        {agents.map((agent, index) => (
          <Card key={agent.id} className="p-4 space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium text-sm text-card-foreground">{agent.role}</h4>
                  <Badge className={getStatusColor(agent.status)}>{agent.status}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{agent.goal}</p>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">Tools</Label>
              <div className="flex flex-wrap gap-1">
                {agent.tools.map((tool) => (
                  <Badge key={tool} variant="outline" className="text-xs">
                    {tool}
                  </Badge>
                ))}
              </div>
            </div>

            {index < agents.length - 1 && (
              <div className="flex justify-center">
                <div className="w-px h-4 bg-border" />
              </div>
            )}
          </Card>
        ))}
      </div>

      <Button variant="outline" className="w-full bg-transparent" size="sm">
        <Plus className="h-3 w-3 mr-1" />
        Add Agent
      </Button>

      <div className="space-y-3 pt-4 border-t border-border">
        <h4 className="font-medium text-sm text-card-foreground">Parameters</h4>
        <div className="space-y-2">
          <div>
            <Label htmlFor="max-iterations" className="text-xs">
              Max Iterations
            </Label>
            <Input id="max-iterations" type="number" defaultValue={5} className="h-8" />
          </div>
          <div>
            <Label htmlFor="temperature" className="text-xs">
              Temperature
            </Label>
            <Input id="temperature" type="number" step="0.1" defaultValue={0.7} className="h-8" />
          </div>
        </div>
      </div>
    </div>
  )
}
