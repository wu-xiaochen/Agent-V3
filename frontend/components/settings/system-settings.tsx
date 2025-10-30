"use client"

import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function SystemSettings() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label htmlFor="llm-provider">LLM Provider</Label>
          <Select defaultValue="siliconflow">
            <SelectTrigger id="llm-provider">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="siliconflow">SiliconFlow</SelectItem>
              <SelectItem value="openai">OpenAI</SelectItem>
              <SelectItem value="anthropic">Anthropic</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="api-key">API Key</Label>
          <Input 
            id="api-key" 
            type="password" 
            placeholder="sk-..." 
          />
        </div>

        <div>
          <Label htmlFor="model">Default Model</Label>
          <Input 
            id="model" 
            placeholder="Qwen/Qwen2.5-7B-Instruct" 
          />
        </div>
      </div>
    </div>
  )
}

