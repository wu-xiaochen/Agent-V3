#!/usr/bin/env python3
"""
Agent功能全面测试脚本
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent

def test_agent_functions():
    """测试Agent的各种功能"""
    print("=== Agent功能全面测试 ===\n")
    
    # 创建Agent实例
    agent = UnifiedAgent()
    
    # 测试用例列表
    test_cases = [
        {
            "name": "搜索功能测试",
            "query": "搜索最新的供应链管理技术趋势",
            "expected_tool": "search"
        },
        {
            "name": "数学计算测试",
            "query": "计算 (123 + 456) * 2 / 3",
            "expected_tool": "calculator"
        },
        {
            "name": "供应链知识测试",
            "query": "什么是供应链管理中的牛鞭效应？",
            "expected_tool": None
        },
        {
            "name": "时间查询测试",
            "query": "现在是什么时间？",
            "expected_tool": "time"
        }
    ]
    
    # 执行测试用例
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== 测试 {i}: {test_case['name']} ===")
        print(f"查询: {test_case['query']}")
        print("-" * 50)
        
        # 运行Agent
        response = agent.run(test_case['query'])
        
        # 打印响应摘要
        response_text = response['response']
        if len(response_text) > 200:
            response_text = response_text[:200] + "..."
        print(f"响应摘要: {response_text}")
        
        # 检查工具使用情况
        tools_used = response['metadata'].get('tools_used', [])
        print(f"使用的工具: {tools_used}")
        
        # 验证预期工具是否被使用
        if test_case['expected_tool']:
            if test_case['expected_tool'] in tools_used:
                print(f"✅ 预期工具 '{test_case['expected_tool']}' 已被使用")
            else:
                print(f"❌ 预期工具 '{test_case['expected_tool']}' 未被使用")
        else:
            print("✅ 无预期工具要求")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    test_agent_functions()