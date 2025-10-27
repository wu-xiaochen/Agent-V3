#!/usr/bin/env python3
"""
测试Agent工具加载
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent
from src.agents.shared.tools import get_tools

def test_agent_tools():
    """测试Agent工具加载"""
    print("=== 测试Agent工具加载 ===")
    
    # 检查可用工具
    tools = get_tools()
    print(f"可用工具数量: {len(tools)}")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    print("\n=== 测试Agent工具配置 ===")
    
    # 创建Agent实例
    agent = UnifiedAgent()
    
    # 检查Agent加载的工具
    print(f"Agent加载的工具数量: {len(agent.tools)}")
    for tool in agent.tools:
        print(f"- {tool.name}: {tool.description}")
    
    # 检查搜索工具是否在列表中
    search_tool_names = [tool.name for tool in agent.tools]
    if "search" in search_tool_names:
        print("\n✅ 搜索工具已正确加载到Agent")
    else:
        print("\n❌ 搜索工具未加载到Agent")
    
    # 测试直接调用搜索工具
    print("\n=== 测试直接调用搜索工具 ===")
    search_tool = None
    for tool in agent.tools:
        if tool.name == "search":
            search_tool = tool
            break
    
    if search_tool:
        query = "最新的供应链管理技术趋势"
        print(f"查询: {query}")
        result = search_tool._run(query)
        print(f"搜索结果: {result[:200]}...")
        if "搜索" in result and ("结果" in result or "链接" in result):
            print("✅ 搜索工具工作正常")
        else:
            print("❌ 搜索工具可能存在问题")
    else:
        print("❌ 未找到搜索工具")

if __name__ == "__main__":
    test_agent_tools()