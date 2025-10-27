"""
提示词加载器模块
"""

import os
import yaml
from typing import Dict, Any, Optional


class PromptLoader:
    """提示词加载器，用于从YAML配置文件中加载提示词"""
    
    def __init__(self):
        self._prompt_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_prompts(self, prompts_config: str) -> Dict[str, Any]:
        """
        从指定YAML配置文件加载提示词
        
        Args:
            prompts_config: 提示词配置文件路径，相对于项目根目录
            
        Returns:
            包含所有提示词的字典
        """
        # 检查缓存
        if prompts_config in self._prompt_cache:
            return self._prompt_cache[prompts_config]
        
        try:
            # 获取绝对路径
            config_path = os.path.join(os.getcwd(), prompts_config)
            
            # 加载YAML配置文件
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # 提取提示词部分
            prompts = config.get('prompts', {})
            
            # 缓存提示词
            self._prompt_cache[prompts_config] = prompts
            
            return prompts
            
        except Exception as e:
            raise ValueError(f"无法加载提示词配置文件 {prompts_config}: {str(e)}")
    
    def get_prompt(self, prompts_config: str, prompt_key: str) -> Optional[str]:
        """
        获取指定的提示词
        
        Args:
            prompts_config: 提示词配置文件路径
            prompt_key: 提示词键名
            
        Returns:
            提示词内容，如果不存在则返回None
        """
        prompts = self.load_prompts(prompts_config)
        prompt_data = prompts.get(prompt_key, {})
        
        if isinstance(prompt_data, dict):
            return prompt_data.get('template', '')
        elif isinstance(prompt_data, str):
            return prompt_data
        else:
            return None
    
    def get_prompt_parameters(self, prompts_config: str, prompt_key: str) -> Dict[str, Any]:
        """
        获取指定提示词的参数
        
        Args:
            prompts_config: 提示词配置文件路径
            prompt_key: 提示词键名
            
        Returns:
            提示词参数字典
        """
        prompts = self.load_prompts(prompts_config)
        prompt_data = prompts.get(prompt_key, {})
        
        if isinstance(prompt_data, dict):
            return prompt_data.get('parameters', {})
        else:
            return {}
    
    def reload_prompts(self, prompts_config: str) -> Dict[str, Any]:
        """
        重新加载提示词，清除缓存
        
        Args:
            prompts_config: 提示词配置文件路径
            
        Returns:
            包含所有提示词的字典
        """
        if prompts_config in self._prompt_cache:
            del self._prompt_cache[prompts_config]
        
        return self.load_prompts(prompts_config)
    
    def get_conversation_states(self, prompts_config: str) -> Dict[str, str]:
        """
        获取对话状态配置
        
        Args:
            prompts_config: 提示词配置文件路径
            
        Returns:
            对话状态字典
        """
        try:
            # 获取绝对路径
            config_path = os.path.join(os.getcwd(), prompts_config)
            
            # 加载YAML配置文件
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # 提取对话状态部分
            return config.get('conversation_states', {})
            
        except Exception as e:
            raise ValueError(f"无法加载对话状态配置 {prompts_config}: {str(e)}")
    
    def get_state_transitions(self, prompts_config: str) -> Dict[str, list]:
        """
        获取状态转换规则
        
        Args:
            prompts_config: 提示词配置文件路径
            
        Returns:
            状态转换规则字典
        """
        try:
            # 获取绝对路径
            config_path = os.path.join(os.getcwd(), prompts_config)
            
            # 加载YAML配置文件
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # 提取状态转换规则部分
            return config.get('state_transitions', {})
            
        except Exception as e:
            raise ValueError(f"无法加载状态转换规则 {prompts_config}: {str(e)}")


# 全局提示词加载器实例
prompt_loader = PromptLoader()