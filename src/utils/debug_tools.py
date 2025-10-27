#!/usr/bin/env python3
"""
调试工具注册
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.shared.tools import get_tools

def debug_tools():
    """调试工具注册"""
    print("调试工具注册...")
    
    # 获取工具列表
    tools = get_tools()
    print(f"获取到 {len(tools)} 个工具")
    
    # 只检查前3个工具
    for i, tool in enumerate(tools[:3]):
        print(f"\n工具 {i+1}:")
        print(f"  类型: {type(tool)}")
        
        # 尝试获取名称
        try:
            if hasattr(tool, 'name'):
                print(f"  名称: {tool.name}")
            elif hasattr(tool, 'get_name'):
                print(f"  名称: {tool.get_name()}")
            else:
                print("  名称: N/A")
        except Exception as e:
            print(f"  获取名称失败: {e}")
        
        # 尝试获取描述
        try:
            if hasattr(tool, 'description'):
                print(f"  描述: {tool.description}")
            else:
                print("  描述: N/A")
        except Exception as e:
            print(f"  获取描述失败: {e}")

if __name__ == "__main__":
    debug_tools()