#!/usr/bin/env python3
"""
详细测试LLMFactory的create_llm方法
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.config.config_loader import config_loader
from src.infrastructure.llm.llm_factory import LLMFactory

def test_llm_factory():
    """测试LLMFactory的create_llm方法"""
    print("正在测试LLMFactory的create_llm方法...")
    
    try:
        # 1. 检查services配置
        print("\n1. 检查services配置...")
        services_config = config_loader.get_services_config()
        print(f"services配置: {services_config}")
        
        # 2. 检查LLM配置
        print("\n2. 检查LLM配置...")
        llm_config = services_config.get("llm", {})
        print(f"LLM配置: {llm_config}")
        provider = llm_config.get("provider", "openai")
        print(f"Provider: {provider}")
        
        # 3. 模拟LLMFactory.create_llm方法的逻辑
        print("\n3. 模拟LLMFactory.create_llm方法的逻辑...")
        if None is None:
            # 获取服务配置中的默认提供商
            services_config = config_loader.get_services_config()
            services = services_config.get("services", {})
            llm_config = services.get("llm", {})
            provider = llm_config.get("provider", "openai")
            print(f"模拟获取的Provider: {provider}")
        
        # 4. 实际调用LLMFactory.create_llm方法
        print("\n4. 实际调用LLMFactory.create_llm方法...")
        llm = LLMFactory.create_llm()
        
        # 5. 检查LLM实例的属性
        print("\n5. 检查LLM实例的属性...")
        print(f"LLM类型: {type(llm)}")
        print(f"模型名称: {llm.model_name}")
        print(f"API Base: {llm.openai_api_base}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_factory()
    sys.exit(0 if success else 1)