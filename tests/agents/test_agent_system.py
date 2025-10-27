#!/usr/bin/env python3
"""
测试智能体系统使用硅基流动API
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.agents.unified.unified_agent import UnifiedAgent


def test_agent():
    """测试智能体系统"""
    print("=== 测试智能体系统 ===")
    
    # 创建智能体
    agent = UnifiedAgent()
    
    # 测试问题列表
    test_queries = [
        "你好，请介绍一下你自己",
        "请解释什么是人工智能",
        "请列出Python的三个主要特点"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试问题 {i}: {query} ---")
        
        try:
            # 流式输出
            print("智能体响应: ", end="")
            full_response = ""
            last_metadata = None
            
            for chunk in agent.stream(query):
                if "response" in chunk:
                    print(chunk["response"], end='', flush=True)
                    full_response += chunk["response"]
                if "metadata" in chunk and not chunk["metadata"].get("is_intermediate_step", False):
                    last_metadata = chunk["metadata"]
            
            print("\n")
            
            # 显示元数据
            if last_metadata:
                print("响应元数据:")
                print(f"  - 使用的工具: {last_metadata.get('tools_used', [])}")
                print(f"  - 智能体类型: {last_metadata.get('agent_type', 'unknown')}")
                print(f"  - 输出格式: {last_metadata.get('output_format', 'normal')}")
                print(f"  - 会话ID: {last_metadata.get('session_id', 'unknown')}")
                print(f"  - 是否有记忆: {last_metadata.get('has_memory', False)}")
                print(f"  - 记忆类型: {last_metadata.get('memory_type', 'in_memory')}")
            else:
                print("未获取到元数据")
            
        except Exception as e:
            print(f"\n错误: {str(e)}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_agent()