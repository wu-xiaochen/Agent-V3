"use client"

import { useState, useEffect, useRef } from "react"
import { Search, Upload, FileText, Tag, Plus, Trash2, Database } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { api } from "@/lib/api"

interface KnowledgeBase {
  id: string
  name: string
  description?: string
  documentCount: number
  tags: string[]
  createdAt?: string
}

export function KnowledgeBrowser() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newKbName, setNewKbName] = useState("")
  const [newKbDescription, setNewKbDescription] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 加载知识库列表
  const loadKnowledgeBases = async () => {
    setIsLoading(true)
    try {
      const result = await api.knowledge.listKnowledgeBases()
      // 暂时使用模拟数据，等后端API实现后替换
      if (result.length === 0) {
        setKnowledgeBases([
          {
            id: "kb-1",
            name: "Product Documentation",
            description: "产品相关文档和说明",
            documentCount: 24,
            tags: ["docs", "product"],
            createdAt: new Date().toISOString()
          },
          {
            id: "kb-2",
            name: "Customer Support",
            description: "客户支持和常见问题",
            documentCount: 156,
            tags: ["support", "faq"],
            createdAt: new Date().toISOString()
          },
          {
            id: "kb-3",
            name: "Research Papers",
            description: "AI和机器学习相关研究",
            documentCount: 42,
            tags: ["research", "ai"],
            createdAt: new Date().toISOString()
          },
        ])
      } else {
        setKnowledgeBases(result)
      }
    } catch (error) {
      console.error("加载知识库失败:", error)
      // 使用模拟数据
      setKnowledgeBases([
        {
          id: "kb-1",
          name: "Product Documentation",
          description: "产品相关文档和说明",
          documentCount: 24,
          tags: ["docs", "product"],
          createdAt: new Date().toISOString()
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  // 创建新知识库
  const handleCreateKnowledgeBase = async () => {
    if (!newKbName.trim()) return

    try {
      const newKb = await api.knowledge.createKnowledgeBase(newKbName, newKbDescription)
      setKnowledgeBases([...knowledgeBases, newKb])
      setIsDialogOpen(false)
      setNewKbName("")
      setNewKbDescription("")
    } catch (error) {
      console.error("创建知识库失败:", error)
      alert("创建知识库功能暂未实现，请等待后端支持")
    }
  }

  // 上传文档
  const handleUploadDocument = (kbId: string) => {
    // TODO: 实现文档上传
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  // 删除知识库
  const handleDeleteKnowledgeBase = async (kbId: string) => {
    if (!confirm("确定要删除这个知识库吗？")) return
    
    try {
      // TODO: 调用删除API
      setKnowledgeBases(knowledgeBases.filter(kb => kb.id !== kbId))
    } catch (error) {
      console.error("删除知识库失败:", error)
    }
  }

  // 过滤知识库
  const filteredKbs = knowledgeBases.filter(kb => 
    kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    kb.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    kb.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="space-y-4">
      {/* 搜索和上传 */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search knowledge bases..." 
            className="pl-8 h-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-primary text-primary-foreground">
              <Plus className="h-3 w-3 mr-1" />
              New KB
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Knowledge Base</DialogTitle>
              <DialogDescription>
                Create a new knowledge base to store and organize your documents.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="kb-name">Name</Label>
                <Input
                  id="kb-name"
                  placeholder="e.g., Product Documentation"
                  value={newKbName}
                  onChange={(e) => setNewKbName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="kb-description">Description</Label>
                <Textarea
                  id="kb-description"
                  placeholder="Describe what this knowledge base contains..."
                  value={newKbDescription}
                  onChange={(e) => setNewKbDescription(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateKnowledgeBase}>
                <Database className="h-4 w-4 mr-2" />
                Create
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* 知识库列表 */}
      <ScrollArea className="h-[calc(100vh-250px)]">
        <div className="space-y-3">
          {isLoading ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              Loading knowledge bases...
            </div>
          ) : filteredKbs.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              {searchQuery ? "No matching knowledge bases found" : "No knowledge bases yet"}
            </div>
          ) : (
            filteredKbs.map((kb) => (
              <Card key={kb.id} className="p-4 space-y-3 hover:bg-accent/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="space-y-1 flex-1 cursor-pointer">
                    <h4 className="font-medium text-sm text-card-foreground">{kb.name}</h4>
                    {kb.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2">{kb.description}</p>
                    )}
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <FileText className="h-3 w-3" />
                      <span>{kb.documentCount} documents</span>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => handleUploadDocument(kb.id)}
                    >
                      <Upload className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => handleDeleteKnowledgeBase(kb.id)}
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </Button>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1">
                  {kb.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      <Tag className="h-2 w-2 mr-1" />
                      {tag}
                    </Badge>
                  ))}
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        multiple
        accept=".pdf,.doc,.docx,.txt,.md"
        onChange={(e) => {
          // TODO: 处理文件上传
          console.log("Files selected:", e.target.files)
        }}
      />
    </div>
  )
}
