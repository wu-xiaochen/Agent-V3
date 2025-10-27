"""
智能体服务

提供智能体管理的核心业务逻辑。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..domain.agent_model import AgentModel, AgentType, AgentStatus, AgentCapability
from ...infrastructure.database import DatabaseService
from ...infrastructure.cache import CacheService


class AgentService:
    """智能体服务类"""
    
    def __init__(self, db_service: DatabaseService, cache_service: CacheService):
        self.db_service = db_service
        self.cache_service = cache_service
        self._agents_cache_key = "agents"
    
    async def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        description: str,
        config: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[AgentCapability]] = None
    ) -> AgentModel:
        """创建新智能体"""
        agent_id = str(uuid.uuid4())
        agent = AgentModel(
            id=agent_id,
            name=name,
            type=agent_type,
            description=description,
            config=config or {},
            capabilities=capabilities or []
        )
        
        # 保存到数据库
        await self.db_service.save("agents", agent_id, agent.__dict__)
        
        # 更新缓存
        await self._update_agents_cache()
        
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[AgentModel]:
        """获取智能体"""
        # 先从缓存获取
        agents_cache = await self.cache_service.get(self._agents_cache_key)
        if agents_cache and agent_id in agents_cache:
            agent_data = agents_cache[agent_id]
            return self._dict_to_agent_model(agent_data)
        
        # 从数据库获取
        agent_data = await self.db_service.get("agents", agent_id)
        if not agent_data:
            return None
            
        return self._dict_to_agent_model(agent_data)
    
    async def get_agents_by_type(self, agent_type: AgentType) -> List[AgentModel]:
        """根据类型获取智能体列表"""
        agents = await self.get_all_agents()
        return [agent for agent in agents if agent.type == agent_type]
    
    async def get_all_agents(self) -> List[AgentModel]:
        """获取所有智能体"""
        # 先从缓存获取
        agents_cache = await self.cache_service.get(self._agents_cache_key)
        if agents_cache:
            return [self._dict_to_agent_model(agent_data) for agent_data in agents_cache.values()]
        
        # 从数据库获取
        agents_data = await self.db_service.query("agents", {})
        agents = [self._dict_to_agent_model(agent_data) for agent_data in agents_data]
        
        # 更新缓存
        agents_dict = {agent.id: agent.__dict__ for agent in agents}
        await self.cache_service.set(self._agents_cache_key, agents_dict, expire=3600)
        
        return agents
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentModel]:
        """更新智能体"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return None
        
        # 更新字段
        if "name" in updates:
            agent.name = updates["name"]
        if "description" in updates:
            agent.description = updates["description"]
        if "config" in updates:
            agent.update_config(updates["config"])
        if "capabilities" in updates:
            agent.capabilities = updates["capabilities"]
        if "status" in updates:
            agent.update_status(updates["status"])
        
        # 更新数据库
        await self.db_service.update("agents", agent_id, agent.__dict__)
        
        # 更新缓存
        await self._update_agents_cache()
        
        return agent
    
    async def delete_agent(self, agent_id: str) -> bool:
        """删除智能体"""
        # 从数据库删除
        result = await self.db_service.delete("agents", agent_id)
        
        if result:
            # 更新缓存
            await self._update_agents_cache()
        
        return result
    
    async def add_capability(self, agent_id: str, capability: AgentCapability) -> bool:
        """为智能体添加能力"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.add_capability(capability)
        
        # 更新数据库
        await self.db_service.update("agents", agent_id, agent.__dict__)
        
        # 更新缓存
        await self._update_agents_cache()
        
        return True
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """更新智能体状态"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.update_status(status)
        
        # 更新数据库
        await self.db_service.update("agents", agent_id, agent.__dict__)
        
        # 更新缓存
        await self._update_agents_cache()
        
        return True
    
    async def _update_agents_cache(self) -> None:
        """更新智能体缓存"""
        agents_data = await self.db_service.query("agents", {})
        agents_dict = {agent_data["id"]: agent_data for agent_data in agents_data}
        await self.cache_service.set(self._agents_cache_key, agents_dict, expire=3600)
    
    def _dict_to_agent_model(self, agent_data: Dict[str, Any]) -> AgentModel:
        """将字典转换为AgentModel对象"""
        # 处理枚举类型
        if "type" in agent_data and isinstance(agent_data["type"], str):
            agent_data["type"] = AgentType(agent_data["type"])
        if "status" in agent_data and isinstance(agent_data["status"], str):
            agent_data["status"] = AgentStatus(agent_data["status"])
        
        # 处理能力列表
        if "capabilities" in agent_data and agent_data["capabilities"]:
            capabilities = []
            for cap_data in agent_data["capabilities"]:
                capability = AgentCapability(
                    name=cap_data["name"],
                    description=cap_data["description"],
                    enabled=cap_data.get("enabled", True),
                    parameters=cap_data.get("parameters", {})
                )
                capabilities.append(capability)
            agent_data["capabilities"] = capabilities
        
        # 处理日期时间
        if "created_at" in agent_data and isinstance(agent_data["created_at"], str):
            agent_data["created_at"] = datetime.fromisoformat(agent_data["created_at"])
        if "updated_at" in agent_data and isinstance(agent_data["updated_at"], str):
            agent_data["updated_at"] = datetime.fromisoformat(agent_data["updated_at"])
        if "last_activity" in agent_data and agent_data["last_activity"] and isinstance(agent_data["last_activity"], str):
            agent_data["last_activity"] = datetime.fromisoformat(agent_data["last_activity"])
        
        return AgentModel(**agent_data)