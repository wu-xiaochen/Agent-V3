#!/usr/bin/env python3
"""
生成生物质锅炉智能寻源的CrewAI配置文件
"""

import sys
import os
import json
import yaml

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.crewai_generator import CrewAIGeneratorTool

def generate_biomass_boiler_crew_config():
    """生成生物质锅炉智能寻源的CrewAI配置文件"""
    print("=== 生成生物质锅炉智能寻源的CrewAI配置文件 ===")
    
    # 创建CrewAI生成器工具实例
    crewai_generator = CrewAIGeneratorTool()
    
    # 定义业务流程
    business_process = "生物质锅炉智能寻源，包括供应商评估、成本分析、质量控制和供应链优化"
    
    print(f"业务流程: {business_process}")
    print("=" * 50)
    
    try:
        # 生成CrewAI配置
        result = crewai_generator._run(business_process)
        print("\n生成的CrewAI配置:")
        print(result)
        
        # 将结果保存为JSON文件
        config_data = {
            "business_process": business_process,
            "crewai_config": result,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        # 保存JSON格式配置
        json_file_path = "/Users/xiaochenwu/Desktop/Agent-V3/biomass_boiler_crew_config.json"
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f"\n配置已保存到JSON文件: {json_file_path}")
        
        # 保存YAML格式配置
        yaml_file_path = "/Users/xiaochenwu/Desktop/Agent-V3/biomass_boiler_crew_config.yaml"
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False, indent=2)
        print(f"配置已保存到YAML文件: {yaml_file_path}")
        
        return True
    except Exception as e:
        print(f"\n错误: 生成配置失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_biomass_boiler_crew_config()
    if success:
        print("\n配置文件生成成功!")
    else:
        print("\n配置文件生成失败!")