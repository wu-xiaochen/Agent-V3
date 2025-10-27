#!/usr/bin/env python3
"""
输出格式示例脚本

此脚本演示如何使用配置文件中的输出格式设置，
以及如何在代码中动态切换输出格式。
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.unified.unified_agent import UnifiedAgent
from src.config.config_loader import config_loader


def demonstrate_output_formats():
    """演示不同输出格式的效果"""
    
    print("=" * 60)
    print("输出格式配置示例")
    print("=" * 60)
    
    # 创建智能体实例
    agent = UnifiedAgent()
    
    # 显示当前配置的输出格式
    output_config = config_loader.get_output_config()
    current_format = output_config.get("format", "normal")
    print(f"\n当前配置的默认输出格式: {current_format}")
    
    # 测试查询
    test_query = "请用一句话介绍你自己"
    
    # 1. 使用默认格式
    print(f"\n1. 使用默认格式 ({current_format}):")
    print("-" * 40)
    response = agent.run(test_query)
    if isinstance(response, dict) and "response" in response:
        print(response["response"])
    
    # 2. 切换到normal格式
    print(f"\n2. 切换到Normal格式:")
    print("-" * 40)
    agent.set_output_format("normal")
    response = agent.run(test_query)
    if isinstance(response, dict) and "response" in response:
        print(response["response"])
    
    # 3. 切换到markdown格式
    print(f"\n3. 切换到Markdown格式:")
    print("-" * 40)
    agent.set_output_format("markdown")
    response = agent.run(test_query)
    if isinstance(response, dict) and "response" in response:
        print(response["response"])
    
    # 4. 切换到json格式
    print(f"\n4. 切换到JSON格式:")
    print("-" * 40)
    agent.set_output_format("json")
    response = agent.run(test_query)
    if isinstance(response, dict) and "response" in response:
        print(response["response"])
    
    # 5. 显示配置文件中的自定义模板
    print(f"\n5. 配置文件中的自定义模板:")
    print("-" * 40)
    templates = output_config.get("custom_templates", {})
    for format_name, template in templates.items():
        print(f"{format_name}: {repr(template)}")
    
    print("\n" + "=" * 60)
    print("输出格式配置示例完成")
    print("=" * 60)


def show_config_file_location():
    """显示配置文件位置和内容"""
    
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "base", "services.yaml"
    )
    
    print(f"\n配置文件位置: {config_path}")
    
    if os.path.exists(config_path):
        print("\n配置文件中的output部分:")
        print("-" * 40)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            in_output_section = False
            
            for line in lines:
                if line.strip() == "output:":
                    in_output_section = True
                    print(line.rstrip())
                    continue
                elif in_output_section and line.startswith("  ") and not line.startswith("    "):
                    # 顶级配置项结束
                    break
                elif in_output_section:
                    print(line.rstrip())
    else:
        print("配置文件不存在!")


if __name__ == "__main__":
    show_config_file_location()
    demonstrate_output_formats()