"use client"

import { useState } from "react"
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
import { CrewCanvas } from "./crew-canvas"
import type { CrewConfig } from "@/lib/types/crewai"

interface CrewDrawerProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function CrewDrawer({ open, onOpenChange }: CrewDrawerProps) {
  const [crews, setCrews] = useState<CrewConfig[]>([])
  const [selectedCrew, setSelectedCrew] = useState<CrewConfig | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  const handleCreateNew = () => {
    const newCrew: CrewConfig = {
      id: `crew-${Date.now()}`,
      name: "New Crew",
      description: "Describe your crew",
      agents: [],
      tasks: [],
      process: "sequential",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    setCrews([...crews, newCrew])
    setSelectedCrew(newCrew)
    setIsCreating(true)
  }

  const handleSave = () => {
    // TODO: API call to save crew
    setIsCreating(false)
  }

  const handleRun = () => {
    // TODO: API call to run crew
    console.log("Running crew:", selectedCrew)
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
                      onClick={() => {
                        setSelectedCrew(crew)
                        setIsCreating(false)
                      }}
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
                          initialNodes={[]}
                          initialEdges={[]}
                          onSave={(nodes, edges) => {
                            console.log("Saving:", nodes, edges)
                          }}
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

