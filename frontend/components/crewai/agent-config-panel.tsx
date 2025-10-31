"use client"

import { useState, useEffect } from "react"
import { X, Search, Plus, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command"
import { api } from "@/lib/api"
import type { ToolInfo } from "@/lib/api/tools"
import type { KnowledgeBase } from "@/lib/api/knowledge-base"
import { Database } from "lucide-react"

interface AgentConfig {
  id: string
  name: string
  role: string
  goal: string
  backstory: string
  verbose?: boolean
  allow_delegation?: boolean
  max_iter?: number
  memory?: boolean
  tools?: string[]
  knowledge_bases?: string[]  // 知识库ID列表
}

interface AgentConfigPanelProps {
  agent: AgentConfig
  onSave: (agent: AgentConfig) => void
  onClose: () => void
}

export function AgentConfigPanel({ agent, onSave, onClose }: AgentConfigPanelProps) {
  const [formData, setFormData] = useState<AgentConfig>(agent)
  const [newTool, setNewTool] = useState("")
  const [availableTools, setAvailableTools] = useState<ToolInfo[]>([])
  const [loadingTools, setLoadingTools] = useState(false)
  const [toolSelectorOpen, setToolSelectorOpen] = useState(false)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [loadingKBs, setLoadingKBs] = useState(false)
  const [kbSelectorOpen, setKbSelectorOpen] = useState(false)

  useEffect(() => {
    setFormData(agent)
  }, [agent])

  // 🆕 加载可用工具列表
  useEffect(() => {
    const loadTools = async () => {
      try {
        setLoadingTools(true)
        const response = await api.toolsList.getEnabled()
        if (response.success) {
          setAvailableTools(response.tools)
          console.log(`✅ 加载了 ${response.tools.length} 个可用工具`)
        }
      } catch (error) {
        console.error('❌ 加载工具列表失败:', error)
      } finally {
        setLoadingTools(false)
      }
    }
    loadTools()
  }, [])

  // 🆕 加载知识库列表
  useEffect(() => {
    const loadKnowledgeBases = async () => {
      try {
        setLoadingKBs(true)
        const kbs = await api.knowledge.listKnowledgeBases()
        setKnowledgeBases(kbs)
        console.log(`✅ 加载了 ${kbs.length} 个知识库`)
      } catch (error) {
        console.error('❌ 加载知识库列表失败:', error)
      } finally {
        setLoadingKBs(false)
      }
    }
    loadKnowledgeBases()
  }, [])

  const handleChange = (field: keyof AgentConfig, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleAddTool = (toolName?: string) => {
    const tool = toolName || newTool.trim()
    if (tool && !formData.tools?.includes(tool)) {
      setFormData(prev => ({
        ...prev,
        tools: [...(prev.tools || []), tool]
      }))
      setNewTool("")
      setToolSelectorOpen(false)
    }
  }

  const handleRemoveTool = (tool: string) => {
    setFormData(prev => ({
      ...prev,
      tools: (prev.tools || []).filter(t => t !== tool)
    }))
  }

  // 🆕 添加知识库
  const handleAddKnowledgeBase = (kbId: string) => {
    if (!formData.knowledge_bases?.includes(kbId)) {
      setFormData(prev => ({
        ...prev,
        knowledge_bases: [...(prev.knowledge_bases || []), kbId]
      }))
      // 自动添加知识库检索工具到工具列表
      const kbToolName = `knowledge_base_search_${kbId}`
      if (!formData.tools?.includes(kbToolName)) {
        handleAddTool(kbToolName)
      }
      setKbSelectorOpen(false)
    }
  }

  // 🆕 移除知识库
  const handleRemoveKnowledgeBase = (kbId: string) => {
    setFormData(prev => ({
      ...prev,
      knowledge_bases: (prev.knowledge_bases || []).filter(kb => kb !== kbId)
    }))
    // 同时移除对应的工具
    const kbToolName = `knowledge_base_search_${kbId}`
    handleRemoveTool(kbToolName)
  }

  const handleSave = () => {
    onSave(formData)
    onClose()
  }

  return (
    <div className="fixed inset-y-0 right-0 w-[400px] bg-background border-l shadow-lg z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Agent Configuration</h3>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="h-[calc(100vh-140px)]">
        <div className="p-4 space-y-4">
          {/* Basic Info */}
          <div className="space-y-3">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                placeholder="Agent Name"
              />
            </div>

            <div>
              <Label htmlFor="role">Role *</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => handleChange("role", e.target.value)}
                placeholder="e.g. Senior Data Analyst"
                required
              />
            </div>

            <div>
              <Label htmlFor="goal">Goal *</Label>
              <Textarea
                id="goal"
                value={formData.goal}
                onChange={(e) => handleChange("goal", e.target.value)}
                placeholder="What is this agent's objective?"
                rows={3}
                required
              />
            </div>

            <div>
              <Label htmlFor="backstory">Backstory *</Label>
              <Textarea
                id="backstory"
                value={formData.backstory}
                onChange={(e) => handleChange("backstory", e.target.value)}
                placeholder="Agent's background and expertise"
                rows={4}
                required
              />
            </div>
          </div>

          <Separator />

          {/* Tools */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Tools</Label>
              {loadingTools && (
                <span className="text-xs text-muted-foreground">Loading...</span>
              )}
            </div>
            
            {/* 🆕 工具选择器（从后端加载） */}
            <Popover open={toolSelectorOpen} onOpenChange={setToolSelectorOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  disabled={loadingTools}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  {loadingTools ? "Loading tools..." : "Select from available tools"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[350px] p-0" align="start">
                <Command>
                  <CommandInput placeholder="Search tools..." />
                  <CommandEmpty>No tools found.</CommandEmpty>
                  <CommandGroup>
                    <ScrollArea className="h-[200px]">
                      {availableTools
                        .filter(tool => !formData.tools?.includes(tool.name))
                        .map((tool) => (
                          <CommandItem
                            key={tool.name}
                            value={tool.name}
                            onSelect={() => handleAddTool(tool.name)}
                            className="cursor-pointer"
                          >
                            <Check
                              className={`mr-2 h-4 w-4 ${
                                formData.tools?.includes(tool.name)
                                  ? "opacity-100"
                                  : "opacity-0"
                              }`}
                            />
                            <div className="flex-1">
                              <div className="font-medium">{tool.display_name}</div>
                              <div className="text-xs text-muted-foreground">
                                {tool.description}
                              </div>
                            </div>
                            <Badge variant="outline" className="ml-2 text-xs">
                              {tool.type}
                            </Badge>
                          </CommandItem>
                        ))}
                    </ScrollArea>
                  </CommandGroup>
                </Command>
              </PopoverContent>
            </Popover>

            {/* 手动输入（备用方案） */}
            <div className="flex gap-2">
              <Input
                value={newTool}
                onChange={(e) => setNewTool(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddTool()}
                placeholder="Or type custom tool name..."
                className="text-sm"
              />
              <Button onClick={() => handleAddTool()} size="sm" variant="secondary">
                Add
              </Button>
            </div>
            
            {/* 已选工具列表 */}
            {formData.tools && formData.tools.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">
                  Selected tools ({formData.tools.length}):
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.tools.map(toolName => {
                    const toolInfo = availableTools.find(t => t.name === toolName)
                    return (
                      <Badge
                        key={toolName}
                        variant="secondary"
                        className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors"
                        onClick={() => handleRemoveTool(toolName)}
                      >
                        {toolInfo?.display_name || toolName}
                        <X className="ml-1 h-3 w-3" />
                      </Badge>
                    )
                  })}
                </div>
              </div>
            )}
          </div>

          <Separator />

          {/* 🆕 Knowledge Bases */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Knowledge Bases</Label>
              {loadingKBs && (
                <span className="text-xs text-muted-foreground">Loading...</span>
              )}
            </div>
            
            {/* 知识库选择器 */}
            <Popover open={kbSelectorOpen} onOpenChange={setKbSelectorOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  disabled={loadingKBs || knowledgeBases.length === 0}
                >
                  <Database className="mr-2 h-4 w-4" />
                  {loadingKBs ? "Loading knowledge bases..." : 
                   knowledgeBases.length === 0 ? "No knowledge bases available" :
                   "Select knowledge base"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[350px] p-0" align="start">
                <Command>
                  <CommandInput placeholder="Search knowledge bases..." />
                  <CommandEmpty>No knowledge bases found.</CommandEmpty>
                  <CommandGroup>
                    <ScrollArea className="h-[200px]">
                      {knowledgeBases
                        .filter(kb => !formData.knowledge_bases?.includes(kb.id))
                        .map((kb) => (
                          <CommandItem
                            key={kb.id}
                            value={kb.name}
                            onSelect={() => handleAddKnowledgeBase(kb.id)}
                            className="cursor-pointer"
                          >
                            <Database className="mr-2 h-4 w-4 text-muted-foreground" />
                            <div className="flex-1">
                              <div className="font-medium">{kb.name}</div>
                              <div className="text-xs text-muted-foreground">
                                {kb.description || "No description"} • {kb.document_count} documents
                              </div>
                            </div>
                          </CommandItem>
                        ))}
                    </ScrollArea>
                  </CommandGroup>
                </Command>
              </PopoverContent>
            </Popover>

            {/* 已选知识库列表 */}
            {formData.knowledge_bases && formData.knowledge_bases.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">
                  Selected knowledge bases ({formData.knowledge_bases.length}):
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.knowledge_bases.map(kbId => {
                    const kb = knowledgeBases.find(k => k.id === kbId)
                    return (
                      <Badge
                        key={kbId}
                        variant="secondary"
                        className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors"
                        onClick={() => handleRemoveKnowledgeBase(kbId)}
                      >
                        <Database className="mr-1 h-3 w-3" />
                        {kb?.name || kbId}
                        <X className="ml-1 h-3 w-3" />
                      </Badge>
                    )
                  })}
                </div>
                <p className="text-xs text-muted-foreground">
                  💡 Knowledge base search tools are automatically added to the tools list
                </p>
              </div>
            )}
          </div>

          <Separator />

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h4 className="font-semibold text-sm">Advanced Settings</h4>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Verbose Mode</Label>
                <p className="text-xs text-muted-foreground">
                  Show detailed execution logs
                </p>
              </div>
              <Switch
                checked={formData.verbose ?? false}
                onCheckedChange={(checked) => handleChange("verbose", checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Allow Delegation</Label>
                <p className="text-xs text-muted-foreground">
                  Can delegate tasks to other agents
                </p>
              </div>
              <Switch
                checked={formData.allow_delegation ?? false}
                onCheckedChange={(checked) => handleChange("allow_delegation", checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Memory</Label>
                <p className="text-xs text-muted-foreground">
                  Remember conversation history
                </p>
              </div>
              <Switch
                checked={formData.memory ?? true}
                onCheckedChange={(checked) => handleChange("memory", checked)}
              />
            </div>

            <div>
              <Label htmlFor="max_iter">Max Iterations</Label>
              <Input
                id="max_iter"
                type="number"
                value={formData.max_iter ?? 15}
                onChange={(e) => handleChange("max_iter", parseInt(e.target.value))}
                min={1}
                max={100}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum number of iterations before stopping (1-100)
              </p>
            </div>
          </div>
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-background">
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="flex-1"
            disabled={!formData.role || !formData.goal || !formData.backstory}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  )
}
