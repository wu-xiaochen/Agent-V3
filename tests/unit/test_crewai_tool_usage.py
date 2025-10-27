#!/usr/bin/env python3
"""
测试智能体是否能够调用CrewAI生成器工具
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.unified.unified_agent import UnifiedAgent

def test_crewai_tool_usage():
    """测试智能体是否能够调用CrewAI生成器工具"""
    print("=== 测试智能体调用CrewAI生成器工具 ===")
    
    # 创建智能体实例
    agent = UnifiedAgent()
    
    # 检查工具列表
    tool_names = [tool.name for tool in agent.tools]
    print(f"智能体可用工具: {tool_names}")
    
    if "crewai_generator" not in tool_names:
        print("错误: crewai_generator工具未加载到智能体中")
        return False
    
    print("成功: crewai_generator工具已加载到智能体中")
    
    # 测试工具调用
    test_query = "请使用crewai_generator工具为生物质锅炉智能寻源生成一个CrewAI团队配置"
    print(f"\n测试查询: {test_query}")
    print("=" * 50)
    
    try:
        # 运行智能体
        response = agent.run(test_query)
        print("\n智能体响应:")
        print(response.get("response", "无响应"))
        
        # 检查响应中是否包含CrewAI配置
        response_text = response.get("response", "")
        # 检查多种可能的CrewAI配置标识
        crewai_indicators = [
            "团队成员角色", "agents", "团队成员配置",
            "工作任务流程", "tasks", "任务流程",
            "团队概述", "团队名称", "工作流程"
        ]
        
        has_agents = any(indicator in response_text for indicator in ["团队成员角色", "agents", "团队成员配置", "团队概述", "团队名称"])
        has_tasks = any(indicator in response_text for indicator in ["工作任务流程", "tasks", "任务流程", "工作流程"])
        
        if has_agents and has_tasks:
            print("\n成功: 智能体成功调用了crewai_generator工具并生成了配置")
            return True
        else:
            print("\n警告: 智能体响应中未检测到CrewAI配置")
            print(f"检测到agents相关关键词: {has_agents}")
            print(f"检测到tasks相关关键词: {has_tasks}")
            return False
    except Exception as e:
        print(f"\n错误: 智能体运行出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_crewai_tool_usage()
    if success:
        print("\n测试成功! 智能体能够正确调用CrewAI生成器工具")
    else:
        print("\n测试失败! 智能体无法调用CrewAI生成器工具")