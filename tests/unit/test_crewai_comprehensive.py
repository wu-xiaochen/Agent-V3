#!/usr/bin/env python3
"""
测试CrewAI生成器工具的全面功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.crewai_generator import CrewAIGeneratorTool

def test_comprehensive_process():
    """测试包含多个角色的业务流程"""
    print("测试包含多个角色的业务流程...")
    
    # 创建工具实例
    tool = CrewAIGeneratorTool()
    
    # 测试包含多个关键词的业务流程
    process = "创建一个完整的供应链优化团队，负责分析库存数据、规划物流策略、协调供应商关系、执行优化方案并审查实施效果"
    
    print(f"业务流程: {process}")
    
    # 测试工具功能
    try:
        result = tool._run(process)
        
        print(f"\n生成的配置:")
        print(f"- 团队名称: {result.get('name', 'N/A')}")
        print(f"- 团队描述: {result.get('description', 'N/A')}")
        print(f"- 智能体数量: {len(result.get('agents', []))}")
        print(f"- 任务数量: {len(result.get('tasks', []))}")
        
        print("\n智能体列表:")
        for i, agent in enumerate(result.get('agents', []), 1):
            print(f"  {i}. {agent.get('name', 'N/A')} - {agent.get('role', 'N/A')}")
        
        print("\n任务列表:")
        for i, task in enumerate(result.get('tasks', []), 1):
            print(f"  {i}. {task.get('name', 'N/A')} - {task.get('description', 'N/A')}")
        
        # 检查结果中是否包含关键信息
        if isinstance(result, dict):
            if "agents" in result and "tasks" in result:
                print("\n✓ 配置包含必要的agents和tasks字段")
                if len(result['agents']) > 1 and len(result['tasks']) > 1:
                    print("✓ 生成的团队包含多个智能体和任务")
                    return True
                else:
                    print("⚠ 生成的团队只包含单个智能体和任务")
                    return False
            else:
                print("\n✗ 配置缺少必要的agents或tasks字段")
                return False
        else:
            print(f"\n✗ 未知的结果类型 {type(result)}")
            return False
            
    except Exception as e:
        print(f"工具执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_process():
    """测试简单业务流程"""
    print("\n\n测试简单业务流程...")
    
    # 创建工具实例
    tool = CrewAIGeneratorTool()
    
    # 测试简单的业务流程
    process = "分析库存数据"
    
    print(f"业务流程: {process}")
    
    # 测试工具功能
    try:
        result = tool._run(process)
        
        print(f"\n生成的配置:")
        print(f"- 团队名称: {result.get('name', 'N/A')}")
        print(f"- 智能体数量: {len(result.get('agents', []))}")
        print(f"- 任务数量: {len(result.get('tasks', []))}")
        
        # 检查结果中是否包含关键信息
        if isinstance(result, dict):
            if "agents" in result and "tasks" in result:
                print("\n✓ 配置包含必要的agents和tasks字段")
                return True
            else:
                print("\n✗ 配置缺少必要的agents或tasks字段")
                return False
        else:
            print(f"\n✗ 未知的结果类型 {type(result)}")
            return False
            
    except Exception as e:
        print(f"工具执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("CrewAI生成器工具全面功能测试")
    print("=" * 80)
    
    # 测试包含多个角色的业务流程
    success1 = test_comprehensive_process()
    
    # 测试简单业务流程
    success2 = test_simple_process()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("所有测试成功!")
    else:
        print("部分测试失败!")
    print("=" * 80)