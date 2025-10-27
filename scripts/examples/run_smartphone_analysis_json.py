#!/usr/bin/env python3
"""
智能手机分析团队示例脚本 - 使用JSON配置
演示如何使用JSON字符串配置CrewAI运行时工具
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.crewai_runtime_tool import CrewAIRuntimeTool


def run_smartphone_analysis_with_json():
    """使用JSON配置运行智能手机分析团队"""
    
    # 创建CrewAI配置JSON
    crew_config = {
        "crewai_config": {
            "name": "智能手机快速分析团队",
            "description": "专注于智能手机市场快速分析的小型团队",
            "agents": [
                {
                    "name": "市场分析师",
                    "role": "负责分析智能手机市场趋势和竞争格局",
                    "goal": "快速分析市场动态，提供简洁的竞争分析报告",
                    "backstory": "你是一位经验丰富的市场分析师，擅长快速把握市场趋势和竞争格局，能够提供简洁有力的分析报告。",
                    "tools": ["search"],
                    "verbose": True,
                    "allow_delegation": False
                }
            ],
            "tasks": [
                {
                    "name": "市场快速分析",
                    "description": "分析当前智能手机市场的主要竞争者和趋势",
                    "agent": "市场分析师",
                    "expected_output": "简洁的市场分析报告，包括主要竞争者、市场趋势和关键洞察",
                    "tools": ["search"]
                }
            ],
            "process": "sequential",
            "verbose": True,
            "memory": True
        }
    }
    
    # 查询问题
    query = "简要分析2024年智能手机市场的主要趋势和竞争格局，重点关注苹果、三星和华为"
    
    print("=" * 60)
    print("智能手机快速分析团队 (JSON配置)")
    print("=" * 60)
    print(f"查询问题: {query}")
    print("-" * 60)
    
    try:
        # 创建CrewAI运行时工具实例
        tool = CrewAIRuntimeTool()
        
        # 准备输入参数
        inputs = {
            "config": json.dumps(crew_config),  # 使用JSON字符串
            "query": query,                      # 必须提供query参数
            "process_type": "sequential"         # 使用顺序流程
        }
        
        print("正在启动智能手机快速分析团队...")
        print("团队配置:")
        
        # 从crewai_config中获取配置
        crewai_config = crew_config.get("crewai_config", {})
        print(f"团队名称: {crewai_config.get('name', '未知')}")
        print(f"团队描述: {crewai_config.get('description', '无描述')}")
        print(f"处理流程: {crewai_config.get('process', 'sequential')}")
        
        agents = crewai_config.get("agents", [])
        print(f"团队成员数量: {len(agents)}")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.get('name', '未知')} - {agent.get('role', '无角色')}")
        
        tasks = crewai_config.get("tasks", [])
        print(f"任务数量: {len(tasks)}")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.get('name', '未知')} - {task.get('description', '无描述')}")
        
        print("-" * 60)
        print("开始执行分析任务...")
        
        # 运行工具
        result = tool._run(**inputs)
        
        print("\n" + "=" * 60)
        print("分析结果")
        print("=" * 60)
        
        if result.get("success", False):
            analysis_result = result.get("result", "")
            
            # 处理CrewOutput对象
            if hasattr(analysis_result, 'raw'):
                # 如果是CrewOutput对象，提取raw属性
                result_text = analysis_result.raw
            elif isinstance(analysis_result, str):
                # 如果是字符串，直接使用
                result_text = analysis_result
            else:
                # 尝试转换为字符串
                result_text = str(analysis_result)
                
            print(result_text)
            
            # 保存结果到文件
            output_file = "/Users/xiaochenwu/Desktop/Agent-V3/results/smartphone_quick_analysis_result.txt"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_text)
            
            # 保存元数据到JSON文件
            metadata_file = "/Users/xiaochenwu/Desktop/Agent-V3/results/smartphone_quick_analysis_metadata.json"
            metadata = {
                "success": result.get("success", False),
                "query": query,
                "config_type": "json_string",
                "process_type": inputs.get("process_type"),
                "timestamp": str(os.times())
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"\n结果已保存到: {output_file}")
            print(f"元数据已保存到: {metadata_file}")
        else:
            print("分析过程中出现错误:")
            print(result.get("error", "未知错误"))
            
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_smartphone_analysis_with_json()