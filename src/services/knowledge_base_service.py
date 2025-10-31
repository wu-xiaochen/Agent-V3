"""
知识库服务

提供知识库的创建、文档上传、Embedding和检索功能
"""

import json
import uuid
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from src.models.knowledge_base import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    Document,
    DocumentChunk,
    SearchRequest,
    SearchResult,
    SearchResponse
)

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """知识库服务"""
    
    def __init__(self, data_dir: str = "data/knowledge_bases"):
        """
        初始化知识库服务
        
        Args:
            data_dir: 知识库数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 向量数据库（使用ChromaDB）
        self.vector_db = None
        self._init_vector_db()
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # 持久化存储
            persist_dir = str(self.data_dir / "chroma")
            Path(persist_dir).mkdir(parents=True, exist_ok=True)
            
            self.vector_db = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"✅ ChromaDB初始化成功: {persist_dir}")
            
        except ImportError:
            logger.warning("⚠️  ChromaDB未安装，知识库功能将受限")
            self.vector_db = None
        except Exception as e:
            logger.error(f"❌ ChromaDB初始化失败: {e}")
            self.vector_db = None
    
    def _get_kb_path(self, kb_id: str) -> Path:
        """获取知识库存储路径"""
        return self.data_dir / kb_id
    
    def _get_kb_meta_file(self, kb_id: str) -> Path:
        """获取知识库元数据文件路径"""
        return self._get_kb_path(kb_id) / "metadata.json"
    
    def _get_doc_meta_file(self, kb_id: str, doc_id: str) -> Path:
        """获取文档元数据文件路径"""
        return self._get_kb_path(kb_id) / "documents" / f"{doc_id}.json"
    
    def list_documents(self, kb_id: str) -> List[Document]:
        """
        列出知识库中的所有文档
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            文档列表
        """
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return []
        
        docs_dir = self._get_kb_path(kb_id) / "documents"
        if not docs_dir.exists():
            return []
        
        documents = []
        for doc_file in docs_dir.glob("*.json"):
            try:
                with open(doc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    documents.append(Document(**data))
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"⚠️  读取文档元数据失败 {doc_file}: {e}")
        
        # 按创建时间倒序排序
        documents.sort(key=lambda x: x.created_at, reverse=True)
        return documents
    
    def delete_document(self, kb_id: str, doc_id: str) -> bool:
        """
        删除知识库中的文档
        
        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return False
        
        doc_meta_file = self._get_doc_meta_file(kb_id, doc_id)
        if not doc_meta_file.exists():
            return False
        
        try:
            # 从向量数据库中删除相关chunks
            if self.vector_db:
                try:
                    collection = self.vector_db.get_collection(name=kb_id)
                    # ChromaDB支持where条件删除
                    collection.delete(where={"doc_id": doc_id})
                    logger.info(f"✅ 向量数据库chunks删除成功: {doc_id}")
                except Exception as e:
                    logger.warning(f"⚠️  删除向量数据失败: {e}")
            
            # 删除文档元数据文件
            doc_meta_file.unlink()
            
            # 更新知识库文档计数
            kb.document_count = max(0, kb.document_count - 1)
            kb.updated_at = datetime.now().isoformat()
            meta_file = self._get_kb_meta_file(kb_id)
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(kb.model_dump(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 文档删除成功: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除文档失败: {e}")
            return False
    
    def create_knowledge_base(self, request: KnowledgeBaseCreate) -> KnowledgeBase:
        """
        创建知识库
        
        Args:
            request: 创建请求
            
        Returns:
            创建的知识库
        """
        kb_id = f"kb_{uuid.uuid4().hex[:12]}"
        kb_path = self._get_kb_path(kb_id)
        kb_path.mkdir(parents=True, exist_ok=True)
        
        # 创建documents子目录
        (kb_path / "documents").mkdir(exist_ok=True)
        
        now = datetime.now().isoformat()
        kb = KnowledgeBase(
            id=kb_id,
            name=request.name,
            description=request.description,
            embedding_model=request.embedding_model,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            created_at=now,
            updated_at=now,
            document_count=0,
            metadata=request.metadata
        )
        
        # 保存元数据
        meta_file = self._get_kb_meta_file(kb_id)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(kb.model_dump(), f, indent=2, ensure_ascii=False)
        
        # 创建ChromaDB collection
        if self.vector_db:
            try:
                self.vector_db.create_collection(
                    name=kb_id,
                    metadata={"kb_name": request.name}
                )
                logger.info(f"✅ 知识库Collection创建成功: {kb_id}")
            except Exception as e:
                logger.error(f"❌ 创建Collection失败: {e}")
        
        logger.info(f"✅ 知识库创建成功: {kb_id} - {request.name}")
        return kb
    
    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """
        获取知识库信息
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            知识库对象，不存在返回None
        """
        meta_file = self._get_kb_meta_file(kb_id)
        if not meta_file.exists():
            return None
        
        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return KnowledgeBase(**data)
    
    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        列出所有知识库
        
        Returns:
            知识库列表
        """
        kbs = []
        for kb_dir in self.data_dir.iterdir():
            if kb_dir.is_dir() and kb_dir.name != "chroma":
                meta_file = kb_dir / "metadata.json"
                if meta_file.exists():
                    with open(meta_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        kbs.append(KnowledgeBase(**data))
        
        # 按创建时间倒序排序
        kbs.sort(key=lambda x: x.created_at, reverse=True)
        return kbs
    
    def update_knowledge_base(self, kb_id: str, request: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        """
        更新知识库
        
        Args:
            kb_id: 知识库ID
            request: 更新请求
            
        Returns:
            更新后的知识库，不存在返回None
        """
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return None
        
        # 更新字段
        if request.name is not None:
            kb.name = request.name
        if request.description is not None:
            kb.description = request.description
        if request.metadata is not None:
            kb.metadata.update(request.metadata)
        
        kb.updated_at = datetime.now().isoformat()
        
        # 保存
        meta_file = self._get_kb_meta_file(kb_id)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(kb.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ 知识库更新成功: {kb_id}")
        return kb
    
    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            是否删除成功
        """
        kb_path = self._get_kb_path(kb_id)
        if not kb_path.exists():
            return False
        
        # 删除ChromaDB collection
        if self.vector_db:
            try:
                self.vector_db.delete_collection(name=kb_id)
                logger.info(f"✅ Collection删除成功: {kb_id}")
            except Exception as e:
                logger.warning(f"⚠️  删除Collection失败: {e}")
        
        # 删除文件
        import shutil
        shutil.rmtree(kb_path)
        
        logger.info(f"✅ 知识库删除成功: {kb_id}")
        return True
    
    def add_document(
        self,
        kb_id: str,
        file_path: str,
        filename: str,
        file_type: str,
        file_size: int,
        metadata: Dict[str, Any] = None
    ) -> Optional[Document]:
        """
        添加文档到知识库
        
        Args:
            kb_id: 知识库ID
            file_path: 文件路径
            filename: 文件名
            file_type: 文件类型
            file_size: 文件大小
            metadata: 元数据
            
        Returns:
            文档对象
        """
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            logger.error(f"❌ 知识库不存在: {kb_id}")
            return None
        
        # 解析文档内容
        from src.infrastructure.multimodal.document_parser import parse_document
        
        try:
            parse_result = parse_document(file_path)
            if not parse_result.get("success"):
                logger.error(f"❌ 文档解析失败: {parse_result.get('error')}")
                return None
            
            content = parse_result.get("full_text") or parse_result.get("content", "")
            
        except Exception as e:
            logger.error(f"❌ 文档解析异常: {e}")
            return None
        
        # 创建文档记录
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        doc = Document(
            id=doc_id,
            kb_id=kb_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            content=content,
            status="processing",
            created_at=now,
            metadata=metadata or {}
        )
        
        # 保存文档元数据
        doc_meta_file = self._get_doc_meta_file(kb_id, doc_id)
        with open(doc_meta_file, "w", encoding="utf-8") as f:
            json.dump(doc.model_dump(), f, indent=2, ensure_ascii=False)
        
        # 分块和向量化
        try:
            chunks = self._split_document(content, kb.chunk_size, kb.chunk_overlap)
            doc.chunk_count = len(chunks)
            
            # 存储到向量数据库
            if self.vector_db:
                self._add_chunks_to_vector_db(kb_id, doc_id, chunks, doc.metadata)
            
            doc.status = "completed"
            logger.info(f"✅ 文档处理成功: {doc_id} ({len(chunks)} chunks)")
            
        except Exception as e:
            doc.status = "failed"
            doc.error_message = str(e)
            logger.error(f"❌ 文档处理失败: {e}")
        
        # 更新文档状态
        with open(doc_meta_file, "w", encoding="utf-8") as f:
            json.dump(doc.model_dump(), f, indent=2, ensure_ascii=False)
        
        # 更新知识库文档计数
        kb.document_count += 1
        kb.updated_at = datetime.now().isoformat()
        meta_file = self._get_kb_meta_file(kb_id)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(kb.model_dump(), f, indent=2, ensure_ascii=False)
        
        return doc
    
    def _split_document(self, content: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        分割文档为块
        
        Args:
            content: 文档内容
            chunk_size: 块大小
            chunk_overlap: 重叠大小
            
        Returns:
            文档块列表
        """
        chunks = []
        start = 0
        content_length = len(content)
        
        while start < content_length:
            end = start + chunk_size
            chunk = content[start:end]
            
            # 如果不是最后一个chunk，尝试在句子边界分割
            if end < content_length:
                # 查找最后一个句号、问号或感叹号
                for sep in ['. ', '。', '! ', '！', '? ', '？', '\n\n']:
                    last_sep = chunk.rfind(sep)
                    if last_sep > chunk_size * 0.5:  # 至少保留一半
                        chunk = chunk[:last_sep + len(sep)]
                        end = start + len(chunk)
                        break
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return [c for c in chunks if c]  # 过滤空块
    
    def _add_chunks_to_vector_db(
        self,
        kb_id: str,
        doc_id: str,
        chunks: List[str],
        doc_metadata: Dict[str, Any]
    ):
        """
        将文档块添加到向量数据库
        
        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            chunks: 文档块列表
            doc_metadata: 文档元数据
        """
        if not self.vector_db:
            logger.warning("⚠️  向量数据库未初始化")
            return
        
        collection = self.vector_db.get_collection(name=kb_id)
        
        # 准备数据
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "chunk_index": i,
                **doc_metadata
            }
            for i in range(len(chunks))
        ]
        
        # 批量添加（ChromaDB会自动生成embeddings）
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"✅ 向量存储成功: {len(chunks)} chunks")
    
    def search(self, request: SearchRequest) -> SearchResponse:
        """
        检索知识库
        
        Args:
            request: 检索请求
            
        Returns:
            检索响应
        """
        start_time = time.time()
        
        if not self.vector_db:
            return SearchResponse(
                success=False,
                kb_id=request.kb_id,
                query=request.query,
                results=[],
                total_results=0,
                search_time=0.0
            )
        
        try:
            collection = self.vector_db.get_collection(name=request.kb_id)
            
            # 执行检索
            results = collection.query(
                query_texts=[request.query],
                n_results=request.top_k,
                where=request.metadata_filter
            )
            
            # 转换结果
            search_results = []
            if results and results["documents"] and len(results["documents"]) > 0:
                for i in range(len(results["documents"][0])):
                    # ChromaDB返回距离，转换为相似度分数（1 - distance）
                    distance = results["distances"][0][i] if results["distances"] else 0
                    score = 1.0 - min(distance, 1.0)  # 确保score在[0,1]范围内
                    
                    if score >= request.score_threshold:
                        search_results.append(SearchResult(
                            content=results["documents"][0][i],
                            score=score,
                            metadata=results["metadatas"][0][i],
                            doc_id=results["metadatas"][0][i].get("doc_id", ""),
                            chunk_id=results["ids"][0][i]
                        ))
            
            search_time = time.time() - start_time
            
            return SearchResponse(
                success=True,
                kb_id=request.kb_id,
                query=request.query,
                results=search_results,
                total_results=len(search_results),
                search_time=search_time
            )
            
        except Exception as e:
            logger.error(f"❌ 检索失败: {e}")
            return SearchResponse(
                success=False,
                kb_id=request.kb_id,
                query=request.query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time
            )

