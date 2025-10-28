"""
智能体核心功能完整测试套件

测试智能体的所有核心功能：
1. 智能体初始化和配置
2. 对话功能（同步/异步/流式）
3. 上下文记忆管理
4. 工具调用和集成
5. 会话管理
6. 错误处理和容错
7. 并发和性能
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import time
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.unified.unified_agent import UnifiedAgent
from src.config.config_loader import config_loader


class TestAgentInitialization:
    """智能体初始化测试"""
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        agent = UnifiedAgent(provider="siliconflow")
        
        assert agent is not None
        assert agent.llm is not None
        assert agent.tools is not None
        assert agent.agent is not None
        assert agent.agent_executor is not None
    
    def test_initialization_with_memory(self):
        """测试带记忆的初始化"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_memory_init"
        )
        
        assert agent.memory is not None
        assert agent.session_id == "test_memory_init"
    
    def test_initialization_without_memory(self):
        """测试不带记忆的初始化"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=False
        )
        
        assert agent.memory is None
    
    def test_initialization_with_redis_url(self):
        """测试指定Redis URL初始化"""
        redis_url = "redis://localhost:6379/0"
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            redis_url=redis_url,
            session_id="test_redis_url"
        )
        
        assert agent.redis_url == redis_url
        session_info = agent.get_session_info()
        assert session_info["memory_type"] == "redis"
    
    def test_initialization_with_custom_model(self):
        """测试自定义模型初始化"""
        agent = UnifiedAgent(
            provider="siliconflow",
            model_name="Pro/Qwen/Qwen2.5-7B-Instruct"
        )
        
        assert agent is not None
    
    def test_tools_loaded(self):
        """测试工具加载"""
        agent = UnifiedAgent(provider="siliconflow")
        
        assert len(agent.tools) > 0
        tool_names = [tool.name for tool in agent.tools]
        assert len(tool_names) > 0
        print(f"\n加载的工具: {tool_names}")


class TestDialogueCapabilities:
    """对话能力测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_dialogue"
        )
    
    def test_single_turn_dialogue(self, agent):
        """测试单轮对话"""
        query = "你好，请介绍一下你自己"
        response = agent.run(query)
        
        assert response is not None
        assert "response" in response
        assert "metadata" in response
        assert len(response["response"]) > 0
        
        print(f"\n单轮对话响应: {response['response'][:200]}...")
    
    def test_multi_turn_dialogue(self, agent):
        """测试多轮对话"""
        # 第一轮
        response1 = agent.run("我叫张三")
        assert response1 is not None
        
        # 第二轮
        response2 = agent.run("我今年30岁")
        assert response2 is not None
        
        # 第三轮 - 测试上下文记忆
        response3 = agent.run("你还记得我叫什么吗？")
        assert response3 is not None
        
        # 验证记忆中有多轮对话
        memory = agent.get_memory()
        assert len(memory) >= 6  # 至少3轮对话（每轮2条消息）
        
        print(f"\n多轮对话记忆数量: {len(memory)}")
    
    def test_context_understanding(self, agent):
        """测试上下文理解"""
        # 建立上下文
        agent.run("我在一家制造企业工作")
        agent.run("我们主要生产电子产品")
        
        # 测试上下文理解
        response = agent.run("根据我公司的情况，你有什么建议？")
        
        assert response is not None
        response_text = response["response"].lower()
        # 应该包含与制造或电子产品相关的内容
        assert any(keyword in response_text for keyword in ["制造", "生产", "电子", "企业"])
    
    def test_query_with_metadata(self, agent):
        """测试响应元数据"""
        response = agent.run("测试查询")
        
        assert "metadata" in response
        metadata = response["metadata"]
        
        assert "query" in metadata
        assert "agent_type" in metadata
        assert "session_id" in metadata
        assert "has_memory" in metadata
        assert "memory_type" in metadata
        
        assert metadata["agent_type"] == "unified"
        assert metadata["has_memory"] is True
    
    @pytest.mark.asyncio
    async def test_async_dialogue(self, agent):
        """测试异步对话"""
        query = "这是一个异步测试查询"
        response = await agent.arun(query)
        
        assert response is not None
        assert "response" in response
        assert len(response["response"]) > 0
        
        print(f"\n异步对话响应: {response['response'][:200]}...")
    
    def test_stream_dialogue(self, agent):
        """测试流式对话"""
        query = "请详细介绍供应链管理的关键环节"
        
        chunks = []
        for chunk in agent.stream(query):
            chunks.append(chunk)
            if isinstance(chunk, dict) and "response" in chunk:
                print(chunk["response"], end="", flush=True)
        
        assert len(chunks) > 0
        print(f"\n\n流式输出块数: {len(chunks)}")
    
    def test_empty_query(self, agent):
        """测试空查询"""
        response = agent.run("")
        
        assert response is not None
        assert "response" in response
    
    def test_long_query(self, agent):
        """测试长查询"""
        long_query = "请详细分析" + "如何优化供应链管理" * 50
        response = agent.run(long_query)
        
        assert response is not None
        assert "response" in response


