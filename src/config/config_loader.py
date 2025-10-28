"""
配置加载模块
用于加载和管理配置文件
"""

import os
import yaml
from functools import lru_cache
from typing import Dict, Any, Optional
from pathlib import Path
from src.shared.exceptions.exceptions import ConfigurationError
from src.shared.utils.helpers import get_env_var, merge_dicts


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置目录路径，默认为项目根目录下的config目录
        """
        if config_dir is None:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            config_dir = os.path.join(project_root, "config")
        
        self.config_dir = Path(config_dir)
        self.base_config_dir = self.config_dir / "base"
        self.env_config_dir = self.config_dir / "environments"
        self._configs = {}
        self._environment = get_env_var("ENVIRONMENT", "development")
    
    def load_config(self, config_name: str, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_name: 配置文件名（不带.yaml扩展名）
            environment: 环境名称，默认使用当前环境
            
        Returns:
            配置字典
        """
        if environment is None:
            environment = self._environment
            
        cache_key = f"{config_name}_{environment}"
        if cache_key in self._configs:
            return self._configs[cache_key]
        
        # 加载基础配置
        base_config_path = self.base_config_dir / f"{config_name}.yaml"
        base_config = self._load_yaml_file(base_config_path)
        
        # 加载环境特定配置
        env_config_path = self.env_config_dir / f"{environment}.yaml"
        env_config = self._load_yaml_file(env_config_path, required=False)
        
        # 合并配置
        if env_config and config_name in env_config:
            config = merge_dicts(base_config, env_config[config_name])
        else:
            config = base_config
            
        # 替换环境变量
        config = self._replace_env_vars(config)
        
        # 缓存配置
        self._configs[cache_key] = config
        
        return config
    
    @lru_cache(maxsize=32)
    def _load_yaml_file_cached(self, file_path: str) -> Dict[str, Any]:
        """
        缓存的YAML文件加载（用于不可变路径）
        
        Args:
            file_path: 文件路径（字符串，用于哈希）
            
        Returns:
            配置字典
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {}
        
        try:
            with open(path_obj, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config is not None else {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"解析YAML文件失败 {file_path}: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"读取配置文件失败 {file_path}: {str(e)}")
    
    def _load_yaml_file(self, file_path: Path, required: bool = True) -> Dict[str, Any]:
        """
        加载YAML文件
        
        Args:
            file_path: 文件路径
            required: 是否必需文件
            
        Returns:
            配置字典
        """
        if not file_path.exists():
            if required:
                raise ConfigurationError(f"配置文件不存在: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"解析配置文件失败 {file_path}: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"读取配置文件失败 {file_path}: {str(e)}")
    
    def _replace_env_vars(self, config: Any) -> Any:
        """
        递归替换配置中的环境变量
        
        Args:
            config: 配置对象
            
        Returns:
            替换后的配置对象
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            default_value = None
            
            if ":" in env_var:
                env_var, default_value = env_var.split(":", 1)
            
            return get_env_var(env_var, default_value)
        else:
            return config
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.load_config("database")
    
    def get_services_config(self) -> Dict[str, Any]:
        """获取服务配置"""
        return self.load_config("services")
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.load_config("logging")
    
    def get_agents_config(self) -> Dict[str, Any]:
        """获取智能体配置"""
        return self.load_config("agents")
    
    def get_crewai_config(self) -> Dict[str, Any]:
        """获取CrewAI配置"""
        services_config = self.get_services_config()
        return services_config.get("crewai", {})
    
    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        获取LLM配置
        
        Args:
            provider: LLM提供商，如果为None则使用默认提供商
            
        Returns:
            LLM配置字典
        """
        services_config = self.get_services_config()
        llm_config = services_config.get("llm", {})
        
        # 如果指定了provider，返回特定provider的配置
        if provider:
            return llm_config.get(provider, {})
        
        return llm_config
    
    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        services_config = self.get_services_config()
        return services_config.get("redis", {})
    
    def get_prompts_config(self) -> Dict[str, Any]:
        """获取提示词配置"""
        return self.load_config("prompts")
    
    def get_prompts(self) -> Dict[str, Any]:
        """获取提示词配置（别名方法）"""
        return self.get_prompts_config()
    
    def get_prompt_config(self, prompt_type: str, default: Any = None) -> Any:
        """
        获取提示词配置
        
        Args:
            prompt_type: 提示词类型，如 'supply_chain_agent.system_prompt'
            default: 默认值
            
        Returns:
            提示词配置
        """
        keys = prompt_type.split('.')
        prompts_config = self.get_prompts_config()
        
        # 首先检查是否在prompts节点下
        if 'prompts' in prompts_config:
            value = prompts_config['prompts']
        else:
            value = prompts_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload_config(self, config_name: str, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        重新加载配置
        
        Args:
            config_name: 配置文件名（不带.yaml扩展名）
            environment: 环境名称，默认使用当前环境
            
        Returns:
            配置字典
        """
        if environment is None:
            environment = self._environment
            
        cache_key = f"{config_name}_{environment}"
        if cache_key in self._configs:
            del self._configs[cache_key]
            
        return self.load_config(config_name, environment)
    
    def set_environment(self, environment: str) -> None:
        """
        设置当前环境
        
        Args:
            environment: 环境名称
        """
        self._environment = environment
        self._configs.clear()
    
    # 保持向后兼容的方法
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（向后兼容）
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        # 尝试从各个配置中查找
        for config_name in ["database", "services", "logging", "agents"]:
            config = self.load_config(config_name)
            keys = key.split('.')
            value = config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    break
            else:
                # 如果所有键都找到了，返回值
                return value
        
        return default
    
    def get_agent_config(self) -> Dict[str, Any]:
        """
        获取智能体配置（向后兼容）
        
        Returns:
            智能体配置字典
        """
        agents_config = self.get_agents_config()
        # 首先尝试获取agents.unified_agent配置，如果不存在则获取agents.supply_chain_agent配置
        agents = agents_config.get("agents", {})
        return agents.get("unified_agent", agents.get("supply_chain_agent", {}))
    
    def get_specific_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        获取特定智能体的配置
        
        Args:
            agent_name: 智能体名称，如 'unified_agent' 或 'supply_chain_agent'
            
        Returns:
            智能体配置字典
        """
        agents_config = self.get_agents_config()
        agents = agents_config.get("agents", {})
        return agents.get(agent_name, {})
    
    def get_tools_config(self) -> Dict[str, Any]:
        """
        获取工具配置
        
        Returns:
            工具配置字典
        """
        services_config = self.get_services_config()
        return services_config.get("tools", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        获取输出格式配置
        
        Returns:
            输出格式配置字典
        """
        services_config = self.get_services_config()
        # services_config有一个"services"键，需要先获取它
        services = services_config.get("services", {})
        return services.get("output", {"format": "normal"})
    
    def reload(self) -> None:
        """重新加载配置文件（向后兼容）"""
        self._configs.clear()


# 全局配置实例
config_loader = ConfigLoader()