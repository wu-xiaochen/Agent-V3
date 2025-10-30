"""
系统配置服务单元测试
"""
import pytest
import json
import os
from pathlib import Path
from datetime import datetime
from src.services.system_config_service import SystemConfigService
from src.models.system_config import SystemConfig, SystemConfigUpdate


@pytest.fixture
def temp_config_file(tmp_path):
    """创建临时配置文件"""
    config_file = tmp_path / "test_system_config.json"
    return str(config_file)


@pytest.fixture
def config_service(temp_config_file):
    """创建配置服务实例"""
    return SystemConfigService(config_file=temp_config_file)


class TestSystemConfigService:
    """系统配置服务测试类"""
    
    def test_init_creates_directory(self, tmp_path):
        """测试初始化时创建目录"""
        config_file = tmp_path / "nested" / "config" / "system.json"
        service = SystemConfigService(config_file=str(config_file))
        
        assert config_file.parent.exists()
        assert service.config_file == config_file
    
    def test_get_config_default_when_file_not_exists(self, config_service):
        """测试文件不存在时返回默认配置"""
        config = config_service.get_config()
        
        assert config.id == "default"
        assert config.llm_provider == "siliconflow"
        assert config.base_url == "https://api.siliconflow.cn/v1"
        assert config.default_model == "Qwen/Qwen2.5-7B-Instruct"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.api_key == ""
        assert config.created_at is not None
        assert config.updated_at is not None
    
    def test_save_config_creates_file(self, config_service, temp_config_file):
        """测试保存配置创建文件"""
        config = SystemConfig(
            api_key="sk-test123456",
            temperature=0.8,
            max_tokens=3000
        )
        
        saved_config = config_service.save_config(config)
        
        # 验证文件存在
        assert Path(temp_config_file).exists()
        
        # 验证返回的配置
        assert saved_config.api_key == "sk-test123456"
        assert saved_config.temperature == 0.8
        assert saved_config.max_tokens == 3000
        assert saved_config.created_at is not None
        assert saved_config.updated_at is not None
    
    def test_save_config_encrypts_api_key(self, config_service, temp_config_file):
        """测试保存配置时加密API Key"""
        config = SystemConfig(api_key="sk-test123456")
        config_service.save_config(config)
        
        # 读取文件内容
        with open(temp_config_file, "r") as f:
            saved_data = json.load(f)
        
        # 验证API Key已加密（不是原始值）
        assert saved_data["api_key"] != "sk-test123456"
        assert len(saved_data["api_key"]) > 0
    
    def test_get_config_decrypts_api_key(self, config_service):
        """测试获取配置时解密API Key"""
        # 先保存一个配置
        original_config = SystemConfig(api_key="sk-test123456")
        config_service.save_config(original_config)
        
        # 再读取配置
        loaded_config = config_service.get_config()
        
        # 验证API Key已解密
        assert loaded_config.api_key == "sk-test123456"
    
    def test_update_config_partial_update(self, config_service):
        """测试部分更新配置"""
        # 保存初始配置
        initial_config = SystemConfig(
            api_key="sk-old",
            temperature=0.7,
            max_tokens=2000
        )
        config_service.save_config(initial_config)
        
        # 部分更新
        update = SystemConfigUpdate(
            temperature=0.9,
            max_tokens=4000
        )
        updated_config = config_service.update_config(update)
        
        # 验证更新的字段
        assert updated_config.temperature == 0.9
        assert updated_config.max_tokens == 4000
        
        # 验证未更新的字段保持不变
        assert updated_config.api_key == "sk-old"
        assert updated_config.llm_provider == "siliconflow"
    
    def test_update_config_with_api_key(self, config_service):
        """测试更新API Key"""
        # 保存初始配置
        initial_config = SystemConfig(api_key="sk-old")
        config_service.save_config(initial_config)
        
        # 更新API Key
        update = SystemConfigUpdate(api_key="sk-new123456")
        updated_config = config_service.update_config(update)
        
        # 验证API Key已更新
        assert updated_config.api_key == "sk-new123456"
        
        # 重新读取验证持久化
        loaded_config = config_service.get_config()
        assert loaded_config.api_key == "sk-new123456"
    
    def test_reset_to_default(self, config_service):
        """测试重置为默认配置"""
        # 先保存一个自定义配置
        custom_config = SystemConfig(
            api_key="sk-custom",
            temperature=0.9,
            max_tokens=5000,
            llm_provider="openai"
        )
        config_service.save_config(custom_config)
        
        # 重置为默认
        default_config = config_service.reset_to_default()
        
        # 验证已重置为默认值
        assert default_config.llm_provider == "siliconflow"
        assert default_config.temperature == 0.7
        assert default_config.max_tokens == 2000
        assert default_config.api_key == ""
    
    def test_api_key_encryption_decryption_roundtrip(self, config_service):
        """测试API Key加密解密往返"""
        test_keys = [
            "sk-short",
            "sk-medium-length-key",
            "sk-very-long-api-key-with-many-characters-1234567890",
            "",  # 空字符串
        ]
        
        for original_key in test_keys:
            encrypted = config_service._encrypt_api_key(original_key)
            decrypted = config_service._decrypt_api_key(encrypted)
            assert decrypted == original_key
    
    def test_config_persistence_across_instances(self, temp_config_file):
        """测试配置在不同服务实例间持久化"""
        # 第一个服务实例保存配置
        service1 = SystemConfigService(config_file=temp_config_file)
        config1 = SystemConfig(
            api_key="sk-persist",
            temperature=0.85,
            max_tokens=3500
        )
        service1.save_config(config1)
        
        # 第二个服务实例读取配置
        service2 = SystemConfigService(config_file=temp_config_file)
        config2 = service2.get_config()
        
        # 验证配置一致
        assert config2.api_key == "sk-persist"
        assert config2.temperature == 0.85
        assert config2.max_tokens == 3500
    
    def test_invalid_json_returns_default(self, config_service, temp_config_file):
        """测试无效JSON文件返回默认配置"""
        # 写入无效的JSON
        with open(temp_config_file, "w") as f:
            f.write("{ invalid json }")
        
        # 获取配置应返回默认值
        config = config_service.get_config()
        
        assert config.id == "default"
        assert config.llm_provider == "siliconflow"
    
    def test_config_timestamps(self, config_service):
        """测试配置时间戳"""
        config = SystemConfig()
        
        # 首次保存
        saved1 = config_service.save_config(config)
        assert saved1.created_at is not None
        assert saved1.updated_at is not None
        created_time = saved1.created_at
        
        # 更新配置
        import time
        time.sleep(0.1)  # 确保时间戳不同
        update = SystemConfigUpdate(temperature=0.9)
        saved2 = config_service.update_config(update)
        
        # created_at应保持不变，updated_at应更新
        assert saved2.created_at == created_time
        assert saved2.updated_at > saved2.created_at
    
    def test_temperature_validation(self):
        """测试temperature参数验证"""
        # 有效值
        config = SystemConfig(temperature=0.0)
        assert config.temperature == 0.0
        
        config = SystemConfig(temperature=2.0)
        assert config.temperature == 2.0
        
        # 无效值应触发验证错误
        with pytest.raises(Exception):
            SystemConfig(temperature=-0.1)
        
        with pytest.raises(Exception):
            SystemConfig(temperature=2.1)
    
    def test_max_tokens_validation(self):
        """测试max_tokens参数验证"""
        # 有效值
        config = SystemConfig(max_tokens=1)
        assert config.max_tokens == 1
        
        config = SystemConfig(max_tokens=100000)
        assert config.max_tokens == 100000
        
        # 无效值应触发验证错误
        with pytest.raises(Exception):
            SystemConfig(max_tokens=0)
        
        with pytest.raises(Exception):
            SystemConfig(max_tokens=100001)
    
    def test_empty_api_key_handling(self, config_service):
        """测试空API Key处理"""
        config = SystemConfig(api_key="")
        saved_config = config_service.save_config(config)
        
        assert saved_config.api_key == ""
        
        loaded_config = config_service.get_config()
        assert loaded_config.api_key == ""


