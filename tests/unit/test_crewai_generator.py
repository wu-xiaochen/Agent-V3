#!/usr/bin/env python3
"""
测试CrewAI生成器工具
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.crewai_generator import CrewAIGeneratorTool

def test_crewai_generator_tool():
    """测试CrewAI生成器工具"""
    print("测试CrewAI生成器工具...")
    
    # 直接创建工具实例
    try:
        crewai_tool = CrewAIGeneratorTool()
        print(f"成功创建CrewAI生成器工具")
        print(f"工具名称: {crewai_tool.name}")
        print(f"工具描述: {crewai_tool.description}")
        
        # 测试工具功能
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
    success = test_crewai_generator_tool()
    sys.exit(0 if success else 1)