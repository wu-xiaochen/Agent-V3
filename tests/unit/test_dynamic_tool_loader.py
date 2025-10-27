"""
动态工具加载器测试用例
验证工具配置系统的功能
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.agents.shared.dynamic_tool_loader import DynamicToolLoader
from src.agents.shared.tool_config_models import (
    ToolType, AuthType, ToolsConfiguration,
    BuiltinToolConfig, APIToolConfig, MCPToolConfig
)
from src.agents.shared.tools import get_tools, get_tools_for_agent


class TestToolConfigModels:
    """测试工具配置数据模型"""
    
    def test_builtin_tool_config(self):
        """测试内置工具配置模型"""
        config = BuiltinToolConfig(
            name="test_tool",
            description="测试工具",
            enabled=True,
            parameters={"param1": "value1"}
        )
        assert config.name == "test_tool"
        assert config.description == "测试工具"
        assert config.enabled is True
        assert config.parameters["param1"] == "value1"
    
    def test_api_tool_config(self):
        """测试API工具配置模型"""
        config = APIToolConfig(
            name="test_api",
            description="测试API工具",
            url="https://api.example.com/test",
            method="POST",
            auth_type=AuthType.BEARER,
            auth_config={"token": "test_token"},
            headers={"Content-Type": "application/json"},
            response_mapping={"result": "$.data"}
        )
        assert config.name == "test_api"
        assert config.url == "https://api.example.com/test"
        assert config.method == "POST"
        assert config.auth_type == AuthType.BEARER
        assert config.auth_config["token"] == "test_token"
        assert config.response_mapping["result"] == "$.data"
    
    def test_mcp_tool_config(self):
        """测试MCP工具配置模型"""
        config = MCPToolConfig(
            name="test_mcp",
            description="测试MCP工具",
            server_url="http://localhost:3000",
            tool_name="test_tool",
            auth_type=AuthType.API_KEY,
            auth_config={"key": "test_key"}
        )
        assert config.name == "test_mcp"
        assert config.server_url == "http://localhost:3000"
        assert config.tool_name == "test_tool"
        assert config.auth_type == AuthType.API_KEY
        assert config.auth_config["key"] == "test_key"
    
    def test_tools_configuration(self):
        """测试完整工具配置模型"""
        config = ToolsConfiguration(
            version="1.0",
            description="测试配置",
            tools=[
                BuiltinToolConfig(
                    name="time",
                    description="时间工具",
                    enabled=True
                ),
                APIToolConfig(
                    name="weather",
                    description="天气API",
                    url="https://api.weather.com",
                    method="GET"
                ),
                MCPToolConfig(
                    name="n8n_tool",
                    description="N8N工具",
                    server_url="http://localhost:5678",
                    tool_name="workflow"
                )
            ],
            tool_groups={
                "basic": ["time"],
                "external": ["weather", "n8n_tool"]
            },
            agent_tool_mapping={
                "unified_agent": ["time", "weather"],
                "api_agent": ["weather", "n8n_tool"]
            }
        )
        
        assert len(config.tools) == 3
        assert config.get_tool("time") is not None
        assert config.get_tool("weather") is not None
        assert config.get_tool("n8n_tool") is not None
        assert config.get_tool("nonexistent") is None
        
        assert config.get_tools_for_agent("unified_agent") == ["time", "weather"]
        assert config.get_tools_for_agent("api_agent") == ["weather", "n8n_tool"]
        assert config.get_tools_for_agent("unknown_agent") == []
    
    def test_config_validation(self):
        """测试配置验证"""
        # 有效配置
        valid_config = {
            "version": "1.0",
            "description": "有效配置",
            "tools": [
                {
                    "type": "builtin",
                    "name": "time",
                    "description": "时间工具",
                    "enabled": True
                }
            ]
        }
        config = ToolsConfiguration(**valid_config)
        assert config.version == "1.0"
        
        # 无效配置（缺少必需字段）
        invalid_config = {
            "version": "1.0",
            "tools": [
                {
                    "type": "builtin",
                    # 缺少name字段
                }
            ]
        }
        with pytest.raises(Exception):
            ToolsConfiguration(**invalid_config)


class TestDynamicToolLoader:
    """测试动态工具加载器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        
        # 创建测试配置文件
        test_config = {
            "version": "1.0",
            "description": "测试配置",
            "tools": [
                {
                    "type": "builtin",
                    "name": "time",
                    "description": "时间工具",
                    "enabled": True
                },
                {
                    "type": "api",
                    "name": "test_api",
                    "description": "测试API",
                    "url": "https://api.example.com/test",
                    "method": "GET",
                    "auth_type": "none"
                }
            ],
            "tool_groups": {
                "basic": ["time"],
                "external": ["test_api"]
            },
            "agent_tool_mapping": {
                "test_agent": ["time", "test_api"]
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
    
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)
    
    def test_load_from_file(self):
        """测试从文件加载配置"""
        loader = DynamicToolLoader()
        config = loader.load_from_file(self.config_path)
        
        assert config.version == "1.0"
        assert len(config.tools) == 2
        assert config.get_tool("time") is not None
        assert config.get_tool("test_api") is not None
    
    def test_load_builtin_tool(self):
        """测试加载内置工具"""
        loader = DynamicToolLoader()
        tool_config = BuiltinToolConfig(
            name="time",
            description="时间工具",
            enabled=True
        )
        
        tool = loader.load_tool(tool_config)
        assert tool is not None
        assert tool.name == "time"
    
    @patch('src.agents.shared.api_tool.APITool')
    def test_load_api_tool(self, mock_api_tool):
        """测试加载API工具"""
        mock_tool_instance = MagicMock()
        mock_tool_instance.name = "test_api"
        mock_api_tool.from_config.return_value = mock_tool_instance
        
        loader = DynamicToolLoader()
        tool_config = APIToolConfig(
            name="test_api",
            description="测试API",
            url="https://api.example.com/test",
            method="GET",
            auth_type=AuthType.NONE
        )
        
        tool = loader.load_tool(tool_config)
        assert tool is not None
        assert tool.name == "test_api"
        mock_api_tool.from_config.assert_called_once_with(tool_config)
    
    @patch('src.agents.shared.mcp_tool.MCPTool')
    def test_load_mcp_tool(self, mock_mcp_tool):
        """测试加载MCP工具"""
        mock_tool_instance = MagicMock()
        mock_tool_instance.name = "test_mcp"
        mock_mcp_tool.from_config.return_value = mock_tool_instance
        
        loader = DynamicToolLoader()
        tool_config = MCPToolConfig(
            name="test_mcp",
            description="测试MCP工具",
            server_url="http://localhost:3000",
            tool_name="test_tool",
            auth_type=AuthType.NONE
        )
        
        tool = loader.load_tool(tool_config)
        assert tool is not None
        assert tool.name == "test_mcp"
        mock_mcp_tool.from_config.assert_called_once_with(tool_config)
    
    def test_load_tools_for_agent(self):
        """测试为智能体加载工具"""
        loader = DynamicToolLoader()
        tools = loader.load_tools_for_agent(self.config_path, "test_agent")
        
        # 应该返回2个工具（time和test_api）
        assert len(tools) == 2
    
    def test_resolve_env_vars(self):
        """测试环境变量解析"""
        loader = DynamicToolLoader()
        
        # 设置测试环境变量
        os.environ["TEST_VAR"] = "test_value"
        
        config_with_env = {
            "url": "https://api.example.com/${TEST_VAR}",
            "auth_config": {
                "token": "${TEST_VAR}"
            }
        }
        
        resolved = loader._resolve_env_vars(config_with_env)
        
        assert resolved["url"] == "https://api.example.com/test_value"
        assert resolved["auth_config"]["token"] == "test_value"
        
        # 清理环境变量
        del os.environ["TEST_VAR"]
    
    def test_validate_tool_config(self):
        """测试工具配置验证"""
        loader = DynamicToolLoader()
        
        # 有效配置
        valid_config = {
            "type": "builtin",
            "name": "time",
            "description": "时间工具",
            "enabled": True
        }
        assert loader.validate_tool_config(valid_config) is True
        
        # 无效配置（缺少type）
        invalid_config = {
            "name": "time",
            "description": "时间工具",
            "enabled": True
        }
        assert loader.validate_tool_config(invalid_config) is False


class TestToolsIntegration:
    """测试工具集成"""
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "integration_test_config.json")
        
        # 创建测试配置文件
        test_config = {
            "version": "1.0",
            "description": "集成测试配置",
            "tools": [
                {
                    "type": "builtin",
                    "name": "time",
                    "description": "时间工具",
                    "enabled": True
                },
                {
                    "type": "builtin",
                    "name": "calculator",
                    "description": "计算器工具",
                    "enabled": True
                }
            ],
            "tool_groups": {
                "basic": ["time", "calculator"]
            },
            "agent_tool_mapping": {
                "integration_test_agent": ["time", "calculator"]
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
    
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)
    
    def test_get_tools_with_config(self):
        """测试使用配置文件获取工具"""
        tools = get_tools(config_path=self.config_path)
        
        # 应该返回2个工具（time和calculator）
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "time" in tool_names
        assert "calculator" in tool_names
    
    def test_get_tools_for_agent(self):
        """测试为特定智能体获取工具"""
        tools = get_tools_for_agent("integration_test_agent", self.config_path)
        
        # 应该返回2个工具（time和calculator）
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "time" in tool_names
        assert "calculator" in tool_names
    
    def test_fallback_to_default_tools(self):
        """测试回退到默认工具"""
        # 使用不存在的配置文件
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        
        # 应该回退到默认工具
        tools = get_tools(config_path=nonexistent_path)
        assert len(tools) > 0  # 默认工具列表不为空
    
    def test_agent_not_in_mapping(self):
        """测试智能体不在映射中的情况"""
        tools = get_tools_for_agent("unknown_agent", self.config_path)
        
        # 应该返回空列表
        assert len(tools) == 0


if __name__ == "__main__":
    pytest.main([__file__])