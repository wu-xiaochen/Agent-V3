#!/usr/bin/env python3
"""
供应链智能体全面测试套件
测试多轮对话、Redis记忆管理、供应链专业属性和业务生成能力
"""

import os
import sys
import json
import time
import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
from langchain_core.language_models import BaseLLM

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent
from src.config import ConfigLoader
from src.agents.supply_chain.supply_chain_agent import ConversationState


class MockLLM(BaseLLM):
    """模拟LLM类，用于测试"""
    
    temperature: float = 0.7
    model: str = "mock-model"
    
    def __init__(self, **kwargs):
        # 不在这里设置新属性，而是使用Pydantic的字段定义
        super().__init__(**kwargs)
        # 将额外属性存储在私有字典中
        self._extra_attrs = {}
        self._extra_attrs['config_loader'] = ConfigLoader()
        self._extra_attrs['prompts_config'] = self._extra_attrs['config_loader'].get_prompts_config()
        self._extra_attrs['conversation_states'] = self._extra_attrs['prompts_config'].get("conversation_states", {})
        self._extra_attrs['state_transitions'] = self._extra_attrs['prompts_config'].get("state_transitions", {})
    
    @property
    def config_loader(self):
        return self._extra_attrs.get('config_loader')
    
    @property
    def prompts_config(self):
        return self._extra_attrs.get('prompts_config')
    
    @property
    def conversation_states(self):
        return self._extra_attrs.get('conversation_states')
    
    @property
    def state_transitions(self):
        return self._extra_attrs.get('state_transitions')
    
    def _generate(self, prompts, stop=None, run_manager=None, **kwargs) -> Any:
        """模拟LLM生成响应"""
        from langchain_core.outputs import LLMResult
        from langchain_core.outputs.generation import Generation
        
        # 为每个prompt创建Generation对象
        generations = []
        for prompt in prompts:
            prompt_text = prompt if prompt else ""
            
            # 根据不同的提示词返回不同的模拟响应
            if "供应链" in prompt_text and "规划" in prompt_text:
                response = """我已为您生成了供应链业务流程规划:

<plan>
{
  "流程名称": "电子产品供应链优化流程",
  "目标": "提高供应链效率，降低成本，提升客户满意度",
  "关键步骤": [
    {
      "步骤": "需求分析与预测",
      "描述": "分析历史数据，预测未来需求趋势",
      "所需资源": ["数据分析工具", "历史销售数据", "市场研究报告"],
      "预期效果": "需求预测准确率提升20%"
    },
    {
      "步骤": "供应商评估与选择",
      "描述": "评估现有供应商，寻找更优供应商",
      "所需资源": ["供应商评估系统", "成本分析工具"],
      "预期效果": "采购成本降低15%"
    },
    {
      "步骤": "库存优化",
      "描述": "优化库存水平，减少库存积压",
      "所需资源": ["库存管理系统", "需求预测模型"],
      "预期效果": "库存周转率提升25%"
    },
    {
      "步骤": "物流配送优化",
      "描述": "优化配送路线，提高配送效率",
      "所需资源": ["物流管理系统", "路线规划工具"],
      "预期效果": "配送时间缩短30%"
    }
  ]
}
</plan>

请确认这个规划是否符合您的需求，或者告诉我需要调整的地方。"""
            elif "CrewAI" in prompt_text and "配置" in prompt_text:
                response = """我已为您生成了CrewAI团队配置:

{
  "agents": [
    {
      "name": "supply_chain_analyst",
      "role": "供应链分析师",
      "goal": "分析供应链数据，识别优化机会",
      "backstory": "你是一位经验丰富的供应链分析师，擅长通过数据分析发现供应链中的问题和机会"
    },
    {
      "name": "procurement_specialist",
      "role": "采购专家",
      "goal": "优化采购策略，降低采购成本",
      "backstory": "你是一位采购专家，拥有丰富的供应商管理经验，擅长谈判和成本控制"
    },
    {
      "name": "logistics_planner",
      "role": "物流规划师",
      "goal": "优化物流配送，提高配送效率",
      "backstory": "你是一位物流规划专家，擅长路线优化和配送网络设计"
    }
  ],
  "tasks": [
    {
      "name": "analysis_task",
      "description": "分析当前供应链数据，识别瓶颈和优化机会。重点关注需求预测、库存管理和物流配送环节"
    },
    {
      "name": "procurement_task",
      "description": "基于分析结果，制定采购优化策略。包括供应商选择、成本控制和合同管理"
    },
    {
      "name": "logistics_task",
      "description": "设计物流配送优化方案。包括路线规划、配送网络设计和最后一公里配送优化"
    }
  ]
}

接下来我可以引导您如何按照业务流程执行操作。您需要了解哪个步骤的具体操作方法？"""
            elif "引导" in prompt_text or "指导" in prompt_text:
                response = """## 供应商评估与分类操作指南

### 当前步骤
步骤1: 供应商评估与分类

### 操作方法
1. **制定评估标准**
   - 质量能力：产品质量认证、质量控制体系
   - 交付能力：生产周期、物流能力、准时交付率
   - 成本能力：价格竞争力、成本结构、付款条件
   - 服务能力：售后服务、技术支持、响应速度
   - 风险控制：财务状况、合规性、可持续发展

2. **收集供应商数据**
   - 发放供应商信息调查表
   - 进行现场审核
   - 收集第三方认证信息
   - 调查市场口碑和客户反馈

3. **评估与打分**
   - 根据评估标准对供应商进行打分
   - 使用加权评分法计算综合得分
   - 建立供应商评估数据库

4. **供应商分类**
   - A类供应商：战略合作伙伴，占供应商总数20%
   - B类供应商：优选供应商，占供应商总数30%
   - C类供应商：普通供应商，占供应商总数50%

### 注意事项
- 确保评估标准的公平性和一致性
- 定期更新供应商评估数据，建议每半年一次
- 建立供应商绩效跟踪机制
- 对不同类别供应商采取差异化管理策略

### 建议技巧
- 使用数字化工具进行供应商管理，如SRM系统
- 建立供应商激励机制，促进持续改进
- 定期与战略供应商召开业务回顾会议
- 建立供应商风险预警机制"""
            else:
                response = "我理解您的需求，请提供更多详细信息以便我为您提供更好的帮助。"
            
            generation = Generation(text=response)
            generations.append([generation])
        
        return LLMResult(generations=generations)
    
    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        """同步调用方法"""
        result = self._generate([prompt], stop, run_manager, **kwargs)
        return result.generations[0].text
    
    async def _acall(self, prompt, stop=None, run_manager=None, **kwargs):
        """异步调用方法"""
        result = self._generate([prompt], stop, run_manager, **kwargs)
        return result.generations[0].text
    
    @property
    def _llm_type(self):
        """返回LLM类型"""
        return "mock_llm"
    
    @property
    def _identifying_params(self):
        """返回识别参数"""
        return {"temperature": self.temperature, "model": self.model}
    
    def __repr__(self):
        """字符串表示"""
        return f"MockLLM(model={self.model}, temperature={self.temperature})"





