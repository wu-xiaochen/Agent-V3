"use client"

import { useState, useEffect, useRef } from "react"
import { Plus, Trash2, Upload, FileText, Search, X, Loader2, Database, Eye, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import type { KnowledgeBase, Document, SearchResponse } from "@/lib/api/knowledge-base"

export function KnowledgeBaseSettings() {
  const { toast } = useToast()
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedKb, setSelectedKb] = useState<KnowledgeBase | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [testQuery, setTestQuery] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // 创建知识库表单
  const [newKbName, setNewKbName] = useState("")
  const [newKbDescription, setNewKbDescription] = useState("")
  const [newKbChunkSize, setNewKbChunkSize] = useState(1000)
  const [newKbChunkOverlap, setNewKbChunkOverlap] = useState(200)

  // 加载知识库列表
  const loadKnowledgeBases = async () => {
    setIsLoading(true)
    try {
      const kbs = await api.knowledge.listKnowledgeBases()
      setKnowledgeBases(kbs)
    } catch (error) {
      console.error("加载知识库失败:", error)
      toast({
        title: "加载失败",
        description: error instanceof Error ? error.message : "无法加载知识库列表",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  // 创建知识库
  const handleCreateKnowledgeBase = async () => {
    if (!newKbName.trim()) {
      toast({
        title: "验证失败",
        description: "请输入知识库名称",
        variant: "destructive"
      })
      return
    }

    setIsCreating(true)
    try {
      const kb = await api.knowledge.createKnowledgeBase({
        name: newKbName,
        description: newKbDescription || "",
        chunk_size: newKbChunkSize,
        chunk_overlap: newKbChunkOverlap
      })
      
      setKnowledgeBases([kb, ...knowledgeBases])
      setIsDialogOpen(false)
      setNewKbName("")
      setNewKbDescription("")
      setNewKbChunkSize(1000)
      setNewKbChunkOverlap(200)
      
      toast({
        title: "创建成功",
        description: `知识库 "${kb.name}" 已创建`
      })
    } catch (error) {
      console.error("创建知识库失败:", error)
      toast({
        title: "创建失败",
        description: error instanceof Error ? error.message : "无法创建知识库",
        variant: "destructive"
      })
    } finally {
      setIsCreating(false)
    }
  }

  // 删除知识库
  const handleDeleteKnowledgeBase = async (kbId: string, kbName: string) => {
    if (!confirm(`确定要删除知识库 "${kbName}" 吗？此操作不可恢复。`)) {
      return
    }

    try {
      await api.knowledge.deleteKnowledgeBase(kbId)
      setKnowledgeBases(knowledgeBases.filter(kb => kb.id !== kbId))
      if (selectedKb?.id === kbId) {
        setSelectedKb(null)
        setDocuments([])
        setSearchResults(null)
      }
      toast({
        title: "删除成功",
        description: `知识库 "${kbName}" 已删除`
      })
    } catch (error) {
      console.error("删除知识库失败:", error)
      toast({
        title: "删除失败",
        description: error instanceof Error ? error.message : "无法删除知识库",
        variant: "destructive"
      })
    }
  }

  // 加载文档列表
  const loadDocuments = async (kbId: string) => {
    setIsLoadingDocs(true)
    try {
      const docs = await api.knowledge.listDocuments(kbId)
      setDocuments(docs)
    } catch (error) {
      console.error("加载文档列表失败:", error)
      toast({
        title: "加载失败",
        description: error instanceof Error ? error.message : "无法加载文档列表",
        variant: "destructive"
      })
    } finally {
      setIsLoadingDocs(false)
    }
  }

  // 选择知识库查看详情
  const handleSelectKb = async (kb: KnowledgeBase) => {
    setSelectedKb(kb)
    setSearchResults(null)
    setDocuments([])
    await loadDocuments(kb.id)
  }

  // 删除文档
  const handleDeleteDocument = async (kbId: string, docId: string, filename: string) => {
    if (!confirm(`确定要删除文档 "${filename}" 吗？`)) {
      return
    }

    try {
      await api.knowledge.deleteDocument(kbId, docId)
      setDocuments(documents.filter(doc => doc.id !== docId))
      await loadKnowledgeBases() // 更新文档计数
      toast({
        title: "删除成功",
        description: `文档 "${filename}" 已删除`
      })
    } catch (error) {
      console.error("删除文档失败:", error)
      toast({
        title: "删除失败",
        description: error instanceof Error ? error.message : "无法删除文档",
        variant: "destructive"
      })
    }
  }

  // 上传文档
  const handleUploadDocument = async (kbId: string, files: FileList | null) => {
    if (!files || files.length === 0) return

    for (const file of Array.from(files)) {
      try {
        // 1. 先上传文件到文件服务
        const uploadResult = await api.files.uploadFile(file, {
          fileType: file.type
        })

        if (!uploadResult.success) {
          throw new Error("文件上传失败")
        }

        // 2. 将文件添加到知识库
        const doc = await api.knowledge.uploadDocument(kbId, {
          file_id: uploadResult.file_id,
          metadata: {
            original_filename: file.name,
            uploaded_at: new Date().toISOString()
          }
        })

        toast({
          title: "上传成功",
          description: `文档 "${doc.filename}" 已添加到知识库`
        })

        // 重新加载知识库列表以更新文档计数
        await loadKnowledgeBases()
        // 如果当前选中了该知识库，重新加载文档列表
        if (selectedKb?.id === kbId) {
          await loadDocuments(kbId)
        }
      } catch (error) {
        console.error("上传文档失败:", error)
          toast({
            title: "上传失败",
            description: `无法上传 "${file.name}": ${error instanceof Error ? error.message : "未知错误"}`,
            variant: "destructive"
          })
      }
    }

    // 重置文件输入
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  // 测试查询
  const handleTestQuery = async (kbId: string, query: string) => {
    if (!query.trim()) {
      toast({
        title: "验证失败",
        description: "请输入查询内容",
        variant: "destructive"
      })
      return
    }

    setIsLoadingDocs(true)
    try {
      const response = await api.knowledge.searchKnowledgeBase(kbId, {
        query,
        top_k: 5,
        score_threshold: 0.0
      })
      setSearchResults(response)
      toast({
        title: "查询成功",
        description: `找到 ${response.total_results} 个相关结果`
      })
    } catch (error) {
      console.error("查询失败:", error)
      toast({
        title: "查询失败",
        description: error instanceof Error ? error.message : "无法执行查询",
        variant: "destructive"
      })
    } finally {
      setIsLoadingDocs(false)
    }
  }

  // 过滤知识库
  const filteredKbs = knowledgeBases.filter(kb => 
    kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    kb.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-4">
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-card-foreground">知识库管理</h3>
          <p className="text-sm text-muted-foreground mt-1">
            创建和管理知识库，上传文档，进行语义检索
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              新建知识库
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>创建知识库</DialogTitle>
              <DialogDescription>
                创建一个新的知识库来存储和组织文档
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="kb-name">名称 *</Label>
                <Input
                  id="kb-name"
                  placeholder="例如: 产品文档"
                  value={newKbName}
                  onChange={(e) => setNewKbName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="kb-description">描述</Label>
                <Textarea
                  id="kb-description"
                  placeholder="描述这个知识库的用途..."
                  value={newKbDescription}
                  onChange={(e) => setNewKbDescription(e.target.value)}
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="kb-chunk-size">分块大小</Label>
                  <Input
                    id="kb-chunk-size"
                    type="number"
                    min="100"
                    max="4000"
                    value={newKbChunkSize}
                    onChange={(e) => setNewKbChunkSize(parseInt(e.target.value) || 1000)}
                  />
                  <p className="text-xs text-muted-foreground">字符数</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="kb-chunk-overlap">重叠大小</Label>
                  <Input
                    id="kb-chunk-overlap"
                    type="number"
                    min="0"
                    max="1000"
                    value={newKbChunkOverlap}
                    onChange={(e) => setNewKbChunkOverlap(parseInt(e.target.value) || 200)}
                  />
                  <p className="text-xs text-muted-foreground">字符数</p>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                取消
              </Button>
              <Button onClick={handleCreateKnowledgeBase} disabled={isCreating}>
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    创建中...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    创建
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* 搜索框 */}
      <div className="relative">
        <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="搜索知识库..."
          className="pl-8"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* 知识库列表 */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <ScrollArea className="h-[calc(100vh-300px)]">
          <div className="space-y-3 pr-3">
            {filteredKbs.length === 0 ? (
              <div className="text-center text-muted-foreground text-sm py-12">
                {searchQuery ? "未找到匹配的知识库" : "暂无知识库，点击上方按钮创建"}
              </div>
            ) : (
              filteredKbs.map((kb) => (
                <Card 
                  key={kb.id} 
                  className={`p-4 space-y-3 hover:bg-accent/50 transition-colors cursor-pointer ${
                    selectedKb?.id === kb.id ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => handleSelectKb(kb)}
                >
                  <div className="flex items-start justify-between">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-sm">{kb.name}</h4>
                        <Badge variant="secondary" className="text-xs">
                          {kb.document_count} 文档
                        </Badge>
                      </div>
                      {kb.description && (
                        <p className="text-xs text-muted-foreground line-clamp-2">{kb.description}</p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>分块: {kb.chunk_size}/{kb.chunk_overlap}</span>
                        <span>模型: {kb.embedding_model}</span>
                        <span>{new Date(kb.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => fileInputRef.current?.click()}
                        title="上传文档"
                      >
                        <Upload className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => handleDeleteKnowledgeBase(kb.id, kb.name)}
                        title="删除知识库"
                      >
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </ScrollArea>
      )}

      {/* 知识库详情面板 */}
      {selectedKb && (
        <Card className="p-4 space-y-4 border-t-2 border-primary">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold">{selectedKb.name}</h4>
              <p className="text-sm text-muted-foreground mt-1">{selectedKb.description}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setSelectedKb(null)}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          <Separator />

          {/* 文档列表 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>文档列表 ({documents.length})</Label>
            </div>
            <ScrollArea className="h-[200px] rounded-md border p-3">
              {isLoadingDocs ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                </div>
              ) : documents.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  暂无文档，请上传文档
                </p>
              ) : (
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <Card key={doc.id} className="p-3 bg-muted/50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium text-sm">{doc.filename}</span>
                            <Badge variant="secondary" className="text-xs">
                              {doc.status}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground ml-6">
                            <span>{(doc.file_size / 1024).toFixed(2)} KB</span>
                            <span>{doc.chunk_count} chunks</span>
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                          </div>
                          {doc.error_message && (
                            <p className="text-xs text-destructive ml-6 mt-1">
                              {doc.error_message}
                            </p>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => handleDeleteDocument(selectedKb.id, doc.id, doc.filename)}
                          title="删除文档"
                        >
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          <Separator />

          {/* 文档上传 */}
          <div className="space-y-2">
            <Label>上传文档</Label>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                className="flex-1"
              >
                <Upload className="h-4 w-4 mr-2" />
                选择文件 (PDF/DOCX/TXT/MD)
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md"
                onChange={(e) => handleUploadDocument(selectedKb.id, e.target.files)}
              />
            </div>
          </div>

          {/* 测试查询 */}
          <div className="space-y-2">
            <Label>测试查询</Label>
            <div className="flex gap-2">
              <Input
                placeholder="输入查询内容..."
                value={testQuery}
                onChange={(e) => setTestQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleTestQuery(selectedKb.id, testQuery)}
              />
              <Button
                size="sm"
                onClick={() => handleTestQuery(selectedKb.id, testQuery)}
                disabled={isLoadingDocs || !testQuery.trim()}
              >
                {isLoadingDocs ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    查询
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* 查询结果 */}
          {searchResults && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>查询结果 ({searchResults.total_results})</Label>
                <Badge variant="outline" className="text-xs">
                  耗时: {searchResults.search_time.toFixed(3)}s
                </Badge>
              </div>
              <ScrollArea className="h-[200px] rounded-md border p-3">
                <div className="space-y-3">
                  {searchResults.results.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      未找到相关结果
                    </p>
                  ) : (
                    searchResults.results.map((result, index) => (
                      <Card key={index} className="p-3 bg-muted/50">
                        <div className="flex items-start justify-between mb-2">
                          <Badge variant="secondary" className="text-xs">
                            相似度: {(result.score * 100).toFixed(1)}%
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {result.doc_id}
                          </Badge>
                        </div>
                        <p className="text-sm line-clamp-3">{result.content}</p>
                        {result.metadata && Object.keys(result.metadata).length > 0 && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            <span>元数据: </span>
                            {Object.entries(result.metadata)
                              .filter(([k]) => k !== "doc_id" && k !== "chunk_index")
                              .slice(0, 3)
                              .map(([k, v]) => `${k}: ${v}`)
                              .join(", ")}
                          </div>
                        )}
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
