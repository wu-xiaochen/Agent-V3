#!/usr/bin/env python3
"""
测试非交互式智能体系统
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent

def test_agent_with_query(query):
    """测试智能体处理查询"""
    print(f"正在测试查询: {query}")
    
    try:
        # 创建智能体实例
        print("正在创建智能体实例...")
        agent = UnifiedAgent()
        
        # 处理查询
        print("正在处理查询...")
        response = agent.run(query)
        
        print("\n=== 智能体响应 ===")
        print(response)
        print("==================")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 测试查询列表
    test_queries = [
        "你好，请简单介绍一下你自己。",
        "什么是供应链管理？",
        "请解释一下什么是区块链技术。"
    ]
    
    for query in test_queries:
        print("\n" + "="*50)
        success = test_agent_with_query(query)
        if not success:
            print(f"查询 '{query}' 测试失败")
            break