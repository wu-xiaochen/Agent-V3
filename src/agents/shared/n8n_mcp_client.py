"""
N8N MCP 客户端
真正调用 Docker 中运行的 n8n-mcp 工具
"""

import json
import logging
import subprocess
import time
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class N8NMCPClient(BaseTool):
    """
    N8N MCP 客户端工具
    
    通过 Docker exec 调用运行中的 n8n-mcp 容器
    真正使用 n8n-mcp 的 42 个工具来生成工作流
    """
    
    name: str = "n8n_mcp_workflow"
    description: str = """【N8N MCP 工作流工具】- 使用 n8n-mcp 生成工作流

⚡ 核心功能:
- 使用 n8n-mcp 的 AI 能力自动生成完整、正确的 n8n 工作流
- 支持所有 n8n 节点类型（AI Agent、Webhook、HTTP 等）
- 自动部署到本地 n8n 实例

📝 输入参数:
- description: 工作流描述（必需），如 "创建AI对话工作流"
- workflow_name: 工作流名称（可选）

💡 使用示例:
description="创建一个AI对话工作流，webhook接收消息，AI Agent处理，返回响应"

⚠️ 注意:
- 需要 n8n-mcp Docker 容器运行中（容器名：n8n-mcp-server）
- 容器会持久化运行，无需每次重启
- 工作流会自动创建并部署到 http://localhost:5678

返回: 创建的工作流配置和访问链接
"""
    
    container_name: str = Field(default="n8n-mcp-server", description="n8n-mcp 容器名称")
    timeout: int = Field(default=60, description="请求超时时间（秒）")
    
    class Config:
        arbitrary_types_allowed = True
    
    def _run(self, description: str, workflow_name: str = "") -> str:
        """
        使用 n8n-mcp 生成并创建工作流
        
        Args:
            description: 工作流描述
            workflow_name: 工作流名称（可选）
            
        Returns:
            工作流创建结果（JSON字符串）
        """
        try:
            logger.info(f"📝 使用 n8n-mcp 生成工作流: {description}")
            
            # 1. 检查容器是否运行
            if not self._check_container():
                return json.dumps({
                    "error": "n8n-mcp 容器未运行",
                    "suggestion": f"请先启动容器: docker start {self.container_name}"
                }, ensure_ascii=False, indent=2)
            
            # 2. 调用 n8n-mcp 的 create_workflow 工具
            logger.info("🚀 调用 n8n-mcp create_workflow...")
            
            # 准备参数
            params = {
                "description": description
            }
            if workflow_name:
                params["name"] = workflow_name
            
            # 调用 MCP 工具
            result = self._call_mcp_tool("create_workflow", params)
            
            if isinstance(result, dict):
                if result.get("error"):
                    return json.dumps({
                        "error": "n8n-mcp 创建工作流失败",
                        "details": result.get("message", str(result)),
                        "suggestion": "请检查工作流描述是否清晰，或查看 n8n-mcp 日志"
                    }, ensure_ascii=False, indent=2)
                
                # 成功创建
                logger.info("✅ n8n-mcp 成功创建工作流")
                
                # 提取工作流信息
                if "content" in result:
                    content_list = result.get("content", [])
                    if isinstance(content_list, list) and len(content_list) > 0:
                        first_content = content_list[0]
                        if isinstance(first_content, dict):
                            text = first_content.get("text", "")
                            try:
                                workflow_data = json.loads(text)
                                workflow_id = workflow_data.get("id", "unknown")
                                workflow_name_actual = workflow_data.get("name", workflow_name or "未命名")
                                
                                return json.dumps({
                                    "success": True,
                                    "workflow_id": workflow_id,
                                    "workflow_name": workflow_name_actual,
                                    "url": f"http://localhost:5678/workflow/{workflow_id}",
                                    "message": "✅ 工作流创建成功！可以在 n8n 界面查看和编辑。",
                                    "note": "此工作流由 n8n-mcp 生成，使用了正确的节点类型和配置"
                                }, ensure_ascii=False, indent=2)
                            except json.JSONDecodeError:
                                pass
                
                return json.dumps(result, ensure_ascii=False, indent=2)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"N8N MCP 客户端执行失败: {e}")
            import traceback
            logger.debug(f"详细错误:\n{traceback.format_exc()}")
            return json.dumps({
                "error": str(e),
                "suggestion": f"请确保 {self.container_name} 容器正在运行"
            }, ensure_ascii=False)
    
    def _check_container(self) -> bool:
        """检查容器是否运行"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.container_name in result.stdout
        except Exception as e:
            logger.error(f"检查容器失败: {e}")
            return False
    
    def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 n8n-mcp 的特定工具
        
        通过 docker exec 发送 JSON-RPC 请求到 n8n-mcp
        
        Args:
            tool_name: 工具名称（如 "create_workflow"）
            params: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            # 准备 JSON-RPC 请求
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            request_json = json.dumps(request)
            logger.debug(f"发送请求: {request_json[:200]}...")
            
            # 使用 docker exec -i 发送请求
            cmd = ["docker", "exec", "-i", self.container_name, "node", "dist/mcp/index.js"]
            
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 发送请求
            stdout, stderr = proc.communicate(input=request_json + "\n", timeout=self.timeout)
            
            logger.debug(f"收到输出: {len(stdout)} 字符")
            logger.debug(f"错误输出: {stderr[:200] if stderr else 'None'}...")
            
            # 解析响应（跳过日志行）
            for line in stdout.split("\n"):
                line = line.strip()
                if not line or line.startswith("["):
                    continue
                
                try:
                    response = json.loads(line)
                    if isinstance(response, dict):
                        if "error" in response:
                            return {
                                "error": True,
                                "message": response["error"].get("message", "Unknown error"),
                                "code": response["error"].get("code", -1)
                            }
                        elif "result" in response:
                            return response["result"]
                except (json.JSONDecodeError, TypeError, ValueError) as parse_error:
                    logger.debug(f"解析行失败: {line[:100]}... 错误: {parse_error}")
                    continue
            
            return {
                "error": True,
                "message": "No valid JSON-RPC response found",
                "stdout_sample": stdout[:500] if stdout else None
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"调用 {tool_name} 超时")
            return {"error": True, "message": f"n8n-mcp 调用超时（{self.timeout}秒）"}
        except Exception as e:
            logger.error(f"调用 {tool_name} 失败: {e}")
            return {"error": True, "message": f"调用失败: {str(e)}"}
    
    async def _arun(self, description: str, workflow_name: str = "") -> str:
        """异步运行"""
        return self._run(description, workflow_name)


def create_n8n_mcp_client(container_name: str = "n8n-mcp-server", timeout: int = 60):
    """创建 N8N MCP 客户端实例"""
    return N8NMCPClient(container_name=container_name, timeout=timeout)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    client = create_n8n_mcp_client()
    print(f"✅ 客户端创建成功: {client.name}")
    
    result = client._run(description="创建一个简单的AI对话工作流")
    print(f"\n📦 结果:\n{result}")

