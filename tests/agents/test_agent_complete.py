#!/usr/bin/env python3
"""
Agent完整功能测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent

def test_agent_complete_functionality():
    """测试Agent完整功能"""
    print("=== Agent完整功能测试 ===\n")
    
    # 创建Agent实例
    agent = UnifiedAgent()
    
    # 检查工具列表
    tools = agent.tools
    tool_names = [tool.name for tool in tools]
    print(f"Agent加载的工具: {tool_names}\n")
    
    # 测试用例
    test_cases = [
        {
            "query": "计算123.45 * 67.89的结果",
            "expected_tool": "calculator",
            "description": "数学计算测试"
        },
        {
            "query": "搜索最新的供应链管理技术趋势",
            "expected_tool": "search",
            "description": "信息搜索测试"
        },
        {
            "query": "现在是什么时间？",
            "expected_tool": "time",
            "description": "时间查询测试"
        },
        {
            "query": "解释什么是牛鞭效应以及如何应对",
            "expected_tool": "search",
            "description": "知识查询测试"
        },
        {
            "query": "计算(100+50)*2-30的结果",
            "expected_tool": "calculator",
            "description": "复杂表达式计算测试"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== 测试 {i}: {test_case['description']} ===")
        print(f"查询: {test_case['query']}")
        print("-" * 50)
        
        response = agent.run(test_case['query'])
        
        # 检查工具使用情况
        metadata = response.get('metadata', {})
        tools_used = metadata.get('tools_used', [])
        
        # 判断测试结果
        if test_case['expected_tool'] in tools_used:
            result = "✅ 通过"
            print(f"结果: {result} - 预期工具 '{test_case['expected_tool']}' 已被使用")
        else:
            result = "❌ 失败"
            print(f"结果: {result} - 预期工具 '{test_case['expected_tool']}' 未被使用，实际使用: {tools_used}")
        
        # 打印响应摘要
        response_text = response.get('response', '')
        if len(response_text) > 100:
            summary = response_text[:100] + "..."
        else:
            summary = response_text
        print(f"响应摘要: {summary}\n")
        
        results.append({
            "test": test_case['description'],
            "result": result,
            "expected_tool": test_case['expected_tool'],
            "used_tools": tools_used
        })
    
    # 测试总结
    print("=" * 60)
    print("测试总结:")
    passed = sum(1 for r in results if "✅" in r['result'])
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！Agent功能正常。")
    else:
        print("⚠️ 部分测试失败，请检查配置和实现。")
    
    return results

if __name__ == "__main__":
    test_agent_complete_functionality()