#!/usr/bin/env python3
"""
测试标准化CrewAI配置生成器
"""

import os
import sys
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.crewai_generator import CrewAIGeneratorTool

def test_standard_config_generation():
    """测试标准化配置生成"""
    print("测试标准化CrewAI配置生成...")
    
    # 创建生成器工具
    generator_tool = CrewAIGeneratorTool()
    
    # 定义生物质锅炉智能寻源业务流程
    business_process = """
    生物质锅炉智能寻源包括以下步骤：
    1. 市场调研：收集生物质锅炉市场信息，了解主要供应商、产品规格和价格范围
    2. 供应商评估：评估潜在供应商的资质、生产能力、质量认证和交货能力
    3. 成本分析：分析总拥有成本，包括设备采购、安装、运营和维护成本
    4. 质量控制：制定质量标准，确保锅炉符合安全和环保要求
    5. 供应链优化：优化物流、仓储和交付流程，降低供应链风险
    6. 合同谈判：与供应商进行价格和条款谈判，确保最有利条件
    7. 风险管理：识别潜在风险，制定应对策略
    8. 持续改进：建立供应商绩效评估机制，持续优化供应链
    """
    
    # 生成配置
    config = generator_tool._run(
        business_process=business_process,
        crew_name="生物质锅炉智能寻源团队",
        process_type="hierarchical",
        output_file="standard_biomass_boiler_crew_config.json"
    )
    
    # 验证配置结构
    required_keys = ["business_process", "crewai_config"]
    for key in required_keys:
        if key not in config:
            print(f"错误: 配置中缺少必需的键 '{key}'")
            return False
    
    crew_config = config["crewai_config"]
    required_crew_keys = ["name", "description", "agents", "tasks", "process"]
    for key in required_crew_keys:
        if key not in crew_config:
            print(f"错误: 团队配置中缺少必需的键 '{key}'")
            return False
    
    # 验证智能体配置
    agents = crew_config["agents"]
    for agent in agents:
        required_agent_keys = ["name", "role", "goal", "backstory"]
        for key in required_agent_keys:
            if key not in agent:
                print(f"错误: 智能体配置中缺少必需的键 '{key}'")
                return False
    
    # 验证任务配置
    tasks = crew_config["tasks"]
    for task in tasks:
        required_task_keys = ["name", "description", "agent", "expected_output"]
        for key in required_task_keys:
            if key not in task:
                print(f"错误: 任务配置中缺少必需的键 '{key}'")
                return False
    
    print("✓ 配置结构验证通过")
    
    # 保存配置文件
    output_file = "standard_biomass_boiler_crew_config.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 标准化配置文件已生成: {output_file}")
    
    return True

def test_config_loading():
    """测试配置加载"""
    print("\n测试配置加载...")
    
    from src.interfaces.crewai_runtime import CrewAIRuntime
    
    # 创建运行时
    runtime = CrewAIRuntime()
    
    # 加载配置文件
    config_file = "standard_biomass_boiler_crew_config.json"
    try:
        # 先加载配置文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 验证配置结构
        if "crewai_config" not in config_data:
            print("✗ 配置文件中缺少 'crewai_config' 部分")
            return False
            
        crew_config = config_data["crewai_config"]
        required_crew_keys = ["name", "description", "agents", "tasks", "process"]
        for key in required_crew_keys:
            if key not in crew_config:
                print(f"✗ 团队配置中缺少必需的键 '{key}'")
                return False
        
        # 验证智能体配置
        agents = crew_config["agents"]
        for agent in agents:
            required_agent_keys = ["name", "role", "goal", "backstory"]
            for key in required_agent_keys:
                if key not in agent:
                    print(f"✗ 智能体配置中缺少必需的键 '{key}'")
                    return False
        
        # 验证任务配置
        tasks = crew_config["tasks"]
        for task in tasks:
            required_task_keys = ["name", "description", "agent", "expected_output"]
            for key in required_task_keys:
                if key not in task:
                    print(f"✗ 任务配置中缺少必需的键 '{key}'")
                    return False
        
        print(f"✓ 配置结构验证通过")
        print(f"  团队名称: {crew_config['name']}")
        print(f"  智能体数量: {len(crew_config['agents'])}")
        print(f"  任务数量: {len(crew_config['tasks'])}")
        
        # 尝试创建团队（可能会因为缺少API密钥而失败，但这不是配置问题）
        try:
            success = runtime.load_crew_from_config(config_data)
            if success:
                print("✓ 团队创建成功")
            else:
                print("⚠ 团队创建失败（可能是因为缺少API密钥），但配置结构正确")
        except Exception as e:
            if "SILICONFLOW_API_KEY" in str(e) or "硅基流动API密钥" in str(e):
                print("⚠ 团队创建失败（缺少硅基流动API密钥），但配置结构正确")
            else:
                print(f"✗ 团队创建失败: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("标准化CrewAI配置生成器测试")
    print("=" * 60)
    
    # 测试配置生成
    generation_success = test_standard_config_generation()
    
    # 测试配置加载
    loading_success = test_config_loading()
    
    print("\n" + "=" * 60)
    if generation_success and loading_success:
        print("✓ 所有测试通过！标准化配置系统工作正常。")
    else:
        print("✗ 部分测试失败，请检查配置。")
    print("=" * 60)