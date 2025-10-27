#!/usr/bin/env python3
"""
智能手机分析团队示例脚本
使用CrewAI运行时工具执行智能手机产品分析和市场研究
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.crewai_runtime_tool import CrewAIRuntimeTool


def run_smartphone_analysis():
    """运行智能手机分析团队"""
    
    # 配置文件路径
    config_file = "/Users/xiaochenwu/Desktop/Agent-V3/smartphone_analysis_crew.json"
    
    # 查询问题
    query = "分析2024年高端智能手机市场的竞争格局，重点关注苹果、三星和华为的产品策略和技术创新点"
    
    print("=" * 60)
    print("智能手机分析团队")
    print("=" * 60)
    print(f"查询问题: {query}")
    print("-" * 60)
    
    try:
        # 创建CrewAI运行时工具实例
        tool = CrewAIRuntimeTool()
        
        # 准备输入参数
        inputs = {
            "config": config_file,  # 使用配置文件路径
            "query": query,         # 必须提供query参数
            "process_type": "hierarchical"  # 使用层次化流程
        }
        
        print("正在启动智能手机分析团队...")
        print("团队配置:")
        
        # 读取并显示配置文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        crew_config = config.get("crewai_config", {})
        print(f"团队名称: {crew_config.get('name', '未知')}")
        print(f"团队描述: {crew_config.get('description', '无描述')}")
        print(f"处理流程: {crew_config.get('process', 'sequential')}")
        
        agents = crew_config.get("agents", [])
        print(f"团队成员数量: {len(agents)}")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.get('name', '未知')} - {agent.get('role', '无角色')}")
        
        tasks = crew_config.get("tasks", [])
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
            output_file = "/Users/xiaochenwu/Desktop/Agent-V3/results/smartphone_analysis_result.txt"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_text)
            
            # 保存元数据到JSON文件
            metadata_file = "/Users/xiaochenwu/Desktop/Agent-V3/results/smartphone_analysis_metadata.json"
            metadata = {
                "success": result.get("success", False),
                "query": query,
                "config_file": config_file,
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
    run_smartphone_analysis()