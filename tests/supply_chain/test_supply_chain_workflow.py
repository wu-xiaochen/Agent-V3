"""
供应链智能体完整业务流程测试

测试供应链智能体的完整业务流程，包括：
1. 需求分析
2. 业务流程规划
3. 流程确认与调整
4. CrewAI团队配置生成
5. n8n工作流生成
6. 用户引导与执行
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.unified.unified_agent import UnifiedAgent
from src.config.config_loader import config_loader


class TestSupplyChainWorkflow:
    """供应链业务流程测试套件"""
    
    @pytest.fixture
    def agent(self):
        """创建统一智能体实例"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_supply_chain_workflow"
        )
    
    def test_agent_initialization(self, agent):
        """测试智能体初始化"""
        assert agent is not None
        assert agent.llm is not None
        assert agent.tools is not None
        assert len(agent.tools) > 0
        assert agent.memory is not None
    
    def test_supply_chain_planning_query(self, agent):
        """测试供应链规划查询"""
        query = """
        我们是一家中型制造企业，目前面临以下供应链挑战：
        1. 库存周转率低，积压严重
        2. 供应商交货不稳定
        3. 需求预测准确率低
        
        请帮我规划一个优化方案。
        """
        
        response = agent.run(query)
        
        assert response is not None
        assert "response" in response
        assert "metadata" in response
        assert len(response["response"]) > 0
        
        # 验证响应包含关键要素
        response_text = response["response"].lower()
        assert any(keyword in response_text for keyword in ["库存", "供应商", "预测", "规划", "优化"])
    
    def test_workflow_automation_query(self, agent):
        """测试工作流自动化查询"""
        query = """
        我需要创建一个n8n工作流来自动化采购订单审批流程。
        流程应该包括：提交申请 -> 部门审批 -> 财务审核 -> 发送订单。
        """
        
        response = agent.run(query)
        
        assert response is not None
        assert "response" in response
        
        # 验证响应包含n8n相关内容
        response_text = response["response"].lower()
        assert any(keyword in response_text for keyword in ["n8n", "工作流", "workflow", "自动化"])
    
    def test_crewai_generation_query(self, agent):
        """测试CrewAI团队配置生成查询"""
        query = """
        根据我们的供应链优化需求，请生成一个CrewAI团队配置。
        团队应该包括：数据分析师、采购专家、库存管理师。
        """
        
        response = agent.run(query)
        
        assert response is not None
        assert "response" in response
        
        # 验证响应包含CrewAI相关内容
        response_text = response["response"].lower()
        assert any(keyword in response_text for keyword in ["crewai", "团队", "配置", "智能体"])
    
    def test_multi_turn_conversation(self, agent):
        """测试多轮对话"""
        # 第一轮：提出需求
        query1 = "我需要优化我们的库存管理系统"
        response1 = agent.run(query1)
        assert response1 is not None
        
        # 第二轮：追问细节
        query2 = "具体应该从哪些方面入手？"
        response2 = agent.run(query2)
        assert response2 is not None
        
        # 第三轮：请求生成配置
        query3 = "帮我生成一个相应的CrewAI团队配置"
        response3 = agent.run(query3)
        assert response3 is not None
        
        # 验证对话历史
        memory = agent.get_memory()
        assert len(memory) >= 6  # 至少3轮对话（用户+助手 各3条）
    
    def test_tool_availability(self, agent):
        """测试工具可用性"""
        tools = agent.tools
        tool_names = [tool.name for tool in tools]
        
        # 验证基础工具
        assert "time" in tool_names or "search" in tool_names or "calculator" in tool_names
        
        # 验证n8n工具存在
        assert "n8n_mcp_generator" in tool_names or any("n8n" in name for name in tool_names)
    
    def test_redis_memory(self, agent):
        """测试Redis记忆功能"""
        session_id = "test_redis_memory"
        query = "记住这个信息：我们的主要供应商是ABC公司"
        
        response = agent.run(query, session_id=session_id)
        assert response is not None
        
        # 清除并重新创建智能体，测试记忆持久化
        agent.clear_memory()
        
        query2 = "我们的主要供应商是谁？"
        response2 = agent.run(query2, session_id=session_id)
        assert response2 is not None
    
    def test_error_handling(self, agent):
        """测试错误处理"""
        # 测试空查询
        response = agent.run("")
        assert response is not None
        assert "response" in response
        
        # 测试无效查询
        response = agent.run("无意义的字符串 !@#$%^&*()")
        assert response is not None
        assert "response" in response


