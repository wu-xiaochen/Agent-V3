"""
知识库管理系统

功能：
1. 知识库 CRUD
2. 文档管理（添加、删除、搜索）
3. 向量检索
4. 知识库挂载到 Agent
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class KnowledgeBaseType(str, Enum):
    """知识库类型"""
    VECTOR = "vector"  # 向量数据库
    SQL = "sql"  # SQL 数据库
    FILE = "file"  # 文件系统
    HYBRID = "hybrid"  # 混合模式


class StorageBackend(str, Enum):
    """存储后端"""
    CHROMADB = "chromadb"
    FAISS = "faiss"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"


class Document:
    """文档模型"""
    
    def __init__(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ):
        self.doc_id = doc_id
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "has_embedding": self.embedding is not None
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Document":
        """从字典创建"""
        return Document(
            doc_id=data["doc_id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding")
        )


class KnowledgeBase:
    """知识库模型"""
    
    def __init__(
        self,
        kb_id: str,
        name: str,
        description: str = "",
        kb_type: KnowledgeBaseType = KnowledgeBaseType.VECTOR,
        storage_backend: StorageBackend = StorageBackend.CHROMADB,
        embedding_model: str = "text-embedding-3-small",
        config: Optional[Dict[str, Any]] = None
    ):
        self.kb_id = kb_id
        self.name = name
        self.description = description
        self.kb_type = kb_type
        self.storage_backend = storage_backend
        self.embedding_model = embedding_model
        self.config = config or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.document_count = 0
        self.attached_agents = []  # 挂载的 agent 列表
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "kb_id": self.kb_id,
            "name": self.name,
            "description": self.description,
            "kb_type": self.kb_type.value,
            "storage_backend": self.storage_backend.value,
            "embedding_model": self.embedding_model,
            "config": self.config,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "document_count": self.document_count,
            "attached_agents": self.attached_agents
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "KnowledgeBase":
        """从字典创建"""
        kb = KnowledgeBase(
            kb_id=data["kb_id"],
            name=data["name"],
            description=data.get("description", ""),
            kb_type=KnowledgeBaseType(data.get("kb_type", "vector")),
            storage_backend=StorageBackend(data.get("storage_backend", "chromadb")),
            embedding_model=data.get("embedding_model", "text-embedding-3-small"),
            config=data.get("config", {})
        )
        kb.created_at = data.get("created_at", kb.created_at)
        kb.updated_at = data.get("updated_at", kb.updated_at)
        kb.document_count = data.get("document_count", 0)
        kb.attached_agents = data.get("attached_agents", [])
        return kb


class KnowledgeBaseManager:
    """
    知识库管理器
    
    负责管理所有知识库的 CRUD 操作
    """
    
    def __init__(self, storage_dir: str = "data/knowledge_bases"):
        """
        初始化知识库管理器
        
        Args:
            storage_dir: 知识库元数据存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 元数据文件
        self.metadata_file = self.storage_dir / "metadata.json"
        
        # 加载已有知识库
        self.knowledge_bases: Dict[str, KnowledgeBase] = {}
        self._load_metadata()
        
        logger.info(f"📚 知识库管理器已初始化，存储目录: {self.storage_dir}")
    
    def create_knowledge_base(
        self,
        name: str,
        description: str = "",
        kb_type: KnowledgeBaseType = KnowledgeBaseType.VECTOR,
        storage_backend: StorageBackend = StorageBackend.CHROMADB,
        embedding_model: str = "text-embedding-3-small",
        config: Optional[Dict[str, Any]] = None
    ) -> KnowledgeBase:
        """
        创建知识库
        
        Args:
            name: 知识库名称
            description: 描述
            kb_type: 知识库类型
            storage_backend: 存储后端
            embedding_model: 嵌入模型
            config: 配置参数
            
        Returns:
            创建的知识库
        """
        # 生成唯一ID
        kb_id = self._generate_kb_id(name)
        
        # 检查是否已存在
        if kb_id in self.knowledge_bases:
            raise ValueError(f"知识库 '{name}' 已存在")
        
        # 创建知识库
        kb = KnowledgeBase(
            kb_id=kb_id,
            name=name,
            description=description,
            kb_type=kb_type,
            storage_backend=storage_backend,
            embedding_model=embedding_model,
            config=config
        )
        
        # 创建知识库数据目录
        kb_data_dir = self.storage_dir / kb_id
        kb_data_dir.mkdir(exist_ok=True)
        
        # 保存到内存和文件
        self.knowledge_bases[kb_id] = kb
        self._save_metadata()
        
        logger.info(f"✅ 创建知识库成功: {name} ({kb_id})")
        return kb
    
    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """获取知识库"""
        return self.knowledge_bases.get(kb_id)
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """列出所有知识库"""
        return [kb.to_dict() for kb in self.knowledge_bases.values()]
    
    def update_knowledge_base(
        self,
        kb_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新知识库
        
        Args:
            kb_id: 知识库ID
            name: 新名称
            description: 新描述
            config: 新配置
            
        Returns:
            是否成功更新
        """
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return False
        
        # 更新字段
        if name:
            kb.name = name
        if description:
            kb.description = description
        if config:
            kb.config.update(config)
        
        kb.updated_at = datetime.now().isoformat()
        
        # 保存
        self._save_metadata()
        logger.info(f"✅ 更新知识库成功: {kb_id}")
        return True
    
    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            是否成功删除
        """
        if kb_id not in self.knowledge_bases:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return False
        
        # 删除数据目录
        kb_data_dir = self.storage_dir / kb_id
        if kb_data_dir.exists():
            import shutil
            shutil.rmtree(kb_data_dir)
        
        # 从内存中删除
        del self.knowledge_bases[kb_id]
        
        # 保存元数据
        self._save_metadata()
        logger.info(f"🗑️  删除知识库成功: {kb_id}")
        return True
    
    def attach_agent(self, kb_id: str, agent_id: str) -> bool:
        """
        将知识库挂载到 Agent
        
        Args:
            kb_id: 知识库ID
            agent_id: AgentID
            
        Returns:
            是否成功挂载
        """
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return False
        
        if agent_id not in kb.attached_agents:
            kb.attached_agents.append(agent_id)
            kb.updated_at = datetime.now().isoformat()
            self._save_metadata()
            logger.info(f"✅ 知识库 {kb_id} 已挂载到 Agent {agent_id}")
        
        return True
    
    def detach_agent(self, kb_id: str, agent_id: str) -> bool:
        """
        从 Agent 卸载知识库
        
        Args:
            kb_id: 知识库ID
            agent_id: AgentID
            
        Returns:
            是否成功卸载
        """
        kb = self.knowledge_bases.get(kb_id)
        if not kb:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return False
        
        if agent_id in kb.attached_agents:
            kb.attached_agents.remove(agent_id)
            kb.updated_at = datetime.now().isoformat()
            self._save_metadata()
            logger.info(f"✅ 知识库 {kb_id} 已从 Agent {agent_id} 卸载")
        
        return True
    
    def _generate_kb_id(self, name: str) -> str:
        """生成知识库ID"""
        content = f"{name}_{datetime.now().isoformat()}"
        return "kb_" + hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _load_metadata(self):
        """加载元数据"""
        if not self.metadata_file.exists():
            return
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for kb_data in data.get("knowledge_bases", []):
                kb = KnowledgeBase.from_dict(kb_data)
                self.knowledge_bases[kb.kb_id] = kb
            
            logger.info(f"📚 加载了 {len(self.knowledge_bases)} 个知识库")
            
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"❌ 加载知识库元数据失败: {e}")
    
    def _save_metadata(self):
        """保存元数据"""
        try:
            data = {
                "knowledge_bases": [kb.to_dict() for kb in self.knowledge_bases.values()]
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except (IOError, OSError) as e:
            logger.error(f"❌ 保存知识库元数据失败: {e}")


# 全局单例
_kb_manager = None


def get_knowledge_base_manager(storage_dir: str = "data/knowledge_bases") -> KnowledgeBaseManager:
    """获取知识库管理器单例"""
    global _kb_manager
    if _kb_manager is None:
        _kb_manager = KnowledgeBaseManager(storage_dir)
    return _kb_manager

