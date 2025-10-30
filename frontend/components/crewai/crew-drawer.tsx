"use client"

import { useState, useEffect } from "react"
import { Users, X, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { CrewCanvas } from "./crew-canvas"
import type { CrewConfig } from "@/lib/types/crewai"
import { api } from "@/lib/api"
import { 
  convertCanvasToCrewConfig, 
  convertCrewConfigToCanvas,
  validateCrewConfig,
  generateCrewId
} from "@/lib/crewai/canvas-converter"
import type { Node, Edge } from "@xyflow/react"

interface CrewDrawerProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function CrewDrawer({ open, onOpenChange }: CrewDrawerProps) {
  const [crews, setCrews] = useState<CrewConfig[]>([])
  const [selectedCrew, setSelectedCrew] = useState<CrewConfig | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [loading, setLoading] = useState(false)
  const [canvasNodes, setCanvasNodes] = useState<Node[]>([])
  const [canvasEdges, setCanvasEdges] = useState<Edge[]>([])
  const { toast } = useToast()

  // 加载Crew列表
  useEffect(() => {
    if (open) {
      loadCrews()
    }
  }, [open])

  const loadCrews = async () => {
    try {
      setLoading(true)
      const result = await api.crewai.listCrews()
      if (result.success) {
        // 转换为CrewConfig格式（简化版）
        const crewList: CrewConfig[] = result.crews.map((c: any) => ({
          id: c.id,
          name: c.name,
          description: c.description,
          agents: [],
          tasks: [],
          process: "sequential",
          createdAt: c.createdAt,
          updatedAt: c.updatedAt,
        }))
        setCrews(crewList)
      }
    } catch (error) {
      console.error("加载Crew列表失败:", error)
      toast({
        title: "加载失败",
        description: "无法加载Crew列表，请稍后重试",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNew = () => {
    const newCrew: CrewConfig = {
      id: generateCrewId(),
      name: "New Crew",
      description: "Describe your crew",
      agents: [],
      tasks: [],
      process: "sequential",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    setSelectedCrew(newCrew)
    setCanvasNodes([])
    setCanvasEdges([])
    setIsCreating(true)
  }

  const handleLoadCrew = async (crewId: string) => {
    try {
      setLoading(true)
      const result = await api.crewai.getCrew(crewId)
      if (result.success && result.crew) {
        setSelectedCrew(result.crew)
        // 转换为Canvas数据
        const { nodes, edges } = convertCrewConfigToCanvas(result.crew)
        setCanvasNodes(nodes)
        setCanvasEdges(edges)
        setIsCreating(false)
      }
    } catch (error) {
      console.error("加载Crew详情失败:", error)
      toast({
        title: "加载失败",
        description: "无法加载Crew详情，请稍后重试",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!selectedCrew) return

    try {
      setLoading(true)
      
      // 从Canvas收集当前数据
      const crewConfig = convertCanvasToCrewConfig(canvasNodes, canvasEdges, {
        id: selectedCrew.id,
        name: selectedCrew.name,
        description: selectedCrew.description,
      })

      // 验证配置
      const validation = validateCrewConfig(crewConfig)
      if (!validation.valid) {
        toast({
          title: "验证失败",
          description: validation.errors.join("\n"),
          variant: "destructive",
        })
        return
      }

      // 保存到后端
      const result = await api.crewai.saveCrew(crewConfig)
      if (result.success) {
        toast({
          title: "保存成功",
          description: `Crew "${crewConfig.name}" 已保存`,
        })
        setIsCreating(false)
        // 刷新列表
        await loadCrews()
      }
    } catch (error) {
      console.error("保存Crew失败:", error)
      toast({
        title: "保存失败",
        description: "无法保存Crew配置，请稍后重试",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async () => {
    if (!selectedCrew) return

    try {
      setLoading(true)
      const result = await api.crewai.executeCrew(selectedCrew.id, {})
      if (result.success) {
        toast({
          title: "执行成功",
          description: `Crew已开始执行，执行ID: ${result.execution_id}`,
        })
      }
    } catch (error) {
      console.error("执行Crew失败:", error)
      toast({
        title: "执行失败",
        description: "无法执行Crew，请稍后重试",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  // 处理Canvas数据更新
  const handleCanvasChange = (nodes: Node[], edges: Edge[]) => {
    setCanvasNodes(nodes)
    setCanvasEdges(edges)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm">
          <Users className="mr-2 h-4 w-4" />
          CrewAI
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-full sm:max-w-[90vw] p-0">
        <div className="flex h-full">
          {/* 左侧列表 */}
          <div className="w-80 border-r bg-muted/10">
            <SheetHeader className="p-6 pb-4">
              <SheetTitle>CrewAI Teams</SheetTitle>
              <SheetDescription>
                Create and manage your AI agent teams
              </SheetDescription>
            </SheetHeader>

            <div className="px-4 pb-4">
              <Button className="w-full" onClick={handleCreateNew}>
                <Plus className="mr-2 h-4 w-4" />
                Create New Crew
              </Button>
            </div>

            <Separator />

            <ScrollArea className="h-[calc(100vh-180px)]">
              <div className="p-4 space-y-2">
                {crews.length === 0 ? (
                  <div className="text-center text-sm text-muted-foreground py-8">
                    <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No crews yet</p>
                    <p className="text-xs">Create your first AI team</p>
                  </div>
                ) : (
                  crews.map((crew) => (
                    <div
                      key={crew.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-all hover:border-primary ${
                        selectedCrew?.id === crew.id ? "border-primary bg-accent" : ""
                      }`}
                      onClick={() => handleLoadCrew(crew.id)}
                    >
                      <div className="font-semibold text-sm">{crew.name}</div>
                      <div className="text-xs text-muted-foreground line-clamp-2">
                        {crew.description}
                      </div>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="secondary" className="text-xs">
                          {crew.agents.length} agents
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {crew.tasks.length} tasks
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>

          {/* 右侧内容 */}
          <div className="flex-1 flex flex-col">
            {selectedCrew ? (
              <>
                {/* 头部 */}
                <div className="p-6 border-b">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold">{selectedCrew.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {selectedCrew.description}
                      </p>
                    </div>
                    {isCreating ? (
                      <Button onClick={handleSave}>Save</Button>
                    ) : (
                      <Button onClick={handleRun}>Run Crew</Button>
                    )}
                  </div>
                </div>

                {/* 主体内容 */}
                <div className="flex-1 overflow-hidden">
                  <Tabs defaultValue="canvas" className="h-full flex flex-col">
                    <div className="px-6 pt-4">
                      <TabsList>
                        <TabsTrigger value="canvas">Canvas</TabsTrigger>
                        <TabsTrigger value="config">Configuration</TabsTrigger>
                        <TabsTrigger value="results">Results</TabsTrigger>
                      </TabsList>
                    </div>

                    <TabsContent value="canvas" className="flex-1 m-0 p-0">
                      <div className="h-[calc(100vh-240px)]">
                        <CrewCanvas
                          crewId={selectedCrew.id}
                          initialNodes={canvasNodes}
                          initialEdges={canvasEdges}
                          onSave={handleCanvasChange}
                          onRun={handleRun}
                        />
                      </div>
                    </TabsContent>

                    <TabsContent value="config" className="flex-1">
                      <ScrollArea className="h-[calc(100vh-240px)]">
                        <div className="p-6 space-y-6">
                          <div className="space-y-4">
                            <div>
                              <Label>Crew Name</Label>
                              <Input
                                value={selectedCrew.name}
                                onChange={(e) =>
                                  setSelectedCrew({
                                    ...selectedCrew,
                                    name: e.target.value,
                                  })
                                }
                              />
                            </div>

                            <div>
                              <Label>Description</Label>
                              <Textarea
                                value={selectedCrew.description}
                                onChange={(e) =>
                                  setSelectedCrew({
                                    ...selectedCrew,
                                    description: e.target.value,
                                  })
                                }
                                rows={3}
                              />
                            </div>

                            <Separator />

                            <div>
                              <h4 className="font-semibold mb-2">Agents ({selectedCrew.agents.length})</h4>
                              <p className="text-sm text-muted-foreground">
                                Configure your AI agents in the Canvas view
                              </p>
                            </div>

                            <div>
                              <h4 className="font-semibold mb-2">Tasks ({selectedCrew.tasks.length})</h4>
                              <p className="text-sm text-muted-foreground">
                                Define tasks in the Canvas view
                              </p>
                            </div>
                          </div>
                        </div>
                      </ScrollArea>
                    </TabsContent>

                    <TabsContent value="results" className="flex-1">
                      <ScrollArea className="h-[calc(100vh-240px)]">
                        <div className="p-6">
                          <div className="text-center text-muted-foreground py-8">
                            <p>No execution results yet</p>
                            <p className="text-xs">Run the crew to see results</p>
                          </div>
                        </div>
                      </ScrollArea>
                    </TabsContent>
                  </Tabs>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Users className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-semibold">No Crew Selected</p>
                  <p className="text-sm">Select a crew or create a new one</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}

