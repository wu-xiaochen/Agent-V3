#!/usr/bin/env python3
"""
测试SerperAPI搜索功能
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.shared.tools import SearchTool
from src.agents.shared.tools import config_loader
import requests
import json

def test_search_tool():
    """测试搜索工具"""
    print("\n=== 测试搜索工具 ===")
    
    # 创建搜索工具实例
    search_tool = SearchTool()
    
    # 直接使用SearchTool中的config_loader
    from src.agents.shared.tools import config_loader
    services_config = config_loader.get_services_config()
    
    print(f"完整服务配置: {json.dumps(services_config, indent=2, ensure_ascii=False)}")
    
    # 获取搜索配置
    print(f"services_config type: {type(services_config)}")
    print(f"services_config keys: {services_config.keys() if isinstance(services_config, dict) else 'Not a dict'}")
    
    # 检查是否有services键
    if isinstance(services_config, dict) and "services" in services_config:
        services_data = services_config["services"]
        print(f"services_data type: {type(services_data)}")
        print(f"services_data keys: {services_data.keys() if isinstance(services_data, dict) else 'Not a dict'}")
        
        if isinstance(services_data, dict) and "tools" in services_data:
            tools_config = services_data["tools"]
            print(f"tools配置: {json.dumps(tools_config, indent=2, ensure_ascii=False)}")
            
            if isinstance(tools_config, dict) and "search" in tools_config:
                search_config = tools_config["search"]
                print(f"search配置: {json.dumps(search_config, indent=2, ensure_ascii=False)}")
            else:
                print("search配置不存在或为空")
                search_config = {}
        else:
            print("tools配置不存在或为空")
            search_config = {}
    else:
        print("services配置不存在或为空")
        search_config = {}
    
    # 获取搜索提供商和API密钥
    provider = search_config.get("provider", "duckduckgo")
    serper_config = search_config.get("serper", {})
    serpapi_config = search_config.get("serpapi", {})
    
    print(f"搜索提供商: {provider}")
    print(f"Serper配置: {json.dumps(serper_config, indent=2, ensure_ascii=False)}")
    print(f"SerpApi配置: {json.dumps(serpapi_config, indent=2, ensure_ascii=False)}")
    
    # 测试查询
    test_queries = [
        "供应链管理最佳实践",
    ]
    
    for query in test_queries:
        print(f"\n搜索查询: {query}")
        print("-" * 50)
        
        try:
            # 执行搜索
            results = search_tool.run(query)
            
            # 打印结果
            print("\n工具返回结果:")
            print(results)
            
        except Exception as e:
            print(f"搜索失败: {str(e)}")
    
    print("\n测试完成!")

def test_serpapi_direct():
    """直接测试SerpApi"""
    print("\n=== 直接测试SerpApi ===")
    
    # 直接使用SearchTool中的config_loader
    from src.agents.shared.tools import config_loader
    services_config = config_loader.get_services_config()
    services_data = services_config.get("services", {})
    search_config = services_data.get("tools", {}).get("search", {})
    serpapi_config = search_config.get("serpapi", {})
    
    print(f"SerpApi配置: {json.dumps(serpapi_config, indent=2, ensure_ascii=False)}")
    
    api_key = serpapi_config.get("api_key")
    print(f"API密钥: {api_key[:10]}..." if api_key and len(api_key) > 10 else f"API密钥: {api_key}")
    
    if not api_key:
        print("未配置SerpApi API密钥")
        return
    
    # 测试搜索
    query = "供应链管理最佳实践"
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": 5
    }
    
    print(f"搜索查询: {query}")
    print("-" * 50)
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            if "organic_results" in data and data["organic_results"]:
                print(f"找到 {len(data['organic_results'])} 个结果:")
                for i, result in enumerate(data["organic_results"], 1):
                    print(f"{i}. {result['title']}")
                    print(f"   {result.get('snippet', '无描述')}")
                    print(f"   链接: {result['link']}\n")
            else:
                print("没有找到搜索结果")
        else:
            error = data.get('error', '未知错误')
            print(f"搜索失败: {error}")
    except Exception as e:
        print(f"搜索出错: {str(e)}")

if __name__ == "__main__":
    test_search_tool()
    test_serpapi_direct()