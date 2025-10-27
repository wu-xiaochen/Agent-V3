#!/usr/bin/env python3
"""
项目结构验证脚本

验证项目结构是否符合规范，检查所有必要的目录和文件是否存在。
"""

import os
import sys
from pathlib import Path


def check_directory_exists(path, description):
    """检查目录是否存在"""
    if os.path.exists(path) and os.path.isdir(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (不存在)")
        return False


def check_file_exists(path, description):
    """检查文件是否存在"""
    if os.path.exists(path) and os.path.isfile(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (不存在)")
        return False


def main():
    """主函数"""
    print("=== Agent-V3 项目结构验证 ===\n")
    
    # 获取项目根目录，无论脚本从哪里运行
    project_root = Path(__file__).parent.parent
    success_count = 0
    total_count = 0
    
    # 检查顶级目录
    print("1. 检查顶级目录:")
    top_level_dirs = [
        ("config", "配置文件目录"),
        ("src", "源代码目录"),
        ("tests", "测试目录"),
        ("docs", "项目文档目录"),
        ("scripts", "运维脚本目录"),
        (".github", "CI/CD配置目录"),
        ("requirements", "依赖管理目录")
    ]
    
    for dir_name, description in top_level_dirs:
        total_count += 1
        if check_directory_exists(project_root / dir_name, description):
            success_count += 1
    
    print("\n2. 检查配置目录结构:")
    config_dirs = [
        ("config/base", "基础配置目录"),
        ("config/environments", "环境配置目录"),
        ("config/schemas", "配置Schema目录")
    ]
    
    for dir_path, description in config_dirs:
        total_count += 1
        if check_directory_exists(project_root / dir_path, description):
            success_count += 1
    
    print("\n3. 检查源代码目录结构:")
    src_dirs = [
        ("src/agents", "Agent实现层"),
        ("src/agents/contracts", "Agent契约定义"),
        ("src/agents/factories", "Agent工厂"),
        ("src/core", "核心业务逻辑"),
        ("src/core/domain", "领域模型"),
        ("src/core/services", "核心服务"),
        ("src/infrastructure", "基础设施层"),
        ("src/infrastructure/database", "数据库服务"),
        ("src/infrastructure/cache", "缓存服务"),
        ("src/infrastructure/external", "外部服务"),
        ("src/infrastructure/embedding", "嵌入服务"),
        ("src/infrastructure/vector_store", "向量存储服务"),
        ("src/interfaces", "接口适配层"),
        ("src/interfaces/api", "API接口"),
        ("src/interfaces/events", "事件处理"),
        ("src/shared", "共享组件"),
        ("src/shared/utils", "工具类"),
        ("src/shared/exceptions", "异常类型"),
        ("src/shared/types", "类型定义")
    ]
    
    for dir_path, description in src_dirs:
        total_count += 1
        if check_directory_exists(project_root / dir_path, description):
            success_count += 1
    
    print("\n4. 检查测试目录结构:")
    test_dirs = [
        ("tests/unit", "单元测试目录"),
        ("tests/integration", "集成测试目录"),
        ("tests/e2e", "端到端测试目录"),
        ("tests/fixtures", "测试数据目录")
    ]
    
    for dir_path, description in test_dirs:
        total_count += 1
        if check_directory_exists(project_root / dir_path, description):
            success_count += 1
    
    print("\n5. 检查文档目录结构:")
    doc_dirs = [
        ("docs/api", "API文档目录"),
        ("docs/deployment", "部署文档目录"),
        ("docs/development", "开发文档目录")
    ]
    
    for dir_path, description in doc_dirs:
        total_count += 1
        if check_directory_exists(project_root / dir_path, description):
            success_count += 1
    
    print("\n6. 检查脚本目录结构:")
    script_dirs = [
        ("scripts/deployment", "部署脚本目录"),
        ("scripts/monitoring", "监控脚本目录"),
        ("scripts/maintenance", "维护脚本目录")
    ]
    
    for dir_path, description in script_dirs:
        total_count += 1
        if check_directory_exists(project_root / dir_path, description):
            success_count += 1
    
    print("\n7. 检查关键文件:")
    key_files = [
        ("README.md", "项目说明文档"),
        ("pyproject.toml", "项目配置文件"),
        ("requirements.txt", "依赖文件"),
        ("main.py", "主程序入口"),
        ("config.yaml", "配置文件"),
        ("prompts.yaml", "提示词配置文件")
    ]
    
    for file_name, description in key_files:
        total_count += 1
        if check_file_exists(project_root / file_name, description):
            success_count += 1
    
    print("\n8. 检查初始化文件:")
    init_files = [
        ("src/__init__.py", "源代码模块初始化"),
        ("src/agents/__init__.py", "智能体模块初始化"),
        ("src/core/__init__.py", "核心模块初始化"),
        ("src/infrastructure/__init__.py", "基础设施模块初始化"),
        ("src/interfaces/__init__.py", "接口模块初始化"),
        ("src/shared/__init__.py", "共享模块初始化")
    ]
    
    for file_path, description in init_files:
        total_count += 1
        if check_file_exists(project_root / file_path, description):
            success_count += 1
    
    # 输出结果
    print(f"\n=== 验证结果 ===")
    print(f"通过: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✓ 项目结构验证通过！")
        return 0
    else:
        print(f"✗ 项目结构验证失败，缺少 {total_count - success_count} 项")
        return 1


if __name__ == "__main__":
    sys.exit(main())