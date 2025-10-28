"""
N8N API 工具包 - 完整功能版本
直接通过 n8n REST API 操作工作流，支持创建、更新、删除、执行等完整功能
参考: https://github.com/czlonkowski/n8n-mcp
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain.tools import BaseTool
from pydantic import Field


class N8NAPIClient:
    """N8N API 客户端"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        初始化 N8N API 客户端
        
        Args:
            api_url: N8N API URL (默认从环境变量读取)
            api_key: N8N API Key (默认从环境变量读取)
        """
        self.api_url = (api_url or os.getenv("N8N_API_URL", "http://localhost:5678")).rstrip('/')
        self.api_key = api_key or os.getenv("N8N_API_KEY", "")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送 HTTP 请求到 N8N API
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: 其他请求参数
            
        Returns:
            API 响应
        """
        url = f"{self.api_url}/api/v1{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            response.raise_for_status()
            
            # 处理空响应
            if not response.content:
                return {"success": True}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"N8N API 请求失败: {e}")
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    pass
            raise Exception(f"N8N API 错误: {error_msg}")
    
    def create_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """创建工作流"""
        return self._request("POST", "/workflows", json=workflow)
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流"""
        return self._request("GET", f"/workflows/{workflow_id}")
    
    def update_workflow(self, workflow_id: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """更新工作流"""
        return self._request("PUT", f"/workflows/{workflow_id}", json=workflow)
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """删除工作流"""
        return self._request("DELETE", f"/workflows/{workflow_id}")
    
    def list_workflows(self, active: bool = None) -> List[Dict[str, Any]]:
        """列出所有工作流"""
        params = {}
        if active is not None:
            params['active'] = str(active).lower()
        response = self._request("GET", "/workflows", params=params)
        return response.get('data', [])
    
    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """激活工作流"""
        return self._request("POST", f"/workflows/{workflow_id}/activate")
    
    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """停用工作流"""
        return self._request("POST", f"/workflows/{workflow_id}/deactivate")
    
    def execute_workflow(self, workflow_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行工作流"""
        payload = {"data": data or {}}
        return self._request("POST", f"/workflows/{workflow_id}/execute", json=payload)
    
    def get_executions(self, workflow_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """获取执行历史"""
        params = {"limit": limit}
        if workflow_id:
            params['workflowId'] = workflow_id
        response = self._request("GET", "/executions", params=params)
        return response.get('data', [])


class N8NCreateWorkflowTool(BaseTool):
    """N8N 创建工作流工具 - 直接在 n8n 实例上创建"""
    
    name: str = "n8n_create_workflow"
    description: str = """直接在 n8n 实例上创建工作流。
    
输入参数:
- name: 工作流名称 (必需)
- nodes: 节点列表 (必需)
- connections: 节点连接关系 (必需)
- active: 是否激活 (可选, 默认 false)
- settings: 工作流设置 (可选)

返回: 创建的工作流信息，包括 ID、名称、创建时间等

示例输入 (JSON):
{
  "name": "我的工作流",
  "nodes": [...],
  "connections": {...},
  "active": false
}
"""
    
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, api_url: str = None, api_key: str = None, **kwargs):
        super().__init__(
            api_url=api_url or os.getenv("N8N_API_URL", "http://localhost:5678"),
            api_key=api_key or os.getenv("N8N_API_KEY", ""),
            **kwargs
        )
        object.__setattr__(self, 'client', N8NAPIClient(self.api_url, self.api_key))
        object.__setattr__(self, 'logger', logging.getLogger(__name__))
    
    def _run(self, workflow_json: str = None, name: str = None, **kwargs) -> str:
        """创建工作流"""
        try:
            # 解析输入
            if workflow_json:
                workflow = json.loads(workflow_json)
            else:
                workflow = kwargs
            
            # 确保有名称
            if not workflow.get('name'):
                if name:
                    workflow['name'] = name
                else:
                    workflow['name'] = f"工作流_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 确保有必需字段
            if 'nodes' not in workflow:
                return json.dumps({
                    "success": False,
                    "error": "缺少必需字段 'nodes'"
                }, ensure_ascii=False)
            
            if 'connections' not in workflow:
                workflow['connections'] = {}
            
            # 移除只读字段
            workflow.pop('active', None)  # active 是只读的
            workflow.pop('id', None)  # id 由系统生成
            workflow.pop('createdAt', None)
            workflow.pop('updatedAt', None)
            
            # 创建工作流
            result = self.client.create_workflow(workflow)
            
            return json.dumps({
                "success": True,
                "workflow_id": result.get('id'),
                "name": result.get('name'),
                "active": result.get('active'),
                "created_at": result.get('createdAt'),
                "url": f"{self.api_url}/workflow/{result.get('id')}",
                "message": f"✅ 工作流 '{result.get('name')}' 已成功创建"
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"创建工作流失败: {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)


class N8NGenerateAndCreateWorkflowTool(BaseTool):
    """N8N 智能生成并创建工作流工具 - AI 描述转工作流"""
    
    name: str = "n8n_generate_and_create_workflow"
    description: str = """根据描述智能生成工作流并直接创建到 n8n 实例。
    
输入: 工作流描述（中文或英文）

示例:
- "创建一个定时任务，每小时发送邮件提醒"
- "创建一个 webhook 接收器，处理数据后发送到 Slack"
- "创建一个简单的 HTTP 请求工作流"

返回: 生成的工作流配置和创建结果
"""
    
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, api_url: str = None, api_key: str = None, **kwargs):
        super().__init__(
            api_url=api_url or os.getenv("N8N_API_URL", "http://localhost:5678"),
            api_key=api_key or os.getenv("N8N_API_KEY", ""),
            **kwargs
        )
        object.__setattr__(self, 'client', N8NAPIClient(self.api_url, self.api_key))
        object.__setattr__(self, 'logger', logging.getLogger(__name__))
    
    def _generate_workflow(self, description: str) -> Dict[str, Any]:
        """根据描述生成工作流"""
        description_lower = description.lower()
        
        nodes = []
        connections = {}
        
        # 1. 确定触发器
        if "webhook" in description_lower or "接收" in description:
            nodes.append({
                "parameters": {
                    "path": "webhook",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300],
                "webhookId": ""
            })
        elif "定时" in description or "schedule" in description_lower or "每" in description:
            nodes.append({
                "parameters": {
                    "rule": {
                        "interval": [{"field": "hours", "hoursInterval": 1}]
                    }
                },
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1,
                "position": [250, 300]
            })
        else:
            nodes.append({
                "parameters": {},
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [250, 300]
            })
        
        # 2. 添加功能节点
        if "http" in description_lower or "请求" in description or "api" in description_lower:
            prev_node = nodes[-1]["name"]
            nodes.append({
                "parameters": {
                    "url": "https://api.example.com/endpoint",
                    "options": {}
                },
                "name": "HTTP Request",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [450, 300]
            })
            connections[prev_node] = {
                "main": [[{"node": "HTTP Request", "type": "main", "index": 0}]]
            }
        
        if "slack" in description_lower or "消息" in description or "通知" in description:
            prev_node = nodes[-1]["name"]
            nodes.append({
                "parameters": {
                    "channel": "#general",
                    "text": "=Hello from n8n!",
                    "options": {}
                },
                "name": "Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 2.1,
                "position": [650, 300]
            })
            connections[prev_node] = {
                "main": [[{"node": "Slack", "type": "main", "index": 0}]]
            }
        
        if "邮件" in description or "email" in description_lower:
            prev_node = nodes[-1]["name"]
            nodes.append({
                "parameters": {
                    "fromEmail": "noreply@example.com",
                    "toEmail": "user@example.com",
                    "subject": "Notification",
                    "text": "This is a notification from n8n"
                },
                "name": "Send Email",
                "type": "n8n-nodes-base.emailSend",
                "typeVersion": 2,
                "position": [650, 300]
            })
            connections[prev_node] = {
                "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
            }
        
        # 如果只有触发器，添加一个 Set 节点
        if len(nodes) == 1:
            nodes.append({
                "parameters": {
                    "values": {
                        "string": [{"name": "message", "value": "Hello from n8n!"}]
                    },
                    "options": {}
                },
                "name": "Set",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.2,
                "position": [450, 300]
            })
            connections[nodes[0]["name"]] = {
                "main": [[{"node": "Set", "type": "main", "index": 0}]]
            }
        
        return {
            "name": description[:50],
            "nodes": nodes,
            "connections": connections,
            "settings": {
                "executionOrder": "v1"
            }
            # 注意: active 字段是只读的，创建后需要单独激活
        }
    
    def _run(self, workflow_description: str) -> str:
        """生成并创建工作流"""
        try:
            self.logger.info(f"生成工作流: {workflow_description}")
            
            # 1. 生成工作流配置
            workflow = self._generate_workflow(workflow_description)
            
            # 2. 创建到 n8n
            result = self.client.create_workflow(workflow)
            
            return json.dumps({
                "success": True,
                "workflow_id": result.get('id'),
                "name": result.get('name'),
                "active": result.get('active'),
                "url": f"{self.api_url}/workflow/{result.get('id')}",
                "message": f"✅ 工作流已成功创建到 n8n 实例",
                "description": workflow_description,
                "nodes_count": len(workflow['nodes']),
                "workflow_json": workflow
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"生成并创建工作流失败: {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)


class N8NListWorkflowsTool(BaseTool):
    """N8N 列出工作流工具"""
    
    name: str = "n8n_list_workflows"
    description: str = """列出 n8n 实例上的所有工作流。
    
可选参数:
- active: 只显示激活的工作流 (true/false)

返回: 工作流列表，包括 ID、名称、状态等
"""
    
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, api_url: str = None, api_key: str = None, **kwargs):
        super().__init__(
            api_url=api_url or os.getenv("N8N_API_URL", "http://localhost:5678"),
            api_key=api_key or os.getenv("N8N_API_KEY", ""),
            **kwargs
        )
        object.__setattr__(self, 'client', N8NAPIClient(self.api_url, self.api_key))
    
    def _run(self, active: str = None) -> str:
        """列出工作流"""
        try:
            active_filter = None
            if active:
                active_filter = active.lower() == 'true'
            
            workflows = self.client.list_workflows(active=active_filter)
            
            return json.dumps({
                "success": True,
                "count": len(workflows),
                "workflows": [
                    {
                        "id": w.get('id'),
                        "name": w.get('name'),
                        "active": w.get('active'),
                        "created_at": w.get('createdAt'),
                        "updated_at": w.get('updatedAt'),
                        "url": f"{self.api_url}/workflow/{w.get('id')}"
                    }
                    for w in workflows
                ]
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)


class N8NExecuteWorkflowTool(BaseTool):
    """N8N 执行工作流工具"""
    
    name: str = "n8n_execute_workflow"
    description: str = """执行指定的工作流。
    
输入参数:
- workflow_id: 工作流 ID (必需)
- data: 执行数据 (可选，JSON 格式)

返回: 执行结果
"""
    
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, api_url: str = None, api_key: str = None, **kwargs):
        super().__init__(
            api_url=api_url or os.getenv("N8N_API_URL", "http://localhost:5678"),
            api_key=api_key or os.getenv("N8N_API_KEY", ""),
            **kwargs
        )
        object.__setattr__(self, 'client', N8NAPIClient(self.api_url, self.api_key))
    
    def _run(self, workflow_id: str, data: str = None) -> str:
        """执行工作流"""
        try:
            exec_data = {}
            if data:
                try:
                    exec_data = json.loads(data)
                except:
                    exec_data = {"input": data}
            
            result = self.client.execute_workflow(workflow_id, exec_data)
            
            return json.dumps({
                "success": True,
                "execution_id": result.get('id'),
                "workflow_id": workflow_id,
                "status": result.get('status'),
                "started_at": result.get('startedAt'),
                "finished_at": result.get('finishedAt'),
                "message": "✅ 工作流执行成功"
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)


class N8NDeleteWorkflowTool(BaseTool):
    """N8N 删除工作流工具"""
    
    name: str = "n8n_delete_workflow"
    description: str = """删除指定的工作流。
    
输入: workflow_id (工作流 ID)

返回: 删除结果
"""
    
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, api_url: str = None, api_key: str = None, **kwargs):
        super().__init__(
            api_url=api_url or os.getenv("N8N_API_URL", "http://localhost:5678"),
            api_key=api_key or os.getenv("N8N_API_KEY", ""),
            **kwargs
        )
        object.__setattr__(self, 'client', N8NAPIClient(self.api_url, self.api_key))
    
    def _run(self, workflow_id: str) -> str:
        """删除工作流"""
        try:
            self.client.delete_workflow(workflow_id)
            
            return json.dumps({
                "success": True,
                "workflow_id": workflow_id,
                "message": f"✅ 工作流 {workflow_id} 已删除"
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)


def create_n8n_api_tools(api_url: str = None, api_key: str = None) -> List[BaseTool]:
    """
    创建所有 N8N API 工具
    
    Args:
        api_url: N8N API URL
        api_key: N8N API Key
        
    Returns:
        N8N 工具列表
    """
    tools = [
        N8NGenerateAndCreateWorkflowTool(api_url=api_url, api_key=api_key),
        N8NCreateWorkflowTool(api_url=api_url, api_key=api_key),
        N8NListWorkflowsTool(api_url=api_url, api_key=api_key),
        N8NExecuteWorkflowTool(api_url=api_url, api_key=api_key),
        N8NDeleteWorkflowTool(api_url=api_url, api_key=api_key),
    ]
    
    return tools

