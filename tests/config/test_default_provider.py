#!/usr/bin/env python3
"""
测试LLMFactory默认provider获取
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

def test_default_provider():
    """测试默认provider获取"""
    print("正在测试默认provider获取...")
    
    try:
        # 获取服务配置
        services_config = config_loader.get_services_config()
        llm_config = services_config.get("llm", {})
        provider = llm_config.get("provider", "openai")
        
        print(f"从配置文件获取的默认provider: {provider}")
        
        # 测试LLMFactory.create_llm方法
        print("\n测试LLMFactory.create_llm方法...")
        llm = LLMFactory.create_llm()
        
        # 检查LLM实例的属性
        print(f"LLM类型: {type(llm)}")
        print(f"模型名称: {llm.model_name}")
        print(f"API Base: {llm.openai_api_base}")
        
        # 发送测试消息
        print("\n正在发送测试消息...")
        response = llm.invoke("你好")
        print(f"响应内容: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_default_provider()
    sys.exit(0 if success else 1)