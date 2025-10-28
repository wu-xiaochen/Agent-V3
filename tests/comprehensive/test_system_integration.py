"""
系统集成测试套件

测试系统各组件的集成：
1. LLM工厂和提供商集成
2. 配置系统集成
3. 存储系统集成
4. 工具系统集成
5. 端到端工作流
"""

import pytest
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.unified.unified_agent import UnifiedAgent
from src.infrastructure.llm.llm_factory import LLMFactory
from src.config.config_loader import config_loader
from src.storage.redis_chat_history import RedisConversationStore, RedisChatMessageHistory
from src.agents.shared.dynamic_tool_loader import DynamicToolLoader


class TestLLMIntegration:
    """LLM集成测试"""
    
    def test_siliconflow_provider(self):
        """测试SiliconFlow提供商"""
        llm = LLMFactory.create_llm("siliconflow")
        assert llm is not None
    
    def test_openai_provider(self):
        """测试OpenAI提供商"""
        if os.getenv("OPENAI_API_KEY"):
            llm = LLMFactory.create_llm("openai")
            assert llm is not None
        else:
            pytest.skip("OpenAI API密钥未配置")
    
    def test_anthropic_provider(self):
        """测试Anthropic提供商"""
        if os.getenv("ANTHROPIC_API_KEY"):
            llm = LLMFactory.create_llm("anthropic")
            assert llm is not None
        else:
            pytest.skip("Anthropic API密钥未配置")
    
    def test_llm_with_custom_parameters(self):
        """测试自定义参数的LLM"""
        llm = LLMFactory.create_llm(
            "siliconflow",
            temperature=0.5,
            max_tokens=1000
        )
        assert llm is not None


class TestConfigurationIntegration:
    """配置系统集成测试"""
    
    def test_hierarchical_config_loading(self):
        """测试分层配置加载"""
        # 加载基础配置
        agents_config = config_loader.get_agents_config()
        assert agents_config is not None
        
        # 加载服务配置
        services_config = config_loader.get_services_config()
        assert services_config is not None
        
        # 加载提示词配置
        prompts_config = config_loader.get_prompts_config()
        assert prompts_config is not None
    
    def test_environment_variable_resolution(self):
        """测试环境变量解析"""
        services_config = config_loader.get_services_config()
        
        # 验证环境变量被正确解析
        llm_config = services_config["services"]["llm"]
        assert "api_key" in llm_config
    
    def test_config_inheritance(self):
        """测试配置继承"""
        # 获取统一智能体配置
        unified_config = config_loader.get_specific_agent_config("unified_agent")
        assert unified_config is not None
        assert "model" in unified_config
        assert "tools" in unified_config
    
    def test_prompt_template_loading(self):
        """测试提示词模板加载"""
        prompts_config = config_loader.get_prompts_config()
        prompts = prompts_config.get("prompts", {})
        
        assert "supply_chain_planning" in prompts
        assert "crewai_generation" in prompts
        
        # 验证模板结构
        planning_prompt = prompts["supply_chain_planning"]
        assert "template" in planning_prompt
        assert "parameters" in planning_prompt
    
    def test_tools_configuration(self):
        """测试工具配置"""
        tools_config_path = "config/tools/tools_config.json"
        assert os.path.exists(tools_config_path)
        
        with open(tools_config_path, 'r') as f:
            tools_config = json.load(f)
        
        assert "tools" in tools_config
        assert "tool_groups" in tools_config
        assert "agent_tool_mapping" in tools_config


