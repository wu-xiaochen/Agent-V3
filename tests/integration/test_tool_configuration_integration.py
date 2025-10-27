"""
工具配置系统集成测试
验证整个工具配置系统的端到端功能
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from src.agents.shared.tools import get_tools, get_tools_for_agent
from src.agents.shared.dynamic_tool_loader import DynamicToolLoader


class TestToolConfigurationIntegration:
    """测试工具配置系统集成"""
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试配置文件
        self.config_path = os.path.join(self.temp_dir, "integration_config.json")
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
                },
                {
                    "type": "api",
                    "name": "weather_api",
                    "description": "天气API工具",
                    "url": "https://api.openweathermap.org/data/2.5/weather",
                    "method": "GET",
                    "auth_type": "api_key",
                    "auth_config": {
                        "key": "${WEATHER_API_KEY}",
                        "header": "X-API-Key"
                    },
                    "parameters": {
                        "q": {
                            "type": "string",
                            "description": "城市名称",
                            "required": True
                        },
                        "units": {
                            "type": "string",
                            "description": "单位系统",
                            "default": "metric"
                        }
                    },
                    "response_mapping": {
                        "temperature": "$.main.temp",
                        "description": "$.weather[0].description",
                        "city": "$.name"
                    }
                },
                {
                    "type": "mcp",
                    "name": "n8n_workflow",
                    "description": "N8N工作流工具",
                    "server_url": "http://localhost:5678",
                    "tool_name": "execute_workflow",
                    "auth_type": "bearer",
                    "auth_config": {
                        "token": "${N8N_API_TOKEN}"
                    },
                    "parameters": {
                        "workflow_id": {
                            "type": "string",
                            "description": "工作流ID",
                            "required": True
                        },
                        "data": {
                            "type": "object",
                            "description": "输入数据",
                            "default": {}
                        }
                    },
                    "response_mapping": {
                        "result": "$.result.data",
                        "execution_id": "$.executionId"
                    }
                }
            ],
            "tool_groups": {
                "basic": ["time", "calculator"],
                "external": ["weather_api", "n8n_workflow"],
                "all": ["time", "calculator", "weather_api", "n8n_workflow"]
            },
            "agent_tool_mapping": {
                "unified_agent": ["time", "calculator", "weather_api"],
                "api_agent": ["weather_api", "n8n_workflow"],
                "basic_agent": ["time", "calculator"]
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # 设置环境变量
        os.environ["WEATHER_API_KEY"] = "test_weather_key"
        os.environ["N8N_API_TOKEN"] = "test_n8n_token"
    
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)
        
        # 清理环境变量
        if "WEATHER_API_KEY" in os.environ:
            del os.environ["WEATHER_API_KEY"]
        if "N8N_API_TOKEN" in os.environ:
            del os.environ["N8N_API_TOKEN"]
    
    def test_load_all_tools(self):
        """测试加载所有工具"""
        tools = get_tools(config_path=self.config_path)
        
        # 应该返回4个工具
        assert len(tools) == 4
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "time" in tool_names
        assert "calculator" in tool_names
        assert "weather_api" in tool_names
        assert "n8n_workflow" in tool_names
    
    def test_load_tools_for_unified_agent(self):
        """测试为统一智能体加载工具"""
        tools = get_tools_for_agent("unified_agent", self.config_path)
        
        # 应该返回3个工具
        assert len(tools) == 3
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "time" in tool_names
        assert "calculator" in tool_names
        assert "weather_api" in tool_names
        assert "n8n_workflow" not in tool_names
    
    def test_load_tools_for_api_agent(self):
        """测试为API智能体加载工具"""
        tools = get_tools_for_agent("api_agent", self.config_path)
        
        # 应该返回2个工具
        assert len(tools) == 2
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "weather_api" in tool_names
        assert "n8n_workflow" in tool_names
        assert "time" not in tool_names
        assert "calculator" not in tool_names
    
    def test_load_tools_for_basic_agent(self):
        """测试为基础智能体加载工具"""
        tools = get_tools_for_agent("basic_agent", self.config_path)
        
        # 应该返回2个工具
        assert len(tools) == 2
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "time" in tool_names
        assert "calculator" in tool_names
        assert "weather_api" not in tool_names
        assert "n8n_workflow" not in tool_names
    
    def test_load_tools_for_unknown_agent(self):
        """测试为未知智能体加载工具"""
        tools = get_tools_for_agent("unknown_agent", self.config_path)
        
        # 应该返回空列表
        assert len(tools) == 0
    
    @patch('src.agents.shared.api_tool.APITool')
    def test_api_tool_integration(self, mock_api_tool):
        """测试API工具集成"""
        # 模拟API工具实例
        mock_tool_instance = MagicMock()
        mock_tool_instance.name = "weather_api"
        mock_api_tool.from_config.return_value = mock_tool_instance
        
        tools = get_tools(config_path=self.config_path)
        
        # 验证API工具被创建
        mock_api_tool.from_config.assert_called_once()
        
        # 验证工具包含在结果中
        tool_names = [tool.name for tool in tools]
        assert "weather_api" in tool_names
    
    @patch('src.agents.shared.mcp_tool.MCPTool')
    def test_mcp_tool_integration(self, mock_mcp_tool):
        """测试MCP工具集成"""
        # 模拟MCP工具实例
        mock_tool_instance = MagicMock()
        mock_tool_instance.name = "n8n_workflow"
        mock_mcp_tool.from_config.return_value = mock_tool_instance
        
        tools = get_tools(config_path=self.config_path)
        
        # 验证MCP工具被创建
        mock_mcp_tool.from_config.assert_called_once()
        
        # 验证工具包含在结果中
        tool_names = [tool.name for tool in tools]
        assert "n8n_workflow" in tool_names
    
    def test_environment_variable_resolution(self):
        """测试环境变量解析"""
        loader = DynamicToolLoader()
        config = loader.load_from_file(self.config_path)
        
        # 获取API工具配置
        weather_api = config.get_tool("weather_api")
        n8n_workflow = config.get_tool("n8n_workflow")
        
        # 验证环境变量被正确解析
        assert weather_api.auth_config["key"] == "test_weather_key"
        assert n8n_workflow.auth_config["token"] == "test_n8n_token"
    
    def test_tool_group_mapping(self):
        """测试工具组映射"""
        loader = DynamicToolLoader()
        config = loader.load_from_file(self.config_path)
        
        # 验证工具组映射
        assert config.tool_groups["basic"] == ["time", "calculator"]
        assert config.tool_groups["external"] == ["weather_api", "n8n_workflow"]
        assert config.tool_groups["all"] == ["time", "calculator", "weather_api", "n8n_workflow"]
    
    def test_invalid_config_handling(self):
        """测试无效配置处理"""
        # 创建无效配置文件
        invalid_config_path = os.path.join(self.temp_dir, "invalid_config.json")
        invalid_config = {
            "version": "1.0",
            "tools": [
                {
                    "type": "invalid_type",
                    "name": "invalid_tool"
                    # 缺少必需字段
                }
            ]
        }
        
        with open(invalid_config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        # 应该回退到默认工具
        tools = get_tools(config_path=invalid_config_path)
        assert len(tools) > 0  # 默认工具列表不为空
    
    def test_missing_config_file(self):
        """测试缺少配置文件处理"""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        
        # 应该回退到默认工具
        tools = get_tools(config_path=nonexistent_path)
        assert len(tools) > 0  # 默认工具列表不为空
    
    def test_config_validation(self):
        """测试配置验证"""
        loader = DynamicToolLoader()
        config = loader.load_from_file(self.config_path)
        
        # 验证配置有效性
        assert config.version == "1.0"
        assert len(config.tools) == 4
        
        # 验证每个工具配置
        for tool_config in config.tools:
            assert tool_config.name is not None
            assert tool_config.description is not None
            assert tool_config.type is not None
    
    def test_tool_parameter_validation(self):
        """测试工具参数验证"""
        loader = DynamicToolLoader()
        config = loader.load_from_file(self.config_path)
        
        # 获取API工具配置
        weather_api = config.get_tool("weather_api")
        
        # 验证参数配置
        assert "q" in weather_api.parameters
        assert "units" in weather_api.parameters
        assert weather_api.parameters["q"]["required"] is True
        assert weather_api.parameters["units"]["default"] == "metric"
    
    def test_response_mapping_validation(self):
        """测试响应映射验证"""
        loader = DynamicToolLoader()
        config = loader.load_from_file(self.config_path)
        
        # 获取API工具配置
        weather_api = config.get_tool("weather_api")
        
        # 验证响应映射
        assert "temperature" in weather_api.response_mapping
        assert "description" in weather_api.response_mapping
        assert "city" in weather_api.response_mapping
        assert weather_api.response_mapping["temperature"] == "$.main.temp"


class TestToolConfigurationWithRealWorldExamples:
    """测试真实世界示例的工具配置"""
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建真实世界示例配置文件
        self.config_path = os.path.join(self.temp_dir, "real_world_config.json")
        real_world_config = {
            "version": "1.0",
            "description": "真实世界示例配置",
            "tools": [
                {
                    "type": "builtin",
                    "name": "search",
                    "description": "搜索工具",
                    "enabled": True
                },
                {
                    "type": "api",
                    "name": "github_api",
                    "description": "GitHub API工具",
                    "url": "https://api.github.com",
                    "method": "GET",
                    "auth_type": "bearer",
                    "auth_config": {
                        "token": "${GITHUB_TOKEN}"
                    },
                    "parameters": {
                        "endpoint": {
                            "type": "string",
                            "description": "API端点",
                            "required": True
                        }
                    },
                    "response_mapping": {
                        "data": "$"
                    }
                },
                {
                    "type": "mcp",
                    "name": "slack_mcp",
                    "description": "Slack MCP工具",
                    "server_url": "https://slack-mcp.example.com",
                    "tool_name": "send_message",
                    "auth_type": "api_key",
                    "auth_config": {
                        "key": "${SLACK_API_KEY}",
                        "header": "Authorization"
                    },
                    "parameters": {
                        "channel": {
                            "type": "string",
                            "description": "频道ID",
                            "required": True
                        },
                        "message": {
                            "type": "string",
                            "description": "消息内容",
                            "required": True
                        }
                    },
                    "response_mapping": {
                        "success": "$.ok",
                        "timestamp": "$.ts"
                    }
                }
            ],
            "tool_groups": {
                "development": ["search", "github_api"],
                "communication": ["slack_mcp"],
                "all": ["search", "github_api", "slack_mcp"]
            },
            "agent_tool_mapping": {
                "dev_agent": ["search", "github_api"],
                "notification_agent": ["slack_mcp"],
                "full_stack_agent": ["search", "github_api", "slack_mcp"]
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(real_world_config, f)
        
        # 设置环境变量
        os.environ["GITHUB_TOKEN"] = "test_github_token"
        os.environ["SLACK_API_KEY"] = "test_slack_key"
    
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)
        
        # 清理环境变量
        if "GITHUB_TOKEN" in os.environ:
            del os.environ["GITHUB_TOKEN"]
        if "SLACK_API_KEY" in os.environ:
            del os.environ["SLACK_API_KEY"]
    
    def test_real_world_config_loading(self):
        """测试真实世界配置加载"""
        tools = get_tools(config_path=self.config_path)
        
        # 应该返回3个工具
        assert len(tools) == 3
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "search" in tool_names
        assert "github_api" in tool_names
        assert "slack_mcp" in tool_names
    
    def test_dev_agent_tools(self):
        """测试开发智能体工具"""
        tools = get_tools_for_agent("dev_agent", self.config_path)
        
        # 应该返回2个工具
        assert len(tools) == 2
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "search" in tool_names
        assert "github_api" in tool_names
        assert "slack_mcp" not in tool_names
    
    def test_notification_agent_tools(self):
        """测试通知智能体工具"""
        tools = get_tools_for_agent("notification_agent", self.config_path)
        
        # 应该返回1个工具
        assert len(tools) == 1
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "slack_mcp" in tool_names
        assert "search" not in tool_names
        assert "github_api" not in tool_names
    
    def test_full_stack_agent_tools(self):
        """测试全栈智能体工具"""
        tools = get_tools_for_agent("full_stack_agent", self.config_path)
        
        # 应该返回3个工具
        assert len(tools) == 3
        
        # 验证工具名称
        tool_names = [tool.name for tool in tools]
        assert "search" in tool_names
        assert "github_api" in tool_names
        assert "slack_mcp" in tool_names


if __name__ == "__main__":
    pytest.main([__file__])