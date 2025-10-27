#!/usr/bin/env python3
"""
测试CrewAI运行时工具注册
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.shared.tools import get_tools


def test_crewai_runtime_tool():
    """测试CrewAI运行时工具是否正确注册"""
    print("测试CrewAI运行时工具注册...")
    
    # 获取所有工具
    tools = get_tools(["crewai_runtime"])
    
    # 检查工具是否成功加载
    if not tools:
        print("❌ 失败: 无法加载crewai_runtime工具")
        return False
    
    if len(tools) != 1:
        print(f"❌ 失败: 期望1个工具，实际加载了{len(tools)}个工具")
        return False
    
    tool = tools[0]
    
    # 检查工具名称和描述
    if tool.name != "crewai_runtime":
        print(f"❌ 失败: 工具名称不正确，期望'crewai_runtime'，实际'{tool.name}'")
        return False
    
    if "运行CrewAI团队" not in tool.description:
        print(f"❌ 失败: 工具描述不正确，期望包含'运行CrewAI团队'，实际'{tool.description}'")
        return False
    
    print("✅ 成功: CrewAI运行时工具正确注册")
    print(f"   工具名称: {tool.name}")
    print(f"   工具描述: {tool.description}")
    
    return True


def test_supply_chain_agent_tools():
    """测试供应链智能体工具列表是否包含CrewAI运行时工具"""
    print("\n测试供应链智能体工具列表...")
    
    # 获取供应链智能体的所有工具
    from src.config.config_loader import config_loader
    agent_config = config_loader.get_specific_agent_config("supply_chain_agent")
    supply_chain_tools = agent_config.get("tools", [])
    
    # 获取所有工具实例
    tools = get_tools(supply_chain_tools)
    
    # 检查CrewAI运行时工具是否在列表中
    crewai_runtime_tool = None
    for tool in tools:
        if tool.name == "crewai_runtime":
            crewai_runtime_tool = tool
            break
    
    if not crewai_runtime_tool:
        print("❌ 失败: 供应链智能体工具列表中未找到crewai_runtime工具")
        print(f"   供应链智能体工具配置: {supply_chain_tools}")
        return False
    
    print("✅ 成功: 供应链智能体工具列表包含CrewAI运行时工具")
    
    # 打印所有工具名称
    tool_names = [tool.name for tool in tools]
    print(f"   所有工具: {', '.join(tool_names)}")
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("CrewAI运行时工具注册测试")
    print("=" * 50)
    
    # 运行测试
    test1_passed = test_crewai_runtime_tool()
    test2_passed = test_supply_chain_agent_tools()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("✅ 所有测试通过")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)