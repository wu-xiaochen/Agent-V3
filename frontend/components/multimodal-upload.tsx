"use client"

import { useState, useRef } from "react"
import { Image as ImageIcon, File, X, Upload, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface UploadedFile {
  id: string
  file: File
  preview?: string
  type: 'image' | 'document'
  status: 'uploading' | 'success' | 'error'
  url?: string
}

interface MultimodalUploadProps {
  onFilesChange: (files: UploadedFile[]) => void
  maxFiles?: number
  acceptImage?: boolean
  acceptDocument?: boolean
}

export function MultimodalUpload({
  onFilesChange,
  maxFiles = 5,
  acceptImage = true,
  acceptDocument = true
}: MultimodalUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    
    if (uploadedFiles.length + files.length > maxFiles) {
      alert(`最多只能上传 ${maxFiles} 个文件`)
      return
    }

    const newFiles: UploadedFile[] = []
    
    for (const file of files) {
      const fileType = file.type.startsWith('image/') ? 'image' : 'document'
      
      // 检查文件类型是否允许
      if (fileType === 'image' && !acceptImage) continue
      if (fileType === 'document' && !acceptDocument) continue
      
      const uploadedFile: UploadedFile = {
        id: `file-${Date.now()}-${Math.random()}`,
        file,
        type: fileType,
        status: 'uploading'
      }
      
      // 为图片生成预览
      if (fileType === 'image') {
        uploadedFile.preview = URL.createObjectURL(file)
      }
      
      newFiles.push(uploadedFile)
    }
    
    setUploadedFiles(prev => [...prev, ...newFiles])
    
    // 模拟上传（实际应该调用API）
    newFiles.forEach(async (uploadedFile, index) => {
      try {
        // TODO: 调用实际的上传API
        const { api } = await import("@/lib/api")
        const response = await api.files.uploadFile(uploadedFile.file, {
          fileType: uploadedFile.type
        })
        
        if (response.success) {
          setUploadedFiles(prev =>
            prev.map(f =>
              f.id === uploadedFile.id
                ? { ...f, status: 'success' as const, url: response.download_url }
                : f
            )
          )
        } else {
          throw new Error(response.error || 'Upload failed')
        }
      } catch (error) {
        console.error("文件上传失败:", error)
        setUploadedFiles(prev =>
          prev.map(f =>
            f.id === uploadedFile.id ? { ...f, status: 'error' as const } : f
          )
        )
      }
    })
    
    // 通知父组件
    onFilesChange([...uploadedFiles, ...newFiles])
    
    // 清空input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeFile = (id: string) => {
    const file = uploadedFiles.find(f => f.id === id)
    if (file?.preview) {
      URL.revokeObjectURL(file.preview)
    }
    
    const newFiles = uploadedFiles.filter(f => f.id !== id)
    setUploadedFiles(newFiles)
    onFilesChange(newFiles)
  }

  const getAcceptTypes = () => {
    const types = []
    if (acceptImage) types.push('image/*')
    if (acceptDocument) types.push('.pdf,.doc,.docx,.txt,.md')
    return types.join(',')
  }

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={getAcceptTypes()}
        onChange={handleFileSelect}
        className="hidden"
      />
      
      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {uploadedFiles.map((file) => (
            <Card
              key={file.id}
              className={cn(
                "relative p-2 flex items-center gap-2",
                file.status === 'error' && "border-destructive"
              )}
            >
              {file.type === 'image' && file.preview ? (
                <img
                  src={file.preview}
                  alt={file.file.name}
                  className="w-16 h-16 object-cover rounded"
                />
              ) : (
                <div className="w-16 h-16 flex items-center justify-center bg-muted rounded">
                  <File className="h-8 w-8 text-muted-foreground" />
                </div>
              )}
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.file.size / 1024).toFixed(1)} KB
                </p>
                {file.status === 'uploading' && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>上传中...</span>
                  </div>
                )}
                {file.status === 'error' && (
                  <p className="text-xs text-destructive">上传失败</p>
                )}
              </div>
              
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 shrink-0"
                onClick={() => removeFile(file.id)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Card>
          ))}
        </div>
      )}
      
      {uploadedFiles.length < maxFiles && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          className="w-full"
        >
          <Upload className="h-4 w-4 mr-2" />
          上传文件 ({uploadedFiles.length}/{maxFiles})
        </Button>
      )}
    </div>
  )
}

