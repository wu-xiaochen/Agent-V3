"""
完整系统测试运行器

运行所有测试套件，验证系统功能完整性
"""

import pytest
import sys
import os


def run_all_tests():
    """运行所有测试"""
    
    # 添加项目根目录到路径
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # 测试配置
    pytest_args = [
        "-v",  # 详细输出
        "-s",  # 显示print输出
        "--tb=short",  # 简短的traceback
        "-x",  # 遇到第一个失败就停止（可选）
        os.path.dirname(__file__)  # 测试目录
    ]
    
    # 运行测试
    result = pytest.main(pytest_args)
    
    return result


def run_specific_test_suite(suite_name):
    """运行特定测试套件"""
    
    test_suites = {
        "core": "tests/comprehensive/test_agent_core_functionality.py",
        "system": "tests/comprehensive/test_system_integration.py",
        "comprehensive": "tests/comprehensive/",
        "supply_chain": "tests/supply_chain/test_supply_chain_workflow.py",
        "n8n_integration": "tests/integration/test_n8n_mcp_integration.py",
        "config": "tests/config/",
        "tools": "tests/tools/",
        "agents": "tests/agents/",
        "unit": "tests/unit/",
        "integration": "tests/integration/"
    }
    
    if suite_name not in test_suites:
        print(f"未知的测试套件：{suite_name}")
        print(f"可用的测试套件：{', '.join(test_suites.keys())}")
        return 1
    
    test_path = test_suites[suite_name]
    pytest_args = ["-v", "-s", "--tb=short", test_path]
    
    return pytest.main(pytest_args)


def print_test_summary():
    """打印测试摘要信息"""
    
    print("\n" + "="*80)
    print("Agent-V3 系统测试套件")
    print("="*80)
    print("\n测试覆盖范围：")
    print("  1. 智能体核心功能测试 (core)")
    print("     - 初始化和配置")
    print("     - 对话能力（同步/异步/流式）")
    print("     - 记忆管理和持久化")
    print("     - 工具调用和集成")
    print("     - 错误处理和容错")
    print("     - 并发和性能")
    print("\n  2. 系统集成测试 (system)")
    print("     - LLM提供商集成")
    print("     - 配置系统集成")
    print("     - Redis存储集成")
    print("     - 工具系统集成")
    print("     - 端到端工作流")
    print("\n  3. 供应链业务流程测试 (supply_chain)")
    print("  4. n8n MCP集成测试 (n8n_integration)")
    print("  5. 配置加载测试 (config)")
    print("  6. 工具功能测试 (tools)")
    print("  7. 智能体系统测试 (agents)")
    print("  8. 单元测试 (unit)")
    print("  9. 集成测试 (integration)")
    print("\n使用方法：")
    print("  - 运行所有测试：python tests/test_all.py")
    print("  - 运行核心测试：python tests/test_all.py core")
    print("  - 运行系统测试：python tests/test_all.py system")
    print("  - 运行综合测试：python tests/test_all.py comprehensive")
    print("  - 使用pytest：pytest tests/ -v")
    print("\n推荐测试顺序：")
    print("  1. core - 验证智能体核心功能")
    print("  2. system - 验证系统集成")
    print("  3. comprehensive - 完整测试")
    print("="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent-V3 系统测试运行器")
    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        help="要运行的测试套件名称（默认：all）"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="显示测试摘要信息"
    )
    
    args = parser.parse_args()
    
    if args.summary:
        print_test_summary()
        sys.exit(0)
    
    # 运行测试
    if args.suite == "all":
        print_test_summary()
        result = run_all_tests()
    else:
        result = run_specific_test_suite(args.suite)
    
    sys.exit(result)

