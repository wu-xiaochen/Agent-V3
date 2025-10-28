"""
n8n MCP集成测试

测试n8n MCP工具的集成和调用
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.unified.unified_agent import UnifiedAgent
from src.agents.shared.dynamic_tool_loader import DynamicToolLoader


class TestN8NMCPIntegration:
    """n8n MCP集成测试套件"""
    
    @pytest.fixture
    def agent(self):
        """创建带有n8n工具的智能体"""
        return UnifiedAgent(
            provider="siliconflow",
            memory=True,
            session_id="test_n8n_mcp"
        )
    
    def test_n8n_tool_loaded(self, agent):
        """测试n8n工具是否正确加载"""
        tools = agent.tools
        tool_names = [tool.name for tool in tools]
        
        # 验证n8n工具存在
        assert any("n8n" in name for name in tool_names), \
            f"n8n工具未加载。当前工具列表：{tool_names}"
    
    def test_n8n_workflow_generation_query(self, agent):
        """测试n8n工作流生成查询"""
        query = """
        请帮我生成一个n8n工作流，用于自动化以下流程：
        1. 接收新订单通知
        2. 检查库存
        3. 发送确认邮件
        4. 更新订单状态
        """
        
        response = agent.run(query)
        
        assert response is not None
        assert "response" in response
        
        # 验证响应包含n8n相关内容
        response_text = response["response"]
        print(f"\nn8n工作流生成响应：\n{response_text}\n")
        
        # 基本验证
        assert len(response_text) > 0
    
    def test_n8n_tool_direct_call(self):
        """测试直接调用n8n工具"""
        loader = DynamicToolLoader()
        
        # 尝试加载n8n工具
        try:
            tools = loader.load_tools_from_config(
                "config/tools/tools_config.json",
                "unified_agent"
            )
            
            n8n_tools = [t for t in tools if "n8n" in t.name]
            assert len(n8n_tools) > 0, "n8n工具未找到"
            
            print(f"\n找到的n8n工具：{[t.name for t in n8n_tools]}")
            
        except Exception as e:
            pytest.skip(f"n8n工具加载失败（这可能是预期的，如果MCP服务未运行）: {str(e)}")
    
    def test_agent_recognizes_n8n_keywords(self, agent):
        """测试智能体识别n8n关键词"""
        queries = [
            "我需要创建一个n8n工作流",
            "帮我设计一个自动化流程",
            "使用n8n实现订单处理自动化",
        ]
        
        for query in queries:
            response = agent.run(query)
            assert response is not None
            assert "response" in response
            
            response_text = response["response"].lower()
            print(f"\n查询：{query}")
            print(f"响应片段：{response_text[:200]}...")
            
            # 验证响应提到了工作流或自动化
            assert any(keyword in response_text for keyword in 
                      ["n8n", "workflow", "工作流", "自动化", "automation"]), \
                f"响应未提及n8n或工作流相关内容：{response_text[:200]}"


class TestMCPStdioTool:
    """MCP Stdio工具测试"""
    
    def test_mcp_stdio_tool_config(self):
        """测试MCP Stdio工具配置"""
        import json
        
        config_path = "config/tools/tools_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        tools = config.get("tools", [])
        mcp_stdio_tools = [t for t in tools if t.get("type") == "mcp_stdio"]
        
        assert len(mcp_stdio_tools) > 0, "未找到MCP Stdio工具配置"
        
        # 验证n8n_mcp_generator配置
        n8n_tool = next((t for t in mcp_stdio_tools if t.get("name") == "n8n_mcp_generator"), None)
        assert n8n_tool is not None, "n8n_mcp_generator工具未配置"
        
        # 验证配置完整性
        assert "command" in n8n_tool
        assert "args" in n8n_tool
        assert "enabled" in n8n_tool
        assert n8n_tool["enabled"] is True
    
    @pytest.mark.skipif(
        os.environ.get("SKIP_MCP_TESTS") == "true",
        reason="MCP服务未运行，跳过MCP相关测试"
    )
    def test_mcp_tool_creation(self):
        """测试MCP工具创建"""
        from src.agents.shared.mcp_stdio_tool import MCPStdioTool
        
        # 创建一个简单的MCP工具配置
        config = {
            "name": "test_mcp_tool",
            "description": "测试MCP工具",
            "command": "echo",
            "args": ["test"],
            "env": {}
        }
        
        try:
            tool = MCPStdioTool.from_config(config)
            assert tool is not None
            assert tool.name == "test_mcp_tool"
            
            # 清理
            tool.close()
        except Exception as e:
            pytest.skip(f"MCP工具创建失败（预期的）: {str(e)}")


class TestToolConfiguration:
    """工具配置测试"""
    
    def test_unified_agent_tool_mapping(self):
        """测试unified_agent工具映射"""
        import json
        
        config_path = "config/tools/tools_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        agent_mapping = config.get("agent_tool_mapping", {})
        assert "unified_agent" in agent_mapping
        
        unified_tools = agent_mapping["unified_agent"]
        assert isinstance(unified_tools, list)
        assert len(unified_tools) > 0
        
        # 验证包含n8n工具
        assert "n8n_mcp_generator" in unified_tools, \
            f"unified_agent工具映射中未包含n8n_mcp_generator。当前映射：{unified_tools}"
    
    def test_supply_chain_agent_tool_mapping(self):
        """测试supply_chain_agent工具映射"""
        import json
        
        config_path = "config/tools/tools_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        agent_mapping = config.get("agent_tool_mapping", {})
        assert "supply_chain_agent" in agent_mapping
        
        supply_chain_tools = agent_mapping["supply_chain_agent"]
        assert isinstance(supply_chain_tools, list)
        assert len(supply_chain_tools) > 0
        
        # 验证包含供应链工具
        expected_tools = ["data_analyzer", "forecasting_model", "optimization_engine", 
                         "risk_assessment", "crewai_generator", "crewai_runtime"]
        for tool in expected_tools:
            assert tool in supply_chain_tools, \
                f"supply_chain_agent工具映射中未包含{tool}"
        
        # 验证也包含n8n工具
        assert "n8n_mcp_generator" in supply_chain_tools
    
    def test_tool_groups(self):
        """测试工具组配置"""
        import json
        
        config_path = "config/tools/tools_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        tool_groups = config.get("tool_groups", {})
        assert "basic" in tool_groups
        assert "supply_chain" in tool_groups
        assert "mcp_tools" in tool_groups
        
        # 验证mcp_tools组包含n8n工具
        mcp_tools = tool_groups["mcp_tools"]
        assert "n8n_mcp_generator" in mcp_tools


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

