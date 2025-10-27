"""
MCP工具测试用例
验证MCP工具的功能
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from src.agents.shared.mcp_tool import MCPTool
from src.agents.shared.tool_config_models import MCPToolConfig, AuthType


class TestMCPTool:
    """测试MCP工具"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = MCPToolConfig(
            name="test_mcp",
            description="测试MCP工具",
            server_url="http://localhost:3000",
            tool_name="test_tool",
            auth_type=AuthType.NONE,
            response_mapping={"result": "$.data"}
        )
        
        self.auth_config = MCPToolConfig(
            name="auth_mcp",
            description="认证MCP工具",
            server_url="http://localhost:3000",
            tool_name="auth_tool",
            auth_type=AuthType.BEARER,
            auth_config={"token": "test_token"}
        )
        
        self.api_key_config = MCPToolConfig(
            name="api_key_mcp",
            description="API密钥MCP工具",
            server_url="http://localhost:3000",
            tool_name="api_key_tool",
            auth_type=AuthType.API_KEY,
            auth_config={"key": "test_api_key", "header": "X-API-Key"}
        )
    
    def test_from_config(self):
        """测试从配置创建MCP工具"""
        tool = MCPTool.from_config(self.config)
        assert tool.name == "test_mcp"
        assert tool.server_url == "http://localhost:3000"
        assert tool.tool_name == "test_tool"
        assert tool.auth_type == AuthType.NONE
        assert tool.response_mapping["result"] == "$.data"
    
    def test_bearer_auth_setup(self):
        """测试Bearer认证设置"""
        tool = MCPTool.from_config(self.auth_config)
        assert tool.auth_type == AuthType.BEARER
        assert tool.auth_config["token"] == "test_token"
    
    def test_api_key_auth_setup(self):
        """测试API密钥认证设置"""
        tool = MCPTool.from_config(self.api_key_config)
        assert tool.auth_type == AuthType.API_KEY
        assert tool.auth_config["key"] == "test_api_key"
        assert tool.auth_config["header"] == "X-API-Key"
    
    @patch('requests.post')
    def test_sync_call_no_auth(self, mock_post):
        """测试无认证的同步调用"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Tool execution result"
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        expected_payload = {
            "name": "test_tool",
            "arguments": {"param1": "value1"}
        }
        mock_post.assert_called_once_with(
            url="http://localhost:3000/call",
            headers={"Content-Type": "application/json"},
            json=expected_payload,
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "Tool execution result"
    
    @patch('requests.post')
    def test_sync_call_bearer_auth(self, mock_post):
        """测试Bearer认证的同步调用"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Authenticated tool execution result"
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.auth_config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"
        }
        expected_payload = {
            "name": "auth_tool",
            "arguments": {"param1": "value1"}
        }
        mock_post.assert_called_once_with(
            url="http://localhost:3000/call",
            headers=expected_headers,
            json=expected_payload,
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "Authenticated tool execution result"
    
    @patch('requests.post')
    def test_sync_call_api_key_auth(self, mock_post):
        """测试API密钥认证的同步调用"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "API key authenticated tool execution result"
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.api_key_config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        expected_headers = {
            "Content-Type": "application/json",
            "X-API-Key": "test_api_key"
        }
        expected_payload = {
            "name": "api_key_tool",
            "arguments": {"param1": "value1"}
        }
        mock_post.assert_called_once_with(
            url="http://localhost:3000/call",
            headers=expected_headers,
            json=expected_payload,
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "API key authenticated tool execution result"
    
    @patch('requests.post')
    def test_sync_call_error_handling(self, mock_post):
        """测试同步调用错误处理"""
        # 模拟请求异常
        mock_post.side_effect = Exception("Connection error")
        
        tool = MCPTool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert result["error"] == "Connection error"
    
    @patch('requests.post')
    def test_sync_call_http_error(self, mock_post):
        """测试HTTP错误处理"""
        # 模拟HTTP错误响应
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert "404 Not Found" in result["error"]
    
    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_async_call_no_auth(self, mock_post):
        """测试无认证的异步调用"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Async tool execution result"
                    }
                ]
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        result = await tool._arun(param1="value1")
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "Async tool execution result"
    
    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_async_call_bearer_auth(self, mock_post):
        """测试Bearer认证的异步调用"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Async authenticated tool execution result"
                    }
                ]
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        tool = MCPTool.from_config(self.auth_config)
        result = await tool._arun(param1="value1")
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "Async authenticated tool execution result"
    
    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_async_call_error_handling(self, mock_post):
        """测试异步调用错误处理"""
        # 模拟请求异常
        mock_post.side_effect = Exception("Connection error")
        
        tool = MCPTool.from_config(self.config)
        result = await tool._arun(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert result["error"] == "Connection error"
    
    @patch('requests.post')
    def test_complex_response_handling(self, mock_post):
        """测试复杂响应处理"""
        # 模拟复杂响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "First result"
                    },
                    {
                        "type": "text",
                        "text": "Second result"
                    },
                    {
                        "type": "image",
                        "data": "base64_image_data"
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证结果
        assert "result" in result
        assert "First result" in result["result"]
        assert "Second result" in result["result"]
        # 默认情况下，非文本内容可能被忽略或特殊处理
    
    @patch('requests.post')
    def test_empty_response_handling(self, mock_post):
        """测试空响应处理"""
        # 模拟空响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "content": []
            }
        }
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证结果
        assert "result" in result
        assert result["result"] == ""
    
    @patch('requests.post')
    def test_malformed_response_handling(self, mock_post):
        """测试格式错误的响应处理"""
        # 模拟格式错误的响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                # 缺少content字段
            }
        }
        mock_post.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证错误处理
        assert "error" in result
    
    @patch('requests.get')
    def test_discover_tools(self, mock_get):
        """测试工具发现"""
        # 模拟工具列表响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tools": [
                {
                    "name": "tool1",
                    "description": "First tool"
                },
                {
                    "name": "tool2",
                    "description": "Second tool"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        tools = tool.discover_tools()
        
        # 验证结果
        assert len(tools) == 2
        assert tools[0]["name"] == "tool1"
        assert tools[1]["name"] == "tool2"
        
        # 验证请求参数
        mock_get.assert_called_once_with(
            url="http://localhost:3000/tools",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    @patch('requests.get')
    def test_get_tool_schema(self, mock_get):
        """测试获取工具模式"""
        # 模拟工具模式响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "test_tool",
            "description": "Test tool description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    }
                },
                "required": ["param1"]
            }
        }
        mock_get.return_value = mock_response
        
        tool = MCPTool.from_config(self.config)
        schema = tool.get_tool_schema("test_tool")
        
        # 验证结果
        assert schema["name"] == "test_tool"
        assert schema["description"] == "Test tool description"
        assert "param1" in schema["inputSchema"]["properties"]
        
        # 验证请求参数
        mock_get.assert_called_once_with(
            url="http://localhost:3000/tool/test_tool/schema",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    def test_response_mapping(self):
        """测试响应映射"""
        # 创建带有复杂响应映射的配置
        complex_config = MCPToolConfig(
            name="complex_mcp",
            description="复杂MCP工具",
            server_url="http://localhost:3000",
            tool_name="complex_tool",
            auth_type=AuthType.NONE,
            response_mapping={
                "result": "$.result.content[0].text",
                "metadata": "$.metadata"
            }
        )
        
        tool = MCPTool.from_config(complex_config)
        
        # 测试响应映射函数
        response_data = {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "mapped_result"
                    }
                ]
            },
            "metadata": {
                "version": "1.0",
                "timestamp": "2023-01-01"
            }
        }
        
        mapped_result = tool._map_response(response_data)
        
        assert mapped_result["result"] == "mapped_result"
        assert mapped_result["metadata"]["version"] == "1.0"


if __name__ == "__main__":
    pytest.main([__file__])