class TestStorageIntegration:
    """存储系统集成测试"""
    
    @pytest.fixture
    def redis_store(self):
        """创建Redis存储"""
        try:
            store = RedisConversationStore(
                redis_url="redis://localhost:6379/0"
            )
            yield store
            # 清理测试数据
            store.clear_all_sessions()
        except Exception as e:
            pytest.skip(f"Redis未运行: {str(e)}")
    
    def test_redis_connection(self, redis_store):
        """测试Redis连接"""
        assert redis_store is not None
        assert redis_store.redis_client is not None
    
    def test_session_creation_and_retrieval(self, redis_store):
        """测试会话创建和检索"""
        session_id = "test_integration_session"
        
        # 创建会话历史
        history = redis_store.get_history(session_id)
        assert history is not None
        
        # 添加消息
        from langchain.schema import HumanMessage, AIMessage
        history.add_message(HumanMessage(content="测试消息"))
        history.add_message(AIMessage(content="测试响应"))
        
        # 检索消息
        messages = history.messages
        assert len(messages) == 2
        
        # 清理
        history.clear()
    
    def test_session_persistence(self, redis_store):
        """测试会话持久化"""
        session_id = "test_persistence_session"
        
        # 创建第一个会话实例
        history1 = redis_store.get_history(session_id)
        from langchain.schema import HumanMessage
        history1.add_message(HumanMessage(content="持久化测试"))
        
        # 创建第二个会话实例（模拟重启）
        history2 = redis_store.get_history(session_id)
        messages = history2.messages
        
        assert len(messages) > 0
        assert any("持久化测试" in msg.content for msg in messages)
        
        # 清理
        history2.clear()
    
    def test_multiple_sessions(self, redis_store):
        """测试多会话管理"""
        sessions = ["session_1", "session_2", "session_3"]
        
        from langchain.schema import HumanMessage
        
        # 创建多个会话
        for session_id in sessions:
            history = redis_store.get_history(session_id)
            history.add_message(HumanMessage(content=f"消息来自{session_id}"))
        
        # 列出所有会话
        all_sessions = redis_store.list_sessions()
        assert len(all_sessions) >= 3
        
        # 清理
        for session_id in sessions:
            redis_store.delete_session(session_id)


class TestToolSystemIntegration:
    """工具系统集成测试"""
    
    def test_dynamic_tool_loader(self):
        """测试动态工具加载器"""
        loader = DynamicToolLoader()
        
        # 加载工具配置
        tools = loader.load_tools_from_config(
            "config/tools/tools_config.json",
            "unified_agent"
        )
        
        assert len(tools) > 0
        print(f"\n动态加载的工具: {[t.name for t in tools]}")
    
    def test_builtin_tools_loading(self):
        """测试内置工具加载"""
        from src.agents.shared.tools import get_tools
        
        tools = get_tools(["time", "calculator", "search"])
        assert len(tools) == 3
        
        tool_names = [t.name for t in tools]
        assert "time" in tool_names
        assert "calculator" in tool_names
        assert "search" in tool_names
    
    def test_agent_specific_tools(self):
        """测试智能体特定工具"""
        from src.agents.shared.tools import get_tools_for_agent
        
        # 加载unified_agent的工具
        unified_tools = get_tools_for_agent("unified_agent")
        assert len(unified_tools) > 0
        
        # 加载supply_chain_agent的工具
        supply_chain_tools = get_tools_for_agent("supply_chain_agent")
        assert len(supply_chain_tools) > 0
        
        print(f"\nUnified Agent工具: {[t.name for t in unified_tools]}")
        print(f"Supply Chain Agent工具: {[t.name for t in supply_chain_tools]}")
    
    def test_tool_configuration_validation(self):
        """测试工具配置验证"""
        loader = DynamicToolLoader()
        
        errors = loader.validate_config("config/tools/tools_config.json")
        
        if errors:
            print(f"\n配置验证发现问题: {errors}")
        else:
            print("\n工具配置验证通过")


