"""
知识库服务单元测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.models.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    SearchRequest
)
from src.services.knowledge_base_service import KnowledgeBaseService


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # 清理
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def kb_service(temp_dir):
    """创建知识库服务实例"""
    return KnowledgeBaseService(data_dir=temp_dir)


@pytest.fixture
def sample_kb(kb_service):
    """创建示例知识库"""
    request = KnowledgeBaseCreate(
        name="测试知识库",
        description="这是一个测试知识库",
        chunk_size=500,
        chunk_overlap=50
    )
    return kb_service.create_knowledge_base(request)


class TestKnowledgeBaseService:
    """知识库服务测试"""
    
    def test_create_knowledge_base(self, kb_service):
        """测试创建知识库"""
        request = KnowledgeBaseCreate(
            name="AI知识库",
            description="收集AI相关文档",
            embedding_model="text-embedding-3-small",
            chunk_size=1000,
            chunk_overlap=200
        )
        
        kb = kb_service.create_knowledge_base(request)
        
        assert kb is not None
        assert kb.name == "AI知识库"
        assert kb.description == "收集AI相关文档"
        assert kb.chunk_size == 1000
        assert kb.chunk_overlap == 200
        assert kb.document_count == 0
        assert kb.id.startswith("kb_")
    
    def test_get_knowledge_base(self, kb_service, sample_kb):
        """测试获取知识库"""
        kb = kb_service.get_knowledge_base(sample_kb.id)
        
        assert kb is not None
        assert kb.id == sample_kb.id
        assert kb.name == sample_kb.name
    
    def test_get_nonexistent_knowledge_base(self, kb_service):
        """测试获取不存在的知识库"""
        kb = kb_service.get_knowledge_base("kb_nonexistent")
        assert kb is None
    
    def test_list_knowledge_bases(self, kb_service):
        """测试列出知识库"""
        # 创建多个知识库
        for i in range(3):
            request = KnowledgeBaseCreate(name=f"KB{i}")
            kb_service.create_knowledge_base(request)
        
        kbs = kb_service.list_knowledge_bases()
        assert len(kbs) == 3
        assert all(kb.name in ["KB0", "KB1", "KB2"] for kb in kbs)
    
    def test_update_knowledge_base(self, kb_service, sample_kb):
        """测试更新知识库"""
        update_request = KnowledgeBaseUpdate(
            name="更新后的名称",
            description="更新后的描述"
        )
        
        updated_kb = kb_service.update_knowledge_base(sample_kb.id, update_request)
        
        assert updated_kb is not None
        assert updated_kb.name == "更新后的名称"
        assert updated_kb.description == "更新后的描述"
    
    def test_update_nonexistent_knowledge_base(self, kb_service):
        """测试更新不存在的知识库"""
        update_request = KnowledgeBaseUpdate(name="新名称")
        result = kb_service.update_knowledge_base("kb_nonexistent", update_request)
        assert result is None
    
    def test_delete_knowledge_base(self, kb_service, sample_kb):
        """测试删除知识库"""
        success = kb_service.delete_knowledge_base(sample_kb.id)
        assert success is True
        
        # 验证已删除
        kb = kb_service.get_knowledge_base(sample_kb.id)
        assert kb is None
    
    def test_delete_nonexistent_knowledge_base(self, kb_service):
        """测试删除不存在的知识库"""
        success = kb_service.delete_knowledge_base("kb_nonexistent")
        assert success is False


class TestDocumentProcessing:
    """文档处理测试"""
    
    def test_split_document(self, kb_service):
        """测试文档分块"""
        content = "这是第一句话。这是第二句话。这是第三句话。" * 100
        chunks = kb_service._split_document(content, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk) > 0 for chunk in chunks)
    
    def test_split_short_document(self, kb_service):
        """测试短文档分块"""
        content = "这是一段短文本"
        chunks = kb_service._split_document(content, chunk_size=1000, chunk_overlap=100)
        
        assert len(chunks) == 1
        assert chunks[0] == content
    
    def test_split_empty_document(self, kb_service):
        """测试空文档分块"""
        content = ""
        chunks = kb_service._split_document(content, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) == 0
    
    def test_add_document(self, kb_service, sample_kb, temp_dir):
        """测试添加文档"""
        # 创建测试文件
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("这是测试文档的内容。包含多个句子。用于测试文档处理功能。", encoding="utf-8")
        
        doc = kb_service.add_document(
            kb_id=sample_kb.id,
            file_path=str(test_file),
            filename="test.txt",
            file_type="text",
            file_size=test_file.stat().st_size,
            metadata={"source": "test"}
        )
        
        assert doc is not None
        assert doc.kb_id == sample_kb.id
        assert doc.filename == "test.txt"
        assert doc.chunk_count > 0
        assert doc.status in ["completed", "failed"]
    
    def test_add_document_to_nonexistent_kb(self, kb_service, temp_dir):
        """测试向不存在的知识库添加文档"""
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("测试内容", encoding="utf-8")
        
        doc = kb_service.add_document(
            kb_id="kb_nonexistent",
            file_path=str(test_file),
            filename="test.txt",
            file_type="text",
            file_size=100
        )
        
        assert doc is None


class TestSearch:
    """检索测试"""
    
    def test_search_without_vector_db(self, kb_service, sample_kb):
        """测试没有向量数据库时的检索"""
        request = SearchRequest(
            kb_id=sample_kb.id,
            query="测试查询",
            top_k=5
        )
        
        # 如果ChromaDB未安装，应该返回空结果
        response = kb_service.search(request)
        
        assert response.kb_id == sample_kb.id
        assert response.query == "测试查询"
        assert isinstance(response.results, list)
    
    @pytest.mark.skipif(True, reason="需要ChromaDB环境")
    def test_search_with_results(self, kb_service, sample_kb, temp_dir):
        """测试有结果的检索（需要ChromaDB）"""
        # 添加文档
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("人工智能是计算机科学的一个分支", encoding="utf-8")
        
        kb_service.add_document(
            kb_id=sample_kb.id,
            file_path=str(test_file),
            filename="test.txt",
            file_type="text",
            file_size=test_file.stat().st_size
        )
        
        # 检索
        request = SearchRequest(
            kb_id=sample_kb.id,
            query="什么是人工智能",
            top_k=3
        )
        
        response = kb_service.search(request)
        
        assert response.success is True
        assert len(response.results) > 0
        assert all(result.score >= 0 for result in response.results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

