#!/usr/bin/env python3
"""
测试硅基流动LLM配置
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.infrastructure.llm.llm_factory import LLMFactory

def test_siliconflow():
    """测试硅基流动LLM"""
    try:
        # 设置环境变量
        os.environ["SILICONFLOW_API_KEY"] = "sk-zueyelhrtzsngjdnqfnwfbsboockestuzwwhujpqrjmjmxyy"
        os.environ["PINECONE_API_KEY"] = "dummy-key"  # 添加虚拟的PINECONE_API_KEY以避免错误
        os.environ["PINECONE_ENVIRONMENT"] = "dummy-env"  # 添加虚拟的PINECONE_ENVIRONMENT以避免错误
        
        # 创建硅基流动LLM实例
        llm = LLMFactory.create_llm(provider="siliconflow")
        
        # 测试简单查询
        prompt = "你好，请简单介绍一下你自己。"
        print(f"发送提示: {prompt}")
        print("等待响应...")
        
        # 获取响应
        response = llm.invoke(prompt)
        print(f"响应内容: {response.content}")
        
        print("\n✅ 硅基流动LLM配置测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 硅基流动LLM配置测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试硅基流动LLM配置...")
    success = test_siliconflow()
    sys.exit(0 if success else 1)