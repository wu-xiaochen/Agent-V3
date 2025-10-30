"""
工具配置API集成测试
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api_server import app

client = TestClient(app)


def test_get_all_tool_configs():
    """测试获取所有工具配置"""
    response = client.get("/api/tools/configs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "tools" in data
    assert "total" in data
    assert isinstance(data["tools"], list)
    assert data["total"] > 0


def test_get_single_tool_config():
    """测试获取单个工具配置"""
    # 获取存在的工具
    response = client.get("/api/tools/time/config")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "tool" in data
    assert data["tool"]["tool_id"] == "time"


def test_get_nonexistent_tool():
    """测试获取不存在的工具"""
    response = client.get("/api/tools/nonexistent/config")
    
    assert response.status_code == 404


def test_update_tool_config():
    """测试更新工具配置"""
    update_data = {
        "enabled": False,
        "mode": "MCP",
        "config": {
            "timeout": 10000,
            "retries": 5
        }
    }
    
    response = client.put("/api/tools/time/config", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert data["tool"]["enabled"] == False
    assert data["tool"]["mode"] == "MCP"
    assert data["tool"]["config"]["timeout"] == 10000
    
    # 验证更新持久化
    response = client.get("/api/tools/time/config")
    data = response.json()
    assert data["tool"]["enabled"] == False


def test_update_nonexistent_tool():
    """测试更新不存在的工具"""
    update_data = {"enabled": False}
    
    response = client.put("/api/tools/nonexistent/config", json=update_data)
    
    assert response.status_code == 404


def test_batch_update_tools():
    """测试批量更新工具配置"""
    # 先获取所有配置
    response = client.get("/api/tools/configs")
    all_tools = response.json()["tools"]
    
    # 修改所有工具为禁用
    for tool in all_tools:
        tool["enabled"] = False
    
    # 批量更新
    response = client.post("/api/tools/configs/batch", json=all_tools)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert data["total"] == len(all_tools)
    
    # 验证所有工具都被禁用
    for tool in data["tools"]:
        assert tool["enabled"] == False


def test_reset_tool_configs():
    """测试重置工具配置"""
    # 先修改一个工具
    update_data = {"enabled": False}
    client.put("/api/tools/time/config", json=update_data)
    
    # 重置
    response = client.post("/api/tools/configs/reset")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert len(data["tools"]) > 0
    
    # 验证time工具恢复为默认（启用）
    time_tool = next(t for t in data["tools"] if t["tool_id"] == "time")
    assert time_tool["enabled"] == True


def test_partial_update():
    """测试部分字段更新"""
    # 只更新enabled字段
    update_data = {"enabled": False}
    
    response = client.put("/api/tools/calculator/config", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["tool"]["enabled"] == False
    # 其他字段应保持不变
    assert "mode" in data["tool"]
    assert "config" in data["tool"]


def test_invalid_update_data():
    """测试无效更新数据"""
    # 无效的mode值
    update_data = {"mode": "INVALID_MODE"}
    
    response = client.put("/api/tools/time/config", json=update_data)
    
    # 应该返回错误（pydantic验证）
    assert response.status_code in [400, 422, 500]


def test_api_error_handling():
    """测试API错误处理"""
    # 发送空数据
    response = client.put("/api/tools/time/config", json={})
    
    # 应该成功（空更新）
    assert response.status_code == 200


def test_workflow():
    """测试完整工作流"""
    # 1. 获取初始配置
    response = client.get("/api/tools/time/config")
    initial_config = response.json()["tool"]
    
    # 2. 更新配置
    update_data = {
        "enabled": not initial_config["enabled"],
        "description": "Updated by integration test"
    }
    response = client.put("/api/tools/time/config", json=update_data)
    assert response.status_code == 200
    
    # 3. 验证更新
    response = client.get("/api/tools/time/config")
    updated_config = response.json()["tool"]
    assert updated_config["enabled"] == update_data["enabled"]
    assert updated_config["description"] == update_data["description"]
    
    # 4. 重置为默认
    response = client.post("/api/tools/configs/reset")
    assert response.status_code == 200
    
    # 5. 验证重置
    response = client.get("/api/tools/time/config")
    reset_config = response.json()["tool"]
    assert reset_config["enabled"] == True  # 默认值


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

