#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试交互模式修复
"""

import subprocess
import sys
import os

def test_interactive_mode():
    """测试交互模式是否修复了EOFError"""
    print("=== 测试交互模式修复 ===")
    
    # 创建测试输入
    test_input = "你好\n请介绍一下人工智能\nexit\n"
    
    try:
        # 运行交互模式并提供测试输入
        process = subprocess.Popen(
            [sys.executable, "main.py", "--interactive"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # 发送测试输入
        stdout, stderr = process.communicate(input=test_input, timeout=30)
        
        print("标准输出:")
        print(stdout)
        
        if stderr:
            print("标准错误:")
            print(stderr)
        
        # 检查是否有EOFError
        if "EOF when reading a line" in stderr:
            print("❌ 测试失败: 仍然存在EOFError")
            return False
        else:
            print("✅ 测试成功: 没有EOFError")
            return True
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ 测试失败: 超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_single_query_mode():
    """测试单次查询模式"""
    print("\n=== 测试单次查询模式 ===")
    
    try:
        # 运行单次查询模式
        result = subprocess.run(
            [sys.executable, "main.py", "--query", "你好，请简单介绍一下你自己", "--stream"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        print("标准输出:")
        print(result.stdout)
        
        if result.stderr:
            print("标准错误:")
            print(result.stderr)
        
        # 检查是否成功
        if result.returncode == 0:
            print("✅ 测试成功: 单次查询模式正常工作")
            return True
        else:
            print(f"❌ 测试失败: 退出码 {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 测试失败: 超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试交互模式
    interactive_ok = test_interactive_mode()
    
    # 测试单次查询模式
    single_query_ok = test_single_query_mode()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"交互模式: {'✅ 通过' if interactive_ok else '❌ 失败'}")
    print(f"单次查询模式: {'✅ 通过' if single_query_ok else '❌ 失败'}")
    
    if interactive_ok and single_query_ok:
        print("\n🎉 所有测试通过！智能体系统已成功使用硅基流动API。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关代码。")