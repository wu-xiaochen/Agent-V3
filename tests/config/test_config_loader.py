#!/usr/bin/env python3
"""
测试配置加载器
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.config_loader import config_loader


def test_config_loader():
    """测试配置加载器"""
    print("=== 测试配置加载器 ===\n")
    
    # 测试services配置
    services_config = config_loader.get_services_config()
    print(f"Services配置键: {list(services_config.keys())}\n")
    
    # 测试output配置
    output_config = config_loader.get_output_config()
    print(f"Output配置: {output_config}\n")
    
    # 检查output配置的各个部分
    print(f"输出格式: {output_config.get('format')}")
    print(f"输出选项: {output_config.get('options')}")
    print(f"自定义模板: {output_config.get('custom_templates')}")
    
    print("\n✅ 配置加载器测试完成")


if __name__ == "__main__":
    test_config_loader()