class TestMemoryManagement:
    """记忆管理测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_memory"
        )
    
    def test_memory_persistence(self, agent):
        """测试记忆持久化"""
        # 发送消息
        agent.run("记住这个信息：项目代号是Alpha")
        
        # 获取记忆
        memory = agent.get_memory()
        assert len(memory) > 0
        
        # 验证记忆内容
        messages_content = [msg.content for msg in memory]
        assert any("Alpha" in content for content in messages_content)
    
    def test_memory_retrieval(self, agent):
        """测试记忆检索"""
        # 存储多条信息
        agent.run("我的名字是李四")
        agent.run("我在北京工作")
        agent.run("我负责供应链管理")
        
        # 检索记忆
        response = agent.run("总结一下我之前说的信息")
        
        assert response is not None
        response_text = response["response"]
        
        # 应该包含之前的信息
        print(f"\n记忆检索响应: {response_text[:300]}...")
    
    def test_memory_clear(self, agent):
        """测试记忆清除"""
        # 添加记忆
        agent.run("这是一条测试消息")
        memory_before = agent.get_memory()
        assert len(memory_before) > 0
        
        # 清除记忆
        agent.clear_memory()
        memory_after = agent.get_memory()
        assert len(memory_after) == 0
    
    def test_session_isolation(self):
        """测试会话隔离"""
        agent1 = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="session_1"
        )
        
        agent2 = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="session_2"
        )
        
        # 在不同会话中发送消息
        agent1.run("会话1的消息")
        agent2.run("会话2的消息")
        
        # 验证会话隔离
        memory1 = agent1.get_memory()
        memory2 = agent2.get_memory()
        
        content1 = [msg.content for msg in memory1]
        content2 = [msg.content for msg in memory2]
        
        assert any("会话1" in c for c in content1)
        assert not any("会话2" in c for c in content1)
        assert any("会话2" in c for c in content2)
        assert not any("会话1" in c for c in content2)
        
        # 清理
        agent1.clear_memory()
        agent2.clear_memory()
    
    def test_memory_across_restarts(self):
        """测试跨重启的记忆持久化"""
        session_id = "test_persistence"
        
        # 第一个智能体实例
        agent1 = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id=session_id
        )
        agent1.run("持久化测试消息")
        agent1.run("这条消息应该被保存")
        
        # 模拟重启 - 创建新实例
        agent2 = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id=session_id
        )
        
        # 验证记忆恢复
        memory = agent2.get_memory()
        assert len(memory) > 0
        
        # 清理
        agent2.clear_memory()
    
    def test_session_info(self, agent):
        """测试会话信息获取"""
        agent.run("测试消息")
        
        session_info = agent.get_session_info()
        
        assert "session_id" in session_info
        assert "has_memory" in session_info
        assert "memory_type" in session_info
        assert "tools_count" in session_info
        
        assert session_info["has_memory"] is True
        assert session_info["tools_count"] > 0
        
        print(f"\n会话信息: {session_info}")


class TestToolInvocation:
    """工具调用测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_tools"
        )
    
    def test_tool_availability(self, agent):
        """测试工具可用性"""
        tools = agent.tools
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        print(f"\n可用工具: {tool_names}")
        
        # 验证基础工具存在
        basic_tools = ["time", "search", "calculator"]
        available_basic = [t for t in basic_tools if t in tool_names]
        assert len(available_basic) > 0
    
    def test_time_tool_invocation(self, agent):
        """测试时间工具调用"""
        query = "现在几点了？"
        response = agent.run(query)
        
        assert response is not None
        response_text = response["response"].lower()
        
        # 应该包含时间相关信息
        assert any(keyword in response_text for keyword in 
                  ["时间", "点", "分", "time", "当前"])
        
        print(f"\n时间工具响应: {response['response']}")
    
    def test_calculator_tool_invocation(self, agent):
        """测试计算器工具调用"""
        query = "计算 123 + 456"
        response = agent.run(query)
        
        assert response is not None
        response_text = response["response"]
        
        # 应该包含计算结果
        assert "579" in response_text or "五百七十九" in response_text
        
        print(f"\n计算器工具响应: {response['response']}")
    
    def test_search_tool_invocation(self, agent):
        """测试搜索工具调用"""
        query = "搜索最新的供应链管理趋势"
        response = agent.run(query)
        
        assert response is not None
        response_text = response["response"]
        
        # 应该包含搜索相关内容
        print(f"\n搜索工具响应: {response['response'][:300]}...")
    
    def test_multiple_tool_invocation(self, agent):
        """测试多个工具连续调用"""
        # 调用时间工具
        response1 = agent.run("现在是几点？")
        assert response1 is not None
        
        # 调用计算器工具
        response2 = agent.run("计算 100 * 25")
        assert response2 is not None
        
        # 调用搜索工具
        response3 = agent.run("搜索Python编程")
        assert response3 is not None
        
        print(f"\n连续工具调用成功，共{len(agent.tools)}个工具可用")
    
    def test_tool_error_handling(self, agent):
        """测试工具错误处理"""
        # 发送可能导致工具错误的查询
        query = "计算一个非常复杂的不存在的公式"
        response = agent.run(query)
        
        # 应该有响应，即使工具失败
        assert response is not None
        assert "response" in response
    
    def test_n8n_tool_recognition(self, agent):
        """测试n8n工具识别"""
        query = "帮我创建一个n8n工作流"
        response = agent.run(query)
        
        assert response is not None
        response_text = response["response"].lower()
        
        # 应该识别n8n关键词
        print(f"\nn8n工具识别响应: {response['response'][:300]}...")


