"use client"

import { useState } from "react"
import { Database, Plus, Upload, Trash2, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

interface KnowledgeBase {
  id: string
  name: string
  description: string
  documentCount: number
  vectorCount: number
  createdAt: string
  enabled: boolean
}

export default function KnowledgeSettingsPage() {
  const [knowledgeBases] = useState<KnowledgeBase[]>([
    {
      id: "kb1",
      name: "供应链知识库",
      description: "供应链管理相关文档和资料",
      documentCount: 15,
      vectorCount: 1250,
      createdAt: "2025-10-25",
      enabled: true
    }
  ])

  return (
    <div className="h-full">
      <ScrollArea className="h-full">
        <div className="p-6 space-y-6">
          {/* 头部 */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">知识库管理</h2>
              <p className="text-muted-foreground">
                管理知识库、上传文档、配置向量数据库
              </p>
            </div>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              创建知识库
            </Button>
          </div>

          <Separator />

          {/* 功能提示 */}
          <Card className="border-dashed">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                知识库功能 (开发中)
              </CardTitle>
              <CardDescription>
                知识库功能正在开发中，敬请期待！即将支持：
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <Badge variant="outline">规划中</Badge>
                  创建和管理多个知识库
                </li>
                <li className="flex items-center gap-2">
                  <Badge variant="outline">规划中</Badge>
                  上传文档（PDF、Word、Markdown等）
                </li>
                <li className="flex items-center gap-2">
                  <Badge variant="outline">规划中</Badge>
                  向量化文档内容（ChromaDB/Faiss）
                </li>
                <li className="flex items-center gap-2">
                  <Badge variant="outline">规划中</Badge>
                  Agent 挂载知识库，进行语义搜索
                </li>
                <li className="flex items-center gap-2">
                  <Badge variant="outline">规划中</Badge>
                  CrewAI 团队共享知识库
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* 现有知识库列表（示例） */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">现有知识库</h3>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {knowledgeBases.map((kb) => (
                <Card key={kb.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Database className="h-4 w-4" />
                        <CardTitle className="text-base">{kb.name}</CardTitle>
                      </div>
                      <Badge variant={kb.enabled ? "default" : "secondary"}>
                        {kb.enabled ? "启用" : "禁用"}
                      </Badge>
                    </div>
                    <CardDescription>{kb.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">文档数量</span>
                        <span className="font-medium">{kb.documentCount}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">向量数量</span>
                        <span className="font-medium">{kb.vectorCount}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">创建时间</span>
                        <span className="font-medium">{kb.createdAt}</span>
                      </div>
                    </div>
                    <Separator className="my-4" />
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1" disabled>
                        <Upload className="mr-2 h-3 w-3" />
                        上传文档
                      </Button>
                      <Button variant="outline" size="sm" disabled>
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}

