"use client"

import { useState } from "react"
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
import { Settings, ChevronRight } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface Tool {
  id: string
  name: string
  description: string
  enabled: boolean
  mode: "API" | "MCP"
  config: {
    endpoint?: string
    timeout?: number
    retries?: number
    [key: string]: any
  }
}

const DEFAULT_TOOLS: Tool[] = [
  {
    id: "time",
    name: "Time Tool",
    description: "Get current date and time in various timezones",
    enabled: true,
    mode: "API",
    config: {
      timeout: 5000,
      retries: 3
    }
  },
  {
    id: "calculator",
    name: "Calculator",
    description: "Perform mathematical calculations",
    enabled: true,
    mode: "API",
    config: {
      timeout: 3000,
      retries: 2
    }
  },
  {
    id: "search",
    name: "Web Search",
    description: "Search the web for information",
    enabled: false,
    mode: "API",
    config: {
      endpoint: "https://api.search.com",
      timeout: 10000,
      retries: 3
    }
  },
  {
    id: "document_generator",
    name: "Document Generator",
    description: "Generate various types of documents",
    enabled: true,
    mode: "API",
    config: {
      timeout: 30000,
      retries: 2
    }
  },
  {
    id: "crewai_generator",
    name: "CrewAI Generator",
    description: "Generate CrewAI team configurations",
    enabled: true,
    mode: "API",
    config: {
      timeout: 60000,
      retries: 1
    }
  },
]

export function ToolSettings() {
  const [tools, setTools] = useState<Tool[]>(DEFAULT_TOOLS)
  const [editingTool, setEditingTool] = useState<Tool | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const { toast } = useToast()

  const handleToggle = (toolId: string) => {
    setTools(tools.map(t => 
      t.id === toolId ? { ...t, enabled: !t.enabled } : t
    ))
    const tool = tools.find(t => t.id === toolId)
    toast({ 
      title: tool?.enabled ? "Tool disabled" : "Tool enabled",
      description: tool?.name 
    })
  }

  const handleSaveConfig = (updatedTool: Tool) => {
    setTools(tools.map(t => t.id === updatedTool.id ? updatedTool : t))
    setIsDialogOpen(false)
    setEditingTool(null)
    toast({ title: "Configuration saved", description: updatedTool.name })
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Enable/disable tools and configure their parameters
      </p>
      
      <div className="space-y-3">
        {tools.map(tool => (
          <Card key={tool.id} className="p-4">
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
                <Dialog open={isDialogOpen && editingTool?.id === tool.id} onOpenChange={setIsDialogOpen}>
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
                    <ToolConfigForm
                      tool={editingTool!}
                      onSave={handleSaveConfig}
                      onCancel={() => {
                        setIsDialogOpen(false)
                        setEditingTool(null)
                      }}
                    />
                  </DialogContent>
                </Dialog>
                
                <Switch 
                  checked={tool.enabled} 
                  onCheckedChange={() => handleToggle(tool.id)}
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
  tool: Tool
  onSave: (tool: Tool) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState<Tool>(tool)

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