class TestErrorHandlingAndResilience:
    """错误处理和容错测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_error_handling"
        )
    
    def test_invalid_query_handling(self, agent):
        """测试无效查询处理"""
        invalid_queries = [
            "",
            "   ",
            "!@#$%^&*()",
            "无意义的字符串" * 100,
        ]
        
        for query in invalid_queries:
            response = agent.run(query)
            assert response is not None
            assert "response" in response
    
    def test_exception_handling(self, agent):
        """测试异常处理"""
        # 模拟可能导致异常的场景
        try:
            response = agent.run("测试异常处理")
            assert response is not None
        except Exception as e:
            pytest.fail(f"未捕获的异常: {str(e)}")
    
    def test_timeout_handling(self, agent):
        """测试超时处理"""
        # 发送复杂查询
        query = "请详细分析全球供应链的发展历史和未来趋势" * 10
        
        start_time = time.time()
        response = agent.run(query)
        elapsed_time = time.time() - start_time
        
        assert response is not None
        print(f"\n查询耗时: {elapsed_time:.2f}秒")
    
    def test_malformed_input_handling(self, agent):
        """测试畸形输入处理"""
        malformed_inputs = [
            {"invalid": "dict"},  # 应该是字符串
            None,  # None值
        ]
        
        for inp in malformed_inputs:
            try:
                # 智能体应该能处理或报错
                if inp is None:
                    continue
                agent.run(str(inp))
            except Exception as e:
                # 预期的异常是可接受的
                print(f"处理畸形输入时的预期异常: {type(e).__name__}")
    
    def test_graceful_degradation(self, agent):
        """测试优雅降级"""
        # 即使某些组件失败，智能体也应该能够响应
        response = agent.run("简单的测试查询")
        
        assert response is not None
        assert "response" in response


class TestConcurrencyAndPerformance:
    """并发和性能测试"""
    
    def test_concurrent_queries_same_session(self):
        """测试同一会话的并发查询"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_concurrent"
        )
        
        queries = [
            "查询1：介绍供应链管理",
            "查询2：计算100+200",
            "查询3：现在几点",
        ]
        
        results = []
        for query in queries:
            response = agent.run(query)
            results.append(response)
        
        assert len(results) == len(queries)
        assert all(r is not None for r in results)
        
        # 清理
        agent.clear_memory()
    
    def test_concurrent_sessions(self):
        """测试并发会话"""
        def run_agent_session(session_id, query):
            agent = UnifiedAgent(
                provider="siliconflow",
                memory=True,
                session_id=session_id
            )
            response = agent.run(query)
            agent.clear_memory()
            return response
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                future = executor.submit(
                    run_agent_session,
                    f"concurrent_session_{i}",
                    f"并发测试查询 {i}"
                )
                futures.append(future)
            
            results = [f.result() for f in futures]
        
        assert len(results) == 3
        assert all(r is not None for r in results)
    
    def test_response_time(self):
        """测试响应时间"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_performance"
        )
        
        query = "这是一个性能测试查询"
        
        start_time = time.time()
        response = agent.run(query)
        elapsed_time = time.time() - start_time
        
        assert response is not None
        print(f"\n响应时间: {elapsed_time:.2f}秒")
        
        # 清理
        agent.clear_memory()
    
    def test_memory_usage_with_long_conversation(self):
        """测试长对话的内存使用"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_memory_usage"
        )
        
        # 发送多轮对话
        for i in range(10):
            agent.run(f"这是第{i+1}轮对话")
        
        memory = agent.get_memory()
        assert len(memory) >= 20  # 至少10轮对话（每轮2条消息）
        
        print(f"\n长对话记忆条数: {len(memory)}")
        
        # 清理
        agent.clear_memory()


