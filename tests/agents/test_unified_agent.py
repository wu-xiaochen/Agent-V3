#!/usr/bin/env python3
"""
统一智能体功能测试脚本
测试所有工具是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.agents.unified.unified_agent import UnifiedAgent

def test_time_tool():
    """测试时间工具"""
    print("=== 测试时间工具 ===")
    agent = UnifiedAgent()
    result = agent.run('请告诉我当前时间')
    print(f"时间工具测试结果: {result['response']}")
    return result

def test_calculator_tool():
    """测试计算器工具"""
    print("\n=== 测试计算器工具 ===")
    agent = UnifiedAgent()
    result = agent.run('计算 123 * 456')
    print(f"计算器工具测试结果: {result['response']}")
    return result

def test_search_tool():
    """测试搜索工具"""
    print("\n=== 测试搜索工具 ===")
    agent = UnifiedAgent()
    result = agent.run('搜索关于人工智能的最新发展')
    print(f"搜索工具测试结果: {result['response'][:200]}...")
    return result

def main():
    """主测试函数"""
    print("开始测试统一智能体的所有工具功能...")
    
    try:
        # 测试时间工具
        test_time_tool()
        
        # 测试计算器工具
        test_calculator_tool()
        
        # 测试搜索工具
        test_search_tool()
        
        print("\n✅ 所有测试完成！统一智能体功能正常。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()