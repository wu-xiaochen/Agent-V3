#!/usr/bin/env python3
"""
测试时间工具
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.agents.shared.tools import TimeTool

def test_time_tool():
    """测试时间工具"""
    print("=== 测试时间工具 ===")
    
    # 创建时间工具实例
    time_tool = TimeTool()
    
    # 测试获取时间
    result = time_tool._run()
    print(f"时间工具返回结果: {result}")
    
    # 检查结果是否包含时间信息
    if "当前时间:" in result:
        print("✅ 时间工具正常工作")
    else:
        print("❌ 时间工具返回结果不正确")
    
    return result

if __name__ == "__main__":
    test_time_tool()