class TestEndToEndWorkflows:
    """端到端工作流测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试智能体"""
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_e2e"
        )
        yield agent
        agent.clear_memory()
    
    def test_complete_conversation_workflow(self, agent):
        """测试完整对话工作流"""
        # 步骤1：初始化对话
        response1 = agent.run("你好，我需要帮助")
        assert response1 is not None
        print(f"\n步骤1 - 初始化: {response1['response'][:100]}...")
        
        # 步骤2：提供上下文
        response2 = agent.run("我在一家制造企业工作，负责供应链管理")
        assert response2 is not None
        print(f"\n步骤2 - 上下文: {response2['response'][:100]}...")
        
        # 步骤3：提出具体问题
        response3 = agent.run("我们的库存周转率很低，怎么优化？")
        assert response3 is not None
        print(f"\n步骤3 - 问题: {response3['response'][:100]}...")
        
        # 步骤4：深入讨论
        response4 = agent.run("能给出具体的实施步骤吗？")
        assert response4 is not None
        print(f"\n步骤4 - 深入: {response4['response'][:100]}...")
        
        # 验证记忆
        memory = agent.get_memory()
        assert len(memory) >= 8  # 4轮对话
        print(f"\n完整工作流记忆条数: {len(memory)}")
    
    def test_tool_chain_workflow(self, agent):
        """测试工具链工作流"""
        # 步骤1：获取时间
        response1 = agent.run("现在几点？")
        assert response1 is not None
        
        # 步骤2：执行计算
        response2 = agent.run("计算从现在到下午5点还有多长时间")
        assert response2 is not None
        
        # 步骤3：搜索信息
        response3 = agent.run("搜索时间管理技巧")
        assert response3 is not None
        
        print("\n工具链工作流完成")
    
    def test_error_recovery_workflow(self, agent):
        """测试错误恢复工作流"""
        # 步骤1：正常查询
        response1 = agent.run("正常查询")
        assert response1 is not None
        
        # 步骤2：可能导致错误的查询
        response2 = agent.run("!!!!!无效查询!!!!!")
        assert response2 is not None  # 应该有响应，即使处理了错误
        
        # 步骤3：恢复正常
        response3 = agent.run("继续正常对话")
        assert response3 is not None
        
        print("\n错误恢复工作流完成")
    
    def test_multi_session_workflow(self):
        """测试多会话工作流"""
        # 创建多个会话
        agents = []
        for i in range(3):
            agent = UnifiedAgent(
                provider="siliconflow",
                memory=True,
                session_id=f"workflow_session_{i}"
            )
            agents.append(agent)
        
        # 在每个会话中运行独立对话
        for i, agent in enumerate(agents):
            response = agent.run(f"这是会话{i}的消息")
            assert response is not None
        
        # 验证会话隔离
        for i, agent in enumerate(agents):
            memory = agent.get_memory()
            assert len(memory) > 0
            
            messages = [msg.content for msg in memory]
            assert any(f"会话{i}" in msg for msg in messages)
        
        # 清理
        for agent in agents:
            agent.clear_memory()
        
        print("\n多会话工作流完成")


class TestSystemHealth:
    """系统健康检查测试"""
    
    def test_config_files_exist(self):
        """测试配置文件存在性"""
        required_configs = [
            "config/base/agents.yaml",
            "config/base/services.yaml",
            "config/base/prompts.yaml",
            "config/base/logging.yaml",
            "config/tools/tools_config.json"
        ]
        
        for config_file in required_configs:
            assert os.path.exists(config_file), f"配置文件不存在: {config_file}"
    
    def test_environment_setup(self):
        """测试环境设置"""
        # 检查关键环境变量
        assert os.getenv("SILICONFLOW_API_KEY") is not None, \
            "SILICONFLOW_API_KEY未设置"
    
    def test_dependencies_import(self):
        """测试依赖导入"""
        try:
            import langchain
            import redis
            import yaml
            import pydantic
            print("\n所有依赖导入成功")
        except ImportError as e:
            pytest.fail(f"依赖导入失败: {str(e)}")
    
    def test_project_structure(self):
        """测试项目结构"""
        required_dirs = [
            "src/agents",
            "src/config",
            "src/infrastructure",
            "src/storage",
            "src/tools",
            "config/base",
            "config/environments",
            "tests"
        ]
        
        for directory in required_dirs:
            assert os.path.isdir(directory), f"目录不存在: {directory}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

