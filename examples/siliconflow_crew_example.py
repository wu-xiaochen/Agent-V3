#!/usr/bin/env python3
"""
硅基流动CrewAI示例
演示如何使用硅基流动API运行CrewAI团队
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置OpenAI环境变量为硅基流动的配置，确保CrewAI使用硅基流动API
os.environ["OPENAI_API_KEY"] = os.getenv("SILICONFLOW_API_KEY", "")
os.environ["OPENAI_API_BASE"] = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

from src.interfaces.crewai_runtime import CrewAIRuntime


def main():
    """主函数"""
    print("=== 硅基流动CrewAI示例 ===\n")
    
    # 检查环境变量
    if not os.getenv("SILICONFLOW_API_KEY"):
        print("错误: 未设置SILICONFLOW_API_KEY环境变量")
        print("请设置环境变量后重试: export SILICONFLOW_API_KEY=your_api_key_here")
        return
    
    # 配置文件路径
    config_file = "standard_biomass_boiler_crew_config.json"
    
    # 检查配置文件是否存在
    if not Path(config_file).exists():
        print(f"错误: 配置文件不存在: {config_file}")
        print("请先运行 test_standard_crew_config.py 生成配置文件")
        return
    
    # 创建运行时
    runtime = CrewAIRuntime()
    
    # 加载配置
    print(f"正在加载配置文件: {config_file}")
    if not runtime.load_config(config_file):
        print("配置文件加载失败")
        return
    
    # 创建团队
    print("\n正在创建CrewAI团队...")
    if not runtime.create_crew():
        print("团队创建失败")
        return
    
    # 示例查询
    query = "如何优化生物质锅炉的供应链管理，降低成本并提高效率？"
    
    print(f"\n执行查询: {query}")
    print("=" * 50)
    
    # 运行团队
    result = runtime.run_crew(query)
    
    if result:
        print("\n=== 执行完成 ===")
        print("结果已保存到 results/ 目录")
    else:
        print("\n执行失败")


if __name__ == "__main__":
    main()