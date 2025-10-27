#!/usr/bin/env python3
"""
Agent交互式测试
允许用户输入查询并测试Agent的响应
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent

def interactive_agent_test():
    """交互式Agent测试"""
    print("=== Agent交互式测试 ===")
    print("输入查询来测试Agent的功能，输入'quit'退出程序")
    print("=" * 60)
    
    # 创建Agent实例
    agent = UnifiedAgent()
    
    # 检查工具列表
    tools = agent.tools
    tool_names = [tool.name for tool in tools]
    print(f"Agent加载的工具: {tool_names}")
    print("=" * 60)
    
    while True:
        try:
            # 获取用户输入
            query = input("\n请输入查询: ")
            
            # 检查是否退出
            if query.lower() in ['quit', 'exit', 'q']:
                print("退出测试程序。")
                break
            
            if not query:
                print("请输入有效的查询。")
                continue
            
            # 运行Agent
            print("\n处理中...")
            response = agent.run(query)
            
            # 显示响应
            print("\n" + "=" * 60)
            print("Agent响应:")
            print(response.get('response', ''))
            
            # 显示工具使用情况
            metadata = response.get('metadata', {})
            tools_used = metadata.get('tools_used', [])
            print(f"\n使用的工具: {tools_used}")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断。")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")

if __name__ == "__main__":
    interactive_agent_test()