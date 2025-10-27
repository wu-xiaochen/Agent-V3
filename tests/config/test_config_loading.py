#!/usr/bin/env python3
"""
测试配置加载
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.config.config_loader import config_loader

def test_config_loading():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    
    # 获取agent配置
    agent_config = config_loader.get_agent_config()
    print("agent_config keys:", agent_config.keys())
    print("agent_config tools:", agent_config.get("tools", []))
    
    # 获取unified_agent配置
    unified_config = config_loader.get_specific_agent_config("unified_agent")
    print("unified_config keys:", unified_config.keys())
    print("unified_config tools:", unified_config.get("tools", []))

if __name__ == "__main__":
    test_config_loading()