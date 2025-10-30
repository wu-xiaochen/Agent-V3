"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { 
  Plus, 
  Search, 
  FileText, 
  Trash2, 
  Upload,
  Database,
  AlertCircle
} from "lucide-react"
import { api } from "@/lib/api"
import type { KnowledgeBase } from "@/lib/api/knowledge-base"

export default function KnowledgePage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKB, setSelectedKB] = useState<KnowledgeBase | null>(null)
  const [loading, setLoading] = useState(false)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const { toast } = useToast()

  // 新建知识库表单
  const [newKB, setNewKB] = useState({
    name: "",
    description: "",
    chunk_size: 1000,
    chunk_overlap: 200
  })

  // 加载知识库列表
  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  const loadKnowledgeBases = async () => {
    try {
      setLoading(true)
      const response = await api.knowledgeBase.list()
      if (response.success) {
        setKnowledgeBases(response.knowledge_bases)
      }
    } catch (error) {
      console.error("加载知识库失败:", error)
      toast({
        title: "加载失败",
        description: "无法加载知识库列表",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateKB = async () => {
    if (!newKB.name.trim()) {
      toast({
        title: "验证失败",
        description: "请输入知识库名称",
        variant: "destructive"
      })
      return
    }

    try {
      const response = await api.knowledgeBase.create(newKB)
      if (response.success) {
        toast({
          title: "创建成功",
          description: `知识库 "${newKB.name}" 已创建`
        })
        setCreateDialogOpen(false)
        setNewKB({ name: "", description: "", chunk_size: 1000, chunk_overlap: 200 })
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error("创建知识库失败:", error)
      toast({
        title: "创建失败",
        description: "无法创建知识库",
        variant: "destructive"
      })
    }
  }

  const handleDeleteKB = async (kbId: string, kbName: string) => {
    if (!confirm(`确定要删除知识库 "${kbName}" 吗？此操作不可撤销。`)) {
      return
    }

    try {
      const response = await api.knowledgeBase.delete(kbId)
      if (response.success) {
        toast({
          title: "删除成功",
          description: `知识库 "${kbName}" 已删除`
        })
        if (selectedKB?.id === kbId) {
          setSelectedKB(null)
        }
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error("删除知识库失败:", error)
      toast({
        title: "删除失败",
        description: "无法删除知识库",
        variant: "destructive"
      })
    }
  }

  // 过滤知识库
  const filteredKBs = knowledgeBases.filter(kb =>
    kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    kb.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Knowledge Base</h1>
          <p className="text-muted-foreground mt-1">
            Manage your knowledge bases and documents
          </p>
        </div>
        
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Knowledge Base
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Knowledge Base</DialogTitle>
              <DialogDescription>
                Create a new knowledge base to store and search documents
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 mt-4">
              <div>
                <Label>Name *</Label>
                <Input
                  value={newKB.name}
                  onChange={(e) => setNewKB({ ...newKB, name: e.target.value })}
                  placeholder="e.g., AI Research"
                />
              </div>
              
              <div>
                <Label>Description</Label>
                <Textarea
                  value={newKB.description}
                  onChange={(e) => setNewKB({ ...newKB, description: e.target.value })}
                  placeholder="Brief description of this knowledge base"
                  rows={3}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Chunk Size</Label>
                  <Input
                    type="number"
                    value={newKB.chunk_size}
                    onChange={(e) => setNewKB({ ...newKB, chunk_size: parseInt(e.target.value) })}
                    min={100}
                    max={4000}
                  />
                  <p className="text-xs text-muted-foreground mt-1">100-4000 characters</p>
                </div>
                
                <div>
                  <Label>Chunk Overlap</Label>
                  <Input
                    type="number"
                    value={newKB.chunk_overlap}
                    onChange={(e) => setNewKB({ ...newKB, chunk_overlap: parseInt(e.target.value) })}
                    min={0}
                    max={1000}
                  />
                  <p className="text-xs text-muted-foreground mt-1">0-1000 characters</p>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateKB}>
                Create
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* 搜索栏 */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            className="pl-10"
            placeholder="Search knowledge bases..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* 知识库列表 */}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground">
          Loading knowledge bases...
        </div>
      ) : filteredKBs.length === 0 ? (
        <Card className="p-12 text-center">
          <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Knowledge Bases</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery ? "No results found. Try a different search." : "Get started by creating your first knowledge base"}
          </p>
          {!searchQuery && (
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Knowledge Base
            </Button>
          )}
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredKBs.map((kb) => (
            <Card
              key={kb.id}
              className="p-6 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedKB(kb)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-1">{kb.name}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {kb.description || "No description"}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteKB(kb.id, kb.name)
                  }}
                  className="shrink-0"
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Documents:</span>
                  <Badge variant="secondary">{kb.document_count}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Chunk Size:</span>
                  <span className="font-medium">{kb.chunk_size}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Created:</span>
                  <span className="font-medium">
                    {new Date(kb.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* 知识库详情对话框（占位，后续扩展） */}
      {selectedKB && (
        <Dialog open={!!selectedKB} onOpenChange={() => setSelectedKB(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{selectedKB.name}</DialogTitle>
              <DialogDescription>
                {selectedKB.description || "No description"}
              </DialogDescription>
            </DialogHeader>
            
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Document upload and search features coming soon...
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground">Knowledge Base ID</p>
                  <p className="font-mono text-sm">{selectedKB.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Document Count</p>
                  <p className="font-semibold">{selectedKB.document_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Embedding Model</p>
                  <p className="text-sm">{selectedKB.embedding_model}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Updated</p>
                  <p className="text-sm">{new Date(selectedKB.updated_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

