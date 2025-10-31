"""
CrewAI执行状态API集成测试
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api_server import app
from src.services.crewai_execution_service import crewai_execution_service


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_crew_config():
    """示例Crew配置"""
    return {
        "name": "Test Crew",
        "agents": [
            {
                "role": "Researcher",
                "goal": "Research topics",
                "backstory": "Expert researcher"
            }
        ],
        "tasks": [
            {
                "description": "Research AI trends",
                "expected_output": "Trend analysis report",
                "agent": "Researcher"
            }
        ]
    }


class TestCrewAIExecutionAPI:
    """测试CrewAI执行状态API端点"""
    
    def test_create_and_get_execution(self, client, sample_crew_config):
        """测试创建执行并获取状态"""
        # 手动创建执行（因为POST端点需要crew_id）
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        
        # 获取状态
        response = client.get(f"/api/crewai/execution/{exec_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data
        
        status = data["status"]
        assert status["execution_id"] == exec_id
        assert status["crew_config"] == sample_crew_config
    
    def test_start_execution(self, client, sample_crew_config):
        """测试开始执行"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        
        response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = response.json()["status"]
        
        assert status["status"] == "running"
    
    def test_pause_execution(self, client, sample_crew_config):
        """测试暂停执行"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        
        response = client.post(f"/api/crewai/execution/{exec_id}/pause")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "执行已暂停"
        
        # 验证状态
        status_response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = status_response.json()["status"]
        assert status["status"] == "paused"
    
    def test_resume_execution(self, client, sample_crew_config):
        """测试恢复执行"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        crewai_execution_service.pause_execution(exec_id)
        
        response = client.post(f"/api/crewai/execution/{exec_id}/resume")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "执行已恢复"
        
        # 验证状态
        status_response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = status_response.json()["status"]
        assert status["status"] == "running"
    
    def test_cancel_execution(self, client, sample_crew_config):
        """测试取消执行"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        
        response = client.post(f"/api/crewai/execution/{exec_id}/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "执行已取消"
        
        # 验证状态
        status_response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = status_response.json()["status"]
        assert status["status"] == "cancelled"
    
    def test_get_execution_logs(self, client, sample_crew_config):
        """测试获取执行日志"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        
        # 添加日志
        crewai_execution_service.add_log(exec_id, "info", "Test log message")
        crewai_execution_service.add_log(exec_id, "success", "Success message")
        
        response = client.get(f"/api/crewai/execution/{exec_id}/logs?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "logs" in data
        assert data["count"] >= 2
        
        logs = data["logs"]
        assert any(log["message"] == "Test log message" for log in logs)
    
    def test_logs_limit(self, client, sample_crew_config):
        """测试日志数量限制"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        
        # 添加多条日志
        for i in range(100):
            crewai_execution_service.add_log(exec_id, "info", f"Log {i}")
        
        # 获取最近10条
        response = client.get(f"/api/crewai/execution/{exec_id}/logs?limit=10")
        logs = response.json()["logs"]
        
        assert len(logs) == 10
        assert "Log 99" in logs[-1]["message"]
    
    def test_invalid_execution_id(self, client):
        """测试无效执行ID"""
        response = client.get("/api/crewai/execution/invalid_id/status")
        
        assert response.status_code == 404
    
    def test_pause_not_running(self, client):
        """测试暂停非运行状态的执行"""
        # 创建但不启动
        sample_config = {"name": "Test"}
        exec_id = crewai_execution_service.create_execution(sample_config)
        
        response = client.post(f"/api/crewai/execution/{exec_id}/pause")
        
        # 应该返回错误
        assert response.status_code in [400, 500]
    
    def test_cancel_completed(self, client, sample_crew_config):
        """测试取消已完成执行"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        crewai_execution_service.complete_execution(exec_id, {"result": "done"})
        
        # 尝试取消已完成的执行
        response = client.post(f"/api/crewai/execution/{exec_id}/cancel")
        
        # 应该返回错误
        assert response.status_code in [400, 500]
    
    def test_progress_update(self, client, sample_crew_config):
        """测试进度更新"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        
        # 更新进度
        crewai_execution_service.update_progress(exec_id, "Agent1", "Task1", 50)
        
        # 获取状态
        response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = response.json()["status"]
        
        assert status["progress"] == 50
        assert status["current_agent"] == "Agent1"
        assert status["current_task"] == "Task1"
    
    def test_complete_execution(self, client, sample_crew_config):
        """测试完成执行"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        crewai_execution_service.complete_execution(exec_id, {"output": "completed"})
        
        response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = response.json()["status"]
        
        assert status["status"] == "completed"
        assert status["progress"] == 100
        assert status["result"] == {"output": "completed"}
    
    def test_fail_execution(self, client, sample_crew_config):
        """测试执行失败"""
        exec_id = crewai_execution_service.create_execution(sample_crew_config)
        crewai_execution_service.start_execution(exec_id)
        crewai_execution_service.fail_execution(exec_id, "Test error")
        
        response = client.get(f"/api/crewai/execution/{exec_id}/status")
        status = response.json()["status"]
        
        assert status["status"] == "failed"
        assert status["error"] == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

