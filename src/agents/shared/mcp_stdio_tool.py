"""
MCP Stdio工具实现
支持通过标准输入输出与MCP服务器通信
"""

import json
import asyncio
import subprocess
import os
from typing import Dict, Any, List, Optional, Union
import threading
import queue
import time

from langchain.tools import BaseTool
from pydantic import Field
from .tool_config_models import MCPToolConfig, AuthType, MCPStdioToolConfig


class MCPStdioTool(BaseTool):
    """MCP Stdio工具类，用于通过标准输入输出与MCP服务器通信"""
    
    # 添加Pydantic字段定义，使用不同的名称避免与BaseTool冲突
    command: str = Field(description="启动MCP服务器的命令")
    command_args: List[str] = Field(default_factory=list, description="命令参数")
    env: Dict[str, str] = Field(default_factory=dict, description="环境变量")
    timeout: int = Field(default=30, description="请求超时时间(秒)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数定义")
    _process: Optional[subprocess.Popen] = None  # 使用下划线前缀表示私有属性
    
    def __init__(
        self,
        name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        parameters: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ):
        """
        初始化MCP Stdio工具
        
        Args:
            name: 工具名称
            command: 启动MCP服务器的命令
            args: 命令参数
            env: 环境变量
            timeout: 请求超时时间(秒)
            parameters: 参数定义
            description: 工具描述
        """
        super().__init__(name=name, description=description)
        
        # 使用setattr设置字段值，避免Pydantic验证错误
        object.__setattr__(self, 'command', command)
        object.__setattr__(self, 'command_args', args)
        object.__setattr__(self, 'env', env or {})
        object.__setattr__(self, 'timeout', timeout)
        object.__setattr__(self, 'parameters', parameters or {})
        object.__setattr__(self, '_process', None)
        
        # 启动MCP服务器进程
        self._start_process()
    
    def _start_process(self):
        """启动MCP服务器进程"""
        try:
            # 合并环境变量
            process_env = os.environ.copy()
            process_env.update(self.env)
            
            # 启动子进程
            process = subprocess.Popen(
                [self.command] + self.command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                env=process_env
            )
            
            # 使用setattr设置_process属性
            object.__setattr__(self, '_process', process)
            
            # 等待进程启动
            time.sleep(1)
            
            # 检查进程是否正常运行
            if self._process.poll() is not None:
                stderr = self._process.stderr.read() if self._process.stderr else ""
                raise Exception(f"MCP server process exited with code {self._process.returncode}: {stderr}")
                
        except Exception as e:
            raise Exception(f"Failed to start MCP server process: {str(e)}")
    
    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到MCP服务器并获取响应"""
        if not self._process or self._process.poll() is not None:
            # 进程已终止，重新启动
            self._start_process()
        
        try:
            # 发送请求
            request_json = json.dumps(request) + "\n"
            self._process.stdin.write(request_json)
            self._process.stdin.flush()
            
            # 读取响应，跳过非 JSON 行（日志输出）
            max_attempts = 100  # 最多尝试读取 100 行
            for _ in range(max_attempts):
                response_line = self._process.stdout.readline()
                if not response_line:
                    raise Exception("No response from MCP server")
                
                line = response_line.strip()
                if not line:
                    continue
                
                # 尝试解析 JSON
                try:
                    response = json.loads(line)
                    # 验证是否是有效的 JSON-RPC 响应
                    if isinstance(response, dict) and ('result' in response or 'error' in response or 'method' in response):
                        return response
                except (json.JSONDecodeError, TypeError, ValueError):
                    # 这是日志行，继续读取下一行
                    continue
            
            raise Exception("Failed to find valid JSON-RPC response after reading multiple lines")
            
        except Exception as e:
            raise Exception(f"Error communicating with MCP server: {str(e)}")
    
    def _run(self, **kwargs) -> Dict[str, Any]:
        """同步执行MCP工具调用"""
        try:
            # 准备请求
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": self.name,
                    "arguments": kwargs
                }
            }
            
            # 发送请求并获取响应
            response = self._send_request(request)
            
            # 检查响应
            if "error" in response:
                return {
                    "error": True,
                    "message": response["error"].get("message", "Unknown error"),
                    "code": response["error"].get("code", -1)
                }
            
            # 返回结果
            result = response.get("result", {})
            result["_metadata"] = {
                "tool_name": self.name,
                "command": self.command,
                "args": self.command_args
            }
            
            return result
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "type": type(e).__name__
            }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """异步执行MCP工具调用"""
        # 在线程池中执行同步操作
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._run(**kwargs))
    
    def discover_tools(self) -> List[Dict[str, Any]]:
        """发现MCP服务器上可用的工具"""
        try:
            # 准备请求
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            # 发送请求并获取响应
            response = self._send_request(request)
            
            # 检查响应
            if "error" in response:
                print(f"Error discovering tools: {response['error'].get('message', 'Unknown error')}")
                return []
            
            # 返回工具列表
            tools = response.get("result", {}).get("tools", [])
            return tools
            
        except Exception as e:
            print(f"Error discovering tools: {str(e)}")
            return []
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """获取当前工具的详细模式"""
        try:
            # 准备请求
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/get",
                "params": {
                    "name": self.name
                }
            }
            
            # 发送请求并获取响应
            response = self._send_request(request)
            
            # 检查响应
            if "error" in response:
                print(f"Error getting tool schema: {response['error'].get('message', 'Unknown error')}")
                return {}
            
            # 返回工具模式
            schema = response.get("result", {})
            return schema
            
        except Exception as e:
            print(f"Error getting tool schema: {str(e)}")
            return {}
    
    def close(self):
        """关闭MCP服务器进程"""
        if hasattr(self, '_process') and self._process:
            self._process.terminate()
            self._process.wait()
            object.__setattr__(self, '_process', None)
    
    def __del__(self):
        """析构函数，确保进程被关闭"""
        self.close()
    
    @classmethod
    def from_config(cls, config: Union[Dict[str, Any], MCPStdioToolConfig]) -> "MCPStdioTool":
        """从配置字典或MCPStdioToolConfig对象创建MCP Stdio工具实例"""
        # 如果是MCPStdioToolConfig对象，转换为字典
        if isinstance(config, MCPStdioToolConfig):
            # Pydantic v2兼容性
            if hasattr(config, 'model_dump'):
                config_dict = config.model_dump()
            else:
                config_dict = config.dict()
        else:
            config_dict = config
        
        # 解析命令和参数
        command = config_dict.get("command", "")
        args = config_dict.get("args", [])
        
        # 如果command是字符串，可能需要分割
        if isinstance(command, str) and not args:
            # 简单的命令分割，实际应用中可能需要更复杂的解析
            parts = command.split()
            command = parts[0]
            args = parts[1:]
        
        # 创建实例但不调用__init__
        instance = object.__new__(cls)
        
        # 手动设置所有属性
        object.__setattr__(instance, 'name', config_dict.get("name", "mcp_stdio_tool"))
        object.__setattr__(instance, 'description', config_dict.get("description", "MCP Stdio工具"))
        object.__setattr__(instance, 'command', command)
        object.__setattr__(instance, 'command_args', args)
        object.__setattr__(instance, 'env', config_dict.get("env", {}))
        object.__setattr__(instance, 'timeout', config_dict.get("timeout", 30))
        object.__setattr__(instance, 'parameters', config_dict.get("parameters", {}))
        object.__setattr__(instance, '_process', None)
        
        # 调用_start_process方法启动进程
        instance._start_process()
        
        return instance