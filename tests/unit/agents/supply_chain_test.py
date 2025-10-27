"""
供应链智能体测试
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.supply_chain.supply_chain_agent import SupplyChainAgent, ConversationState
from src.tools.crewai_generator import CrewAIGenerator
from src.tools.crewai_runtime_tool import CrewAIRuntimeTool


@pytest.fixture
def mock_llm():
    """模拟LLM"""
    # 使用Mock替代FakeLLM
    llm = Mock()
    llm.return_value = "测试响应"
    return llm


@pytest.fixture
def supply_chain_agent(mock_llm):
    """创建供应链智能体实例"""
    with patch('src.agents.supply_chain.supply_chain_agent.RedisConversationStore'):
        agent = SupplyChainAgent(
            llm=mock_llm,
            redis_url=None,  # 使用内存存储
            session_id="test_session",
            verbose=True
        )
        return agent


@pytest.mark.asyncio
async def test_initial_state(supply_chain_agent):
    """测试初始状态"""
    assert supply_chain_agent.current_state == ConversationState.INITIAL
    
    # 处理用户输入
    result = await supply_chain_agent.process_user_input("测试输入")
    
    # 应该转换到规划状态
    assert supply_chain_agent.current_state == ConversationState.PLANNING
    assert "response" in result
    assert "state" in result


@pytest.mark.asyncio
async def test_planning_state(supply_chain_agent):
    """测试规划状态"""
    # 设置为规划状态
    supply_chain_agent._transition_state(ConversationState.PLANNING)
    
    # 模拟规划响应
    with patch.object(supply_chain_agent, '_extract_content_from_tags') as mock_extract:
        mock_extract.return_value = '{"name": "测试计划", "objective": "测试目标"}'
        
        # 模拟LLMChain
        with patch('src.agents.supply_chain.supply_chain_agent.LLMChain') as mock_chain:
            mock_chain_instance = Mock()
            mock_chain_instance.arun = AsyncMock(return_value="<plan>{\"name\": \"测试计划\", \"objective\": \"测试目标\"}</plan>")
            mock_chain.return_value = mock_chain_instance
            
            # 处理用户输入
            result = await supply_chain_agent.process_user_input("我需要优化供应链")
            
            # 应该转换到确认状态
            assert supply_chain_agent.current_state == ConversationState.CONFIRMATION
            assert "response" in result
            assert supply_chain_agent.business_plan is not None


@pytest.mark.asyncio
async def test_confirmation_state(supply_chain_agent):
    """测试确认状态"""
    # 按照正确的流程转换状态
    # 1. 从INITIAL转换到PLANNING
    supply_chain_agent._transition_state(ConversationState.PLANNING)
    
    # 2. 从PLANNING转换到CONFIRMATION
    supply_chain_agent._transition_state(ConversationState.CONFIRMATION)
    supply_chain_agent.business_plan = {"name": "测试计划", "objective": "测试目标"}
    
    # 处理确认输入
    result = await supply_chain_agent.process_user_input("确认")
    
    # 应该转换到CrewAI生成状态
    assert supply_chain_agent.current_state == ConversationState.CREWAI_GENERATION
    assert "response" in result


@pytest.mark.asyncio
async def test_crewai_generation_state(supply_chain_agent):
    """测试CrewAI生成状态"""
    # 设置为CrewAI生成状态
    supply_chain_agent._transition_state(ConversationState.CREWAI_GENERATION)
    supply_chain_agent.business_plan = {"name": "测试计划", "objective": "测试目标"}
    
    # 模拟CrewAI生成器
    with patch.object(supply_chain_agent.crewai_generator, 'generate_crew_config') as mock_generate:
        mock_generate.return_value = {"agents": [], "tasks": []}
        
        # 处理用户输入
        result = await supply_chain_agent.process_user_input("任意输入")
        
        # 应该转换到执行状态
        assert supply_chain_agent.current_state == ConversationState.CREWAI_EXECUTION
        assert "response" in result
        assert supply_chain_agent.crewai_config is not None


@pytest.mark.asyncio
async def test_crewai_execution_state(supply_chain_agent):
    """测试CrewAI执行状态"""
    # 先转换到初始状态，然后到规划状态，再到CrewAI生成状态，最后到执行状态
    supply_chain_agent._transition_state(ConversationState.INITIAL)
    supply_chain_agent._transition_state(ConversationState.PLANNING)
    supply_chain_agent._transition_state(ConversationState.CREWAI_GENERATION)
    supply_chain_agent._transition_state(ConversationState.CREWAI_EXECUTION)
    supply_chain_agent.crewai_config = {"agents": [], "tasks": []}
    
    # 模拟CrewAIRuntimeTool
    with patch('src.agents.supply_chain.supply_chain_agent.CrewAIRuntimeTool') as mock_tool_class:
        mock_tool = Mock()
        mock_tool._run = AsyncMock(return_value={"success": True, "result": "执行成功"})
        mock_tool_class.return_value = mock_tool
        
        # 将模拟工具添加到工具列表
        supply_chain_agent.tools = [mock_tool]
        
        # 处理用户输入
        result = await supply_chain_agent.process_user_input("执行任务")
        
        # 应该转换到引导状态
        assert supply_chain_agent.current_state == ConversationState.GUIDANCE
        assert "response" in result
        assert "execution_result" in result


@pytest.mark.asyncio
async def test_crewai_execution_skip(supply_chain_agent):
    """测试CrewAI执行跳过"""
    # 设置为CrewAI执行状态
    supply_chain_agent._transition_state(ConversationState.CREWAI_EXECUTION)
    supply_chain_agent.crewai_config = {"agents": [], "tasks": []}
    
    # 处理跳过输入
    result = await supply_chain_agent.process_user_input("跳过")
    
    # 应该转换到引导状态
    assert supply_chain_agent.current_state == ConversationState.GUIDANCE
    assert "response" in result
    assert "已跳过CrewAI团队执行" in result["response"]


@pytest.mark.asyncio
async def test_crewai_execution_failure(supply_chain_agent):
    """测试CrewAI执行失败"""
    # 设置为CrewAI执行状态
    supply_chain_agent._transition_state(ConversationState.CREWAI_EXECUTION)
    supply_chain_agent.crewai_config = {"agents": [], "tasks": []}
    
    # 模拟CrewAIRuntimeTool失败
    with patch('src.agents.supply_chain.supply_chain_agent.CrewAIRuntimeTool') as mock_tool_class:
        mock_tool = Mock()
        mock_tool._run = AsyncMock(return_value={"success": False, "error": "执行失败"})
        mock_tool_class.return_value = mock_tool
        
        # 将模拟工具添加到工具列表
        supply_chain_agent.tools = [mock_tool]
        
        # 处理用户输入
        result = await supply_chain_agent.process_user_input("执行任务")
        
        # 应该保持在执行状态
        assert supply_chain_agent.current_state == ConversationState.CREWAI_EXECUTION
        assert "response" in result
        assert "error" in result


@pytest.mark.asyncio
async def test_guidance_state(supply_chain_agent):
    """测试引导状态"""
    # 设置为引导状态
    supply_chain_agent._transition_state(ConversationState.GUIDANCE)
    supply_chain_agent.business_plan = {"name": "测试计划", "objective": "测试目标"}
    
    # 模拟引导响应
    with patch.object(supply_chain_agent, '_extract_content_from_tags') as mock_extract:
        mock_extract.return_value = "这是引导内容"
        
        # 模拟LLMChain
        with patch('src.agents.supply_chain.supply_chain_agent.LLMChain') as mock_chain:
            mock_chain_instance = Mock()
            mock_chain_instance.arun = AsyncMock(return_value="<guidance>这是引导内容</guidance>")
            mock_chain.return_value = mock_chain_instance
            
            # 处理用户输入
            result = await supply_chain_agent.process_user_input("如何执行第一步")
            
            # 应该保持在引导状态
            assert supply_chain_agent.current_state == ConversationState.GUIDANCE
            assert "response" in result


@pytest.mark.asyncio
async def test_chat_method(supply_chain_agent):
    """测试chat方法"""
    # 处理用户输入
    response = await supply_chain_agent.chat("测试输入")
    
    # 应该返回响应字符串
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_run_method(supply_chain_agent):
    """测试run方法"""
    # 处理用户输入
    result = await supply_chain_agent.run("测试输入")
    
    # 应该返回字典
    assert isinstance(result, dict)
    assert "response" in result
    assert "metadata" in result
    assert len(result["response"]) > 0


@pytest.mark.asyncio
async def test_stream_method(supply_chain_agent):
    """测试stream方法"""
    # 处理用户输入
    async for chunk in supply_chain_agent.stream("测试输入"):
        # 应该返回字符串块
        assert isinstance(chunk, str)
        assert len(chunk) > 0


@pytest.mark.asyncio
async def test_intent_detection(supply_chain_agent):
    """测试意图检测"""
    # 测试确认意图
    intent = supply_chain_agent._detect_intent("确认")
    assert intent == "confirm"
    
    # 测试修改意图
    intent = supply_chain_agent._detect_intent("修改")
    assert intent == "modify"
    
    # 测试生成CrewAI意图
    intent = supply_chain_agent._detect_intent("生成CrewAI")
    assert intent == "generate_crewai"
    
    # 测试引导意图
    intent = supply_chain_agent._detect_intent("如何执行")
    assert intent == "guidance"
    
    # 测试默认规划意图
    intent = supply_chain_agent._detect_intent("未知输入")
    assert intent == "planning"


@pytest.mark.asyncio
async def test_content_extraction(supply_chain_agent):
    """测试内容提取"""
    # 测试从标签中提取内容
    content = supply_chain_agent._extract_content_from_tags("<plan>这是计划内容</plan>", "plan")
    assert content == "这是计划内容"
    
    # 测试没有标签的情况
    content = supply_chain_agent._extract_content_from_tags("没有标签的内容", "plan")
    assert content is None


@pytest.mark.asyncio
async def test_state_transition(supply_chain_agent):
    """测试状态转换"""
    # 测试初始状态
    assert supply_chain_agent.current_state == ConversationState.INITIAL
    
    # 转换到规划状态
    supply_chain_agent._transition_state(ConversationState.PLANNING)
    assert supply_chain_agent.current_state == ConversationState.PLANNING
    
    # 转换到确认状态
    supply_chain_agent._transition_state(ConversationState.CONFIRMATION)
    assert supply_chain_agent.current_state == ConversationState.CONFIRMATION
    
    # 转换到CrewAI生成状态
    supply_chain_agent._transition_state(ConversationState.CREWAI_GENERATION)
    assert supply_chain_agent.current_state == ConversationState.CREWAI_GENERATION
    
    # 转换到CrewAI执行状态
    supply_chain_agent._transition_state(ConversationState.CREWAI_EXECUTION)
    assert supply_chain_agent.current_state == ConversationState.CREWAI_EXECUTION
    
    # 转换到引导状态
    supply_chain_agent._transition_state(ConversationState.GUIDANCE)
    assert supply_chain_agent.current_state == ConversationState.GUIDANCE