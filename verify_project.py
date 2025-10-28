#!/usr/bin/env python3
"""
项目完整性验证脚本

验证Agent-V3项目的完整性和正确性
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import List, Tuple

class Color:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text:^60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Color.GREEN}✓ {text}{Color.END}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Color.YELLOW}⚠ {text}{Color.END}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Color.RED}✗ {text}{Color.END}")

def print_info(text: str):
    """打印信息"""
    print(f"{Color.BLUE}ℹ {text}{Color.END}")

def check_file_exists(filepath: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(filepath)

def check_directory_exists(dirpath: str) -> bool:
    """检查目录是否存在"""
    return os.path.isdir(dirpath)

def verify_project_structure() -> Tuple[int, int]:
    """验证项目结构"""
    print_header("验证项目结构")
    
    required_dirs = [
        "src/agents",
        "src/config",
        "src/infrastructure",
        "src/storage",
        "src/tools",
        "src/prompts",
        "config/base",
        "config/environments",
        "config/tools",
        "tests/comprehensive",
        "tests/integration",
        "docs"
    ]
    
    success = 0
    total = len(required_dirs)
    
    for directory in required_dirs:
        if check_directory_exists(directory):
            print_success(f"目录存在: {directory}")
            success += 1
        else:
            print_error(f"目录缺失: {directory}")
    
    return success, total

def verify_config_files() -> Tuple[int, int]:
    """验证配置文件"""
    print_header("验证配置文件")
    
    required_configs = [
        "config/base/agents.yaml",
        "config/base/services.yaml",
        "config/base/prompts.yaml",
        "config/base/logging.yaml",
        "config/tools/tools_config.json"
    ]
    
    success = 0
    total = len(required_configs)
    
    for config_file in required_configs:
        if check_file_exists(config_file):
            print_success(f"配置存在: {config_file}")
            
            # 验证配置可解析
            try:
                if config_file.endswith('.yaml'):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                    print_success(f"  └─ YAML格式正确")
                elif config_file.endswith('.json'):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print_success(f"  └─ JSON格式正确")
                success += 1
            except Exception as e:
                print_error(f"  └─ 解析失败: {str(e)}")
        else:
            print_error(f"配置缺失: {config_file}")
    
    return success, total

def verify_source_files() -> Tuple[int, int]:
    """验证源代码文件"""
    print_header("验证源代码文件")
    
    required_files = [
        "src/agents/unified/unified_agent.py",
        "src/agents/supply_chain/supply_chain_agent.py",
        "src/agents/shared/tools.py",
        "src/agents/shared/dynamic_tool_loader.py",
        "src/agents/shared/mcp_stdio_tool.py",
        "src/config/config_loader.py",
        "src/infrastructure/llm/llm_factory.py",
        "src/storage/redis_chat_history.py",
        "src/tools/supply_chain_tools.py",
        "src/tools/crewai_generator.py",
        "main.py"
    ]
    
    success = 0
    total = len(required_files)
    
    for source_file in required_files:
        if check_file_exists(source_file):
            print_success(f"源文件存在: {source_file}")
            success += 1
        else:
            print_error(f"源文件缺失: {source_file}")
    
    return success, total

def verify_test_files() -> Tuple[int, int]:
    """验证测试文件"""
    print_header("验证测试文件")
    
    required_tests = [
        "tests/comprehensive/test_agent_core_functionality.py",
        "tests/comprehensive/test_system_integration.py",
        "tests/integration/test_n8n_mcp_integration.py",
        "tests/test_all.py"
    ]
    
    success = 0
    total = len(required_tests)
    
    for test_file in required_tests:
        if check_file_exists(test_file):
            print_success(f"测试文件存在: {test_file}")
            success += 1
        else:
            print_error(f"测试文件缺失: {test_file}")
    
    return success, total

def verify_documentation() -> Tuple[int, int]:
    """验证文档"""
    print_header("验证文档")
    
    required_docs = [
        "README.md",
        "docs/QUICKSTART.md",
        "docs/ARCHITECTURE.md",
        "docs/TESTING.md",
        "PROJECT_SUMMARY.md"
    ]
    
    success = 0
    total = len(required_docs)
    
    for doc_file in required_docs:
        if check_file_exists(doc_file):
            print_success(f"文档存在: {doc_file}")
            success += 1
        else:
            print_error(f"文档缺失: {doc_file}")
    
    return success, total

def verify_config_content() -> Tuple[int, int]:
    """验证配置内容"""
    print_header("验证配置内容")
    
    checks = []
    
    # 验证agents.yaml
    try:
        with open("config/base/agents.yaml", 'r', encoding='utf-8') as f:
            agents_config = yaml.safe_load(f)
        
        if "agents" in agents_config:
            if "unified_agent" in agents_config["agents"]:
                print_success("unified_agent配置存在")
                checks.append(True)
            else:
                print_error("unified_agent配置缺失")
                checks.append(False)
            
            if "supply_chain_agent" in agents_config["agents"]:
                print_success("supply_chain_agent配置存在")
                checks.append(True)
            else:
                print_error("supply_chain_agent配置缺失")
                checks.append(False)
        else:
            print_error("agents配置格式错误")
            checks.append(False)
    except Exception as e:
        print_error(f"读取agents.yaml失败: {str(e)}")
        checks.append(False)
    
    # 验证prompts.yaml
    try:
        with open("config/base/prompts.yaml", 'r', encoding='utf-8') as f:
            prompts_config = yaml.safe_load(f)
        
        if "prompts" in prompts_config:
            required_prompts = ["supply_chain_planning", "crewai_generation", "user_guidance"]
            for prompt_name in required_prompts:
                if prompt_name in prompts_config["prompts"]:
                    print_success(f"提示词存在: {prompt_name}")
                    checks.append(True)
                else:
                    print_error(f"提示词缺失: {prompt_name}")
                    checks.append(False)
        else:
            print_error("prompts配置格式错误")
            checks.append(False)
    except Exception as e:
        print_error(f"读取prompts.yaml失败: {str(e)}")
        checks.append(False)
    
    # 验证tools_config.json
    try:
        with open("config/tools/tools_config.json", 'r', encoding='utf-8') as f:
            tools_config = json.load(f)
        
        if "tools" in tools_config:
            n8n_tool = any(t.get("name") == "n8n_mcp_generator" for t in tools_config["tools"])
            if n8n_tool:
                print_success("n8n_mcp_generator工具配置存在")
                checks.append(True)
            else:
                print_error("n8n_mcp_generator工具配置缺失")
                checks.append(False)
        
        if "agent_tool_mapping" in tools_config:
            if "unified_agent" in tools_config["agent_tool_mapping"]:
                print_success("unified_agent工具映射存在")
                checks.append(True)
            else:
                print_error("unified_agent工具映射缺失")
                checks.append(False)
        else:
            print_error("工具映射配置缺失")
            checks.append(False)
    except Exception as e:
        print_error(f"读取tools_config.json失败: {str(e)}")
        checks.append(False)
    
    success = sum(checks)
    total = len(checks)
    
    return success, total

def verify_environment() -> Tuple[int, int]:
    """验证环境设置"""
    print_header("验证环境设置")
    
    checks = []
    
    # 检查环境变量
    env_vars = ["SILICONFLOW_API_KEY"]
    for var in env_vars:
        if os.getenv(var):
            print_success(f"环境变量已设置: {var}")
            checks.append(True)
        else:
            print_warning(f"环境变量未设置: {var}")
            checks.append(False)
    
    # 检查依赖
    try:
        import langchain
        print_success("LangChain已安装")
        checks.append(True)
    except ImportError:
        print_error("LangChain未安装")
        checks.append(False)
    
    try:
        import redis
        print_success("Redis包已安装")
        checks.append(True)
    except ImportError:
        print_error("Redis包未安装")
        checks.append(False)
    
    try:
        import yaml
        print_success("PyYAML已安装")
        checks.append(True)
    except ImportError:
        print_error("PyYAML未安装")
        checks.append(False)
    
    # 检查Redis连接（可选）
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print_success("Redis服务运行正常")
        checks.append(True)
    except Exception:
        print_warning("Redis服务未运行（可选）")
        checks.append(False)
    
    success = sum(checks)
    total = len(checks)
    
    return success, total

def print_summary(results: dict):
    """打印总结"""
    print_header("验证总结")
    
    total_success = sum(r[0] for r in results.values())
    total_checks = sum(r[1] for r in results.values())
    percentage = (total_success / total_checks * 100) if total_checks > 0 else 0
    
    for category, (success, total) in results.items():
        status = Color.GREEN if success == total else (Color.YELLOW if success > 0 else Color.RED)
        print(f"{status}{category}: {success}/{total}{Color.END}")
    
    print(f"\n{Color.BOLD}总体完成度: {total_success}/{total_checks} ({percentage:.1f}%){Color.END}")
    
    if percentage == 100:
        print(f"\n{Color.GREEN}{Color.BOLD}🎉 项目验证完全通过！{Color.END}")
    elif percentage >= 80:
        print(f"\n{Color.YELLOW}{Color.BOLD}✓ 项目基本完整，有少量警告{Color.END}")
    else:
        print(f"\n{Color.RED}{Color.BOLD}⚠ 项目存在较多问题，需要修复{Color.END}")

def main():
    """主函数"""
    print(f"\n{Color.BOLD}Agent-V3 项目完整性验证{Color.END}")
    print(f"{Color.BLUE}{'='*60}{Color.END}")
    
    results = {}
    
    # 执行各项验证
    results["项目结构"] = verify_project_structure()
    results["配置文件"] = verify_config_files()
    results["源代码"] = verify_source_files()
    results["测试文件"] = verify_test_files()
    results["文档"] = verify_documentation()
    results["配置内容"] = verify_config_content()
    results["环境设置"] = verify_environment()
    
    # 打印总结
    print_summary(results)
    
    # 返回状态码
    total_success = sum(r[0] for r in results.values())
    total_checks = sum(r[1] for r in results.values())
    percentage = (total_success / total_checks * 100) if total_checks > 0 else 0
    
    sys.exit(0 if percentage == 100 else 1)

if __name__ == "__main__":
    main()

