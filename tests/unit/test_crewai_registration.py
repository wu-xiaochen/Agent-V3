#!/usr/bin/env python3
"""
测试CrewAI生成器工具注册
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.shared.tools import get_tools

def test_crewai_generator_registration():
    """测试CrewAI生成器工具是否已正确注册"""
    print("测试CrewAI生成器工具注册...")
    
    # 获取工具列表
    tools = get_tools()
    
    # 检查CrewAI生成器工具是否在列表中
    crewai_tool = None
    for tool in tools:
        if tool.name == "crewai_generator":
            crewai_tool = tool
            break
    
    if not crewai_tool:
        print("错误: CrewAI生成器工具未找到")
        print("可用工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        return False
    
    print(f"找到CrewAI生成器工具: {crewai_tool.name}")
    print(f"工具描述: {crewai_tool.description}")
    
    # 测试工具功能
    try:
        business_process = "分析供应链数据，制定优化计划，并协调各部门执行"
        result = crewai_tool._run(
            business_process=business_process,
            crew_name="测试供应链团队",
            process_type="sequential"
        )
        
        print("\n生成的CrewAI配置:")
        print(f"团队名称: {result.get('name')}")
        print(f"团队描述: {result.get('description')}")
        print(f"智能体数量: {len(result.get('agents', []))}")
        print(f"任务数量: {len(result.get('tasks', []))}")
        
        # 打印智能体信息
        for i, agent in enumerate(result.get('agents', [])):
            print(f"\n智能体 {i+1}:")
            print(f"  名称: {agent.get('name')}")
            print(f"  角色: {agent.get('role')}")
            print(f"  目标: {agent.get('goal')}")
        
        # 打印任务信息
        for i, task in enumerate(result.get('tasks', [])):
            print(f"\n任务 {i+1}:")
            print(f"  名称: {task.get('name')}")
            print(f"  描述: {task.get('description')}")
            print(f"  负责智能体: {task.get('agent')}")
        
        print("\n测试成功!")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crewai_generator_registration()
    sys.exit(0 if success else 1)