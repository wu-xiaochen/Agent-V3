#!/usr/bin/env python3
"""
SerpApi搜索工具测试脚本
"""

import os
import sys
import json

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.shared.tools import SearchTool, config_loader

def test_serpapi_search():
    """测试SerpApi搜索功能"""
    print("=== 测试SerpApi搜索功能 ===")
    
    # 获取搜索配置
    services_config = config_loader.get_services_config()
    services_data = services_config.get("services", {})
    search_config = services_data.get("tools", {}).get("search", {})
    
    print(f"搜索提供商: {search_config.get('provider')}")
    print(f"最大结果数: {search_config.get('max_results')}")
    
    # 创建搜索工具实例
    search_tool = SearchTool()
    
    # 测试搜索
    query = "供应链管理最佳实践"
    print(f"\n搜索查询: {query}")
    print("-" * 50)
    
    try:
        # 使用_run方法进行搜索
        result = search_tool._run(query)
        print(f"搜索结果:\n{result}")
        
        # 检查结果是否包含有效内容
        if result and "没有找到相关结果" not in result:
            print("\n✅ 搜索成功！")
        else:
            print("\n❌ 搜索失败或无结果")
            
    except Exception as e:
        print(f"\n❌ 搜索出错: {str(e)}")

def test_different_queries():
    """测试不同的搜索查询"""
    print("\n\n=== 测试不同查询 ===")
    
    search_tool = SearchTool()
    queries = [
        "Python编程最佳实践",
        "人工智能发展趋势",
        "最新科技新闻"
    ]
    
    for query in queries:
        print(f"\n搜索: {query}")
        print("-" * 30)
        try:
            result = search_tool._run(query)
            # 只显示前200个字符
            print(result[:200] + "..." if len(result) > 200 else result)
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_serpapi_search()
    test_different_queries()