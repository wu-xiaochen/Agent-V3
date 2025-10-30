"""
工具配置服务

提供工具配置的CRUD操作和持久化存储
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.tool_config import ToolConfig, ToolConfigUpdate
import logging

logger = logging.getLogger(__name__)

# 配置文件路径
TOOL_CONFIG_FILE = Path("data/tool_configs.json")

# 默认工具配置
DEFAULT_TOOLS = [
    {
        "tool_id": "time",
        "name": "Time Tool",
        "description": "Get current date and time in various timezones",
        "enabled": True,
        "mode": "API",
        "config": {
            "timeout": 5000,
            "retries": 3
        }
    },
    {
        "tool_id": "calculator",
        "name": "Calculator",
        "description": "Perform mathematical calculations",
        "enabled": True,
        "mode": "API",
        "config": {
            "timeout": 3000,
            "retries": 2
        }
    },
    {
        "tool_id": "search",
        "name": "Web Search",
        "description": "Search the web for information",
        "enabled": False,
        "mode": "API",
        "config": {
            "endpoint": "https://api.search.com",
            "timeout": 10000,
            "retries": 3
        }
    },
    {
        "tool_id": "document_generator",
        "name": "Document Generator",
        "description": "Generate various types of documents",
        "enabled": True,
        "mode": "API",
        "config": {
            "timeout": 30000,
            "retries": 2
        }
    },
    {
        "tool_id": "crewai_generator",
        "name": "CrewAI Generator",
        "description": "Generate CrewAI team configurations",
        "enabled": True,
        "mode": "API",
        "config": {
            "timeout": 60000,
            "retries": 1
        }
    }
]


class ToolConfigService:
    """工具配置服务类"""
    
    def __init__(self):
        """初始化服务"""
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """确保配置文件存在"""
        if not TOOL_CONFIG_FILE.exists():
            TOOL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._save_configs(DEFAULT_TOOLS)
            logger.info(f"Created default tool config file at {TOOL_CONFIG_FILE}")
    
    def _load_configs(self) -> List[Dict[str, Any]]:
        """从文件加载配置"""
        try:
            with open(TOOL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tools', [])
        except Exception as e:
            logger.error(f"Failed to load tool configs: {e}")
            return DEFAULT_TOOLS.copy()
    
    def _save_configs(self, configs: List[Dict[str, Any]]):
        """保存配置到文件"""
        try:
            data = {
                'tools': configs,
                'updated_at': datetime.now().isoformat()
            }
            with open(TOOL_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(configs)} tool configs")
        except Exception as e:
            logger.error(f"Failed to save tool configs: {e}")
            raise
    
    def get_all_configs(self) -> List[ToolConfig]:
        """获取所有工具配置"""
        configs_data = self._load_configs()
        configs = []
        for data in configs_data:
            try:
                # 确保updated_at字段存在
                if 'updated_at' not in data:
                    data['updated_at'] = datetime.now().isoformat()
                config = ToolConfig(**data)
                configs.append(config)
            except Exception as e:
                logger.error(f"Failed to parse tool config: {e}, data: {data}")
                continue
        
        logger.info(f"Loaded {len(configs)} tool configs")
        return configs
    
    def get_config(self, tool_id: str) -> Optional[ToolConfig]:
        """获取单个工具配置"""
        configs = self.get_all_configs()
        for config in configs:
            if config.tool_id == tool_id:
                return config
        return None
    
    def update_config(self, tool_id: str, update: ToolConfigUpdate) -> Optional[ToolConfig]:
        """更新工具配置"""
        configs_data = self._load_configs()
        
        # 查找并更新配置
        found = False
        for config in configs_data:
            if config.get('tool_id') == tool_id:
                # 更新字段
                if update.enabled is not None:
                    config['enabled'] = update.enabled
                if update.mode is not None:
                    config['mode'] = update.mode
                if update.config is not None:
                    config['config'] = update.config
                if update.description is not None:
                    config['description'] = update.description
                
                # 更新时间戳
                config['updated_at'] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            logger.warning(f"Tool {tool_id} not found")
            return None
        
        # 保存配置
        self._save_configs(configs_data)
        
        # 返回更新后的配置
        return self.get_config(tool_id)
    
    def update_all_configs(self, configs: List[ToolConfig]) -> List[ToolConfig]:
        """批量更新工具配置"""
        configs_data = []
        for config in configs:
            config.updated_at = datetime.now()
            # 使用model_dump而不是dict，并指定mode='json'以正确序列化datetime
            config_dict = config.model_dump(mode='json')
            configs_data.append(config_dict)
        
        self._save_configs(configs_data)
        logger.info(f"Batch updated {len(configs)} tool configs")
        
        return self.get_all_configs()
    
    def reset_to_default(self) -> List[ToolConfig]:
        """重置为默认配置"""
        self._save_configs(DEFAULT_TOOLS.copy())
        logger.info("Reset tool configs to default")
        return self.get_all_configs()


# 全局服务实例
_tool_config_service: Optional[ToolConfigService] = None


def get_tool_config_service() -> ToolConfigService:
    """获取工具配置服务实例（单例）"""
    global _tool_config_service
    if _tool_config_service is None:
        _tool_config_service = ToolConfigService()
    return _tool_config_service

