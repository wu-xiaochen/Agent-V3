"""
CrewAI执行状态管理服务
负责跟踪CrewAI执行状态、进度和日志
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from threading import Lock
import uuid
from enum import Enum


class ExecutionStatus(str, Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(str, Enum):
    """日志级别枚举"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class CrewAIExecutionService:
    """CrewAI执行服务类"""
    
    def __init__(self):
        """初始化执行服务"""
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
    
    def create_execution(self, crew_config: Dict, inputs: Dict = None) -> str:
        """
        创建新的执行实例
        
        Args:
            crew_config: Crew配置
            inputs: 执行输入参数
            
        Returns:
            执行ID
        """
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        with self.lock:
            self.executions[execution_id] = {
                "execution_id": execution_id,
                "crew_config": crew_config,
                "inputs": inputs or {},
                "status": ExecutionStatus.PENDING.value,
                "progress": 0,
                "current_agent": None,
                "current_task": None,
                "logs": [],
                "started_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_at": None,
                "result": None,
                "error": None
            }
        
        return execution_id
    
    def start_execution(self, execution_id: str) -> bool:
        """
        开始执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功
        """
        with self.lock:
            if execution_id not in self.executions:
                return False
            
            self.executions[execution_id].update({
                "status": ExecutionStatus.RUNNING.value,
                "started_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            self._add_log(execution_id, LogLevel.INFO, "🚀 开始执行")
            return True
    
    def update_progress(
        self, 
        execution_id: str, 
        current_agent: Optional[str] = None,
        current_task: Optional[str] = None,
        progress: int = 0
    ) -> None:
        """
        更新执行进度
        
        Args:
            execution_id: 执行ID
            current_agent: 当前执行的Agent
            current_task: 当前执行的任务
            progress: 进度百分比 (0-100)
        """
        with self.lock:
            if execution_id in self.executions:
                updates = {
                    "progress": max(0, min(100, progress)),
                    "updated_at": datetime.now().isoformat()
                }
                
                if current_agent is not None:
                    updates["current_agent"] = current_agent
                
                if current_task is not None:
                    updates["current_task"] = current_task
                
                self.executions[execution_id].update(updates)
    
    def add_log(
        self, 
        execution_id: str, 
        level: str, 
        message: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        添加日志
        
        Args:
            execution_id: 执行ID
            level: 日志级别
            message: 日志消息
            metadata: 额外元数据
        """
        self._add_log(execution_id, level, message, metadata)
    
    def _add_log(
        self, 
        execution_id: str, 
        level: str, 
        message: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """内部添加日志方法"""
        with self.lock:
            if execution_id in self.executions:
                log_entry = {
                    "level": level,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata or {}
                }
                self.executions[execution_id]["logs"].append(log_entry)
    
    def pause_execution(self, execution_id: str) -> bool:
        """
        暂停执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功
        """
        with self.lock:
            if execution_id not in self.executions:
                return False
            
            if self.executions[execution_id]["status"] != ExecutionStatus.RUNNING.value:
                return False
            
            self.executions[execution_id].update({
                "status": ExecutionStatus.PAUSED.value,
                "updated_at": datetime.now().isoformat()
            })
            
            self._add_log(execution_id, LogLevel.WARNING, "⏸️ 执行已暂停")
            return True
    
    def resume_execution(self, execution_id: str) -> bool:
        """
        恢复执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功
        """
        with self.lock:
            if execution_id not in self.executions:
                return False
            
            if self.executions[execution_id]["status"] != ExecutionStatus.PAUSED.value:
                return False
            
            self.executions[execution_id].update({
                "status": ExecutionStatus.RUNNING.value,
                "updated_at": datetime.now().isoformat()
            })
            
            self._add_log(execution_id, LogLevel.INFO, "▶️ 恢复执行")
            return True
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        取消执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功
        """
        with self.lock:
            if execution_id not in self.executions:
                return False
            
            status = self.executions[execution_id]["status"]
            if status in [ExecutionStatus.COMPLETED.value, ExecutionStatus.CANCELLED.value]:
                return False
            
            self.executions[execution_id].update({
                "status": ExecutionStatus.CANCELLED.value,
                "updated_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            })
            
            self._add_log(execution_id, LogLevel.WARNING, "⏹️ 执行已取消")
            return True
    
    def complete_execution(
        self, 
        execution_id: str, 
        result: Any,
        success: bool = True
    ) -> None:
        """
        完成执行
        
        Args:
            execution_id: 执行ID
            result: 执行结果
            success: 是否成功
        """
        with self.lock:
            if execution_id in self.executions:
                status = ExecutionStatus.COMPLETED.value if success else ExecutionStatus.FAILED.value
                
                self.executions[execution_id].update({
                    "status": status,
                    "progress": 100,
                    "result": result,
                    "completed_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
                
                if success:
                    self._add_log(execution_id, LogLevel.SUCCESS, "✅ 执行完成")
                else:
                    self._add_log(execution_id, LogLevel.ERROR, "❌ 执行失败")
    
    def fail_execution(self, execution_id: str, error: str) -> None:
        """
        标记执行失败
        
        Args:
            execution_id: 执行ID
            error: 错误信息
        """
        with self.lock:
            if execution_id in self.executions:
                self.executions[execution_id].update({
                    "status": ExecutionStatus.FAILED.value,
                    "error": error,
                    "completed_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
                
                self._add_log(execution_id, LogLevel.ERROR, f"❌ 执行失败: {error}")
    
    def get_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        获取执行状态
        
        Args:
            execution_id: 执行ID
            
        Returns:
            执行状态信息
        """
        with self.lock:
            return self.executions.get(execution_id)
    
    def get_recent_logs(
        self, 
        execution_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取最近的日志
        
        Args:
            execution_id: 执行ID
            limit: 返回日志数量限制
            
        Returns:
            日志列表
        """
        with self.lock:
            if execution_id not in self.executions:
                return []
            
            logs = self.executions[execution_id]["logs"]
            return logs[-limit:] if len(logs) > limit else logs
    
    def cleanup_old_executions(self, max_age_hours: int = 24) -> int:
        """
        清理旧的执行记录
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的记录数
        """
        from datetime import timedelta
        
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(hours=max_age_hours)
            
            to_remove = []
            for exec_id, exec_data in self.executions.items():
                started_at = datetime.fromisoformat(exec_data["started_at"])
                if started_at < cutoff:
                    to_remove.append(exec_id)
            
            for exec_id in to_remove:
                del self.executions[exec_id]
            
            return len(to_remove)


# 全局实例
crewai_execution_service = CrewAIExecutionService()


