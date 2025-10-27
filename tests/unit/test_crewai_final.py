#!/usr/bin/env python3
"""
最终验证CrewAI生成器工具的注册和使用
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.shared.tools import get_tools

def test_crewai_generator_in_system():
    """测试CrewAI生成器工具是否正确注册到系统中"""
    print("测试CrewAI生成器工具在系统中的注册和使用...")
    
    # 获取所有工具，包括CrewAI生成器工具
    all_tools = get_tools(["search", "calculator", "time", "crewai_generator"])
    
    # 查找CrewAI生成器工具
    crewai_tool = None
    for tool in all_tools:
        if hasattr(tool, 'name') and tool.name == 'crewai_generator':
            crewai_tool = tool
            break
    
    if not crewai_tool:
        print("错误: CrewAI生成器工具未在系统中注册")
        return False
    
    print(f"✓ 找到CrewAI生成器工具: {type(crewai_tool)}")
    print(f"  - 工具名称: {crewai_tool.name}")
    print(f"  - 工具描述: {crewai_tool.description}")
    
    # 测试工具功能
    print("\n测试工具功能...")
    try:
        process = "创建一个完整的供应链优化团队，负责分析库存数据、规划物流策略、协调供应商关系、执行优化方案并审查实施效果"
        result = crewai_tool._run(process)
        
        print(f"✓ 工具执行成功!")
        print(f"  - 生成的团队包含 {len(result.get('agents', []))} 个智能体")
        print(f"  - 生成的团队包含 {len(result.get('tasks', []))} 个任务")
        
        # 验证结果结构
        if isinstance(result, dict) and "agents" in result and "tasks" in result:
            print("✓ 生成的配置结构正确")
            return True
        else:
            print("✗ 生成的配置结构不正确")
            return False
            
    except Exception as e:
        print(f"✗ 工具执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_crewai_generator_directly():
    """直接测试CrewAI生成器工具"""
    print("\n\n直接测试CrewAI生成器工具...")
    
    # 直接导入并创建工具实例
    from src.tools.crewai_generator import CrewAIGeneratorTool
    
    tool = CrewAIGeneratorTool()
    
    print(f"✓ 创建工具实例: {type(tool)}")
    print(f"  - 工具名称: {tool.name}")
    print(f"  - 工具描述: {tool.description}")
    
    # 测试工具功能
    print("\n测试工具功能...")
    try:
        process = "分析库存数据并预测需求"
        result = tool._run(process)
        
        print(f"✓ 工具执行成功!")
        print(f"  - 生成的团队名称: {result.get('name', 'N/A')}")
        print(f"  - 生成的团队包含 {len(result.get('agents', []))} 个智能体")
        print(f"  - 生成的团队包含 {len(result.get('tasks', []))} 个任务")
        
        # 验证结果结构
        if isinstance(result, dict) and "agents" in result and "tasks" in result:
            print("✓ 生成的配置结构正确")
            return True
        else:
            print("✗ 生成的配置结构不正确")
            return False
            
    except Exception as e:
        print(f"✗ 工具执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_all_tools():
    """测试所有工具的注册情况"""
    print("\n\n测试所有工具的注册情况...")
    
    # 获取所有工具，包括CrewAI生成器工具
    tools = get_tools(["search", "calculator", "time", "crewai_generator"])
    
    print(f"✓ 系统中共有 {len(tools)} 个工具:")
    
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool.name} - {tool.description}")
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("CrewAI生成器工具最终验证测试")
    print("=" * 80)
    
    # 测试CrewAI生成器工具在系统中的注册和使用
    success1 = test_crewai_generator_in_system()
    
    # 直接测试CrewAI生成器工具
    success2 = test_crewai_generator_directly()
    
    # 测试所有工具的注册情况
    success3 = test_all_tools()
    
    print("\n" + "=" * 80)
    if success1 and success2 and success3:
        print("✓ 所有测试成功! CrewAI生成器工具已正确注册并可以使用!")
    else:
        print("✗ 部分测试失败!")
    print("=" * 80)