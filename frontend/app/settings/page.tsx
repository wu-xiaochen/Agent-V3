"use client"

import { useState } from "react"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AgentSettings } from "@/components/settings/agent-settings"
import { ToolSettings } from "@/components/settings/tool-settings"
import { SystemSettings } from "@/components/settings/system-settings"
import { KnowledgeBaseSettings } from "@/components/settings/knowledge-base-settings"
import { AppearanceSettings } from "@/components/settings/appearance-settings"
import Link from "next/link"

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("agents")

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-6xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground mt-1">
              Configure your AI agents, tools, and system preferences
            </p>
          </div>
        </div>

        {/* Settings Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="tools">Tools</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
            <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Agent Configuration</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Manage AI agents, customize their prompts and behaviors
              </p>
            </div>
            <AgentSettings />
          </TabsContent>

          <TabsContent value="tools" className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Tool Configuration</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Enable, disable, and configure tools available to your agents
              </p>
            </div>
            <ToolSettings />
          </TabsContent>

          <TabsContent value="system" className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold mb-2">System Configuration</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Configure LLM providers, API keys, and default model parameters
              </p>
            </div>
            <SystemSettings />
          </TabsContent>

          <TabsContent value="knowledge" className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Knowledge Base</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Manage knowledge bases and RAG capabilities
              </p>
            </div>
            <KnowledgeBaseSettings />
          </TabsContent>

          <TabsContent value="appearance" className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Appearance & Display</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Customize the look and feel of your workspace
              </p>
            </div>
            <AppearanceSettings />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
