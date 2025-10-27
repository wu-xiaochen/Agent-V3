#!/usr/bin/env python3
"""
测试输出格式是否正确应用
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_dir)

from src.agents.unified.unified_agent import UnifiedAgent
from src.config.config_loader import config_loader


def test_output_formats():
    """测试各种输出格式"""
    print("=== 测试输出格式配置 ===\n")
    
    # 获取配置文件中的输出配置
    output_config = config_loader.get_output_config()
    print(f"配置文件中的默认输出格式: {output_config.get('format')}")
    print(f"配置选项: {output_config.get('options')}")
    print(f"自定义模板: {output_config.get('custom_templates', {}).keys()}\n")
    
    # 创建智能体
    agent = UnifiedAgent()
    
    # 测试查询
    query = "请简单介绍一下人工智能"
    
    # 测试默认格式（从配置文件读取）
    print("=== 测试默认格式（从配置文件读取）===")
    response = agent.run(query)
    print(response['response'])
    print(f"输出格式: {response['metadata']['output_format']}\n")
    
    # 测试normal格式
    print("=== 测试Normal格式 ===")
    agent.set_output_format('normal')
    response = agent.run(query)
    print(response['response'])
    print(f"输出格式: {response['metadata']['output_format']}\n")
    
    # 测试markdown格式
    print("=== 测试Markdown格式 ===")
    agent.set_output_format('markdown')
    response = agent.run(query)
    print(response['response'])
    print(f"输出格式: {response['metadata']['output_format']}\n")
    
    # 测试json格式
    print("=== 测试JSON格式 ===")
    agent.set_output_format('json')
    response = agent.run(query)
    print(response['response'])
    print(f"输出格式: {response['metadata']['output_format']}\n")
    
    print("✅ 输出格式测试完成")


if __name__ == "__main__":
    test_output_formats()