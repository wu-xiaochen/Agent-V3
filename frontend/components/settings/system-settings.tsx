"use client"

import { useState, useEffect } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card } from "@/components/ui/card"
import { Save, Eye, EyeOff } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface SystemConfig {
  llmProvider: string
  apiKey: string
  baseUrl: string
  defaultModel: string
  temperature: number
  maxTokens: number
}

const DEFAULT_CONFIG: SystemConfig = {
  llmProvider: "siliconflow",
  apiKey: "",
  baseUrl: "https://api.siliconflow.cn/v1",
  defaultModel: "Qwen/Qwen2.5-7B-Instruct",
  temperature: 0.7,
  maxTokens: 2000
}

const PROVIDER_CONFIGS = {
  siliconflow: {
    baseUrl: "https://api.siliconflow.cn/v1",
    models: [
      "Qwen/Qwen2.5-7B-Instruct",
      "Qwen/Qwen2.5-14B-Instruct",
      "deepseek-ai/DeepSeek-V2.5",
      "THUDM/glm-4-9b-chat"
    ]
  },
  openai: {
    baseUrl: "https://api.openai.com/v1",
    models: [
      "gpt-4",
      "gpt-4-turbo",
      "gpt-3.5-turbo"
    ]
  },
  anthropic: {
    baseUrl: "https://api.anthropic.com/v1",
    models: [
      "claude-3-opus-20240229",
      "claude-3-sonnet-20240229",
      "claude-3-haiku-20240307"
    ]
  }
}

export function SystemSettings() {
  const [config, setConfig] = useState<SystemConfig>(DEFAULT_CONFIG)
  const [showApiKey, setShowApiKey] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const { toast } = useToast()

  // 加载保存的配置
  useEffect(() => {
    const saved = localStorage.getItem("system_config")
    if (saved) {
      try {
        setConfig(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to load system config:", e)
      }
    }
  }, [])

  const handleChange = (key: keyof SystemConfig, value: any) => {
    setConfig({ ...config, [key]: value })
    setHasChanges(true)
  }

  const handleProviderChange = (provider: string) => {
    const providerConfig = PROVIDER_CONFIGS[provider as keyof typeof PROVIDER_CONFIGS]
    setConfig({
      ...config,
      llmProvider: provider,
      baseUrl: providerConfig.baseUrl,
      defaultModel: providerConfig.models[0]
    })
    setHasChanges(true)
  }

  const handleSave = () => {
    localStorage.setItem("system_config", JSON.stringify(config))
    setHasChanges(false)
    toast({ 
      title: "Settings saved",
      description: "System configuration has been updated"
    })
  }

  const handleReset = () => {
    setConfig(DEFAULT_CONFIG)
    setHasChanges(true)
    toast({ 
      title: "Settings reset",
      description: "Configuration reset to defaults"
    })
  }

  const currentProvider = PROVIDER_CONFIGS[config.llmProvider as keyof typeof PROVIDER_CONFIGS]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          Configure your LLM provider and API settings
        </p>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset}>
            Reset
          </Button>
          <Button onClick={handleSave} disabled={!hasChanges}>
            <Save className="mr-2 h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </div>

      <Card className="p-6 space-y-6">
        <div>
          <Label htmlFor="llm-provider" className="text-base font-semibold">
            LLM Provider
          </Label>
          <Select 
            value={config.llmProvider} 
            onValueChange={handleProviderChange}
          >
            <SelectTrigger id="llm-provider" className="mt-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="siliconflow">SiliconFlow</SelectItem>
              <SelectItem value="openai">OpenAI</SelectItem>
              <SelectItem value="anthropic">Anthropic</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground mt-1">
            Choose your preferred LLM provider
          </p>
        </div>

        <div>
          <Label htmlFor="api-key" className="text-base font-semibold">
            API Key
          </Label>
          <div className="flex gap-2 mt-2">
            <Input 
              id="api-key" 
              type={showApiKey ? "text" : "password"}
              value={config.apiKey}
              onChange={(e) => handleChange("apiKey", e.target.value)}
              placeholder="sk-..." 
              className="flex-1"
            />
            <Button
              variant="outline"
              size="icon"
              onClick={() => setShowApiKey(!showApiKey)}
            >
              {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Your API key will be stored locally
          </p>
        </div>

        <div>
          <Label htmlFor="base-url" className="text-base font-semibold">
            Base URL
          </Label>
          <Input 
            id="base-url"
            value={config.baseUrl}
            onChange={(e) => handleChange("baseUrl", e.target.value)}
            placeholder="https://api.example.com/v1" 
            className="mt-2"
          />
          <p className="text-xs text-muted-foreground mt-1">
            API endpoint for the selected provider
          </p>
        </div>

        <div>
          <Label htmlFor="model" className="text-base font-semibold">
            Default Model
          </Label>
          <Select 
            value={config.defaultModel} 
            onValueChange={(value) => handleChange("defaultModel", value)}
          >
            <SelectTrigger id="model" className="mt-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {currentProvider?.models.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground mt-1">
            Default model for new conversations
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="temperature" className="text-base font-semibold">
              Temperature
            </Label>
            <Input 
              id="temperature"
              type="number"
              min="0"
              max="2"
              step="0.1"
              value={config.temperature}
              onChange={(e) => handleChange("temperature", parseFloat(e.target.value))}
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              0 = Focused, 2 = Creative
            </p>
          </div>

          <div>
            <Label htmlFor="max-tokens" className="text-base font-semibold">
              Max Tokens
            </Label>
            <Input 
              id="max-tokens"
              type="number"
              min="100"
              max="32000"
              step="100"
              value={config.maxTokens}
              onChange={(e) => handleChange("maxTokens", parseInt(e.target.value))}
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Maximum response length
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
