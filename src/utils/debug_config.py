#!/usr/bin/env python3
"""
调试配置加载问题
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.config_loader import config_loader

def debug_config():
    """调试配置加载"""
    print("正在调试配置加载...")
    
    try:
        # 1. 检查环境变量
        print(f"当前环境: {config_loader._environment}")
        
        # 2. 检查配置目录
        print(f"配置目录: {config_loader.config_dir}")
        print(f"基础配置目录: {config_loader.base_config_dir}")
        print(f"环境配置目录: {config_loader.env_config_dir}")
        
        # 3. 直接加载services配置
        print("\n直接加载services配置...")
        services_config = config_loader.load_config("services")
        print(f"services配置: {services_config}")
        
        # 4. 检查LLM配置
        print("\n检查LLM配置...")
        llm_config = services_config.get("llm", {})
        print(f"LLM配置: {llm_config}")
        provider = llm_config.get("provider", "openai")
        print(f"Provider: {provider}")
        
        # 5. 检查get_services_config方法
        print("\n检查get_services_config方法...")
        services_config2 = config_loader.get_services_config()
        print(f"get_services_config返回: {services_config2}")
        
        # 6. 检查环境特定配置
        print("\n检查环境特定配置...")
        env_config_path = config_loader.env_config_dir / f"{config_loader._environment}.yaml"
        print(f"环境配置文件路径: {env_config_path}")
        print(f"环境配置文件是否存在: {env_config_path.exists()}")
        
        if env_config_path.exists():
            env_config = config_loader._load_yaml_file(env_config_path, required=False)
            print(f"环境配置内容: {env_config}")
        
        return True
        
    except Exception as e:
        print(f"调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_config()
    sys.exit(0 if success else 1)