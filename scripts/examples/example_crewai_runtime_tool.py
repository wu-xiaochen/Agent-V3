#!/usr/bin/env python3
"""
CrewAI运行时工具使用示例
演示如何通过智能体使用CrewAI运行时工具
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.shared.tools import get_tools
from src.tools.crewai_generator import generate_crew_from_process


def example_crewai_runtime_tool():
    """演示CrewAI运行时工具的使用"""
    print("=" * 60)
    print("CrewAI运行时工具使用示例")
    print("=" * 60)
    
    # 1. 生成CrewAI配置
    print("\n1. 生成CrewAI配置...")
    business_process = "分析供应链风险并提出优化方案"
    crew_config = generate_crew_from_process(
        business_process=business_process,
        crew_name="供应链风险分析团队",
        process_type="sequential"
    )
    
    print(f"生成的团队配置: {crew_config['name']}")
    print(f"智能体数量: {len(crew_config['agents'])}")
    print(f"任务数量: {len(crew_config['tasks'])}")
    
    # 2. 获取CrewAI运行时工具
    print("\n2. 获取CrewAI运行时工具...")
    tools = get_tools(["crewai_runtime"])
    crewai_runtime_tool = tools[0]
    
    # 3. 运行CrewAI团队
    print("\n3. 运行CrewAI团队...")
    query = "分析当前全球供应链面临的主要风险，并提出应对策略"
    
    # 将配置转换为JSON字符串
    import json
    config_json = json.dumps(crew_config)
    
    # 运行工具
    result = crewai_runtime_tool._run(
        config=config_json,
        query=query
    )
    
    # 4. 显示结果
    print("\n4. 执行结果:")
    if result.get("success"):
        print("✅ 团队执行成功")
        print(f"结果: {result.get('result', '无结果')}")
    else:
        print("❌ 团队执行失败")
        print(f"错误: {result.get('error', '未知错误')}")
    
    return result.get("success", False)


def example_crewai_runtime_with_file():
    """演示使用配置文件的CrewAI运行时工具"""
    print("\n" + "=" * 60)
    print("使用配置文件的CrewAI运行时工具示例")
    print("=" * 60)
    
    # 1. 生成并保存CrewAI配置
    print("\n1. 生成并保存CrewAI配置...")
    business_process = "优化库存管理流程"
    crew_config = generate_crew_from_process(
        business_process=business_process,
        crew_name="库存优化团队",
        process_type="hierarchical",
        output_file="inventory_optimization_crew.json"
    )
    
    print(f"配置已保存到: inventory_optimization_crew.json")
    
    # 2. 获取CrewAI运行时工具
    print("\n2. 获取CrewAI运行时工具...")
    tools = get_tools(["crewai_runtime"])
    crewai_runtime_tool = tools[0]
    
    # 3. 运行CrewAI团队
    print("\n3. 运行CrewAI团队...")
    query = "分析当前库存管理中的问题，并提出优化方案"
    
    # 使用配置文件路径
    result = crewai_runtime_tool._run(
        config="inventory_optimization_crew.json",
        query=query
    )
    
    # 4. 显示结果
    print("\n4. 执行结果:")
    if result.get("success"):
        print("✅ 团队执行成功")
        print(f"结果: {result.get('result', '无结果')}")
    else:
        print("❌ 团队执行失败")
        print(f"错误: {result.get('error', '未知错误')}")
    
    return result.get("success", False)


if __name__ == "__main__":
    print("开始演示CrewAI运行时工具的使用...")
    
    # 示例1: 直接使用JSON配置
    success1 = example_crewai_runtime_tool()
    
    # 示例2: 使用配置文件
    success2 = example_crewai_runtime_with_file()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ 所有示例执行成功")
        sys.exit(0)
    else:
        print("❌ 部分示例执行失败")
        sys.exit(1)