#!/usr/bin/env python3
"""
测试自定义输出格式模板
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.shared.output_formatter import OutputFormatter
from src.config.config_loader import config_loader


def test_custom_templates():
    """测试自定义模板功能"""
    print("=== 测试自定义输出格式模板 ===\n")
    
    # 加载配置
    output_config = config_loader.get_output_config()
    print(f"输出配置: {output_config}\n")
    
    # 创建带有自定义配置的OutputFormatter实例
    formatter = OutputFormatter("normal", output_config)
    
    # 测试数据
    test_response = "这是一个关于人工智能的详细回答，包含多个技术要点。"
    test_metadata = {
        "agent_name": "AI助手",
        "session_id": "test_session_123",
        "timestamp": "2023-11-15T10:30:00Z",
        "confidence": 0.95,
        "sources": ["source1", "source2"]
    }
    
    # 测试Normal格式自定义模板
    print("1. 测试Normal格式自定义模板:")
    formatter.set_format("normal")
    normal_output = formatter.format_response(test_response, test_metadata)
    print(normal_output)
    print("\n" + "-" * 50 + "\n")
    
    # 测试Markdown格式自定义模板
    print("2. 测试Markdown格式自定义模板:")
    formatter.set_format("markdown")
    markdown_output = formatter.format_response(test_response, test_metadata)
    print(markdown_output)
    print("\n" + "-" * 50 + "\n")
    
    # 测试JSON格式自定义模板
    print("3. 测试JSON格式自定义模板:")
    formatter.set_format("json")
    json_output = formatter.format_response(test_response, test_metadata)
    print(json_output)
    print("\n" + "-" * 50 + "\n")
    
    # 测试配置选项
    print("4. 测试配置选项:")
    print(f"包含元数据: {formatter.config.get('options', {}).get('include_metadata', False)}")
    print(f"美化输出: {formatter.config.get('options', {}).get('pretty_print', False)}")
    print(f"缩进空格: {formatter.config.get('options', {}).get('indent', 2)}")
    print("\n" + "-" * 50 + "\n")
    
    print("✅ 自定义模板测试完成")


if __name__ == "__main__":
    test_custom_templates()