"""
知识库数据模型

定义知识库、文档和检索结果的数据结构
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class KnowledgeBase(BaseModel):
    """知识库模型"""
    id: str
    name: str
    description: str = ""
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    created_at: str
    updated_at: str
    document_count: int = 0
    metadata: Dict[str, Any] = {}


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    embedding_model: str = Field(default="text-embedding-3-small")
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class Document(BaseModel):
    """文档模型"""
    id: str
    kb_id: str
    filename: str
    file_type: str
    file_size: int
    file_path: str
    content: str
    chunk_count: int = 0
    status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    created_at: str
    metadata: Dict[str, Any] = {}


class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    kb_id: str
    file_id: str  # 从文件服务上传后获得的ID
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """文档块模型"""
    id: str
    doc_id: str
    kb_id: str
    content: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}


class SearchRequest(BaseModel):
    """知识库检索请求"""
    kb_id: str
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata_filter: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """检索结果"""
    content: str
    score: float
    metadata: Dict[str, Any]
    doc_id: str
    chunk_id: str


class SearchResponse(BaseModel):
    """检索响应"""
    success: bool
    kb_id: str
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float

