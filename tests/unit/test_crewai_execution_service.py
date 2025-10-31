"""
CrewAI执行服务单元测试
"""
import pytest
from datetime import datetime
from src.services.crewai_execution_service import (
    CrewAIExecutionService,
    ExecutionStatus,
    LogLevel
)


class TestCrewAIExecutionService:
    """测试CrewAI执行服务"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return CrewAIExecutionService()
    
    @pytest.fixture
    def sample_crew_config(self):
        """示例Crew配置"""
        return {
            "name": "Test Crew",
            "agents": [
                {"role": "Researcher", "goal": "Research topics"}
            ],
            "tasks": [
                {"description": "Research AI trends"}
            ]
        }
    
    def test_create_execution(self, service, sample_crew_config):
        """测试创建执行"""
        exec_id = service.create_execution(sample_crew_config)
        
        assert exec_id.startswith("exec_")
        assert len(exec_id) > 10
        
        status = service.get_status(exec_id)
        assert status is not None
        assert status["crew_config"] == sample_crew_config
        assert status["status"] == ExecutionStatus.PENDING.value
    
    def test_start_execution(self, service, sample_crew_config):
        """测试开始执行"""
        exec_id = service.create_execution(sample_crew_config)
        success = service.start_execution(exec_id)
        
        assert success is True
        status = service.get_status(exec_id)
        assert status["status"] == ExecutionStatus.RUNNING.value
    
    def test_update_progress(self, service, sample_crew_config):
        """测试更新进度"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        service.update_progress(exec_id, "Agent1", "Task1", 50)
        
        status = service.get_status(exec_id)
        assert status["progress"] == 50
        assert status["current_agent"] == "Agent1"
        assert status["current_task"] == "Task1"
    
    def test_add_log(self, service, sample_crew_config):
        """测试添加日志"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        service.add_log(exec_id, LogLevel.INFO, "Test log message")
        
        logs = service.get_recent_logs(exec_id)
        assert len(logs) > 0
        assert any(log["message"] == "Test log message" for log in logs)
    
    def test_pause_execution(self, service, sample_crew_config):
        """测试暂停执行"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        success = service.pause_execution(exec_id)
        
        assert success is True
        status = service.get_status(exec_id)
        assert status["status"] == ExecutionStatus.PAUSED.value
    
    def test_resume_execution(self, service, sample_crew_config):
        """测试恢复执行"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        service.pause_execution(exec_id)
        
        success = service.resume_execution(exec_id)
        
        assert success is True
        status = service.get_status(exec_id)
        assert status["status"] == ExecutionStatus.RUNNING.value
    
    def test_cancel_execution(self, service, sample_crew_config):
        """测试取消执行"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        success = service.cancel_execution(exec_id)
        
        assert success is True
        status = service.get_status(exec_id)
        assert status["status"] == ExecutionStatus.CANCELLED.value
    
    def test_complete_execution(self, service, sample_crew_config):
        """测试完成执行"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        result = {"output": "Task completed"}
        service.complete_execution(exec_id, result, True)
        
        status = service.get_status(exec_id)
        assert status["status"] == ExecutionStatus.COMPLETED.value
        assert status["progress"] == 100
        assert status["result"] == result
    
    def test_fail_execution(self, service, sample_crew_config):
        """测试执行失败"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        service.fail_execution(exec_id, "Test error")
        
        status = service.get_status(exec_id)
        assert status["status"] == ExecutionStatus.FAILED.value
        assert status["error"] == "Test error"
    
    def test_get_recent_logs(self, service, sample_crew_config):
        """测试获取最近日志"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        # 添加多条日志
        for i in range(100):
            service.add_log(exec_id, LogLevel.INFO, f"Log {i}")
        
        # 获取最近10条
        logs = service.get_recent_logs(exec_id, 10)
        assert len(logs) == 10
        
        # 最后一条应该是"Log 99"
        assert "Log 99" in logs[-1]["message"]
    
    def test_cleanup_old_executions(self, service, sample_crew_config):
        """测试清理旧执行"""
        # 创建多个执行
        for i in range(5):
            exec_id = service.create_execution(sample_crew_config)
            service.start_execution(exec_id)
        
        # 清理（24小时内）
        cleaned = service.cleanup_old_executions(max_age_hours=24)
        assert cleaned == 0  # 刚创建的，不应该被清理
        
        # 清理（-1小时，应该清理所有）
        cleaned = service.cleanup_old_executions(max_age_hours=-1)
        assert cleaned == 5
    
    def test_cannot_pause_when_not_running(self, service, sample_crew_config):
        """测试非运行状态无法暂停"""
        exec_id = service.create_execution(sample_crew_config)
        # 不启动，直接暂停
        success = service.pause_execution(exec_id)
        assert success is False
    
    def test_cannot_resume_when_not_paused(self, service, sample_crew_config):
        """测试非暂停状态无法恢复"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        # 运行状态恢复
        success = service.resume_execution(exec_id)
        assert success is False
    
    def test_cannot_cancel_when_completed(self, service, sample_crew_config):
        """测试已完成状态无法取消"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        service.complete_execution(exec_id, {})
        
        # 已完成状态取消
        success = service.cancel_execution(exec_id)
        assert success is False
    
    def test_log_timestamp(self, service, sample_crew_config):
        """测试日志时间戳"""
        exec_id = service.create_execution(sample_crew_config)
        service.start_execution(exec_id)
        
        service.add_log(exec_id, LogLevel.INFO, "Test")
        logs = service.get_recent_logs(exec_id)
        
        assert "timestamp" in logs[-1]
        assert logs[-1]["timestamp"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

