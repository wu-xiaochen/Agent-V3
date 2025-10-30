"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
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
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Settings, ChevronRight, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { toolsListApi, type ToolConfig, type ToolConfigUpdate } from "@/lib/api/tools"

export function ToolSettings() {
  const [tools, setTools] = useState<ToolConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [editingTool, setEditingTool] = useState<ToolConfig | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const { toast } = useToast()

  // 加载工具配置
  useEffect(() => {
    loadTools()
  }, [])

  const loadTools = async () => {
    try {
      setLoading(true)
      const configs = await toolsListApi.getAllConfigs()
      setTools(configs)
    } catch (error) {
      console.error('Failed to load tools:', error)
      toast({
        title: "Error",
        description: "Failed to load tool configurations",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (toolId: string) => {
    const tool = tools.find(t => t.tool_id === toolId)
    if (!tool) return

    try {
      const updated = await toolsListApi.updateConfig(toolId, {
        enabled: !tool.enabled
      })
      
      setTools(tools.map(t => 
        t.tool_id === toolId ? updated : t
      ))
      
      toast({ 
        title: updated.enabled ? "Tool enabled" : "Tool disabled",
        description: updated.name
      })
    } catch (error) {
      console.error('Failed to toggle tool:', error)
      toast({
        title: "Error",
        description: "Failed to update tool",
        variant: "destructive"
      })
    }
  }

  const handleSaveConfig = async (updatedTool: ToolConfig) => {
    try {
      const update: ToolConfigUpdate = {
        enabled: updatedTool.enabled,
        mode: updatedTool.mode,
        config: updatedTool.config,
        description: updatedTool.description
      }
      
      const result = await toolsListApi.updateConfig(updatedTool.tool_id, update)
      
      setTools(tools.map(t => t.tool_id === result.tool_id ? result : t))
      setIsDialogOpen(false)
      setEditingTool(null)
      
      toast({ 
        title: "Configuration saved", 
        description: result.name 
      })
    } catch (error) {
      console.error('Failed to save config:', error)
      toast({
        title: "Error",
        description: "Failed to save configuration",
        variant: "destructive"
      })
    }
  }

  const handleReset = async () => {
    try {
      const configs = await toolsListApi.resetToDefault()
      setTools(configs)
      toast({
        title: "Reset successful",
        description: "Tool configurations reset to default"
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
          <p className="text-sm text-muted-foreground">Loading tool configurations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          Enable/disable tools and configure their parameters
        </p>
        <Button variant="outline" size="sm" onClick={handleReset}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Reset to Default
        </Button>
      </div>
      
      <div className="space-y-3">
        {tools.map(tool => (
          <Card key={tool.tool_id} className="p-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Label className="font-semibold text-base">{tool.name}</Label>
                  <Badge 
                    variant={tool.mode === "API" ? "default" : "secondary"} 
                    className="text-xs"
                  >
                    {tool.mode}
                  </Badge>
                  <Badge 
                    variant={tool.enabled ? "default" : "outline"}
                    className="text-xs"
                  >
                    {tool.enabled ? "Enabled" : "Disabled"}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {tool.description}
                </p>
              </div>
              
              <div className="flex items-center gap-2">
                <Dialog open={isDialogOpen && editingTool?.tool_id === tool.tool_id} onOpenChange={setIsDialogOpen}>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingTool(tool)
                        setIsDialogOpen(true)
                      }}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px]">
                    {editingTool && (
                      <ToolConfigForm
                        tool={editingTool}
                        onSave={handleSaveConfig}
                        onCancel={() => {
                          setIsDialogOpen(false)
                          setEditingTool(null)
                        }}
                      />
                    )}
                  </DialogContent>
                </Dialog>
                
                <Switch 
                  checked={tool.enabled} 
                  onCheckedChange={() => handleToggle(tool.tool_id)}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

function ToolConfigForm({
  tool,
  onSave,
  onCancel,
}: {
  tool: ToolConfig
  onSave: (tool: ToolConfig) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState<ToolConfig>(tool)

  const handleConfigChange = (key: string, value: any) => {
    setFormData({
      ...formData,
      config: {
        ...formData.config,
        [key]: value
      }
    })
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Configure {tool.name}</DialogTitle>
        <DialogDescription>
          Adjust the tool's parameters and settings
        </DialogDescription>
      </DialogHeader>
      
      <div className="space-y-4 py-4">
        <div>
          <Label htmlFor="mode">Mode</Label>
          <Select 
            value={formData.mode} 
            onValueChange={(value: "API" | "MCP") => 
              setFormData({ ...formData, mode: value })
            }
          >
            <SelectTrigger id="mode">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="API">API</SelectItem>
              <SelectItem value="MCP">MCP</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {formData.config.endpoint !== undefined && (
          <div>
            <Label htmlFor="endpoint">API Endpoint</Label>
            <Input
              id="endpoint"
              value={formData.config.endpoint || ""}
              onChange={(e) => handleConfigChange("endpoint", e.target.value)}
              placeholder="https://api.example.com"
            />
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="timeout">Timeout (ms)</Label>
            <Input
              id="timeout"
              type="number"
              value={formData.config.timeout || 5000}
              onChange={(e) => handleConfigChange("timeout", parseInt(e.target.value))}
            />
          </div>
          
          <div>
            <Label htmlFor="retries">Max Retries</Label>
            <Input
              id="retries"
              type="number"
              value={formData.config.retries || 3}
              onChange={(e) => handleConfigChange("retries", parseInt(e.target.value))}
            />
          </div>
        </div>

        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
          />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button onClick={() => onSave(formData)}>
          Save Configuration
        </Button>
      </DialogFooter>
    </>
  )
}
