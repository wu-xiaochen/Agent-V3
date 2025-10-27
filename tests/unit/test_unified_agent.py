#!/usr/bin/env python3
"""
UnifiedAgent 测试脚本

这个脚本用于测试 UnifiedAgent 的各种功能，确保所有组件正常工作。
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.agents.unified.unified_agent import UnifiedAgent


def test_basic_creation():
    """测试基本创建功能"""
    print("测试基本创建功能...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
        print("✓ 基本创建成功")
        return True
    except Exception as e:
        print(f"✗ 基本创建失败: {e}")
        return False


def test_memory_creation():
    """测试带记忆功能的创建"""
    print("测试带记忆功能的创建...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo', memory=True)
        print("✓ 带记忆功能创建成功")
        return True
    except Exception as e:
        print(f"✗ 带记忆功能创建失败: {e}")
        return False


def test_run_method():
    """测试run方法"""
    print("测试run方法...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
        response = agent.run("说一句简短的话")
        if response and 'response' in response and len(response['response']) > 0:
            print("✓ run方法测试成功")
            return True
        else:
            print("✗ run方法返回空响应")
            return False
    except Exception as e:
        print(f"✗ run方法测试失败: {e}")
        return False


def test_stream_method():
    """测试stream方法"""
    print("测试stream方法...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
        chunks = list(agent.stream("说一个词"))
        if chunks and len(chunks) > 0:
            print("✓ stream方法测试成功")
            return True
        else:
            print("✗ stream方法返回空响应")
            return False
    except Exception as e:
        print(f"✗ stream方法测试失败: {e}")
        return False


def test_chat_method():
    """测试chat方法"""
    print("测试chat方法...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
        response = agent.chat("你好")
        if response and 'response' in response and len(response['response']) > 0:
            print("✓ chat方法测试成功")
            return True
        else:
            print("✗ chat方法返回空响应")
            return False
    except Exception as e:
        print(f"✗ chat方法测试失败: {e}")
        return False


def test_memory_functionality():
    """测试记忆功能"""
    print("测试记忆功能...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo', memory=True)
        # 第一轮对话
        response1 = agent.chat("我的名字是测试用户", session_id="test_memory")
        # 第二轮对话，测试记忆
        response2 = agent.chat("我叫什么名字？", session_id="test_memory")
        
        if response2 and 'response' in response2 and "测试用户" in response2['response']:
            print("✓ 记忆功能测试成功")
            return True
        else:
            print("✗ 记忆功能测试失败，智能体未记住用户名字")
            return False
    except Exception as e:
        print(f"✗ 记忆功能测试失败: {e}")
        return False


def test_tool_usage():
    """测试工具使用"""
    print("测试工具使用...")
    try:
        agent = UnifiedAgent(provider='openai', model_name='gpt-3.5-turbo')
        # 测试计算器工具
        response = agent.run("1+1等于几？")
        if response and 'response' in response and "2" in response['response']:
            print("✓ 工具使用测试成功")
            return True
        else:
            print("✗ 工具使用测试失败，未得到正确计算结果")
            return False
    except Exception as e:
        print(f"✗ 工具使用测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("开始运行 UnifiedAgent 测试套件...\n")
    
    tests = [
        test_basic_creation,
        test_memory_creation,
        test_run_method,
        test_stream_method,
        test_chat_method,
        test_memory_functionality,
        test_tool_usage
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！UnifiedAgent 功能正常。")
        return True
    else:
        print("❌ 部分测试失败，请检查相关功能。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)