#!/usr/bin/env python3
"""
测试输出格式配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.shared.output_formatter import OutputFormatter
from src.config.config_loader import config_loader


def test_output_format_config():
    """测试输出格式配置"""
    print("=== 测试输出格式配置 ===\n")
    
    # 加载配置
    output_config = config_loader.get_output_config()
    print(f"输出配置: {output_config}\n")
    
    # 测试默认格式
    output_format = output_config.get("format", "normal")
    print(f"默认输出格式: {output_format}\n")
    
    # 创建OutputFormatter实例
    formatter = OutputFormatter(output_format, output_config)
    
    # 测试不同格式的输出
    test_response = "这是一个测试响应"
    test_metadata = {"agent_name": "测试智能体", "session_id": "test_session"}
    
    print("1. 测试Normal格式:")
    normal_output = formatter.format_response(test_response, test_metadata)
    print(normal_output)
    print("\n" + "-" * 50 + "\n")
    
    print("2. 测试Markdown格式:")
    formatter.set_format("markdown")
    markdown_output = formatter.format_response(test_response, test_metadata)
    print(markdown_output)
    print("\n" + "-" * 50 + "\n")
    
    print("3. 测试JSON格式:")
    formatter.set_format("json")
    json_output = formatter.format_response(test_response, test_metadata)
    print(json_output)
    print("\n" + "-" * 50 + "\n")
    
    # 测试自定义模板
    print("4. 测试自定义模板:")
    formatter.set_format("normal")
    normal_with_template = formatter.format_response(test_response, test_metadata)
    print(normal_with_template)
    print("\n" + "-" * 50 + "\n")
    
    formatter.set_format("markdown")
    markdown_with_template = formatter.format_response(test_response, test_metadata)
    print(markdown_with_template)
    print("\n" + "-" * 50 + "\n")
    
    formatter.set_format("json")
    json_with_template = formatter.format_response(test_response, test_metadata)
    print(json_with_template)
    print("\n" + "-" * 50 + "\n")
    
    print("✅ 输出格式配置测试完成")


if __name__ == "__main__":
    test_output_format_config()