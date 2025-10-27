#!/usr/bin/env python3
"""
供应链智能体工具功能测试脚本
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent
from src.config.config_loader import ConfigLoader
from src.infrastructure.llm.llm_factory import LLMFactory
from src.agents.shared.tools import get_tools


async def test_tools_loading():
    """测试工具加载功能"""
    print("=== 测试工具加载功能 ===")
    
    # 测试加载所有工具
    all_tools = get_tools()
    print(f"所有可用工具数量: {len(all_tools)}")
    for tool in all_tools:
        print(f"- {tool.name}: {tool.description}")
    
    # 测试加载供应链工具
    supply_chain_tools = get_tools(["data_analyzer", "forecasting_model", "optimization_engine", "risk_assessment"])
    print(f"\n供应链工具数量: {len(supply_chain_tools)}")
    for tool in supply_chain_tools:
        print(f"- {tool.name}: {tool.description}")
    
    return supply_chain_tools


async def test_supply_chain_tools():
    """测试供应链工具功能"""
    print("\n=== 测试供应链工具功能 ===")
    
    # 加载工具
    tools = await test_tools_loading()
    
    # 测试数据分析工具
    print("\n1. 测试数据分析工具")
    data_analyzer = tools[0]
    test_data = "[100, 120, 110, 130, 125, 140, 135, 150, 145, 160]"
    result = await data_analyzer._arun(f"分析数据: {test_data}, 类型: 趋势分析")
    print(f"分析结果: {result}")
    
    # 测试预测模型工具
    print("\n2. 测试预测模型工具")
    forecasting_model = tools[1]
    result = await forecasting_model._arun(f"预测数据: {test_data}, 预测类型: 线性预测, 预测期数: 3")
    print(f"预测结果: {result}")
    
    # 测试优化引擎工具
    print("\n3. 测试优化引擎工具")
    optimization_engine = tools[2]
    result = await optimization_engine._arun("优化类型: 库存优化, 参数: 需求量=1000, 持有成本=0.2, 订购成本=50")
    print(f"优化结果: {result}")
    
    # 测试风险评估工具
    print("\n4. 测试风险评估工具")
    risk_assessment = tools[3]
    result = await risk_assessment._arun("风险类型: 供应商风险, 供应商信息: 供应商A, 交货准时率=85%, 质量合格率=92%")
    print(f"评估结果: {result}")


async def test_supply_chain_agent():
    """测试供应链智能体"""
    print("\n=== 测试供应链智能体 ===")
    
    # 加载配置
    config_loader = ConfigLoader()
    
    # 创建LLM实例
    llm_factory = LLMFactory()
    llm_config = config_loader.get_llm_config()
    print(f"LLM配置: {llm_config}")
    
    # 获取provider
    provider = llm_config.get("provider", "siliconflow")
    print(f"LLM提供商: {provider}")
    
    # 创建LLM实例
    llm = llm_factory.create_llm(provider=provider)
    
    # 创建供应链智能体（不使用Redis）
    try:
        agent = SupplyChainAgent(
            llm=llm,
            redis_url="redis://localhost:6379",
            session_id="test_session",
            verbose=True
        )
        
        # 测试工具加载
        print(f"\n智能体工具数量: {len(agent.tools)}")
        for tool in agent.tools:
            print(f"- {tool.name}: {tool.description}")
        
        # 测试对话
        print("\n测试对话功能:")
        test_input = "我需要优化我的库存管理，当前库存周转率低，占用资金多"
        response = await agent.chat(test_input)
        print(f"用户输入: {test_input}")
        print(f"智能体响应: {response}")
    except ConnectionError as e:
        print(f"无法连接到Redis，跳过智能体测试: {str(e)}")
        # 直接测试工具加载
        print("\n直接测试工具加载:")
        
        # 创建一个简单的智能体实例，不初始化Redis
        agent = SupplyChainAgent.__new__(SupplyChainAgent)
        agent.llm = llm
        agent.tools_config = ["data_analyzer", "forecasting_model", "optimization_engine", "risk_assessment"]
        agent.tools = get_tools(agent.tools_config)
        
        print(f"智能体工具数量: {len(agent.tools)}")
        for tool in agent.tools:
            print(f"- {tool.name}: {tool.description}")


async def main():
    """主函数"""
    try:
        # 测试工具功能
        await test_supply_chain_tools()
        
        # 测试智能体
        await test_supply_chain_agent()
        
        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())