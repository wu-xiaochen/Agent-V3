#!/usr/bin/env python3
"""
项目结构验证脚本
验证项目目录结构是否符合规范要求
"""

import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 必需的目录结构
REQUIRED_DIRS = {
    "config": {
        "base": {},
        "environments": {},
        "schemas": {},
        "examples": {}
    },
    "src": {
        "agents": {
            "contracts": {},
            "factories": {}
        },
        "core": {
            "domain": {},
            "services": {}
        },
        "infrastructure": {
            "database": {},
            "cache": {},
            "external": {}
        },
        "interfaces": {
            "api": {},
            "events": {}
        },
        "shared": {
            "utils": {},
            "exceptions": {},
            "types": {}
        }
    },
    "tests": {
        "unit": {},
        "integration": {},
        "e2e": {},
        "fixtures": {}
    },
    "docs": {
        "api": {},
        "deployment": {},
        "development": {}
    },
    "scripts": {
        "setup": {},
        "deployment": {},
        "monitoring": {},
        "maintenance": {},
        "config_generation": {},
        "execution": {}
    },
    "examples": {},
    "logs": {},
    "requirements": {}
}

# 必需的根目录文件
REQUIRED_ROOT_FILES = [
    "README.md",
    "main.py",
    "pyproject.toml",
    "requirements.txt",
    ".env.example"
]

def check_directory_structure():
    """检查目录结构是否符合规范"""
    print("检查项目目录结构...")
    errors = []
    
    def check_dir(dir_path, structure):
        """递归检查目录结构"""
        if not dir_path.exists():
            errors.append(f"缺少必需目录: {dir_path}")
            return
        
        if not dir_path.is_dir():
            errors.append(f"路径不是目录: {dir_path}")
            return
        
        # 检查子目录
        for name, sub_structure in structure.items():
            check_dir(dir_path / name, sub_structure)
    
    # 检查所有必需目录
    for name, structure in REQUIRED_DIRS.items():
        check_dir(PROJECT_ROOT / name, structure)
    
    return errors

def check_root_files():
    """检查根目录必需文件"""
    print("检查根目录必需文件...")
    errors = []
    
    for file_name in REQUIRED_ROOT_FILES:
        file_path = PROJECT_ROOT / file_name
        if not file_path.exists():
            errors.append(f"缺少必需文件: {file_path}")
    
    return errors

def check_naming_conventions():
    """检查命名规范"""
    print("检查命名规范...")
    errors = []
    
    # 检查目录命名（应为小写蛇形命名）
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # 检查是否为小写蛇形命名
            if not item.name.replace('_', '').islower():
                errors.append(f"目录命名不符合规范（应为小写蛇形命名）: {item.name}")
    
    # 检查Python文件命名
    for py_file in PROJECT_ROOT.rglob("*.py"):
        # 检查是否为小写蛇形命名
        if not py_file.name.replace('_', '').replace('-', '').islower():
            # 排除一些特殊文件
            if not any(pattern in py_file.name for pattern in ["__init__", "test_", "example_"]):
                errors.append(f"Python文件命名不符合规范: {py_file}")
    
    return errors

def check_config_files():
    """检查配置文件组织"""
    print("检查配置文件组织...")
    errors = []
    
    config_dir = PROJECT_ROOT / "config"
    if config_dir.exists():
        # 检查是否有配置文件散落在config根目录
        for item in config_dir.iterdir():
            if item.is_file() and item.suffix in ['.yaml', '.yml', '.json']:
                # 允许的根目录配置文件
                allowed_files = ['README.md']
                if item.name not in allowed_files and not item.name.startswith('.'):
                    errors.append(f"配置文件应放在config/base或config/environments目录: {item.name}")
    
    return errors

def main():
    """主函数"""
    print("=" * 50)
    print("项目结构验证")
    print("=" * 50)
    
    all_errors = []
    
    # 执行各项检查
    all_errors.extend(check_directory_structure())
    all_errors.extend(check_root_files())
    all_errors.extend(check_naming_conventions())
    all_errors.extend(check_config_files())
    
    # 输出结果
    print("\n" + "=" * 50)
    if all_errors:
        print(f"发现 {len(all_errors)} 个问题:")
        for i, error in enumerate(all_errors, 1):
            print(f"{i}. {error}")
        return 1
    else:
        print("项目结构验证通过！")
        return 0

if __name__ == "__main__":
    sys.exit(main())