class TestSupplyChainTools:
    """供应链工具测试套件"""
    
    def test_data_analyzer_tool(self):
        """测试数据分析工具"""
        from src.tools.supply_chain_tools import DataAnalyzerTool
        
        tool = DataAnalyzerTool()
        assert tool is not None
        assert tool.name == "data_analyzer"
        
        # 测试工具调用
        result = tool._run("分析销售数据")
        assert result is not None
        assert isinstance(result, str)
    
    def test_forecasting_model_tool(self):
        """测试预测模型工具"""
        from src.tools.supply_chain_tools import ForecastingModelTool
        
        tool = ForecastingModelTool()
        assert tool is not None
        assert tool.name == "forecasting_model"
        
        # 测试工具调用
        result = tool._run("预测下个月需求")
        assert result is not None
        assert isinstance(result, str)
    
    def test_optimization_engine_tool(self):
        """测试优化引擎工具"""
        from src.tools.supply_chain_tools import OptimizationEngineTool
        
        tool = OptimizationEngineTool()
        assert tool is not None
        assert tool.name == "optimization_engine"
        
        # 测试工具调用
        result = tool._run("优化库存策略")
        assert result is not None
        assert isinstance(result, str)
    
    def test_risk_assessment_tool(self):
        """测试风险评估工具"""
        from src.tools.supply_chain_tools import RiskAssessmentTool
        
        tool = RiskAssessmentTool()
        assert tool is not None
        assert tool.name == "risk_assessment"
        
        # 测试工具调用
        result = tool._run("评估供应商风险")
        assert result is not None
        assert isinstance(result, str)
    
    def test_crewai_generator_tool(self):
        """测试CrewAI生成器工具"""
        from src.tools.crewai_generator import CrewAIGeneratorTool
        
        tool = CrewAIGeneratorTool()
        assert tool is not None
        assert tool.name == "crewai_generator"


class TestConfiguration:
    """配置测试套件"""
    
    def test_agents_config(self):
        """测试智能体配置"""
        config = config_loader.get_agents_config()
        assert config is not None
        assert "agents" in config
        
        # 验证supply_chain_agent配置
        agents = config["agents"]
        assert "supply_chain_agent" in agents
        
        supply_chain_config = agents["supply_chain_agent"]
        assert "model" in supply_chain_config
        assert "tools" in supply_chain_config
        assert "memory" in supply_chain_config
    
    def test_prompts_config(self):
        """测试提示词配置"""
        config = config_loader.get_prompts_config()
        assert config is not None
        assert "prompts" in config
        
        prompts = config["prompts"]
        assert "supply_chain_planning" in prompts
        assert "crewai_generation" in prompts
        assert "user_guidance" in prompts
    
    def test_services_config(self):
        """测试服务配置"""
        config = config_loader.get_services_config()
        assert config is not None
        assert "services" in config
        
        services = config["services"]
        assert "llm" in services
        assert "redis" in services
        assert "crewai" in services
    
    def test_redis_config(self):
        """测试Redis配置"""
        config = config_loader.get_redis_config()
        assert config is not None
        assert "host" in config
        assert "port" in config
        assert "db" in config
    
    def test_tools_config(self):
        """测试工具配置"""
        config = config_loader.get_tools_config()
        assert config is not None


class TestIntegration:
    """集成测试套件"""
    
    @pytest.fixture
    def agent(self):
        """创建智能体实例"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_integration"
        )
    
    def test_end_to_end_supply_chain_workflow(self, agent):
        """端到端供应链工作流测试"""
        # 步骤1：需求分析
        query1 = "我们需要优化供应链管理，主要问题是库存积压和交货延迟"
        response1 = agent.run(query1)
        assert response1 is not None
        print(f"\n步骤1 - 需求分析响应：{response1['response'][:200]}...")
        
        # 步骤2：请求详细规划
        query2 = "请给出详细的优化方案"
        response2 = agent.run(query2)
        assert response2 is not None
        print(f"\n步骤2 - 详细规划响应：{response2['response'][:200]}...")
        
        # 步骤3：请求CrewAI配置
        query3 = "根据这个方案，生成一个CrewAI团队配置"
        response3 = agent.run(query3)
        assert response3 is not None
        print(f"\n步骤3 - CrewAI配置响应：{response3['response'][:200]}...")
        
        # 步骤4：请求n8n工作流
        query4 = "同时帮我生成一个n8n工作流来自动化采购流程"
        response4 = agent.run(query4)
        assert response4 is not None
        print(f"\n步骤4 - n8n工作流响应：{response4['response'][:200]}...")
        
        # 验证整个流程
        memory = agent.get_memory()
        assert len(memory) >= 8  # 4轮对话，每轮2条消息
        
        # 清理
        agent.clear_memory()
    
    def test_concurrent_sessions(self):
        """测试并发会话"""
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
        
        # 两个会话独立运行
        response1 = agent1.run("我是会话1，需要优化库存")
        response2 = agent2.run("我是会话2，需要评估风险")
        
        assert response1 is not None
        assert response2 is not None
        
        # 验证会话隔离
        memory1 = agent1.get_memory()
        memory2 = agent2.get_memory()
        
        assert len(memory1) > 0
        assert len(memory2) > 0
        
        # 清理
        agent1.clear_memory()
        agent2.clear_memory()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

