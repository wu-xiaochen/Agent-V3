#!/usr/bin/env python3
"""
UnifiedAgent 使用示例

这个脚本展示了如何使用 UnifiedAgent 类进行各种操作，包括：
- 基本对话
- 工具使用
- 流式输出
- 记忆功能
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.unified.unified_agent import UnifiedAgent


def example_basic_chat():
    """基本对话示例"""
    print("=== 基本对话示例 ===")
    agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
    
    response = agent.run("你好，请简单介绍一下自己")
    print(response)
    print()


def example_tool_usage():
    """工具使用示例"""
    print("=== 工具使用示例 ===")
    agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
    
    # 使用时间工具
    print("查询当前时间:")
    response = agent.run("现在几点了？")
    print(response)
    
    # 使用计算器工具
    print("\n进行数学计算:")
    response = agent.run("计算一下 123 乘以 456 等于多少？")
    print(response)
    print()


def example_streaming():
    """流式输出示例"""
    print("=== 流式输出示例 ===")
    agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
    
    print("流式输出:")
    for chunk in agent.stream("请写一首关于春天的短诗"):
        print(chunk, end='', flush=True)
    print()
    print()


def example_memory():
    """记忆功能示例"""
    print("=== 记忆功能示例 ===")
    agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo', memory=True)
    
    # 第一轮对话
    print("第一轮对话:")
    response1 = agent.chat("我喜欢吃苹果", session_id="memory_test")
    print(response1)
    
    # 第二轮对话，测试记忆
    print("\n第二轮对话:")
    response2 = agent.chat("我刚才说我喜欢吃什么？", session_id="memory_test")
    print(response2)
    print()


def main():
    """主函数"""
    print("UnifiedAgent 使用示例\n")
    
    try:
        example_basic_chat()
        example_tool_usage()
        example_streaming()
        example_memory()
        
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()