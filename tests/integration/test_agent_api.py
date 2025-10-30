"""
Agent配置API集成测试
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api_server import app

client = TestClient(app)


def test_get_all_agents():
    """测试获取所有Agent"""
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "agents" in data
    assert len(data["agents"]) > 0


def test_get_single_agent():
    """测试获取单个Agent"""
    response = client.get("/api/agents/unified_agent")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["agent"]["id"] == "unified_agent"


def test_get_nonexistent_agent():
    """测试获取不存在的Agent"""
    response = client.get("/api/agents/nonexistent")
    assert response.status_code == 404


def test_create_agent():
    """测试创建Agent"""
    new_agent = {
        "name": "API Test Agent",
        "description": "Created by API test",
        "system_prompt": "You are a test agent",
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 1500,
        "tools": ["time", "calculator"]
    }
    
    response = client.post("/api/agents", json=new_agent)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["agent"]["name"] == "API Test Agent"
    
    # 清理：删除创建的agent
    agent_id = data["agent"]["id"]
    client.delete(f"/api/agents/{agent_id}")


def test_update_agent():
    """测试更新Agent"""
    update_data = {
        "name": "Updated Agent",
        "temperature": 0.8
    }
    
    response = client.put("/api/agents/unified_agent", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["agent"]["name"] == "Updated Agent"
    assert data["agent"]["temperature"] == 0.8


def test_delete_agent():
    """测试删除Agent"""
    # 先创建
    new_agent = {
        "name": "To Delete",
        "system_prompt": "test"
    }
    response = client.post("/api/agents", json=new_agent)
    agent_id = response.json()["agent"]["id"]
    
    # 删除
    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # 验证删除
    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 404


def test_cannot_delete_last_agent():
    """测试不能删除最后一个Agent"""
    # 先重置确保只有一个agent
    client.post("/api/agents/reset")
    
    # 尝试删除唯一的agent
    response = client.delete("/api/agents/unified_agent")
    assert response.status_code == 400


def test_reset_agents():
    """测试重置Agent"""
    response = client.post("/api/agents/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["agents"]) > 0


def test_workflow():
    """测试完整工作流"""
    # 1. 创建
    new_agent = {
        "name": "Workflow Test",
        "system_prompt": "test workflow"
    }
    response = client.post("/api/agents", json=new_agent)
    agent_id = response.json()["agent"]["id"]
    
    # 2. 更新
    update = {"name": "Updated Workflow"}
    response = client.put(f"/api/agents/{agent_id}", json=update)
    assert response.status_code == 200
    
    # 3. 获取验证
    response = client.get(f"/api/agents/{agent_id}")
    assert response.json()["agent"]["name"] == "Updated Workflow"
    
    # 4. 删除
    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

