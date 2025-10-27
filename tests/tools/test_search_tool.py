#!/usr/bin/env python3
"""
直接测试搜索工具
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.shared.tools import SearchTool

def test_search_tool():
    """测试搜索工具"""
    print("=== 测试搜索工具 ===")
    
    # 创建搜索工具实例
    search_tool = SearchTool()
    
    # 测试查询
    query = "最新的供应链管理技术趋势"
    print(f"查询: {query}")
    print("-" * 50)
    
    # 执行搜索
    result = search_tool._run(query)
    
    # 打印结果
    print(f"搜索结果:\n{result}")
    
    # 检查结果是否包含搜索结果
    if "搜索" in result and ("结果" in result or "链接" in result):
        print("\n✅ 搜索工具工作正常")
    else:
        print("\n❌ 搜索工具可能存在问题")

if __name__ == "__main__":
    test_search_tool()