class TestSupplyChainAgentComprehensive(unittest.TestCase):
    """供应链智能体全面测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.llm = MockLLM(temperature=0.7)
        # 使用内存存储模式进行测试
        self.agent = SupplyChainAgent(
            llm=self.llm,
            redis_url=None,  # 使用内存存储
            session_id="test_session_comprehensive",
            verbose=True
        )
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.agent.current_state.value, "INITIAL")
        self.assertIsNone(self.agent.business_plan)
        self.assertIsNone(self.agent.crewai_config)
    
    async def async_test_planning_state(self):
        """测试业务流程规划状态"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        user_input = "我需要优化我的电子产品供应链，提高效率降低成本"
        response = await self.agent.chat(user_input)
        
        # 验证状态转换 - 处理完规划后应该转换到确认状态
        self.assertEqual(self.agent.current_state.value, "CONFIRMATION")
        
        # 验证业务规划生成
        self.assertIsNotNone(self.agent.business_plan)
        
        # 验证响应内容
        self.assertIn("电子产品供应链优化流程", response)
        self.assertIn("需求分析与预测", response)
        self.assertIn("供应商评估与选择", response)
        
        # 验证JSON结构
        try:
            plan_data = self.agent.business_plan if isinstance(self.agent.business_plan, dict) else json.loads(self.agent.business_plan)
            self.assertIn("流程名称", plan_data)
            self.assertIn("目标", plan_data)
            self.assertIn("关键步骤", plan_data)
            self.assertIsInstance(plan_data["关键步骤"], list)
            self.assertGreater(len(plan_data["关键步骤"]), 0)
        except json.JSONDecodeError:
            self.fail("业务规划不是有效的JSON格式")
    
    def test_planning_state(self):
        """测试业务流程规划状态"""
        asyncio.run(self.async_test_planning_state())
    
    async def async_test_confirmation_state(self):
        """测试流程确认状态"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 先进入规划状态
        user_input = "我需要优化我的电子产品供应链"
        await self.agent.chat(user_input)
        
        # 确认流程
        confirm_input = "这个流程很好，我确认使用这个流程"
        response = await self.agent.chat(confirm_input)
        
        # 验证状态转换
        self.assertEqual(self.agent.current_state.value, "CREWAI_GENERATION")  # 确认后转换到CrewAI生成状态
        
        # 验证响应内容
        self.assertIn("确认", response)
    
    def test_confirmation_state(self):
        """测试流程确认状态"""
        asyncio.run(self.async_test_confirmation_state())
    
    async def async_test_crewai_generation_state(self):
        """测试CrewAI配置生成状态"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 先进入确认状态
        user_input = "我需要优化我的电子产品供应链"
        await self.agent.chat(user_input)
        confirm_input = "这个流程很好，我确认使用这个流程"
        await self.agent.chat(confirm_input)
        
        # 生成CrewAI配置
        crewai_input = "请生成CrewAI团队配置"
        response = await self.agent.chat(crewai_input)
        
        # 验证状态转换
        self.assertEqual(self.agent.current_state.value, "GUIDANCE")  # 生成CrewAI配置后转换到引导状态
        
        # 验证CrewAI配置生成
        self.assertIsNotNone(self.agent.crewai_config)
        
        # 验证响应内容 - 检查是否包含CrewAI相关的关键词
        crewai_keywords = ["CrewAI", "Agent", "Task", "Crew", "agents", "tasks", "团队", "配置"]
        has_crewai_keyword = any(keyword in response for keyword in crewai_keywords)
        self.assertTrue(has_crewai_keyword, f"响应中应包含CrewAI相关的关键词，实际响应: {response[:200]}...")
    
    def test_crewai_generation_state(self):
        """测试CrewAI配置生成状态"""
        asyncio.run(self.async_test_crewai_generation_state())
    
    async def async_test_guidance_state(self):
        """测试用户引导状态"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 先进入CrewAI生成状态
        user_input = "我需要优化我的电子产品供应链"
        await self.agent.chat(user_input)
        confirm_input = "这个流程很好，我确认使用这个流程"
        await self.agent.chat(confirm_input)
        crewai_input = "请生成CrewAI团队配置"
        await self.agent.chat(crewai_input)
        
        # 进入引导状态
        guidance_input = "请指导我如何执行第一步"
        response = await self.agent.chat(guidance_input)
        
        # 验证状态转换
        self.assertEqual(self.agent.current_state.value, "GUIDANCE")
        
        # 验证响应内容包含关键信息
        self.assertIn("需求分析与预测", response)
        # 检查是否包含操作指导相关的关键词（至少包含一个）
        guidance_keywords = ["操作方法", "注意事项", "建议技巧", "步骤", "方法", "指南"]
        has_guidance_keyword = any(keyword in response for keyword in guidance_keywords)
        self.assertTrue(has_guidance_keyword, f"响应中应包含操作指导相关的关键词，实际响应: {response[:200]}...")
    
    def test_guidance_state(self):
        """测试用户引导状态"""
        asyncio.run(self.async_test_guidance_state())
    
    async def async_test_multi_turn_conversation(self):
        """测试多轮对话"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 第一轮对话
        user_input1 = "我需要优化我的电子产品供应链"
        response1 = await self.agent.chat(user_input1)
        self.assertEqual(self.agent.current_state.value, "CONFIRMATION")  # 处理完规划后转换到确认状态
        
        # 第二轮对话
        user_input2 = "这个流程很好，我确认使用这个流程"
        response2 = await self.agent.chat(user_input2)
        self.assertEqual(self.agent.current_state.value, "CREWAI_GENERATION")  # 确认后转换到CrewAI生成状态
        
        # 第三轮对话
        user_input3 = "请生成CrewAI团队配置"
        response3 = await self.agent.chat(user_input3)
        self.assertEqual(self.agent.current_state.value, "GUIDANCE")  # 生成CrewAI配置后转换到引导状态
        
        # 验证对话历史
        conversation_history = self.agent.conversation_history.messages
        self.assertGreaterEqual(len(conversation_history), 8)  # 初始消息+3轮对话，每轮2条消息（用户+AI）
    
    def test_multi_turn_conversation(self):
        """测试多轮对话"""
        asyncio.run(self.async_test_multi_turn_conversation())
    
    async def async_test_session_management(self):
        """测试会话管理"""
        # 获取初始会话信息
        session_info = self.agent.get_session_info()
        self.assertEqual(session_info["session_id"], "test_session_comprehensive")
        self.assertEqual(session_info["message_count"], 0)
        
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 进行一次对话
        user_input = "我需要优化我的电子产品供应链"
        await self.agent.chat(user_input)
        
        # 获取更新后的会话信息
        session_info = self.agent.get_session_info()
        self.assertEqual(session_info["message_count"], 4)  # 初始消息+实际对话，每轮2条消息（用户+AI）
        self.assertIsNotNone(self.agent.business_plan)
    
    def test_session_management(self):
        """测试会话管理"""
        asyncio.run(self.async_test_session_management())
    
    async def async_test_session_reset(self):
        """测试会话重置"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 进行一些对话
        user_input = "我需要优化我的电子产品供应链"
        await self.agent.chat(user_input)
        
        # 验证状态已改变
        self.assertEqual(self.agent.current_state.value, "CONFIRMATION")  # 处理完规划后转换到确认状态
        self.assertIsNotNone(self.agent.business_plan)
        
        # 重置会话
        self.agent.reset_session()
        
        # 验证重置后的状态
        self.assertEqual(self.agent.current_state.value, "INITIAL")
        self.assertIsNone(self.agent.business_plan)
        self.assertIsNone(self.agent.crewai_config)
        
        # 验证会话信息
        session_info = self.agent.get_session_info()
        self.assertEqual(session_info["message_count"], 0)
    
    def test_session_reset(self):
        """测试会话重置"""
        asyncio.run(self.async_test_session_reset())
    
    async def async_test_streaming_output(self):
        """测试流式输出"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 然后发送第二个消息来测试流式输出
        user_input = "我需要优化我的电子产品供应链"
        
        # 收集流式输出
        stream_chunks = []
        async for chunk in self.agent.stream(user_input):
            stream_chunks.append(chunk)
        
        # 验证流式输出不为空
        self.assertGreater(len(stream_chunks), 0)
        
        # 验证合并后的内容包含预期关键词
        stream_output = "".join(stream_chunks)
        
        # 验证流式输出包含关键信息
        self.assertIn("供应链业务流程规划", stream_output)
        self.assertIn("电子产品供应链优化流程", stream_output)
    
    def test_streaming_output(self):
        """测试流式输出"""
        asyncio.run(self.async_test_streaming_output())
    
    async def async_test_supply_chain_domain_knowledge(self):
        """测试供应链领域知识"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 然后发送第二个消息来测试供应链领域知识
        user_input = "我需要优化我的电子产品供应链"
        response = await self.agent.chat(user_input)
        
        # 验证供应链专业术语
        self.assertIn("需求分析与预测", response)
        self.assertIn("供应商评估与选择", response)
        self.assertIn("库存优化", response)
        self.assertIn("物流配送优化", response)
        
        # 验证供应链专业指标
        try:
            plan_data = self.agent.business_plan if isinstance(self.agent.business_plan, dict) else json.loads(self.agent.business_plan)
            steps = plan_data["关键步骤"]
            
            # 验证每个步骤包含必要的供应链元素
            for step in steps:
                self.assertIn("步骤", step)
                self.assertIn("描述", step)
                self.assertIn("所需资源", step)
                self.assertIn("预期效果", step)
        except json.JSONDecodeError:
            self.fail("业务规划不是有效的JSON格式")
    
    def test_supply_chain_domain_knowledge(self):
        """测试供应链领域知识"""
        asyncio.run(self.async_test_supply_chain_domain_knowledge())
    
    async def async_test_business_plan_generation(self):
        """测试业务规划生成能力"""
        # 先发送一个初始消息，将状态转换到规划状态
        await self.agent.chat("你好")
        
        # 然后发送第二个消息来测试业务规划生成
        user_input = "我需要优化我的电子产品供应链"
        response = await self.agent.chat(user_input)
        
        # 验证业务规划生成
        self.assertIsNotNone(self.agent.business_plan)
        
        # 验证业务规划结构
        try:
            plan_data = self.agent.business_plan if isinstance(self.agent.business_plan, dict) else json.loads(self.agent.business_plan)
            
            # 验证必要字段
            self.assertIn("流程名称", plan_data)
            self.assertIn("目标", plan_data)
            self.assertIn("关键步骤", plan_data)
            
            # 验证流程名称
            self.assertIsInstance(plan_data["流程名称"], str)
            self.assertGreater(len(plan_data["流程名称"]), 0)
            
            # 验证目标
            self.assertIsInstance(plan_data["目标"], str)
            self.assertGreater(len(plan_data["目标"]), 0)
            
            # 验证关键步骤
            self.assertIsInstance(plan_data["关键步骤"], list)
            self.assertGreater(len(plan_data["关键步骤"]), 0)
            
            # 验证每个步骤的结构
            for step in plan_data["关键步骤"]:
                self.assertIn("步骤", step)
                self.assertIn("描述", step)
                self.assertIn("所需资源", step)
                self.assertIn("预期效果", step)
                
                # 验证步骤内容
                self.assertIsInstance(step["步骤"], str)
                self.assertIsInstance(step["描述"], str)
                self.assertIsInstance(step["所需资源"], list)
                self.assertIsInstance(step["预期效果"], str)
                
                self.assertGreater(len(step["步骤"]), 0)
                self.assertGreater(len(step["描述"]), 0)
                self.assertGreater(len(step["所需资源"]), 0)
                self.assertGreater(len(step["预期效果"]), 0)
        except json.JSONDecodeError:
            self.fail("业务规划不是有效的JSON格式")
    
    def test_business_plan_generation(self):
        """测试业务规划生成能力"""
        asyncio.run(self.async_test_business_plan_generation())


def run_comprehensive_tests():
    """运行全面测试"""
    print("开始运行供应链智能体全面测试...")
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSupplyChainAgentComprehensive)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！供应链智能体功能正常。")
    else:
        print(f"\n❌ 测试失败！失败: {len(result.failures)}, 错误: {len(result.errors)}")
        
        # 输出失败详情
        for test, traceback in result.failures + result.errors:
            print(f"\n失败测试: {test}")
            print(f"错误信息: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)