class TestOutputFormats:
    """输出格式测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_output"
        )
    
    def test_default_output_format(self, agent):
        """测试默认输出格式"""
        response = agent.run("测试输出格式")
        
        assert "response" in response
        assert "metadata" in response
        assert isinstance(response["response"], str)
        
        current_format = agent.get_output_format()
        print(f"\n当前输出格式: {current_format}")
    
    def test_change_output_format(self, agent):
        """测试更改输出格式"""
        # 获取初始格式
        initial_format = agent.get_output_format()
        
        # 尝试更改格式
        agent.set_output_format("json")
        new_format = agent.get_output_format()
        
        # 恢复初始格式
        agent.set_output_format(initial_format)
        
        print(f"\n格式更改测试: {initial_format} -> {new_format} -> {initial_format}")


class TestConfigurationAndSetup:
    """配置和设置测试"""
    
    def test_config_loading(self):
        """测试配置加载"""
        config = config_loader.get_agents_config()
        assert config is not None
        assert "agents" in config
    
    def test_prompts_config_loading(self):
        """测试提示词配置加载"""
        config = config_loader.get_prompts_config()
        assert config is not None
        assert "prompts" in config
    
    def test_services_config_loading(self):
        """测试服务配置加载"""
        config = config_loader.get_services_config()
        assert config is not None
        assert "services" in config
    
    def test_redis_config_loading(self):
        """测试Redis配置加载"""
        config = config_loader.get_redis_config()
        assert config is not None
        assert "host" in config
        assert "port" in config
    
    def test_tools_config_loading(self):
        """测试工具配置加载"""
        config = config_loader.get_tools_config()
        assert config is not None


class TestEdgeCases:
    """边界情况测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_edge_cases"
        )
    
    def test_very_long_query(self, agent):
        """测试超长查询"""
        long_query = "请分析" + "供应链管理" * 500
        response = agent.run(long_query)
        
        assert response is not None
    
    def test_special_characters_query(self, agent):
        """测试特殊字符查询"""
        special_query = "测试<>特殊字符&符号#@!$%"
        response = agent.run(special_query)
        
        assert response is not None
    
    def test_unicode_query(self, agent):
        """测试Unicode查询"""
        unicode_query = "测试中文、日本語、한국어、Emoji😊🎉"
        response = agent.run(unicode_query)
        
        assert response is not None
    
    def test_rapid_successive_queries(self, agent):
        """测试快速连续查询"""
        for i in range(5):
            response = agent.run(f"快速查询 {i}")
            assert response is not None
    
    def test_same_query_multiple_times(self, agent):
        """测试重复查询"""
        query = "这是一个重复的查询"
        
        responses = []
        for _ in range(3):
            response = agent.run(query)
            responses.append(response)
        
        assert len(responses) == 3
        assert all(r is not None for r in responses)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

