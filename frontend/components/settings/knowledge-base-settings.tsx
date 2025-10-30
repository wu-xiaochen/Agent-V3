"use client"

import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"

export function KnowledgeBaseSettings() {
  return (
    <div className="space-y-4">
      <div className="text-center py-12 text-muted-foreground">
        <p>Knowledge base feature coming soon...</p>
        <Button className="mt-4" disabled>
          <Plus className="mr-2 h-4 w-4" />
          Create Knowledge Base
        </Button>
      </div>
    </div>
  )
}

