"""
向量存储接口

支持多种向量数据库后端：
- ChromaDB (默认，轻量级，无需额外服务)
- FAISS (Facebook AI，高性能)
- Pinecone (云服务)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """向量存储抽象基类"""
    
    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文档"""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索文档"""
        pass
    
    @abstractmethod
    def delete_documents(self, ids: List[str]) -> bool:
        """删除文档"""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """获取文档数量"""
        pass


class ChromaDBStore(VectorStore):
    """
    ChromaDB 向量存储
    
    优点：
    - 轻量级，无需额外服务
    - 易于部署
    - 支持本地和远程模式
    """
    
    def __init__(
        self,
        collection_name: str,
        persist_directory: str,
        embedding_function: Optional[Any] = None
    ):
        """
        初始化 ChromaDB 存储
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录
            embedding_function: 嵌入函数
        """
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "ChromaDB 未安装。请运行: pip install chromadb"
            )
        
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # 创建客户端
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.persist_directory)
        ))
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        
        logger.info(f"✅ ChromaDB 存储已初始化: {collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文档到向量存储"""
        try:
            # 生成ID（如果未提供）
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # 添加文档
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ 添加 {len(documents)} 个文档到 ChromaDB")
            return ids
            
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似文档"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_dict
            )
            
            # 格式化结果
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    doc = results["documents"][0][i]
                    distance = results["distances"][0][i] if "distances" in results else 0.0
                    metadata = results["metadatas"][0][i] if "metadatas" in results else {}
                    
                    formatted_results.append((doc, distance, metadata))
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 搜索文档失败: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """删除文档"""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"🗑️  删除 {len(ids)} 个文档")
            return True
        except Exception as e:
            logger.error(f"❌ 删除文档失败: {e}")
            return False
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"❌ 获取文档数量失败: {e}")
            return 0


class FAISSStore(VectorStore):
    """
    FAISS 向量存储
    
    优点：
    - 高性能
    - 适合大规模数据
    - Facebook AI 出品
    """
    
    def __init__(
        self,
        index_path: str,
        embedding_dim: int = 768,
        embedding_function: Optional[Any] = None
    ):
        """
        初始化 FAISS 存储
        
        Args:
            index_path: 索引文件路径
            embedding_dim: 嵌入维度
            embedding_function: 嵌入函数
        """
        try:
            import faiss
            import numpy as np
        except ImportError:
            raise ImportError(
                "FAISS 未安装。请运行: pip install faiss-cpu 或 pip install faiss-gpu"
            )
        
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedding_dim = embedding_dim
        self.embedding_function = embedding_function
        
        # 创建或加载索引
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            logger.info(f"✅ 加载 FAISS 索引: {index_path}")
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
            logger.info(f"✅ 创建 FAISS 索引: {index_path}")
        
        # 文档存储（ID -> 文档内容和元数据）
        self.documents = {}
        self.doc_id_to_index = {}  # doc_id -> index_position
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文档到向量存储"""
        try:
            import numpy as np
            import uuid
            
            # 生成ID
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # 生成嵌入
            if self.embedding_function is None:
                raise ValueError("需要提供 embedding_function")
            
            embeddings = []
            for doc in documents:
                embedding = self.embedding_function(doc)
                embeddings.append(embedding)
            
            embeddings_array = np.array(embeddings).astype('float32')
            
            # 添加到索引
            start_index = self.index.ntotal
            self.index.add(embeddings_array)
            
            # 保存文档信息
            for i, doc_id in enumerate(ids):
                self.documents[doc_id] = {
                    "content": documents[i],
                    "metadata": metadatas[i] if metadatas else {}
                }
                self.doc_id_to_index[doc_id] = start_index + i
            
            # 保存索引
            import faiss
            faiss.write_index(self.index, str(self.index_path))
            
            logger.info(f"✅ 添加 {len(documents)} 个文档到 FAISS")
            return ids
            
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似文档"""
        try:
            import numpy as np
            
            # 生成查询嵌入
            if self.embedding_function is None:
                raise ValueError("需要提供 embedding_function")
            
            query_embedding = self.embedding_function(query)
            query_array = np.array([query_embedding]).astype('float32')
            
            # 搜索
            distances, indices = self.index.search(query_array, top_k)
            
            # 格式化结果
            results = []
            for i, idx in enumerate(indices[0]):
                if idx == -1:  # FAISS 返回 -1 表示没有找到
                    continue
                
                # 查找对应的文档ID
                doc_id = None
                for did, index_pos in self.doc_id_to_index.items():
                    if index_pos == idx:
                        doc_id = did
                        break
                
                if doc_id and doc_id in self.documents:
                    doc_info = self.documents[doc_id]
                    results.append((
                        doc_info["content"],
                        float(distances[0][i]),
                        doc_info["metadata"]
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索文档失败: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """删除文档"""
        # FAISS 不支持直接删除，需要重建索引
        logger.warning("⚠️  FAISS 不支持直接删除文档，需要重建索引")
        return False
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        return self.index.ntotal


def create_vector_store(
    backend: str,
    collection_name: str,
    persist_directory: str,
    embedding_function: Optional[Any] = None,
    **kwargs
) -> VectorStore:
    """
    创建向量存储实例
    
    Args:
        backend: 后端类型 (chromadb, faiss)
        collection_name: 集合名称
        persist_directory: 持久化目录
        embedding_function: 嵌入函数
        **kwargs: 其他参数
        
    Returns:
        向量存储实例
    """
    if backend.lower() == "chromadb":
        return ChromaDBStore(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=embedding_function
        )
    elif backend.lower() == "faiss":
        index_path = Path(persist_directory) / f"{collection_name}.faiss"
        return FAISSStore(
            index_path=str(index_path),
            embedding_dim=kwargs.get("embedding_dim", 768),
            embedding_function=embedding_function
        )
    else:
        raise ValueError(f"不支持的向量存储后端: {backend}")

