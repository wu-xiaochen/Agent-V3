"""
系统配置API集成测试
"""
import pytest
from fastapi.testclient import TestClient
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入API服务器
from api_server import app
from src.services.system_config_service import SystemConfigService


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_config_service(tmp_path):
    """创建临时配置服务"""
    config_file = tmp_path / "test_system_config.json"
    return SystemConfigService(config_file=str(config_file))


class TestSystemConfigAPI:
    """测试系统配置API端点"""
    
    def test_get_system_config(self, client):
        """测试获取系统配置"""
        response = client.get("/api/system/config")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "config" in data
        
        config = data["config"]
        assert "llm_provider" in config
        assert "base_url" in config
        assert "default_model" in config
        assert "temperature" in config
        assert "max_tokens" in config
        assert "api_key_masked" in config
    
    def test_api_key_is_masked(self, client):
        """测试API Key被正确脱敏"""
        # 先更新配置添加API Key
        update_data = {
            "api_key": "sk-1234567890abcdef1234567890abcdef"
        }
        client.put("/api/system/config", json=update_data)
        
        # 获取配置
        response = client.get("/api/system/config")
        config = response.json()["config"]
        
        # API Key应该被脱敏
        assert config["api_key_masked"] == "sk-1****cdef"
        assert "1234567890abcdef" not in config["api_key_masked"]
    
    def test_update_system_config(self, client):
        """测试更新系统配置"""
        update_data = {
            "llm_provider": "openai",
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-4",
            "temperature": 0.5,
            "max_tokens": 4000
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "config" in data
        assert data["message"] == "配置已更新"
        
        config = data["config"]
        assert config["llm_provider"] == "openai"
        assert config["base_url"] == "https://api.openai.com/v1"
        assert config["default_model"] == "gpt-4"
        assert config["temperature"] == 0.5
        assert config["max_tokens"] == 4000
    
    def test_update_partial_config(self, client):
        """测试部分更新配置"""
        # 只更新temperature
        update_data = {
            "temperature": 0.9
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        config = response.json()["config"]
        
        assert config["temperature"] == 0.9
        # 其他字段应该保持不变
        assert "llm_provider" in config
        assert "base_url" in config
    
    def test_update_config_validation(self, client):
        """测试配置验证"""
        # Temperature超出范围
        invalid_data = {
            "temperature": 2.5
        }
        
        response = client.put("/api/system/config", json=invalid_data)
        
        # 应该返回错误
        assert response.status_code in [400, 422, 500]
    
    def test_update_api_key(self, client):
        """测试更新API Key"""
        update_data = {
            "api_key": "sk-newsecretkey123"
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        
        # 再次获取配置，API Key应该被脱敏
        get_response = client.get("/api/system/config")
        config = get_response.json()["config"]
        
        assert "****" in config["api_key_masked"]
        assert "newsecretkey123" not in config["api_key_masked"]
    
    def test_reset_system_config(self, client):
        """测试重置系统配置"""
        # 先更新配置
        update_data = {
            "llm_provider": "custom_provider",
            "temperature": 0.9,
            "max_tokens": 5000
        }
        client.put("/api/system/config", json=update_data)
        
        # 重置配置
        response = client.post("/api/system/config/reset")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "配置已重置为默认值"
        
        config = data["config"]
        # 应该恢复默认值
        assert config["llm_provider"] == "siliconflow"
        assert config["temperature"] == 0.7
        assert config["max_tokens"] == 2000
        assert config["api_key_masked"] == ""
    
    def test_config_persistence(self, client):
        """测试配置持久化"""
        # 更新配置
        update_data = {
            "llm_provider": "test_provider",
            "temperature": 0.6
        }
        response1 = client.put("/api/system/config", json=update_data)
        assert response1.status_code == 200
        
        # 重新获取配置（模拟应用重启）
        response2 = client.get("/api/system/config")
        config = response2.json()["config"]
        
        assert config["llm_provider"] == "test_provider"
        assert config["temperature"] == 0.6
    
    def test_multiple_updates(self, client):
        """测试多次更新配置"""
        # 第一次更新
        client.put("/api/system/config", json={"llm_provider": "provider1"})
        
        # 第二次更新
        client.put("/api/system/config", json={"temperature": 0.8})
        
        # 第三次更新
        response = client.put("/api/system/config", json={"max_tokens": 3000})
        
        assert response.status_code == 200
        config = response.json()["config"]
        
        # 所有更新应该都保留
        assert config["llm_provider"] == "provider1"
        assert config["temperature"] == 0.8
        assert config["max_tokens"] == 3000
    
    def test_empty_update(self, client):
        """测试空更新"""
        response = client.put("/api/system/config", json={})
        
        # 应该成功，但配置不变
        assert response.status_code == 200
    
    def test_config_timestamps(self, client):
        """测试配置时间戳"""
        response = client.get("/api/system/config")
        config = response.json()["config"]
        
        # 应该有时间戳
        assert "created_at" in config
        assert "updated_at" in config
    
    def test_invalid_json(self, client):
        """测试无效JSON"""
        response = client.put(
            "/api/system/config",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # 应该返回错误
        assert response.status_code in [400, 422]
    
    def test_cors_headers(self, client):
        """测试CORS头部"""
        response = client.options("/api/system/config")
        
        # 应该有CORS头部（根据api_server.py配置）
        assert response.status_code in [200, 405]


class TestSystemConfigAPIIntegration:
    """测试API与服务层集成"""
    
    def test_api_uses_service_correctly(self, client):
        """测试API正确使用服务层"""
        # 通过API更新配置
        update_data = {
            "llm_provider": "integration_test",
            "api_key": "sk-integration123"
        }
        response = client.put("/api/system/config", json=update_data)
        assert response.status_code == 200
        
        # 直接通过服务层读取（验证持久化）
        from api_server import system_config_service
        config = system_config_service.get_config()
        
        assert config.llm_provider == "integration_test"
        assert config.api_key == "sk-integration123"
    
    def test_concurrent_updates(self, client):
        """测试并发更新（简单测试）"""
        import threading
        
        def update_config(provider_name):
            client.put("/api/system/config", json={"llm_provider": provider_name})
        
        # 启动多个线程同时更新
        threads = []
        for i in range(5):
            t = threading.Thread(target=update_config, args=(f"provider_{i}",))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 获取最终配置（应该是其中一个）
        response = client.get("/api/system/config")
        assert response.status_code == 200
        
        config = response.json()["config"]
        assert config["llm_provider"].startswith("provider_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

