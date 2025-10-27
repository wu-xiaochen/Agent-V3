#!/usr/bin/env python3
"""
Agent搜索功能完整测试脚本
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent

def test_agent_search():
    """测试Agent的搜索功能"""
    print("=== 测试Agent搜索功能 ===")
    
    # 创建Agent实例
    agent = UnifiedAgent()
    
    # 测试查询
    query = "搜索最新的供应链管理技术趋势"
    print(f"查询: {query}")
    print("-" * 50)
    
    # 运行Agent
    response = agent.run(query)
    
    # 打印响应
    print(f"响应:\n{response['response']}")
    
    # 打印元数据
    print("\n=== 元数据 ===")
    for key, value in response['metadata'].items():
        print(f"{key}: {value}")
    
    # 检查是否使用了搜索工具
    if 'search' in response['metadata'].get('tools_used', []):
        print("\n✅ 搜索工具已成功使用")
    else:
        print("\n❌ 搜索工具未被使用")

if __name__ == "__main__":
    test_agent_search()