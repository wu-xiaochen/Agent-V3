#!/usr/bin/env python3
"""
供应链智能体示例

这个示例展示了如何使用SupplyChainAgent进行供应链业务流程规划、确认和CrewAI配置生成。
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入供应链智能体和相关工具
from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent
from src.infrastructure.llm.llm_factory import LLMFactory


async def main():
    """主函数"""
    # 创建LLM实例
    llm = LLMFactory.create_llm(
        provider="openai",  # 可以是 "openai", "anthropic", "huggingface"
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=2000
    )
    
    # 创建供应链智能体
    try:
        # 尝试使用Redis存储
        agent = SupplyChainAgent(
            llm=llm,
            redis_url="redis://localhost:6379/0",
            session_id="supply_chain_demo",
            verbose=True
        )
        print("✅ 供应链智能体创建成功，使用Redis存储")
    except ConnectionError as e:
        print(f"⚠️ Redis连接失败: {e}")
        print("🔄 回退到内存存储模式")
        
        # 创建不带Redis的智能体
        agent = SupplyChainAgent(
            llm=llm,
            redis_url=None,
            session_id="supply_chain_demo",
            verbose=True
        )
        print("✅ 供应链智能体创建成功，使用内存存储")
    
    # 示例1: 业务流程规划
    print("=" * 50)
    print("示例1: 业务流程规划")
    print("=" * 50)
    
    user_input = "我需要优化公司的采购流程，目前采购周期长、成本高，希望能缩短采购周期30%，降低成本15%"
    response = await agent.chat(user_input)
    print(f"用户: {user_input}")
    print(f"智能体: {response}")
    print()
    
    # 示例2: 确认流程规划
    print("=" * 50)
    print("示例2: 确认流程规划")
    print("=" * 50)
    
    user_input = "确认"
    response = await agent.chat(user_input)
    print(f"用户: {user_input}")
    print(f"智能体: {response}")
    print()
    
    # 示例3: 获取会话信息
    print("=" * 50)
    print("示例3: 获取会话信息")
    print("=" * 50)
    
    session_info = agent.get_session_info()
    print(f"会话信息: {json.dumps(session_info, indent=2, ensure_ascii=False)}")
    print()
    
    # 示例4: 流式输出
    print("=" * 50)
    print("示例4: 流式输出")
    print("=" * 50)
    
    user_input = "如何进行供应商评估与分类？"
    print(f"用户: {user_input}")
    print("智能体: ", end="", flush=True)
    
    async for chunk in agent.stream(user_input):
        print(chunk, end="", flush=True)
    print("\n")
    
    # 示例5: 运行智能体（获取完整结果）
    print("=" * 50)
    print("示例5: 运行智能体（获取完整结果）")
    print("=" * 50)
    
    user_input = "请生成一个完整的供应链优化方案，包括库存管理和物流配送优化"
    result = await agent.run(user_input)
    
    print(f"用户: {user_input}")
    print(f"智能体: {result['response']}")
    print(f"元数据: {json.dumps(result['metadata'], indent=2, ensure_ascii=False)}")
    print()
    
    # 示例6: 重置会话
    print("=" * 50)
    print("示例6: 重置会话")
    print("=" * 50)
    
    agent.reset_session()
    print("会话已重置")
    
    session_info = agent.get_session_info()
    print(f"重置后的会话信息: {json.dumps(session_info, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())