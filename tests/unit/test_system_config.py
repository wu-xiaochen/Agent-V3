"""
系统配置服务单元测试
"""
import pytest
import os
import json
from pathlib import Path
from datetime import datetime

from src.models.system_config import SystemConfig, SystemConfigUpdate, SystemConfigResponse
from src.services.system_config_service import SystemConfigService


class TestSystemConfigModels:
    """测试系统配置数据模型"""
    
    def test_system_config_default_values(self):
        """测试默认配置值"""
        config = SystemConfig()
        
        assert config.id == "default"
        assert config.llm_provider == "siliconflow"
        assert config.api_key == ""
        assert config.base_url == "https://api.siliconflow.cn/v1"
        assert config.default_model == "Qwen/Qwen2.5-7B-Instruct"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
    
    def test_system_config_custom_values(self):
        """测试自定义配置值"""
        config = SystemConfig(
            llm_provider="openai",
            api_key="sk-test123",
            base_url="https://api.openai.com/v1",
            default_model="gpt-4",
            temperature=0.5,
            max_tokens=4000
        )
        
        assert config.llm_provider == "openai"
        assert config.api_key == "sk-test123"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.default_model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 4000
    
    def test_system_config_validation(self):
        """测试配置验证"""
        # Temperature范围验证
        with pytest.raises(ValueError):
            SystemConfig(temperature=-0.1)
        
        with pytest.raises(ValueError):
            SystemConfig(temperature=2.1)
        
        # Max tokens范围验证
        with pytest.raises(ValueError):
            SystemConfig(max_tokens=0)
        
        with pytest.raises(ValueError):
            SystemConfig(max_tokens=100001)
    
    def test_system_config_update(self):
        """测试配置更新模型"""
        update = SystemConfigUpdate(
            llm_provider="anthropic",
            temperature=0.8
        )
        
        assert update.llm_provider == "anthropic"
        assert update.temperature == 0.8
        assert update.api_key is None
        assert update.base_url is None
    
    def test_system_config_response_masking(self):
        """测试API Key脱敏"""
        config = SystemConfig(api_key="sk-1234567890abcdef1234567890abcdef")
        response = SystemConfigResponse.from_system_config(config)
        
        assert response.api_key_masked == "sk-1****cdef"
        assert "1234567890abcdef1234567890ab" not in response.api_key_masked
    
    def test_system_config_response_short_key(self):
        """测试短API Key脱敏"""
        config = SystemConfig(api_key="sk-123")
        response = SystemConfigResponse.from_system_config(config)
        
        # 短key会显示****+后4位，"sk-123"总共6个字符，后4位是"-123"
        assert response.api_key_masked == "****-123"
    
    def test_system_config_response_empty_key(self):
        """测试空API Key"""
        config = SystemConfig(api_key="")
        response = SystemConfigResponse.from_system_config(config)
        
        assert response.api_key_masked == ""


class TestSystemConfigService:
    """测试系统配置服务"""
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """创建临时配置文件"""
        return tmp_path / "test_system_config.json"
    
    @pytest.fixture
    def service(self, temp_config_file):
        """创建服务实例"""
        return SystemConfigService(config_file=str(temp_config_file))
    
    def test_get_config_default(self, service, temp_config_file):
        """测试获取默认配置（文件不存在）"""
        assert not temp_config_file.exists()
        
        config = service.get_config()
        
        assert config.id == "default"
        assert config.llm_provider == "siliconflow"
        assert config.created_at is not None
        assert config.updated_at is not None
    
    def test_save_config(self, service, temp_config_file):
        """测试保存配置"""
        config = SystemConfig(
            llm_provider="openai",
            api_key="sk-test123",
            temperature=0.8
        )
        
        saved_config = service.save_config(config)
        
        assert temp_config_file.exists()
        assert saved_config.created_at is not None
        assert saved_config.updated_at is not None
    
    def test_encrypt_decrypt_api_key(self, service):
        """测试API Key加密和解密"""
        original_key = "sk-1234567890abcdef"
        
        encrypted = service._encrypt_api_key(original_key)
        assert encrypted != original_key
        
        decrypted = service._decrypt_api_key(encrypted)
        assert decrypted == original_key
    
    def test_save_and_load_config(self, service):
        """测试保存和加载配置"""
        # 保存配置
        original_config = SystemConfig(
            llm_provider="anthropic",
            api_key="sk-secret123",
            base_url="https://api.anthropic.com/v1",
            default_model="claude-3-opus",
            temperature=0.6,
            max_tokens=3000
        )
        service.save_config(original_config)
        
        # 加载配置
        loaded_config = service.get_config()
        
        assert loaded_config.llm_provider == "anthropic"
        assert loaded_config.api_key == "sk-secret123"  # 应该被解密
        assert loaded_config.base_url == "https://api.anthropic.com/v1"
        assert loaded_config.default_model == "claude-3-opus"
        assert loaded_config.temperature == 0.6
        assert loaded_config.max_tokens == 3000
    
    def test_update_config(self, service):
        """测试更新配置"""
        # 先保存初始配置
        initial_config = SystemConfig(llm_provider="siliconflow")
        service.save_config(initial_config)
        
        # 更新部分字段
        update = SystemConfigUpdate(
            llm_provider="openai",
            temperature=0.9
        )
        updated_config = service.update_config(update)
        
        assert updated_config.llm_provider == "openai"
        assert updated_config.temperature == 0.9
        assert updated_config.max_tokens == 2000  # 未更新的字段保持不变
    
    def test_reset_to_default(self, service):
        """测试重置为默认配置"""
        # 先保存自定义配置
        custom_config = SystemConfig(
            llm_provider="openai",
            api_key="sk-custom",
            temperature=0.9
        )
        service.save_config(custom_config)
        
        # 重置为默认
        default_config = service.reset_to_default()
        
        assert default_config.llm_provider == "siliconflow"
        assert default_config.api_key == ""
        assert default_config.temperature == 0.7
    
    def test_config_persistence(self, service, temp_config_file):
        """测试配置持久化"""
        config = SystemConfig(
            llm_provider="test_provider",
            api_key="test_key"
        )
        service.save_config(config)
        
        # 创建新的服务实例（模拟应用重启）
        new_service = SystemConfigService(config_file=str(temp_config_file))
        loaded_config = new_service.get_config()
        
        assert loaded_config.llm_provider == "test_provider"
        assert loaded_config.api_key == "test_key"
    
    def test_empty_api_key_handling(self, service):
        """测试空API Key处理"""
        config = SystemConfig(api_key="")
        
        encrypted = service._encrypt_api_key(config.api_key)
        assert encrypted == ""
        
        decrypted = service._decrypt_api_key(encrypted)
        assert decrypted == ""
    
    def test_timestamps_on_save(self, service):
        """测试保存时更新时间戳"""
        config = SystemConfig()
        
        # 首次保存
        saved_config = service.save_config(config)
        assert saved_config.created_at is not None
        assert saved_config.updated_at is not None
        first_updated_at = saved_config.updated_at
        
        # 再次保存
        import time
        time.sleep(0.1)  # 确保时间戳不同
        saved_config.llm_provider = "updated"
        updated_config = service.save_config(saved_config)
        
        assert updated_config.updated_at > first_updated_at
        assert updated_config.created_at == saved_config.created_at


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

