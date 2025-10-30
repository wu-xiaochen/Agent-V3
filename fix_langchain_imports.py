#!/usr/bin/env python3
"""
自动修复 LangChain 1.0 导入路径
"""

import os
import re
from pathlib import Path

# 导入映射：旧路径 -> 新路径
IMPORT_MAPPINGS = {
    r'from langchain\.schema import (.+)': r'try:\n    from langchain.schema import \1\nexcept ImportError:\n    from langchain_core.messages import \1',
    r'from langchain\.callbacks\.base import (.+)': r'try:\n    from langchain.callbacks.base import \1\nexcept ImportError:\n    from langchain_core.callbacks import \1',
    r'from langchain\.agents import AgentExecutor': 'try:\n    from langchain.agents import AgentExecutor\nexcept ImportError:\n    from langchain_classic.agents import AgentExecutor',
}

def fix_file(filepath):
    """修复单个文件的导入"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        for old_pattern, new_import in IMPORT_MAPPINGS.items():
            if re.search(old_pattern, content):
                # 只替换第一次出现
                content = re.sub(old_pattern, new_import, content, count=1)
                modified = True
        
        if modified and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复: {filepath}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ 错误 {filepath}: {e}")
        return False

def main():
    """主函数"""
    src_dir = Path("src")
    python_files = list(src_dir.rglob("*.py"))
    
    print(f"🔍 发现 {len(python_files)} 个 Python 文件")
    print("🔧 开始修复导入...\n")
    
    fixed_count = 0
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n✅ 修复完成！共修复 {fixed_count} 个文件")

if __name__ == "__main__":
    main()

