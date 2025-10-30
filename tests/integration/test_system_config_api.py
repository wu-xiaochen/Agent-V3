"""
系统配置API集成测试
"""
import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture
def temp_config_file(tmp_path):
    """创建临时配置文件"""
    config_file = tmp_path / "test_system_config_api.json"
    return str(config_file)


@pytest.fixture
def client(temp_config_file, monkeypatch):
    """创建测试客户端"""
    # 导入并创建app
    from api_server import app
    from src.services.system_config_service import SystemConfigService
    
    # 替换配置服务的配置文件路径
    original_service = None
    
    def mock_get_service():
        return SystemConfigService(config_file=temp_config_file)
    
    # 在导入时替换全局服务实例
    import api_server
    original_service = api_server.system_config_service
    api_server.system_config_service = mock_get_service()
    
    client = TestClient(app)
    
    yield client
    
    # 恢复原服务
    api_server.system_config_service = original_service


class TestSystemConfigAPI:
    """系统配置API测试类"""
    
    def test_get_config_default(self, client):
        """测试获取默认配置"""
        response = client.get("/api/system/config")
        
        assert response.status_code == 200
        result = response.json()
        
        # 验证响应结构
        assert result["success"] is True
        assert "config" in result
        
        data = result["config"]
        
        # 验证默认配置
        assert data["id"] == "default"
        assert data["llm_provider"] == "siliconflow"
        assert data["base_url"] == "https://api.siliconflow.cn/v1"
        assert data["default_model"] == "Qwen/Qwen2.5-7B-Instruct"
        assert data["temperature"] == 0.7
        assert data["max_tokens"] == 2000
        
        # 验证API Key已脱敏
        assert "api_key_masked" in data
        assert data["api_key_masked"] == ""
        
        # 验证时间戳存在
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_update_config_full(self, client):
        """测试完整更新配置"""
        update_data = {
            "llm_provider": "openai",
            "api_key": "sk-test123456789",
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-4",
            "temperature": 0.9,
            "max_tokens": 4000
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        data = result["config"]
        
        # 验证更新后的配置
        assert data["llm_provider"] == "openai"
        assert data["base_url"] == "https://api.openai.com/v1"
        assert data["default_model"] == "gpt-4"
        assert data["temperature"] == 0.9
        assert data["max_tokens"] == 4000
        
        # 验证API Key已脱敏
        assert data["api_key_masked"] == "sk-t****6789"
    
    def test_update_config_partial(self, client):
        """测试部分更新配置"""
        # 只更新temperature和max_tokens
        update_data = {
            "temperature": 0.85,
            "max_tokens": 3500
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        result = response.json()
        data = result["config"]
        
        # 验证更新的字段
        assert data["temperature"] == 0.85
        assert data["max_tokens"] == 3500
        
        # 验证未更新的字段保持默认值
        assert data["llm_provider"] == "siliconflow"
        assert data["default_model"] == "Qwen/Qwen2.5-7B-Instruct"
    
    def test_update_config_api_key_only(self, client):
        """测试只更新API Key"""
        update_data = {
            "api_key": "sk-new-api-key-12345"
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        data = response.json()["config"]
        
        # 验证API Key已脱敏
        assert data["api_key_masked"] == "sk-n****2345"
        
        # 验证其他字段保持不变
        assert data["llm_provider"] == "siliconflow"
    
    def test_reset_config(self, client):
        """测试重置配置"""
        # 先更新配置
        update_data = {
            "llm_provider": "openai",
            "api_key": "sk-test",
            "temperature": 0.9,
            "max_tokens": 5000
        }
        client.put("/api/system/config", json=update_data)
        
        # 重置配置
        response = client.post("/api/system/config/reset")
        
        assert response.status_code == 200
        data = response.json()["config"]
        
        # 验证已重置为默认值
        assert data["llm_provider"] == "siliconflow"
        assert data["base_url"] == "https://api.siliconflow.cn/v1"
        assert data["default_model"] == "Qwen/Qwen2.5-7B-Instruct"
        assert data["temperature"] == 0.7
        assert data["max_tokens"] == 2000
        assert data["api_key_masked"] == ""
    
    def test_config_persistence(self, client):
        """测试配置持久化"""
        # 更新配置
        update_data = {
            "api_key": "sk-persist-test",
            "temperature": 0.88
        }
        response1 = client.put("/api/system/config", json=update_data)
        assert response1.status_code == 200
        
        # 再次获取配置，验证已持久化
        response2 = client.get("/api/system/config")
        assert response2.status_code == 200
        
        data = response2.json()["config"]
        assert data["temperature"] == 0.88
        assert data["api_key_masked"] == "sk-p****test"
    
    def test_invalid_temperature_validation(self, client):
        """测试temperature参数验证"""
        # 温度过低
        update_data = {"temperature": -0.1}
        response = client.put("/api/system/config", json=update_data)
        assert response.status_code == 422  # Validation error
        
        # 温度过高
        update_data = {"temperature": 2.1}
        response = client.put("/api/system/config", json=update_data)
        assert response.status_code == 422
    
    def test_invalid_max_tokens_validation(self, client):
        """测试max_tokens参数验证"""
        # 太小
        update_data = {"max_tokens": 0}
        response = client.put("/api/system/config", json=update_data)
        assert response.status_code == 422
        
        # 太大
        update_data = {"max_tokens": 100001}
        response = client.put("/api/system/config", json=update_data)
        assert response.status_code == 422
    
    def test_update_with_empty_api_key(self, client):
        """测试使用空API Key更新"""
        update_data = {"api_key": ""}
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 200
        data = response.json()["config"]
        assert data["api_key_masked"] == ""
    
    def test_multiple_updates_sequence(self, client):
        """测试连续多次更新"""
        # 第一次更新
        update1 = {"temperature": 0.5}
        response1 = client.put("/api/system/config", json=update1)
        assert response1.status_code == 200
        assert response1.json()["config"]["temperature"] == 0.5
        
        # 第二次更新
        update2 = {"max_tokens": 1500}
        response2 = client.put("/api/system/config", json=update2)
        assert response2.status_code == 200
        data2 = response2.json()["config"]
        assert data2["max_tokens"] == 1500
        assert data2["temperature"] == 0.5  # 保持第一次更新的值
        
        # 第三次更新
        update3 = {"llm_provider": "anthropic"}
        response3 = client.put("/api/system/config", json=update3)
        assert response3.status_code == 200
        data3 = response3.json()["config"]
        assert data3["llm_provider"] == "anthropic"
        assert data3["temperature"] == 0.5
        assert data3["max_tokens"] == 1500
    
    def test_response_format_consistency(self, client):
        """测试响应格式一致性"""
        # GET和PUT应返回相同格式的响应
        response_get = client.get("/api/system/config")
        response_put = client.put("/api/system/config", json={"temperature": 0.7})
        response_reset = client.post("/api/system/config/reset")
        
        assert response_get.status_code == 200
        assert response_put.status_code == 200
        assert response_reset.status_code == 200
        
        # 验证所有响应包含success和config
        for response in [response_get, response_put, response_reset]:
            result = response.json()
            assert "success" in result
            assert "config" in result
            
            # 验证config包含必需字段
            config = result["config"]
            required_fields = [
                "id", "llm_provider", "api_key_masked", "base_url",
                "default_model", "temperature", "max_tokens",
                "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in config
    
    def test_concurrent_updates(self, client):
        """测试并发更新（简单模拟）"""
        # 模拟两个快速连续的更新
        update1 = {"temperature": 0.6}
        update2 = {"temperature": 0.8}
        
        response1 = client.put("/api/system/config", json=update1)
        response2 = client.put("/api/system/config", json=update2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # 最后一次更新应该生效
        response_final = client.get("/api/system/config")
        assert response_final.json()["config"]["temperature"] == 0.8
    
    def test_api_key_masking_edge_cases(self, client):
        """测试API Key脱敏的边界情况"""
        test_cases = [
            ("", ""),  # 空字符串
            ("short", "****hort"),  # 短Key
            ("sk-1234567890", "sk-1****7890"),  # 正常长度
            ("x", "****x"),  # 单字符
            ("ab", "****ab"),  # 两字符
        ]
        
        for api_key, expected_masked in test_cases:
            update_data = {"api_key": api_key}
            response = client.put("/api/system/config", json=update_data)
            
            assert response.status_code == 200
            data = response.json()["config"]
            assert data["api_key_masked"] == expected_masked
    
    def test_config_update_timestamps(self, client):
        """测试配置更新时间戳"""
        import time
        
        # 第一次更新
        response1 = client.put("/api/system/config", json={"temperature": 0.5})
        data1 = response1.json()["config"]
        created_at = data1["created_at"]
        updated_at_1 = data1["updated_at"]
        
        # 等待一小段时间
        time.sleep(0.2)
        
        # 第二次更新
        response2 = client.put("/api/system/config", json={"temperature": 0.6})
        data2 = response2.json()["config"]
        updated_at_2 = data2["updated_at"]
        
        # created_at应保持不变
        assert data2["created_at"] == created_at
        
        # updated_at应该更新
        assert updated_at_2 > updated_at_1


class TestSystemConfigAPIErrorHandling:
    """系统配置API错误处理测试"""
    
    def test_invalid_json_body(self, client):
        """测试无效JSON请求体"""
        response = client.put(
            "/api/system/config",
            data="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        
        # 应返回400或422
        assert response.status_code in [400, 422]
    
    def test_invalid_field_type(self, client):
        """测试无效字段类型"""
        # temperature应该是float
        update_data = {"temperature": "invalid"}
        response = client.put("/api/system/config", json=update_data)
        
        assert response.status_code == 422
    
    def test_unknown_fields_ignored(self, client):
        """测试未知字段被忽略"""
        update_data = {
            "temperature": 0.8,
            "unknown_field": "should_be_ignored"
        }
        
        response = client.put("/api/system/config", json=update_data)
        
        # 应该成功，但忽略未知字段
        assert response.status_code == 200
        data = response.json()["config"]
        assert data["temperature"] == 0.8
        assert "unknown_field" not in data
