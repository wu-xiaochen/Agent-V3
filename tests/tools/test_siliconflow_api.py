#!/usr/bin/env python3
"""
测试硅基流动API连接
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.infrastructure.llm.llm_factory import LLMFactory
from src.config.config_loader import config_loader

def test_siliconflow_api():
    """测试硅基流动API连接"""
    print("正在测试硅基流动API连接...")
    
    try:
        # 检查环境变量
        api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            print("错误: SILICONFLOW_API_KEY环境变量未设置")
            return False
        
        # 创建LLM实例
        print("正在创建硅基流动LLM实例...")
        llm = LLMFactory.create_llm(provider="siliconflow")
        
        # 发送测试消息
        print("正在发送测试消息...")
        response = llm.invoke("你好，请简单介绍一下你自己。")
        
        print("测试成功!")
        print(f"响应内容: {response.content}")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_siliconflow_api()
    sys.exit(0 if success else 1)