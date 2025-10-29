"""知识库基础设施模块"""

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeBaseManager,
    KnowledgeBaseType,
    StorageBackend,
    Document,
    get_knowledge_base_manager
)

__all__ = [
    "KnowledgeBase",
    "KnowledgeBaseManager",
    "KnowledgeBaseType",
    "StorageBackend",
    "Document",
    "get_knowledge_base_manager"
]

