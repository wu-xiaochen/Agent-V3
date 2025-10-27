#!/usr/bin/env python3
"""
测试CrewAI生成器工具的注册和功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.shared.tools import get_tools

def test_crewai_generator_registration():
    """测试CrewAI生成器工具是否正确注册"""
    print("测试CrewAI生成器工具注册...")
    
    # 获取包含CrewAI生成器的工具列表
    tools = get_tools(["crewai_generator"])
    
    if not tools:
        print("错误: 没有获取到任何工具")
        return False
    
    print(f"获取到 {len(tools)} 个工具")
    
    # 检查第一个工具
    tool = tools[0]
    print(f"工具类型: {type(tool)}")
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
    
    # 测试工具功能
    print("\n测试工具功能...")
    try:
        process = "创建一个供应链优化团队，负责分析库存数据、预测需求、优化物流路径"
        result = tool._run(process)
        
        print("工具执行成功!")
        print(f"生成的配置长度: {len(result)} 字符")
        
        # 检查结果中是否包含关键信息
        if isinstance(result, dict):
            if "agents" in result and "tasks" in result:
                print("配置包含必要的agents和tasks字段")
                print(f"生成的团队包含 {len(result['agents'])} 个智能体和 {len(result['tasks'])} 个任务")
                return True
            else:
                print("警告: 配置可能缺少必要字段")
                return False
        elif isinstance(result, str):
            if "agents" in result and "tasks" in result:
                print("配置包含必要的agents和tasks字段")
                return True
            else:
                print("警告: 配置可能缺少必要字段")
                return False
        else:
            print(f"警告: 未知的结果类型 {type(result)}")
            return False
            
    except Exception as e:
        print(f"工具执行失败: {str(e)}")
        return False

def test_all_tools():
    """测试所有工具的注册情况"""
    print("\n测试所有工具的注册情况...")
    
    # 获取所有工具
    tools = get_tools()
    
    print(f"总共获取到 {len(tools)} 个工具:")
    
    for i, tool in enumerate(tools, 1):
        print(f"\n工具 {i}:")
        print(f"  类型: {type(tool)}")
        print(f"  名称: {tool.name}")
        print(f"  描述: {tool.description}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("CrewAI生成器工具注册测试")
    print("=" * 60)
    
    # 测试CrewAI生成器工具注册
    success = test_crewai_generator_registration()
    
    # 测试所有工具
    test_all_tools()
    
    print("\n" + "=" * 60)
    if success:
        print("测试成功!")
    else:
        print("测试失败!")
    print("=" * 60)