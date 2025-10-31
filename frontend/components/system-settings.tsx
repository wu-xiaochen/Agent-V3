"use client"

import { useState, useEffect } from "react"
import { Save, RefreshCw, Moon, Sun, Globe, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { getSystemConfig, updateSystemConfig, resetSystemConfig, type SystemConfig } from "@/lib/api/system"
import { useAppStore } from "@/lib/store"

interface Settings {
  // 通用设置
  language: string
  theme: "light" | "dark" | "system"
  
  // API设置
  apiBaseUrl: string
  apiTimeout: number
  
  // LLM设置
  defaultProvider: string
  defaultModel: string
  temperature: number
  maxTokens: number
  
  // 功能设置
  enableMemory: boolean
  enableStreaming: boolean
  enableFileUpload: boolean
  enableMultimodal: boolean
  
  // 高级设置
  debugMode: boolean
  logLevel: string
}

export function SystemSettings() {
  const { toast } = useToast()
  const { setDarkMode } = useAppStore()
  const [settings, setSettings] = useState<Settings>({
    language: "zh-CN",
    theme: "dark",
    apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
    apiTimeout: 30,
    defaultProvider: "siliconflow",
    defaultModel: "deepseek-chat",
    temperature: 0.7,
    maxTokens: 2000,
    enableMemory: true,
    enableStreaming: true,
    enableFileUpload: true,
    enableMultimodal: true,
    debugMode: false,
    logLevel: "info",
  })

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [apiKeyValue, setApiKeyValue] = useState<string>("") // 单独的API Key状态

  // 加载系统配置
  useEffect(() => {
    const loadConfig = async () => {
      setIsLoading(true)
      try {
        const config = await getSystemConfig()
        
        // 从后端配置映射到前端设置
        setSettings(prev => ({
          ...prev,
          defaultProvider: config.llm_provider || prev.defaultProvider,
          defaultModel: config.default_model || prev.defaultModel,
          temperature: config.temperature ?? prev.temperature,
          maxTokens: config.max_tokens ?? prev.maxTokens,
          apiBaseUrl: config.base_url || prev.apiBaseUrl,
        }))
        
        // API Key保持脱敏显示
        setApiKeyValue(config.api_key_masked || "***")
      } catch (error) {
        console.error("加载配置失败:", error)
        toast({
          title: "加载配置失败",
          description: error instanceof Error ? error.message : "无法从服务器加载配置",
          variant: "destructive"
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadConfig()
  }, [toast])

  const handleSave = async () => {
   面向后端API保存配置
    setIsSaving(true)
    try {
      await updateSystemConfig({
        llm_provider: settings.defaultProvider,
        api_key: apiKeyValue && !apiKeyValue.includes("*") ? apiKeyValue : undefined, // 只有修改时才发送
        base_url: settings.apiBaseUrl,
        default_model: settings.defaultModel,
        temperature: settings.temperature,
        max_tokens: settings.maxTokens,
      })
      
      toast({
        title: "保存成功",
        description: "系统配置已更新",
      })
      
      // 重新加载配置以获取最新的脱敏API Key
      const config = await getSystemConfig()
      setApiKeyValue(config.api_key_masked || "***")
    } catch (error) {
      console.error("保存设置失败:", error)
      toast({
        title: "保存失败",
        description: error instanceof Error ? error.message : "无法保存配置",
        variant: "destructive"
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleReset = async () => {
    if (!confirm("确定要重置所有设置为默认值吗？")) {
      return
    }
    
    setIsSaving(true)
    try {
      const defaultConfig = await resetSystemConfig()
      
      // 更新前端状态
      setSettings(prev => ({
        ...prev,
        defaultProvider: defaultConfig.llm_provider || "siliconflow",
        defaultModel: defaultConfig.default_model || "deepseek-chat",
        temperature: defaultConfig.temperature ?? 0.7,
        maxTokens: defaultConfig.max_tokens ?? 2000,
        apiBaseUrl: defaultConfig.base_url || "http://localhost:8000",
      }))
      
      setApiKeyValue(defaultConfig.api_key_masked || "***")
      
      toast({
        title: "重置成功",
        description: "系统配置已重置为默认值",
      })
    } catch (error) {
      console.error("重置配置失败:", error)
      toast({
        title: "重置失败",
        description: error instanceof Error ? error.message : "无法重置配置",
        variant: "destructive"
      })
    } finally {
      setIsSaving(false)
    }
  }

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
    
    // 如果是主题切换，同步更新全局状态和localStorage
    if (key === "theme") {
      const themeValue = value as "light" | "dark" | "system"
      if (themeValue === "system") {
        // 跟随系统
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
        setDarkMode(prefersDark)
        localStorage.setItem("theme", prefersDark ? "dark" : "light")
      } else {
        // 明确指定浅色或深色
        const isDark = themeValue === "dark"
        setDarkMode(isDark)
        localStorage.setItem("theme", themeValue)
      }
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-card-foreground">系统设置</h3>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={handleReset}>
            <RefreshCw className="h-3 w-3 mr-1" />
            重置
          </Button>
          <Button size="sm" onClick={handleSave} disabled={isSaving}>
            <Save className="h-3 w-3 mr-1" />
            {isSaving ? "保存中..." : "保存"}
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="text-muted-foreground">加载配置中...</div>
        </div>
      ) : (
        <ScrollArea className="h-[calc(100vh-200px)]">
          <div className="space-y-6 pr-3">
          {/* 通用设置 */}
          <Card className="p-4 space-y-4">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              <h4 className="font-medium text-sm">通用设置</h4>
            </div>
            <Separator />
            
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="language" className="text-xs">
                  语言
                </Label>
                <Select value={settings.language} onValueChange={(value) => updateSetting("language", value)}>
                  <SelectTrigger id="language" className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="zh-CN">简体中文</SelectItem>
                    <SelectItem value="en-US">English</SelectItem>
                    <SelectItem value="ja-JP">日本語</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="theme" className="text-xs">
                  主题
                </Label>
                <Select value={settings.theme} onValueChange={(value: any) => updateSetting("theme", value)}>
                  <SelectTrigger id="theme" className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">
                      <div className="flex items-center gap-2">
                        <Sun className="h-3 w-3" />
                        <span>浅色</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="dark">
                      <div className="flex items-center gap-2">
                        <Moon className="h-3 w-3" />
                        <span>深色</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="system">
                      <div className="flex items-center gap-2">
                        <Globe className="h-3 w-3" />
                        <span>跟随系统</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>

          {/* API设置 */}
          <Card className="p-4 space-y-4">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <h4 className="font-medium text-sm">API 设置</h4>
            </div>
            <Separator />
            
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="api-url" className="text-xs">
                  API 基础URL
                </Label>
                <Input
                  id="api-url"
                  value={settings.apiBaseUrl}
                  onChange={(e) => updateSetting("apiBaseUrl", e.target.value)}
                  className="h-8"
                  placeholder="http://localhost:8000"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="api-timeout" className="text-xs">
                  请求超时 (秒)
                </Label>
                <Input
                  id="api-timeout"
                  type="number"
                  value={settings.apiTimeout}
                  onChange={(e) => updateSetting("apiTimeout", parseInt(e.target.value))}
                  className="h-8"
                />
              </div>
            </div>
          </Card>

          {/* LLM Provider配置 */}
          <Card className="p-4 space-y-4">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <h4 className="font-medium text-sm">LLM Provider 配置</h4>
            </div>
            <Separator />
            
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="api-key" className="text-xs">
                  API Key
                </Label>
                <Input
                  id="api-key"
                  type="password"
                  value={apiKeyValue}
                  onChange={(e) => setApiKeyValue(e.target.value)}
                  className="h-8"
                  placeholder="输入API Key（留空则不修改）"
                />
                <p className="text-xs text-muted-foreground">
                  如果显示为 ***，表示当前已保存的Key（输入新值将覆盖）
                </p>
              </div>
            </div>
          </Card>

          {/* LLM设置 */}
          <Card className="p-4 space-y-4">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <h4 className="font-medium text-sm">LLM 配置</h4>
            </div>
            <Separator />
            
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="provider" className="text-xs">
                  默认提供商
                </Label>
                <Select value={settings.defaultProvider} onValueChange={(value) => updateSetting("defaultProvider", value)}>
                  <SelectTrigger id="provider" className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="siliconflow">SiliconFlow</SelectItem>
                    <SelectItem value="openai">OpenAI</SelectItem>
                    <SelectItem value="anthropic">Anthropic</SelectItem>
                    <SelectItem value="google">Google</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="model" className="text-xs">
                  默认模型
                </Label>
                <Input
                  id="model"
                  value={settings.defaultModel}
                  onChange={(e) => updateSetting("defaultModel", e.target.value)}
                  className="h-8"
                  placeholder="deepseek-chat"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="temp" className="text-xs">
                  Temperature ({settings.temperature})
                </Label>
                <Input
                  id="temp"
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => updateSetting("temperature", parseFloat(e.target.value))}
                  className="h-2"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-tokens" className="text-xs">
                  最大 Tokens
                </Label>
                <Input
                  id="max-tokens"
                  type="number"
                  value={settings.maxTokens}
                  onChange={(e) => updateSetting("maxTokens", parseInt(e.target.value))}
                  className="h-8"
                />
              </div>
            </div>
          </Card>

          {/* 功能设置 */}
          <Card className="p-4 space-y-4">
            <h4 className="font-medium text-sm">功能开关</h4>
            <Separator />
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="memory" className="text-xs cursor-pointer">
                  启用会话记忆
                </Label>
                <Switch
                  id="memory"
                  checked={settings.enableMemory}
                  onCheckedChange={(checked) => updateSetting("enableMemory", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="streaming" className="text-xs cursor-pointer">
                  启用流式输出
                </Label>
                <Switch
                  id="streaming"
                  checked={settings.enableStreaming}
                  onCheckedChange={(checked) => updateSetting("enableStreaming", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="file-upload" className="text-xs cursor-pointer">
                  启用文件上传
                </Label>
                <Switch
                  id="file-upload"
                  checked={settings.enableFileUpload}
                  onCheckedChange={(checked) => updateSetting("enableFileUpload", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="multimodal" className="text-xs cursor-pointer">
                  启用多模态支持
                </Label>
                <Switch
                  id="multimodal"
                  checked={settings.enableMultimodal}
                  onCheckedChange={(checked) => updateSetting("enableMultimodal", checked)}
                />
              </div>
            </div>
          </Card>

          {/* 高级设置 */}
          <Card className="p-4 space-y-4">
            <h4 className="font-medium text-sm">高级设置</h4>
            <Separator />
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="debug" className="text-xs cursor-pointer">
                  调试模式
                </Label>
                <Switch
                  id="debug"
                  checked={settings.debugMode}
                  onCheckedChange={(checked) => updateSetting("debugMode", checked)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="log-level" className="text-xs">
                  日志级别
                </Label>
                <Select value={settings.logLevel} onValueChange={(value) => updateSetting("logLevel", value)}>
                  <SelectTrigger id="log-level" className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="debug">Debug</SelectItem>
                    <SelectItem value="info">Info</SelectItem>
                    <SelectItem value="warn">Warning</SelectItem>
                    <SelectItem value="error">Error</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>

          {/* 底部说明 */}
          <div className="text-xs text-muted-foreground bg-muted/50 rounded-md p-3">
            <p>💡 设置保存后将立即生效</p>
            <p className="mt-1">🔄 某些设置可能需要刷新页面才能完全应用</p>
          </div>
        </div>
      </ScrollArea>
      )}
    </div>
  )
}

