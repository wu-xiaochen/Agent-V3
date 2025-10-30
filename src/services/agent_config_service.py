"""
Agent配置服务

提供Agent配置的CRUD操作和持久化存储
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.agent_config import AgentConfig, AgentConfigCreate, AgentConfigUpdate
import logging

logger = logging.getLogger(__name__)

# 配置文件路径
AGENT_CONFIG_FILE = Path("data/agent_configs.json")

# 默认Agent配置
DEFAULT_AGENTS = [
    {
        "id": "unified_agent",
        "name": "Unified Agent",
        "description": "通用智能助手，可以处理各种任务",
        "system_prompt": "你是一个智能助手，可以帮助用户完成各种任务。你拥有多个工具，可以查询时间、进行计算、生成文档等。请根据用户的需求选择合适的工具，并提供有帮助的回答。",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "tools": ["time", "calculator", "document_generator"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
]


class AgentConfigService:
    """Agent配置服务类"""
    
    def __init__(self):
        """初始化服务"""
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """确保配置文件存在"""
        if not AGENT_CONFIG_FILE.exists():
            AGENT_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._save_configs(DEFAULT_AGENTS.copy())
            logger.info(f"Created default agent config file at {AGENT_CONFIG_FILE}")
    
    def _load_configs(self) -> List[Dict[str, Any]]:
        """从文件加载配置"""
        try:
            with open(AGENT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('agents', [])
        except Exception as e:
            logger.error(f"Failed to load agent configs: {e}")
            return DEFAULT_AGENTS.copy()
    
    def _save_configs(self, configs: List[Dict[str, Any]]):
        """保存配置到文件"""
        try:
            data = {
                'agents': configs,
                'updated_at': datetime.now().isoformat()
            }
            with open(AGENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(configs)} agent configs")
        except Exception as e:
            logger.error(f"Failed to save agent configs: {e}")
            raise
    
    def _generate_id(self, name: str) -> str:
        """生成Agent ID"""
        import re
        # 转换为小写，替换空格为下划线，移除特殊字符
        agent_id = re.sub(r'[^a-z0-9_]', '', name.lower().replace(' ', '_'))
        
        # 检查ID是否已存在
        existing_ids = [config['id'] for config in self._load_configs()]
        if agent_id not in existing_ids:
            return agent_id
        
        # 如果存在，添加数字后缀
        counter = 1
        while f"{agent_id}_{counter}" in existing_ids:
            counter += 1
        return f"{agent_id}_{counter}"
    
    def get_all_configs(self) -> List[AgentConfig]:
        """获取所有Agent配置"""
        configs_data = self._load_configs()
        configs = []
        for data in configs_data:
            try:
                # 确保时间字段存在
                if 'created_at' not in data:
                    data['created_at'] = datetime.now().isoformat()
                if 'updated_at' not in data:
                    data['updated_at'] = datetime.now().isoformat()
                
                config = AgentConfig(**data)
                configs.append(config)
            except Exception as e:
                logger.error(f"Failed to parse agent config: {e}, data: {data}")
                continue
        
        logger.info(f"Loaded {len(configs)} agent configs")
        return configs
    
    def get_config(self, agent_id: str) -> Optional[AgentConfig]:
        """获取单个Agent配置"""
        configs = self.get_all_configs()
        for config in configs:
            if config.id == agent_id:
                return config
        return None
    
    def create_config(self, create_data: AgentConfigCreate) -> AgentConfig:
        """创建Agent配置"""
        configs_data = self._load_configs()
        
        # 生成ID
        agent_id = self._generate_id(create_data.name)
        
        # 创建新配置
        now = datetime.now()
        new_config = AgentConfig(
            id=agent_id,
            name=create_data.name,
            description=create_data.description,
            system_prompt=create_data.system_prompt,
            model=create_data.model,
            temperature=create_data.temperature,
            max_tokens=create_data.max_tokens,
            tools=create_data.tools,
            created_at=now,
            updated_at=now
        )
        
        # 添加到列表
        configs_data.append(new_config.model_dump(mode='json'))
        
        # 保存
        self._save_configs(configs_data)
        
        logger.info(f"Created agent config: {agent_id}")
        return new_config
    
    def update_config(self, agent_id: str, update: AgentConfigUpdate) -> Optional[AgentConfig]:
        """更新Agent配置"""
        configs_data = self._load_configs()
        
        # 查找并更新配置
        found = False
        for config in configs_data:
            if config.get('id') == agent_id:
                # 更新字段
                if update.name is not None:
                    config['name'] = update.name
                if update.description is not None:
                    config['description'] = update.description
                if update.system_prompt is not None:
                    config['system_prompt'] = update.system_prompt
                if update.model is not None:
                    config['model'] = update.model
                if update.temperature is not None:
                    config['temperature'] = update.temperature
                if update.max_tokens is not None:
                    config['max_tokens'] = update.max_tokens
                if update.tools is not None:
                    config['tools'] = update.tools
                
                # 更新时间戳
                config['updated_at'] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            logger.warning(f"Agent {agent_id} not found")
            return None
        
        # 保存配置
        self._save_configs(configs_data)
        
        # 返回更新后的配置
        return self.get_config(agent_id)
    
    def delete_config(self, agent_id: str) -> bool:
        """删除Agent配置"""
        configs_data = self._load_configs()
        
        # 不允许删除最后一个Agent
        if len(configs_data) <= 1:
            logger.warning("Cannot delete the last agent")
            return False
        
        # 查找并删除
        original_length = len(configs_data)
        configs_data = [c for c in configs_data if c.get('id') != agent_id]
        
        if len(configs_data) == original_length:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        # 保存配置
        self._save_configs(configs_data)
        
        logger.info(f"Deleted agent config: {agent_id}")
        return True
    
    def reset_to_default(self) -> List[AgentConfig]:
        """重置为默认配置"""
        self._save_configs(DEFAULT_AGENTS.copy())
        logger.info("Reset agent configs to default")
        return self.get_all_configs()


# 全局服务实例
_agent_config_service: Optional[AgentConfigService] = None


def get_agent_config_service() -> AgentConfigService:
    """获取Agent配置服务实例（单例）"""
    global _agent_config_service
    if _agent_config_service is None:
        _agent_config_service = AgentConfigService()
    return _agent_config_service

