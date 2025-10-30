"use client"

import { useCallback, useState } from "react"
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
} from "reactflow"
import "reactflow/dist/style.css"
import { Button } from "@/components/ui/button"
import { Plus, Play, Save, Trash2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import type { FlowNode, FlowEdge, CrewAgent, CrewTask } from "@/lib/types/crewai"

// 自定义节点组件
import { AgentNode } from "./agent-node"
import { TaskNode } from "./task-node"
import { AgentConfigPanel } from "./agent-config-panel"
import { TaskConfigPanel } from "./task-config-panel"

const nodeTypes = {
  agent: AgentNode,
  task: TaskNode,
}

interface CrewCanvasProps {
  crewId?: string
  initialNodes?: FlowNode[]
  initialEdges?: FlowEdge[]
  onSave?: (nodes: Node[], edges: Edge[]) => void
  onRun?: () => void
}

export function CrewCanvas({
  crewId,
  initialNodes = [],
  initialEdges = [],
  onSave,
  onRun,
}: CrewCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [showConfigPanel, setShowConfigPanel] = useState(false)

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds))
    },
    [setEdges]
  )

  const handleAddAgent = useCallback(() => {
    const newAgent: FlowNode = {
      id: `agent-${Date.now()}`,
      type: "agent",
      position: { x: Math.random() * 400, y: Math.random() * 300 },
      data: {
        label: "New Agent",
        description: "Agent description",
        agent: {
          id: `agent-${Date.now()}`,
          name: "New Agent",
          role: "Role",
          goal: "Goal",
          backstory: "Backstory",
          tools: [],
        },
      },
    }
    setNodes((nds) => [...nds, newAgent as Node])
  }, [setNodes])

  const handleAddTask = useCallback(() => {
    const newTask: FlowNode = {
      id: `task-${Date.now()}`,
      type: "task",
      position: { x: Math.random() * 400 + 400, y: Math.random() * 300 },
      data: {
        label: "New Task",
        description: "Task description",
        task: {
          id: `task-${Date.now()}`,
          description: "Task description",
          expectedOutput: "Expected output",
          agent: "",
          dependencies: [],
        },
      },
    }
    setNodes((nds) => [...nds, newTask as Node])
  }, [setNodes])

  const handleSave = () => {
    if (onSave) {
      onSave(nodes, edges)
    }
  }

  const handleRun = () => {
    if (onRun) {
      onRun()
    }
  }

  const handleNodeClick = (_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
    setShowConfigPanel(true)
  }

  const handleUpdateNode = (updatedData: CrewAgent | CrewTask) => {
    if (!selectedNode) return
    
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedNode.id) {
          return {
            ...node,
            data: {
              ...node.data,
              [node.type === "agent" ? "agent" : "task"]: updatedData,
              label: updatedData.name || (updatedData as CrewTask).description?.slice(0, 20) || "Untitled",
            },
          }
        }
        return node
      })
    )
  }

  const getAllAgents = (): CrewAgent[] => {
    return nodes
      .filter((n) => n.type === "agent")
      .map((n) => n.data.agent)
      .filter(Boolean)
  }

  const handleDeleteNode = useCallback(() => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id))
      setEdges((eds) => eds.filter((e) => e.source !== selectedNode.id && e.target !== selectedNode.id))
      setSelectedNode(null)
    }
  }, [selectedNode, setNodes, setEdges])

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
      >
        <Background />
        <Controls />
        <MiniMap />
        
        {/* 工具栏 */}
        <Panel position="top-left" className="space-x-2">
          <Button size="sm" onClick={handleAddAgent} variant="secondary">
            <Plus className="mr-2 h-4 w-4" />
            Add Agent
          </Button>
          <Button size="sm" onClick={handleAddTask} variant="secondary">
            <Plus className="mr-2 h-4 w-4" />
            Add Task
          </Button>
        </Panel>

        <Panel position="top-right" className="space-x-2">
          {selectedNode && (
            <Button size="sm" onClick={handleDeleteNode} variant="destructive">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          )}
          <Button size="sm" onClick={handleSave} variant="outline">
            <Save className="mr-2 h-4 w-4" />
            Save
          </Button>
          <Button size="sm" onClick={handleRun}>
            <Play className="mr-2 h-4 w-4" />
            Run Crew
          </Button>
        </Panel>
      </ReactFlow>

      {/* 配置面板 */}
      {showConfigPanel && selectedNode && (
        <>
          {selectedNode.type === "agent" && selectedNode.data.agent && (
            <AgentConfigPanel
              agent={selectedNode.data.agent}
              onUpdate={handleUpdateNode}
              onClose={() => {
                setShowConfigPanel(false)
                setSelectedNode(null)
              }}
            />
          )}
          {selectedNode.type === "task" && selectedNode.data.task && (
            <TaskConfigPanel
              task={selectedNode.data.task}
              agents={getAllAgents()}
              onUpdate={handleUpdateNode}
              onClose={() => {
                setShowConfigPanel(false)
                setSelectedNode(null)
              }}
            />
          )}
        </>
      )}
    </div>
  )
}

