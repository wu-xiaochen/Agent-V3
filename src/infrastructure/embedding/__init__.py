"""
嵌入服务模块

提供文本嵌入生成的抽象接口及实现。
"""

from .embedding_service import EmbeddingService, OpenAIEmbeddingService, SentenceTransformerEmbeddingService, HuggingFaceEmbeddingService, CohereEmbeddingService, EmbeddingServiceFactory

__all__ = [
    "EmbeddingService",
    "OpenAIEmbeddingService",
    "SentenceTransformerEmbeddingService",
    "HuggingFaceEmbeddingService",
    "CohereEmbeddingService",
    "EmbeddingServiceFactory"
]