class TestSystemConfigResponseModel:
    """系统配置响应模型测试"""
    
    def test_api_key_masking_long_key(self):
        """测试长API Key脱敏"""
        from src.models.system_config import SystemConfigResponse
        
        config = SystemConfig(api_key="sk-1234567890abcdef")
        response = SystemConfigResponse.from_system_config(config)
        
        assert response.api_key_masked == "sk-1****cdef"
    
    def test_api_key_masking_short_key(self):
        """测试短API Key脱敏"""
        from src.models.system_config import SystemConfigResponse
        
        config = SystemConfig(api_key="short")
        response = SystemConfigResponse.from_system_config(config)
        
        assert response.api_key_masked == "****hort"
    
    def test_api_key_masking_empty_key(self):
        """测试空API Key脱敏"""
        from src.models.system_config import SystemConfigResponse
        
        config = SystemConfig(api_key="")
        response = SystemConfigResponse.from_system_config(config)
        
        assert response.api_key_masked == ""
    
    def test_response_model_preserves_other_fields(self):
        """测试响应模型保留其他字段"""
        from src.models.system_config import SystemConfigResponse
        
        config = SystemConfig(
            id="test",
            llm_provider="openai",
            api_key="sk-test123456",
            base_url="https://api.openai.com",
            default_model="gpt-4",
            temperature=0.8,
            max_tokens=3000
        )
        
        response = SystemConfigResponse.from_system_config(config)
        
        assert response.id == "test"
        assert response.llm_provider == "openai"
        assert response.base_url == "https://api.openai.com"
        assert response.default_model == "gpt-4"
        assert response.temperature == 0.8
        assert response.max_tokens == 3000
