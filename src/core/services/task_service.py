"""
任务服务

提供任务管理的核心业务逻辑。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..domain.task_model import TaskModel, TaskStatus, TaskPriority, TaskResult
from ...infrastructure.database import DatabaseService
from ...infrastructure.cache import CacheService


class TaskService:
    """任务服务类"""
    
    def __init__(self, db_service: DatabaseService, cache_service: CacheService):
        self.db_service = db_service
        self.cache_service = cache_service
        self._tasks_cache_key = "tasks"
    
    async def create_task(
        self,
        title: str,
        description: str,
        agent_id: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        input_data: Optional[Dict[str, Any]] = None
    ) -> TaskModel:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        task = TaskModel(
            id=task_id,
            title=title,
            description=description,
            agent_id=agent_id,
            priority=priority,
            input_data=input_data or {}
        )
        
        # 保存到数据库
        await self.db_service.save("tasks", task_id, task.__dict__)
        
        # 更新缓存
        await self._update_tasks_cache()
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[TaskModel]:
        """获取任务"""
        # 先从缓存获取
        tasks_cache = await self.cache_service.get(self._tasks_cache_key)
        if tasks_cache and task_id in tasks_cache:
            task_data = tasks_cache[task_id]
            return self._dict_to_task_model(task_data)
        
        # 从数据库获取
        task_data = await self.db_service.get("tasks", task_id)
        if not task_data:
            return None
            
        return self._dict_to_task_model(task_data)
    
    async def get_tasks_by_agent(self, agent_id: str) -> List[TaskModel]:
        """根据智能体ID获取任务列表"""
        tasks = await self.get_all_tasks()
        return [task for task in tasks if task.agent_id == agent_id]
    
    async def get_tasks_by_status(self, status: TaskStatus) -> List[TaskModel]:
        """根据状态获取任务列表"""
        tasks = await self.get_all_tasks()
        return [task for task in tasks if task.status == status]
    
    async def get_pending_tasks(self, agent_id: Optional[str] = None) -> List[TaskModel]:
        """获取待处理任务"""
        tasks = await self.get_tasks_by_status(TaskStatus.PENDING)
        if agent_id:
            tasks = [task for task in tasks if task.agent_id == agent_id]
        
        # 按优先级排序
        priority_order = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        return sorted(tasks, key=lambda task: priority_order[task.priority])
    
    async def get_all_tasks(self) -> List[TaskModel]:
        """获取所有任务"""
        # 先从缓存获取
        tasks_cache = await self.cache_service.get(self._tasks_cache_key)
        if tasks_cache:
            return [self._dict_to_task_model(task_data) for task_data in tasks_cache.values()]
        
        # 从数据库获取
        tasks_data = await self.db_service.query("tasks", {})
        tasks = [self._dict_to_task_model(task_data) for task_data in tasks_data]
        
        # 更新缓存
        tasks_dict = {task.id: task.__dict__ for task in tasks}
        await self.cache_service.set(self._tasks_cache_key, tasks_dict, expire=3600)
        
        return tasks
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[TaskModel]:
        """更新任务"""
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # 更新字段
        if "title" in updates:
            task.title = updates["title"]
        if "description" in updates:
            task.description = updates["description"]
        if "priority" in updates:
            task.update_priority(updates["priority"])
        if "input_data" in updates:
            task.input_data.update(updates["input_data"])
        
        # 更新数据库
        await self.db_service.update("tasks", task_id, task.__dict__)
        
        # 更新缓存
        await self._update_tasks_cache()
        
        return task
    
    async def start_task(self, task_id: str) -> bool:
        """开始任务"""
        task = await self.get_task(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False
        
        task.start()
        
        # 更新数据库
        await self.db_service.update("tasks", task_id, task.__dict__)
        
        # 更新缓存
        await self._update_tasks_cache()
        
        return True
    
    async def complete_task(self, task_id: str, result: TaskResult) -> bool:
        """完成任务"""
        task = await self.get_task(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return False
        
        task.complete(result)
        
        # 更新数据库
        await self.db_service.update("tasks", task_id, task.__dict__)
        
        # 更新缓存
        await self._update_tasks_cache()
        
        return True
    
    async def fail_task(self, task_id: str, error: str) -> bool:
        """标记任务失败"""
        task = await self.get_task(task_id)
        if not task or task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            return False
        
        task.fail(error)
        
        # 更新数据库
        await self.db_service.update("tasks", task_id, task.__dict__)
        
        # 更新缓存
        await self._update_tasks_cache()
        
        return True
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = await self.get_task(task_id)
        if not task or task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return False
        
        task.cancel()
        
        # 更新数据库
        await self.db_service.update("tasks", task_id, task.__dict__)
        
        # 更新缓存
        await self._update_tasks_cache()
        
        return True
    
    async def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        # 从数据库删除
        result = await self.db_service.delete("tasks", task_id)
        
        if result:
            # 更新缓存
            await self._update_tasks_cache()
        
        return result
    
    async def _update_tasks_cache(self) -> None:
        """更新任务缓存"""
        tasks_data = await self.db_service.query("tasks", {})
        tasks_dict = {task_data["id"]: task_data for task_data in tasks_data}
        await self.cache_service.set(self._tasks_cache_key, tasks_dict, expire=3600)
    
    def _dict_to_task_model(self, task_data: Dict[str, Any]) -> TaskModel:
        """将字典转换为TaskModel对象"""
        # 处理枚举类型
        if "status" in task_data and isinstance(task_data["status"], str):
            task_data["status"] = TaskStatus(task_data["status"])
        if "priority" in task_data and isinstance(task_data["priority"], str):
            task_data["priority"] = TaskPriority(task_data["priority"])
        
        # 处理结果对象
        if "result" in task_data and task_data["result"]:
            result_data = task_data["result"]
            task_data["result"] = TaskResult(
                success=result_data["success"],
                data=result_data.get("data"),
                error=result_data.get("error"),
                execution_time=result_data.get("execution_time")
            )
        
        # 处理日期时间
        for field in ["created_at", "updated_at", "started_at", "completed_at"]:
            if field in task_data and task_data[field] and isinstance(task_data[field], str):
                task_data[field] = datetime.fromisoformat(task_data[field])
        
        return TaskModel(**task_data)