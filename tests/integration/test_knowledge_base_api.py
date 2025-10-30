"""
知识库API集成测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient


# 导入FastAPI app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api_server import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_kb_dir():
    """创建临时知识库目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestKnowledgeBaseAPI:
    """知识库API测试"""
    
    def test_create_knowledge_base(self, client):
        """测试创建知识库"""
        response = client.post(
            "/api/knowledge-bases",
            json={
                "name": "测试API知识库",
                "description": "通过API创建",
                "chunk_size": 800,
                "chunk_overlap": 100
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "knowledge_base" in data
        assert data["knowledge_base"]["name"] == "测试API知识库"
    
    def test_list_knowledge_bases(self, client):
        """测试列出知识库"""
        # 先创建一个
        client.post(
            "/api/knowledge-bases",
            json={"name": "KB1"}
        )
        
        response = client.get("/api/knowledge-bases")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "knowledge_bases" in data
        assert isinstance(data["knowledge_bases"], list)
        assert data["total"] >= 1
    
    def test_get_knowledge_base(self, client):
        """测试获取知识库详情"""
        # 创建知识库
        create_response = client.post(
            "/api/knowledge-bases",
            json={"name": "获取测试KB"}
        )
        kb_id = create_response.json()["knowledge_base"]["id"]
        
        # 获取详情
        response = client.get(f"/api/knowledge-bases/{kb_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["knowledge_base"]["id"] == kb_id
    
    def test_get_nonexistent_knowledge_base(self, client):
        """测试获取不存在的知识库"""
        response = client.get("/api/knowledge-bases/kb_nonexistent")
        assert response.status_code == 404
    
    def test_update_knowledge_base(self, client):
        """测试更新知识库"""
        # 创建知识库
        create_response = client.post(
            "/api/knowledge-bases",
            json={"name": "原始名称"}
        )
        kb_id = create_response.json()["knowledge_base"]["id"]
        
        # 更新
        response = client.put(
            f"/api/knowledge-bases/{kb_id}",
            json={
                "name": "更新后名称",
                "description": "新描述"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["knowledge_base"]["name"] == "更新后名称"
    
    def test_delete_knowledge_base(self, client):
        """测试删除知识库"""
        # 创建知识库
        create_response = client.post(
            "/api/knowledge-bases",
            json={"name": "待删除KB"}
        )
        kb_id = create_response.json()["knowledge_base"]["id"]
        
        # 删除
        response = client.delete(f"/api/knowledge-bases/{kb_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证已删除
        get_response = client.get(f"/api/knowledge-bases/{kb_id}")
        assert get_response.status_code == 404
    
    def test_search_knowledge_base(self, client):
        """测试检索知识库"""
        # 创建知识库
        create_response = client.post(
            "/api/knowledge-bases",
            json={"name": "检索测试KB"}
        )
        kb_id = create_response.json()["knowledge_base"]["id"]
        
        # 检索
        response = client.post(
            f"/api/knowledge-bases/{kb_id}/search",
            json={
                "query": "测试查询",
                "top_k": 5,
                "score_threshold": 0.5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "kb_id" in data
        assert "query" in data
        assert "results" in data
        assert data["query"] == "测试查询"
    
    def test_create_knowledge_base_invalid_data(self, client):
        """测试创建知识库时的数据验证"""
        # 空名称
        response = client.post(
            "/api/knowledge-bases",
            json={"name": ""}
        )
        assert response.status_code == 422
        
        # chunk_size太小
        response = client.post(
            "/api/knowledge-bases",
            json={
                "name": "测试",
                "chunk_size": 50  # < 100
            }
        )
        assert response.status_code == 422
    
    def test_create_knowledge_base_default_values(self, client):
        """测试默认值"""
        response = client.post(
            "/api/knowledge-bases",
            json={"name": "默认值测试"}
        )
        
        assert response.status_code == 200
        data = response.json()
        kb = data["knowledge_base"]
        
        assert kb["embedding_model"] == "text-embedding-3-small"
        assert kb["chunk_size"] == 1000
        assert kb["chunk_overlap"] == 200
        assert kb["document_count"] == 0


class TestDocumentUploadAPI:
    """文档上传API测试"""
    
    @pytest.mark.skip(reason="需要文件管理器环境")
    def test_upload_document(self, client):
        """测试上传文档"""
        # 创建知识库
        create_response = client.post(
            "/api/knowledge-bases",
            json={"name": "文档测试KB"}
        )
        kb_id = create_response.json()["knowledge_base"]["id"]
        
        # 上传文档（需要先上传文件获得file_id）
        # 这里跳过实际文件上传，仅测试API结构
        pass
    
    def test_upload_document_to_nonexistent_kb(self, client):
        """测试向不存在的知识库上传文档"""
        response = client.post(
            "/api/knowledge-bases/kb_nonexistent/documents",
            json={
                "file_id": "file_test",
                "metadata": {}
            }
        )
        
        # 应该返回404（知识库或文件不存在）
        assert response.status_code in [404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

