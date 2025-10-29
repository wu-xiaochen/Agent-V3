"use client"

import { X, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAppStore } from "@/lib/store"
import { cn } from "@/lib/utils"
import { CrewAIVisualizer } from "./crewai-visualizer"
import { KnowledgeBrowser } from "./knowledge-browser"
import { ToolsSettings } from "./tools-settings"

export function ToolPanel() {
  const { toolPanelOpen, setToolPanelOpen, activeTab, setActiveTab } = useAppStore()

  return (
    <>
      {!toolPanelOpen && (
        <Button
          onClick={() => setToolPanelOpen(true)}
          className="fixed right-4 top-4 z-50 bg-primary text-primary-foreground hover:bg-primary/90"
          size="icon"
        >
          <Menu className="h-4 w-4" />
        </Button>
      )}

      <div
        className={cn(
          "fixed right-0 top-0 h-screen w-[400px] bg-card border-l border-border shadow-2xl transition-transform duration-300 z-40",
          toolPanelOpen ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Tools</h2>
          <Button variant="ghost" size="icon" onClick={() => setToolPanelOpen(false)}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-[calc(100%-64px)]">
          <TabsList className="w-full grid grid-cols-4 rounded-none border-b border-border">
            <TabsTrigger value="crewai">CrewAI</TabsTrigger>
            <TabsTrigger value="n8n">N8N</TabsTrigger>
            <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
            <TabsTrigger value="tools">Tools</TabsTrigger>
          </TabsList>

          <TabsContent value="crewai" className="h-full p-4 overflow-auto">
            <CrewAIVisualizer />
          </TabsContent>

          <TabsContent value="n8n" className="h-full p-4 overflow-auto">
            <div className="space-y-4">
              <h3 className="font-semibold text-card-foreground">N8N Workflows</h3>
              <p className="text-sm text-muted-foreground">Connect and manage your N8N automation workflows here.</p>
            </div>
          </TabsContent>

          <TabsContent value="knowledge" className="h-full p-4 overflow-auto">
            <KnowledgeBrowser />
          </TabsContent>

          <TabsContent value="tools" className="h-full p-4 overflow-auto">
            <ToolsSettings />
          </TabsContent>
        </Tabs>
      </div>
    </>
  )
}
