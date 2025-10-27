"""
API工具测试用例
验证API工具的功能
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock, Mock
import requests
import aiohttp

from src.agents.shared.api_tool import APITool
from src.agents.shared.tool_config_models import APIToolConfig, AuthType


class TestAPITool:
    """测试API工具"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = APIToolConfig(
            name="test_api",
            description="测试API工具",
            endpoint="https://api.example.com/test",
            method="GET",
            headers={"Content-Type": "application/json"},
            response_mapping={"result": "$.data"}
        )
        
        self.auth_config = APIToolConfig(
            name="auth_api",
            description="认证API工具",
            endpoint="https://api.example.com/auth",
            method="POST",
            auth={"type": AuthType.BEARER, "token": "test_token"},
            headers={"Content-Type": "application/json"}
        )
        
        self.basic_auth_config = APIToolConfig(
            name="basic_auth_api",
            description="基本认证API工具",
            endpoint="https://api.example.com/basic_auth",
            method="GET",
            auth={"type": AuthType.BASIC, "username": "test_user", "password": "test_pass"}
        )
        
        self.api_key_config = APIToolConfig(
            name="api_key_auth",
            description="API密钥认证工具",
            endpoint="https://api.example.com/api_key",
            method="GET",
            auth={"type": AuthType.API_KEY, "key": "test_api_key", "additional_headers": {"api_key_header": "X-API-Key"}}
        )
    
    def test_from_config(self):
        """测试从配置创建API工具"""
        tool = APITool.from_config(self.config)
        assert tool.name == "test_api"
        assert tool.endpoint == "https://api.example.com/test"
        assert tool.method == "GET"
        assert tool.auth_type == AuthType.NONE
        assert tool.headers["Content-Type"] == "application/json"
        assert tool.response_mapping["result"] == "$.data"
    
    def test_bearer_auth_setup(self):
        """测试Bearer认证设置"""
        tool = APITool.from_config(self.auth_config)
        assert tool.auth_type == AuthType.BEARER
        assert tool.auth_config["token"] == "test_token"
    
    def test_basic_auth_setup(self):
        """测试基本认证设置"""
        tool = APITool.from_config(self.basic_auth_config)
        assert tool.auth_type == AuthType.BASIC
        assert tool.auth_config["username"] == "test_user"
        assert tool.auth_config["password"] == "test_pass"
    
    def test_api_key_auth_setup(self):
        """测试API密钥认证设置"""
        tool = APITool.from_config(self.api_key_config)
        assert tool.auth_type == AuthType.API_KEY
        assert tool.auth_config["key"] == "test_api_key"
        assert tool.auth_config["additional_headers"]["api_key_header"] == "X-API-Key"
    
    @patch('requests.request')
    def test_sync_request_no_auth(self, mock_request):
        """测试无认证的同步请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data", "status": "success"}
        mock_request.return_value = mock_response
        
        tool = APITool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.example.com/test",
            headers={"Content-Type": "application/json"},
            params={"param1": "value1"},
            json=None,
            auth=None,
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "test_data"
    
    @patch('requests.request')
    def test_sync_request_bearer_auth(self, mock_request):
        """测试Bearer认证的同步请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "auth_data", "status": "success"}
        mock_request.return_value = mock_response
        
        tool = APITool.from_config(self.auth_config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"
        }
        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.example.com/auth",
            headers=expected_headers,
            params={"param1": "value1"},
            json=None,
            auth=None,
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "auth_data"
    
    @patch('requests.request')
    def test_sync_request_basic_auth(self, mock_request):
        """测试基本认证的同步请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "basic_auth_data", "status": "success"}
        mock_request.return_value = mock_response
        
        tool = APITool.from_config(self.basic_auth_config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.example.com/basic_auth",
            headers={"Content-Type": "application/json"},
            params={"param1": "value1"},
            json=None,
            auth=("test_user", "test_pass"),
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "basic_auth_data"
    
    @patch('requests.request')
    def test_sync_request_api_key_auth(self, mock_request):
        """测试API密钥认证的同步请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "api_key_data", "status": "success"}
        mock_request.return_value = mock_response
        
        tool = APITool.from_config(self.api_key_config)
        result = tool._run(param1="value1")
        
        # 验证请求参数
        expected_headers = {
            "Content-Type": "application/json",
            "X-API-Key": "test_api_key"
        }
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.example.com/api_key",
            headers=expected_headers,
            params={"param1": "value1"},
            json=None,
            auth=None,
            timeout=30
        )
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "api_key_data"
    
    @patch('requests.request')
    def test_sync_request_error_handling(self, mock_request):
        """测试同步请求错误处理"""
        # 模拟请求异常
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        tool = APITool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert result["error"] == "Connection error"
    
    @patch('requests.request')
    def test_sync_request_http_error(self, mock_request):
        """测试HTTP错误处理"""
        # 模拟HTTP错误响应
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_request.return_value = mock_response
        
        tool = APITool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert "404 Not Found" in result["error"]
    
    @patch('requests.request')
    def test_sync_request_json_error(self, mock_request):
        """测试JSON解析错误处理"""
        # 模拟无效JSON响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_response
        
        tool = APITool.from_config(self.config)
        result = tool._run(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert "Invalid JSON" in result["error"]
    
    @patch('aiohttp.ClientSession.request')
    @pytest.mark.asyncio
    async def test_async_request_no_auth(self, mock_request):
        """测试无认证的异步请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {"data": "async_data", "status": "success"}
        mock_request.return_value.__aenter__.return_value = mock_response
        
        tool = APITool.from_config(self.config)
        result = await tool._arun(param1="value1")
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "async_data"
    
    @patch('aiohttp.ClientSession.request')
    @pytest.mark.asyncio
    async def test_async_request_bearer_auth(self, mock_request):
        """测试Bearer认证的异步请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {"data": "async_auth_data", "status": "success"}
        mock_request.return_value.__aenter__.return_value = mock_response
        
        tool = APITool.from_config(self.auth_config)
        result = await tool._arun(param1="value1")
        
        # 验证结果
        assert "result" in result
        assert result["result"] == "async_auth_data"
    
    @patch('aiohttp.ClientSession.request')
    @pytest.mark.asyncio
    async def test_async_request_error_handling(self, mock_request):
        """测试异步请求错误处理"""
        # 模拟请求异常
        mock_request.side_effect = aiohttp.ClientError("Connection error")
        
        tool = APITool.from_config(self.config)
        result = await tool._arun(param1="value1")
        
        # 验证错误处理
        assert "error" in result
        assert result["error"] == "Connection error"
    
    def test_response_mapping(self):
        """测试响应映射"""
        # 创建带有复杂响应映射的配置
        complex_config = APIToolConfig(
            name="complex_api",
            description="复杂API工具",
            url="https://api.example.com/complex",
            method="GET",
            auth_type=AuthType.NONE,
            response_mapping={
                "result": "$.data.result",
                "status": "$.status",
                "metadata": "$.metadata"
            }
        )
        
        tool = APITool.from_config(complex_config)
        
        # 测试响应映射函数
        response_data = {
            "data": {
                "result": "mapped_result",
                "details": "some_details"
            },
            "status": "success",
            "metadata": {
                "version": "1.0",
                "timestamp": "2023-01-01"
            }
        }
        
        mapped_result = tool._map_response(response_data)
        
        assert mapped_result["result"] == "mapped_result"
        assert mapped_result["status"] == "success"
        assert mapped_result["metadata"]["version"] == "1.0"
    
    def test_response_mapping_missing_field(self):
        """测试响应映射中缺少字段的情况"""
        config = APIToolConfig(
            name="missing_field_api",
            description="缺少字段API工具",
            url="https://api.example.com/missing",
            method="GET",
            auth_type=AuthType.NONE,
            response_mapping={
                "result": "$.data.result",
                "missing": "$.nonexistent.field"
            }
        )
        
        tool = APITool.from_config(config)
        
        response_data = {
            "data": {
                "result": "mapped_result"
            },
            "status": "success"
        }
        
        mapped_result = tool._map_response(response_data)
        
        assert mapped_result["result"] == "mapped_result"
        # 缺少的字段应该被忽略或设置为None
        assert "missing" not in mapped_result or mapped_result["missing"] is None
    
    def test_retry_logic(self):
        """测试重试逻辑"""
        # 创建带有重试配置的API工具
        retry_config = APIToolConfig(
            name="retry_api",
            description="重试API工具",
            url="https://api.example.com/retry",
            method="GET",
            auth_type=AuthType.NONE,
            retry_attempts=3,
            retry_delay=1
        )
        
        tool = APITool.from_config(retry_config)
        
        # 验证重试配置
        assert tool.retry_attempts == 3
        assert tool.retry_delay == 1
        
        # 注意：实际的重试逻辑测试需要更复杂的模拟，这里只是验证配置
        # 在实际应用中，可以使用unittest.mock的side_effect来模拟多次失败后成功的情况


if __name__ == "__main__":
    pytest.main([__file__])