#!/usr/bin/env python3
"""
测试UnifiedAgent使用配置文件中的输出格式
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.unified.unified_agent import UnifiedAgent


def test_unified_agent_output_config():
    """测试UnifiedAgent使用配置文件中的输出格式"""
    print("=== 测试UnifiedAgent使用配置文件中的输出格式 ===\n")
    
    # 创建UnifiedAgent实例
    agent = UnifiedAgent()
    
    # 检查输出配置
    print(f"输出配置: {agent.output_config}\n")
    
    # 检查输出格式
    print(f"当前输出格式: {agent.output_formatter.get_format()}")
    
    # 测试不同格式的输出
    test_response = "这是一个测试响应，验证UnifiedAgent是否正确使用了配置文件中的输出格式。"
    test_metadata = {
        "agent_name": "UnifiedAgent",
        "session_id": "test_session_456",
        "timestamp": "2023-11-15T11:00:00Z"
    }
    
    print("\n1. 测试默认格式(Normal):")
    agent.output_formatter.set_format("normal")
    normal_output = agent.output_formatter.format_response(test_response, test_metadata)
    print(normal_output)
    print("\n" + "-" * 50 + "\n")
    
    print("2. 测试Markdown格式:")
    agent.output_formatter.set_format("markdown")
    markdown_output = agent.output_formatter.format_response(test_response, test_metadata)
    print(markdown_output)
    print("\n" + "-" * 50 + "\n")
    
    print("3. 测试JSON格式:")
    agent.output_formatter.set_format("json")
    json_output = agent.output_formatter.format_response(test_response, test_metadata)
    print(json_output)
    print("\n" + "-" * 50 + "\n")
    
    print("✅ UnifiedAgent输出格式配置测试完成")


if __name__ == "__main__":
    test_unified_agent_output_config()