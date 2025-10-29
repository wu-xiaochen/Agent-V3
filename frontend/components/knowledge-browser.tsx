"use client"

import { useState } from "react"
import { Search, Upload, FileText, Tag } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

interface KnowledgeBase {
  id: string
  name: string
  documentCount: number
  tags: string[]
}

export function KnowledgeBrowser() {
  const [knowledgeBases] = useState<KnowledgeBase[]>([
    {
      id: "kb-1",
      name: "Product Documentation",
      documentCount: 24,
      tags: ["docs", "product"],
    },
    {
      id: "kb-2",
      name: "Customer Support",
      documentCount: 156,
      tags: ["support", "faq"],
    },
    {
      id: "kb-3",
      name: "Research Papers",
      documentCount: 42,
      tags: ["research", "ai"],
    },
  ])

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search knowledge bases..." className="pl-8 h-9" />
        </div>
        <Button size="sm" className="bg-primary text-primary-foreground">
          <Upload className="h-3 w-3 mr-1" />
          Upload
        </Button>
      </div>

      <ScrollArea className="h-[calc(100vh-250px)]">
        <div className="space-y-3">
          {knowledgeBases.map((kb) => (
            <Card key={kb.id} className="p-4 space-y-3 hover:bg-accent/50 transition-colors cursor-pointer">
              <div className="flex items-start justify-between">
                <div className="space-y-1 flex-1">
                  <h4 className="font-medium text-sm text-card-foreground">{kb.name}</h4>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <FileText className="h-3 w-3" />
                    <span>{kb.documentCount} documents</span>
                  </div>
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
          ))}
        </div>
      </ScrollArea>

      <Button variant="outline" className="w-full bg-transparent" size="sm">
        Create New Knowledge Base
      </Button>
    </div>
  )
}
