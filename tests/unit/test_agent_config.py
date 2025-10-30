"""
Agent配置服务单元测试
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.services.agent_config_service import AgentConfigService
from src.models.agent_config import AgentConfig, AgentConfigCreate, AgentConfigUpdate


@pytest.fixture
def temp_config_dir(monkeypatch):
    """创建临时配置目录"""
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / "agent_configs.json"
    
    # 修改配置文件路径
    monkeypatch.setattr("src.services.agent_config_service.AGENT_CONFIG_FILE", temp_file)
    
    yield temp_dir
    
    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def service(temp_config_dir):
    """创建服务实例"""
    return AgentConfigService()


def test_service_initialization(service, temp_config_dir):
    """测试服务初始化"""
    assert service is not None
    config_file = Path(temp_config_dir) / "agent_configs.json"
    assert config_file.exists()


def test_get_all_configs(service):
    """测试获取所有配置"""
    configs = service.get_all_configs()
    assert isinstance(configs, list)
    assert len(configs) > 0
    assert isinstance(configs[0], AgentConfig)


def test_get_single_config(service):
    """测试获取单个配置"""
    config = service.get_config("unified_agent")
    assert config is not None
    assert config.id == "unified_agent"
    
    # 不存在的agent
    config = service.get_config("nonexistent")
    assert config is None


def test_create_config(service):
    """测试创建配置"""
    create_data = AgentConfigCreate(
        name="Test Agent",
        description="Test description",
        system_prompt="You are a test agent",
        model="gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=1000,
        tools=["time"]
    )
    
    new_config = service.create_config(create_data)
    assert new_config is not None
    assert new_config.name == "Test Agent"
    assert new_config.id == "test_agent"
    
    # 验证持久化
    reloaded = service.get_config("test_agent")
    assert reloaded is not None
    assert reloaded.name == "Test Agent"


def test_update_config(service):
    """测试更新配置"""
    update = AgentConfigUpdate(
        name="Updated Name",
        temperature=0.9
    )
    
    updated = service.update_config("unified_agent", update)
    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.temperature == 0.9
    
    # 验证持久化
    reloaded = service.get_config("unified_agent")
    assert reloaded.name == "Updated Name"


def test_delete_config(service):
    """测试删除配置"""
    # 先创建一个新agent
    create_data = AgentConfigCreate(
        name="To Delete",
        system_prompt="test"
    )
    new_config = service.create_config(create_data)
    agent_id = new_config.id
    
    # 删除
    success = service.delete_config(agent_id)
    assert success == True
    
    # 验证删除
    config = service.get_config(agent_id)
    assert config is None


def test_cannot_delete_last_agent(service):
    """测试不能删除最后一个agent"""
    success = service.delete_config("unified_agent")
    assert success == False


def test_reset_to_default(service):
    """测试重置为默认配置"""
    # 先修改配置
    update = AgentConfigUpdate(name="Modified")
    service.update_config("unified_agent", update)
    
    # 重置
    configs = service.reset_to_default()
    assert len(configs) > 0
    
    # 验证恢复
    config = service.get_config("unified_agent")
    assert config.name == "Unified Agent"


def test_id_generation(service):
    """测试ID生成"""
    # 测试正常生成
    create1 = AgentConfigCreate(name="My Agent", system_prompt="test")
    agent1 = service.create_config(create1)
    assert agent1.id == "my_agent"
    
    # 测试重复名称（应该添加后缀）
    create2 = AgentConfigCreate(name="My Agent", system_prompt="test")
    agent2 = service.create_config(create2)
    assert agent2.id == "my_agent_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

