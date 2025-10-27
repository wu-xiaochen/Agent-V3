#!/usr/bin/env python3
"""
测试CrewAI生成器工具的详细输出
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.crewai_generator import CrewAIGeneratorTool

def test_crewai_generator_output():
    """测试CrewAI生成器工具的详细输出"""
    print("测试CrewAI生成器工具的详细输出...")
    
    # 创建工具实例
    tool = CrewAIGeneratorTool()
    
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
    
    # 测试工具功能
    print("\n测试工具功能...")
    try:
        process = "创建一个供应链优化团队，负责分析库存数据、预测需求、优化物流路径"
        result = tool._run(process)
        
        print(f"工具执行成功!")
        print(f"生成的配置长度: {len(result)} 字符")
        print(f"生成的配置内容: {result}")
        
        # 检查结果中是否包含关键信息
        if "agents" in result and "tasks" in result:
            print("配置包含必要的agents和tasks字段")
        else:
            print("警告: 配置可能缺少必要字段")
            
    except Exception as e:
        print(f"工具执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("CrewAI生成器工具详细输出测试")
    print("=" * 60)
    
    test_crewai_generator_output()
    
    print("\n" + "=" * 60)