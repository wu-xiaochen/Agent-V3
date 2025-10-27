#!/usr/bin/env python3
"""
测试Agent时间工具使用情况
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent

def test_agent_time_tool():
    """测试Agent使用时间工具"""
    print("=== 测试Agent时间工具使用 ===")
    
    # 创建Agent实例
    agent = UnifiedAgent()
    
    # 检查工具列表
    tools = agent.tools
    print(f"Agent加载的工具数量: {len(tools)}")
    tool_names = [tool.name for tool in tools]
    print(f"工具名称列表: {tool_names}")
    
    # 检查时间工具是否在列表中
    if "time" in tool_names:
        print("✅ 时间工具已加载到Agent")
        
        # 测试时间查询
        query = "现在是什么时间？"
        print(f"\n查询: {query}")
        print("-" * 50)
        
        response = agent.run(query)
        
        # 检查是否使用了时间工具
        metadata = response.get('metadata', {})
        tools_used = metadata.get('tools_used', [])
        print(f"\n使用的工具: {tools_used}")
        
        if 'time' in tools_used:
            print("✅ 时间工具已被使用")
        else:
            print("❌ 时间工具未被使用")
            print("可能原因: Agent认为不需要使用工具就能回答问题")
    else:
        print("❌ 时间工具未加载到Agent")
    
    return response

if __name__ == "__main__":
    test_agent_time_tool()