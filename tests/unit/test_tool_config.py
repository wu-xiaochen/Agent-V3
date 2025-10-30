"""
工具配置服务单元测试
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.services.tool_config_service import ToolConfigService, TOOL_CONFIG_FILE
from src.models.tool_config import ToolConfig, ToolConfigUpdate


@pytest.fixture
def temp_config_dir(monkeypatch):
    """创建临时配置目录"""
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / "tool_configs.json"
    
    # 修改配置文件路径
    monkeypatch.setattr("src.services.tool_config_service.TOOL_CONFIG_FILE", temp_file)
    
    yield temp_dir
    
    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def service(temp_config_dir):
    """创建服务实例"""
    return ToolConfigService()


def test_service_initialization(service, temp_config_dir):
    """测试服务初始化"""
    assert service is not None
    
    # 检查配置文件是否创建
    config_file = Path(temp_config_dir) / "tool_configs.json"
    assert config_file.exists()


def test_get_all_configs(service):
    """测试获取所有配置"""
    configs = service.get_all_configs()
    
    assert isinstance(configs, list)
    assert len(configs) > 0
    
    # 检查第一个配置
    first_config = configs[0]
    assert isinstance(first_config, ToolConfig)
    assert hasattr(first_config, 'tool_id')
    assert hasattr(first_config, 'enabled')
    assert hasattr(first_config, 'mode')


def test_get_single_config(service):
    """测试获取单个配置"""
    # 获取存在的工具
    config = service.get_config("time")
    assert config is not None
    assert config.tool_id == "time"
    assert config.name == "Time Tool"
    
    # 获取不存在的工具
    config = service.get_config("nonexistent")
    assert config is None


def test_update_config(service):
    """测试更新配置"""
    # 更新工具配置
    update = ToolConfigUpdate(
        enabled=False,
        mode="MCP",
        config={"timeout": 10000}
    )
    
    updated_config = service.update_config("time", update)
    
    assert updated_config is not None
    assert updated_config.enabled == False
    assert updated_config.mode == "MCP"
    assert updated_config.config["timeout"] == 10000
    
    # 验证持久化
    reloaded_config = service.get_config("time")
    assert reloaded_config.enabled == False
    assert reloaded_config.mode == "MCP"


def test_update_nonexistent_tool(service):
    """测试更新不存在的工具"""
    update = ToolConfigUpdate(enabled=False)
    result = service.update_config("nonexistent", update)
    assert result is None


def test_partial_update(service):
    """测试部分字段更新"""
    # 只更新enabled字段
    update = ToolConfigUpdate(enabled=False)
    updated_config = service.update_config("calculator", update)
    
    assert updated_config.enabled == False
    # 其他字段应保持不变
    assert updated_config.mode == "API"  # 默认值


def test_batch_update(service):
    """测试批量更新"""
    # 获取现有配置并修改
    configs = service.get_all_configs()
    
    # 修改所有工具为禁用
    for config in configs:
        config.enabled = False
    
    # 批量更新
    updated_configs = service.update_all_configs(configs)
    
    assert len(updated_configs) == len(configs)
    
    # 验证所有工具都被禁用
    for config in updated_configs:
        assert config.enabled == False


def test_reset_to_default(service):
    """测试重置为默认配置"""
    # 先修改配置
    update = ToolConfigUpdate(enabled=False)
    service.update_config("time", update)
    
    # 重置
    configs = service.reset_to_default()
    
    assert len(configs) > 0
    
    # 验证time工具恢复为启用
    time_config = service.get_config("time")
    assert time_config.enabled == True


def test_config_persistence(service, temp_config_dir):
    """测试配置持久化"""
    # 更新配置
    update = ToolConfigUpdate(enabled=False, description="Updated description")
    service.update_config("time", update)
    
    # 创建新服务实例（模拟重启）
    new_service = ToolConfigService()
    
    # 验证配置被持久化
    config = new_service.get_config("time")
    assert config.enabled == False
    assert config.description == "Updated description"


def test_invalid_tool_id():
    """测试无效工具ID"""
    service = ToolConfigService()
    
    # 空字符串
    config = service.get_config("")
    assert config is None
    
    # 特殊字符
    config = service.get_config("@#$%")
    assert config is None


def test_concurrent_updates(service):
    """测试并发更新（基础测试）"""
    # 第一次更新
    update1 = ToolConfigUpdate(enabled=False)
    service.update_config("time", update1)
    
    # 第二次更新
    update2 = ToolConfigUpdate(enabled=True)
    service.update_config("time", update2)
    
    # 验证最后一次更新生效
    config = service.get_config("time")
    assert config.enabled == True


def test_config_validation():
    """测试配置验证"""
    # 测试有效配置
    config = ToolConfig(
        tool_id="test",
        name="Test Tool",
        enabled=True,
        mode="API",
        config={"timeout": 5000}
    )
    assert config.tool_id == "test"
    
    # 测试无效mode（应该抛出验证错误）
    with pytest.raises(Exception):
        ToolConfig(
            tool_id="test",
            name="Test",
            mode="INVALID"  # 不在 ["API", "MCP"] 中
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

