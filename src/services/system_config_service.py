"""
系统配置服务
负责系统配置的加载、保存、加密等功能
"""
import json
import os
from datetime import datetime
from typing import Optional
from pathlib import Path
import base64

from src.models.system_config import SystemConfig, SystemConfigUpdate


class SystemConfigService:
    """系统配置服务类"""
    
    def __init__(self, config_file: str = "data/system_config.json"):
        """
        初始化配置服务
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 简单的加密密钥（实际生产环境应使用环境变量或密钥管理服务）
        self._encryption_key = os.getenv("CONFIG_ENCRYPTION_KEY", "default_key_change_in_production")
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """
        简单加密API Key（生产环境应使用更安全的加密方法）
        
        Args:
            api_key: 原始API Key
            
        Returns:
            加密后的API Key
        """
        if not api_key:
            return ""
        # 简单的base64编码（仅用于演示，生产环境应使用AES等）
        return base64.b64encode(api_key.encode()).decode()
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """
        解密API Key
        
        Args:
            encrypted_key: 加密的API Key
            
        Returns:
            解密后的API Key
        """
        if not encrypted_key:
            return ""
        try:
            return base64.b64decode(encrypted_key.encode()).decode()
        except Exception:
            return encrypted_key  # 如果解密失败，返回原值（可能是未加密的）
    
    def get_config(self) -> SystemConfig:
        """
        获取系统配置
        
        Returns:
            系统配置对象
        """
        if not self.config_file.exists():
            # 返回默认配置
            config = SystemConfig()
            config.created_at = datetime.now()
            config.updated_at = datetime.now()
            return config
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # 解密API Key
            if "api_key" in data and data["api_key"]:
                data["api_key"] = self._decrypt_api_key(data["api_key"])
            
            config = SystemConfig(**data)
            return config
        except Exception as e:
            print(f"加载配置失败: {e}，返回默认配置")
            config = SystemConfig()
            config.created_at = datetime.now()
            config.updated_at = datetime.now()
            return config
    
    def save_config(self, config: SystemConfig) -> SystemConfig:
        """
        保存系统配置
        
        Args:
            config: 系统配置对象
            
        Returns:
            保存后的配置对象
        """
        # 更新时间戳
        if not config.created_at:
            config.created_at = datetime.now()
        config.updated_at = datetime.now()
        
        # 准备保存的数据（加密API Key）
        save_data = config.model_dump(mode='json')
        if save_data.get("api_key"):
            save_data["api_key"] = self._encrypt_api_key(save_data["api_key"])
        
        # 保存到文件
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return config
    
    def update_config(self, update: SystemConfigUpdate) -> SystemConfig:
        """
        更新系统配置
        
        Args:
            update: 配置更新对象
            
        Returns:
            更新后的配置对象
        """
        # 获取当前配置
        current_config = self.get_config()
        
        # 应用更新
        update_data = update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(current_config, key, value)
        
        # 保存并返回
        return self.save_config(current_config)
    
    def reset_to_default(self) -> SystemConfig:
        """
        重置为默认配置
        
        Returns:
            默认配置对象
        """
        default_config = SystemConfig()
        default_config.created_at = datetime.now()
        default_config.updated_at = datetime.now()
        return self.save_config(default_config)

