#!/usr/bin/env python3
"""
使用CrewAI生成器工具的示例
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.shared.tools import get_tools

def example_usage():
    """展示如何使用CrewAI生成器工具"""
    print("=" * 80)
    print("CrewAI生成器工具使用示例")
    print("=" * 80)
    
    # 获取工具列表，包括CrewAI生成器工具
    tools = get_tools(["crewai_generator"])
    
    # 获取CrewAI生成器工具
    crewai_tool = tools[0]
    
    print(f"工具名称: {crewai_tool.name}")
    print(f"工具描述: {crewai_tool.description}")
    print()
    
    # 示例1: 简单业务流程
    print("示例1: 简单业务流程")
    print("-" * 40)
    process1 = "分析库存数据"
    result1 = crewai_tool._run(process1)
    
    print(f"业务流程: {process1}")
    print(f"生成的团队名称: {result1.get('name', 'N/A')}")
    print(f"智能体数量: {len(result1.get('agents', []))}")
    print(f"任务数量: {len(result1.get('tasks', []))}")
    print()
    
    # 示例2: 复杂业务流程
    print("示例2: 复杂业务流程")
    print("-" * 40)
    process2 = "创建一个完整的供应链优化团队，负责分析库存数据、规划物流策略、协调供应商关系、执行优化方案并审查实施效果"
    result2 = crewai_tool._run(process2)
    
    print(f"业务流程: {process2}")
    print(f"生成的团队名称: {result2.get('name', 'N/A')}")
    print(f"智能体数量: {len(result2.get('agents', []))}")
    print(f"任务数量: {len(result2.get('tasks', []))}")
    
    # 显示生成的智能体
    print("\n生成的智能体:")
    for i, agent in enumerate(result2.get('agents', []), 1):
        print(f"  {i}. {agent.get('name', 'N/A')} - {agent.get('description', 'N/A')}")
    
    # 显示生成的任务
    print("\n生成的任务:")
    for i, task in enumerate(result2.get('tasks', []), 1):
        print(f"  {i}. {task.get('name', 'N/A')} - {task.get('description', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("示例完成!")
    print("=" * 80)

if __name__ == "__main__":
    example_usage()