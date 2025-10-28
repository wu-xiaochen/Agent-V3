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
    """N8N 创建工作流工具（高级，需要完整 JSON）"""
    
    name: str = "n8n_create_workflow"
    description: str = """使用完整 JSON 配置创建 n8n 工作流（高级功能，慎用）。

⚠️ 重要警告:
- 此工具需要严格有效的 JSON 格式
- 不推荐在对话中使用（LLM 很难生成正确的 JSON）
- 推荐使用: n8n_generate_and_create_workflow 代替

仅在以下情况使用:
- 你有完整的、经过验证的 n8n 工作流 JSON
- 从现有工作流导出并复制配置

否则强烈建议使用: n8n_generate_and_create_workflow

输入要求:
- workflow_json: 必须是完整、有效的 JSON 字符串
- 所有字符串必须正确闭合
- 必须包含 "name" 和 "nodes" 字段
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
                # 尝试清理和修复 JSON
                try:
                    workflow = json.loads(workflow_json)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON 解析失败，尝试修复: {e}")
                    # 尝试修复常见的 JSON 问题
                    cleaned_json = workflow_json.strip()
                    # 移除可能的 markdown 代码块标记
                    if cleaned_json.startswith('```'):
                        lines = cleaned_json.split('\n')
                        cleaned_json = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                    # 再次尝试解析
                    try:
                        workflow = json.loads(cleaned_json)
                    except json.JSONDecodeError:
                        return json.dumps({
                            "success": False,
                            "error": f"无效的 JSON 格式: {str(e)}。请检查 JSON 语法，特别是字符串是否正确闭合。"
                        }, ensure_ascii=False)
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
    description: str = """根据简短描述自动生成并创建 n8n 工作流。

重要: 
- 只需提供简短的工作流描述（1-2句话）
- 不要提供 JSON 或复杂的配置
- 工具会自动生成合适的工作流

输入格式: 简短的文本描述

正确示例:
- "每小时检查库存"
- "接收订单请求"
- "定时发送报告"
- "自动化采购流程"

错误示例（不要这样做）:
- 不要提供 JSON 配置
- 不要提供详细的节点配置
- 不要提供复杂的步骤说明

返回: 创建结果，包含工作流 ID 和访问链接
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
    
    def _generate_workflow_with_llm(self, description: str) -> Dict[str, Any]:
        """使用 LLM 智能生成工作流结构"""
        from src.infrastructure.llm.llm_factory import LLMFactory
        
        self.logger.info(f"使用 LLM 生成工作流: {description}")
        
        # 创建 LLM 实例
        llm = LLMFactory.create_llm(provider="siliconflow")
        
        # 设计提示词，让 LLM 理解 n8n 工作流结构
        prompt = f"""你是一个 n8n 工作流设计专家。根据用户需求设计一个简洁但完整的工作流。

用户需求: {description}

请设计一个包含 3-6 个节点的工作流，要求：
1. 第一个节点必须是触发器（trigger）
2. 后续节点实现业务逻辑
3. 节点之间要有清晰的连接关系
4. 使用真实可用的 n8n 节点类型

可用的节点类型：
- 触发器: manualTrigger, webhook, scheduleTrigger
- 数据处理: set (设置变量), if (条件判断), merge (合并数据), splitInBatches (批处理)
- HTTP: httpRequest (API 调用)
- 其他: code (JavaScript代码), function (函数节点)

请以 JSON 格式返回工作流设计，格式如下：
{{
  "workflow_name": "工作流名称",
  "nodes": [
    {{
      "name": "节点名称",
      "type": "节点类型（如 manualTrigger, set, httpRequest 等）",
      "description": "节点功能描述",
      "position": [x坐标, y坐标]
    }}
  ],
  "connections": [
    {{
      "from": "源节点名称",
      "to": "目标节点名称"
    }}
  ]
}}

只返回 JSON，不要其他说明。"""
        
        try:
            # 调用 LLM 生成设计
            response = llm.invoke(prompt)
            design_text = response.content if hasattr(response, 'content') else str(response)
            
            # 清理可能的 markdown 代码块
            if "```json" in design_text:
                design_text = design_text.split("```json")[1].split("```")[0].strip()
            elif "```" in design_text:
                design_text = design_text.split("```")[1].split("```")[0].strip()
            
            # 解析 LLM 的设计
            design = json.loads(design_text)
            
            # 将设计转换为 n8n 格式
            return self._convert_design_to_n8n(design, description)
            
        except Exception as e:
            self.logger.error(f"LLM 生成工作流失败，使用简化版本: {e}")
            # 如果 LLM 失败，使用简化的默认工作流
            return self._generate_simple_fallback_workflow(description)
    
    def _convert_design_to_n8n(self, design: Dict, description: str) -> Dict[str, Any]:
        """将 LLM 的设计转换为 n8n 工作流格式"""
        nodes = []
        connections = {}
        
        # 转换节点
        for i, node_design in enumerate(design.get("nodes", [])):
            node_type = node_design.get("type", "n8n-nodes-base.set")
            if not node_type.startswith("n8n-nodes-base."):
                node_type = f"n8n-nodes-base.{node_type}"
            
            # 根据节点类型设置参数
            parameters = self._get_node_parameters(node_type, node_design)
            
            node = {
                "name": node_design.get("name", f"Node{i+1}"),
                "type": node_type,
                "typeVersion": self._get_type_version(node_type),
                "position": node_design.get("position", [250 + i*200, 300]),
                "parameters": parameters
            }
            nodes.append(node)
        
        # 转换连接
        for conn in design.get("connections", []):
            from_node = conn.get("from")
            to_node = conn.get("to")
            if from_node and to_node:
                if from_node not in connections:
                    connections[from_node] = {"main": [[]]}
                connections[from_node]["main"][0].append({
                    "node": to_node,
                    "type": "main",
                    "index": 0
                })
        
        return {
            "name": design.get("workflow_name", description[:50]),
            "nodes": nodes,
            "connections": connections,
            "settings": {
                "executionOrder": "v1"
            }
        }
    
    def _get_node_parameters(self, node_type: str, node_design: Dict) -> Dict:
        """根据节点类型生成参数"""
        if "trigger" in node_type.lower():
            if "schedule" in node_type.lower():
                return {
                    "rule": {
                        "interval": [{"field": "hours", "hoursInterval": 1}]
                    }
                }
            elif "webhook" in node_type.lower():
                return {
                    "path": "webhook",
                    "responseMode": "onReceived"
                }
            else:
                return {}
        
        elif "httpRequest" in node_type:
            return {
                "method": "POST",
                "url": "https://api.example.com/endpoint",
                "sendBody": true,
                "specifyBody": "json",
                "jsonBody": "={}",
                "options": {}
            }
        
        elif node_type == "n8n-nodes-base.set":
            desc = node_design.get("description", "")
            return {
                "values": {
                    "string": [
                        {"name": "data", "value": desc or "处理数据"},
                        {"name": "timestamp", "value": "={{$now.format('YYYY-MM-DD HH:mm:ss')}}"}
                    ]
                },
                "options": {}
            }
        
        elif node_type == "n8n-nodes-base.if":
            return {
                "conditions": {
                    "string": [
                        {"value1": "={{$json.status}}", "operation": "equals", "value2": "active"}
                    ]
                }
            }
        
        else:
            return {}
    
    def _get_type_version(self, node_type: str) -> int:
        """获取节点类型版本"""
        version_map = {
            "n8n-nodes-base.httpRequest": 4,
            "n8n-nodes-base.set": 3,
            "n8n-nodes-base.if": 1,
            "n8n-nodes-base.merge": 2,
            "n8n-nodes-base.splitInBatches": 2,
            "n8n-nodes-base.scheduleTrigger": 1,
            "n8n-nodes-base.webhook": 1,
            "n8n-nodes-base.manualTrigger": 1,
        }
        return version_map.get(node_type, 1)
    
    def _generate_simple_fallback_workflow(self, description: str) -> Dict[str, Any]:
        """简化的备用工作流（当 LLM 失败时）"""
        self.logger.info(f"生成简化备用工作流: {description[:100]}...")
        
        description_lower = description.lower()
        
        nodes = []
        connections = {}
        
        # 1. 确定触发器（简化版本）
        trigger_node = None
        if "webhook" in description_lower or "接收" in description:
            trigger_node = {
                "parameters": {
                    "path": "webhook",
                    "responseMode": "onReceived"
                },
                "name": "When_webhook_called",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300]
            }
        elif "定时" in description or "schedule" in description_lower or "每" in description or "hour" in description_lower:
            trigger_node = {
                "parameters": {
                    "rule": {
                        "interval": [{"field": "hours", "hoursInterval": 1}]
                    }
                },
                "name": "Schedule",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1,
                "position": [250, 300]
            }
        else:
            trigger_node = {
                "parameters": {},
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [250, 300]
            }
        
        nodes.append(trigger_node)
        
        # 2. 根据描述添加完整的业务流程节点
        prev_node_name = nodes[0]["name"]
        
        if "采购" in description or "purchase" in description_lower or "procurement" in description_lower:
            # 完整的采购自动化流程（7个节点，包含条件判断）
            
            # 节点1: 接收采购请求数据
            nodes.append({
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "requestId", "value": "={{$now.format('YYYYMMDD-HHmmss')}}-{{$runIndex}}"},
                            {"name": "itemName", "value": "办公用品"},
                            {"name": "quantity", "value": "50"},
                            {"name": "unitPrice", "value": "100"},
                            {"name": "totalAmount", "value": "={{$json.quantity * $json.unitPrice}}"},
                            {"name": "requestedBy", "value": "采购部"},
                            {"name": "urgency", "value": "normal"}
                        ]
                    },
                    "options": {}
                },
                "name": "接收采购请求",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [450, 300]
            })
            connections[prev_node_name] = {
                "main": [[{"node": "接收采购请求", "type": "main", "index": 0}]]
            }
            
            # 节点2: 检查预算和库存
            nodes.append({
                "parameters": {
                    "method": "POST",
                    "url": "https://api.example.com/check-budget",
                    "sendBody": true,
                    "specifyBody": "json",
                    "jsonBody": "={\"amount\": {{$json.totalAmount}}, \"requestId\": \"{{$json.requestId}}\"}",
                    "options": {}
                },
                "name": "检查预算可用性",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [650, 300]
            })
            connections["接收采购请求"] = {
                "main": [[{"node": "检查预算可用性", "type": "main", "index": 0}]]
            }
            
            # 节点3: 判断金额是否需要特殊审批
            nodes.append({
                "parameters": {
                    "conditions": {
                        "number": [
                            {"value1": "={{$json.totalAmount}}", "operation": "larger", "value2": "10000"}
                        ]
                    }
                },
                "name": "判断是否需要高层审批",
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": [850, 300]
            })
            connections["检查预算可用性"] = {
                "main": [[{"node": "判断是否需要高层审批", "type": "main", "index": 0}]]
            }
            
            # 节点4a: 高层审批流程（金额>10000）
            nodes.append({
                "parameters": {
                    "method": "POST",
                    "url": "https://api.example.com/high-level-approval",
                    "sendBody": true,
                    "specifyBody": "json",
                    "jsonBody": "={\"requestId\": \"{{$json.requestId}}\", \"amount\": {{$json.totalAmount}}, \"approver\": \"CFO\"}",
                    "options": {}
                },
                "name": "发送高层审批",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [1050, 200]
            })
            
            # 节点4b: 部门经理审批（金额<=10000）
            nodes.append({
                "parameters": {
                    "method": "POST",
                    "url": "https://api.example.com/manager-approval",
                    "sendBody": true,
                    "specifyBody": "json",
                    "jsonBody": "={\"requestId\": \"{{$json.requestId}}\", \"amount\": {{$json.totalAmount}}, \"approver\": \"Manager\"}",
                    "options": {}
                },
                "name": "发送部门审批",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [1050, 400]
            })
            
            connections["判断是否需要高层审批"] = {
                "main": [
                    [{"node": "发送高层审批", "type": "main", "index": 0}],
                    [{"node": "发送部门审批", "type": "main", "index": 0}]
                ]
            }
            
            # 节点5: 合并审批结果
            nodes.append({
                "parameters": {
                    "mode": "mergeByPosition"
                },
                "name": "合并审批结果",
                "type": "n8n-nodes-base.merge",
                "typeVersion": 2,
                "position": [1250, 300]
            })
            connections["发送高层审批"] = {
                "main": [[{"node": "合并审批结果", "type": "main", "index": 0}]]
            }
            connections["发送部门审批"] = {
                "main": [[{"node": "合并审批结果", "type": "main", "index": 1}]]
            }
            
            # 节点6: 创建采购订单
            nodes.append({
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "orderId", "value": "PO-={{$json.requestId}}"},
                            {"name": "status", "value": "approved"},
                            {"name": "approvedBy", "value": "={{$json.approver}}"},
                            {"name": "orderDate", "value": "={{$now.format('YYYY-MM-DD HH:mm:ss')}}"},
                            {"name": "expectedDelivery", "value": "={{$now.plus({days: 7}).format('YYYY-MM-DD')}}"}
                        ]
                    },
                    "options": {}
                },
                "name": "生成采购订单",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [1450, 300]
            })
            connections["合并审批结果"] = {
                "main": [[{"node": "生成采购订单", "type": "main", "index": 0}]]
            }
            
            # 节点7: 发送通知和更新系统
            nodes.append({
                "parameters": {
                    "method": "POST",
                    "url": "https://api.example.com/notify",
                    "sendBody": true,
                    "specifyBody": "json",
                    "jsonBody": "={\"type\": \"purchase_order_created\", \"orderId\": \"{{$json.orderId}}\", \"message\": \"采购订单已创建并发送给供应商\", \"recipients\": [\"procurement@company.com\", \"finance@company.com\"]}",
                    "options": {}
                },
                "name": "发送通知并更新系统",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [1650, 300]
            })
            connections["生成采购订单"] = {
                "main": [[{"node": "发送通知并更新系统", "type": "main", "index": 0}]]
            }
            
        elif "库存" in description or "inventory" in description_lower:
            # 智能库存管理流程（6个节点，包含循环和条件）
            
            # 节点1: 获取所有产品库存数据
            nodes.append({
                "parameters": {
                    "method": "GET",
                    "url": "https://api.example.com/inventory/all-products",
                    "options": {
                        "response": {
                            "response": {
                                "fullResponse": false,
                                "neverError": false
                            }
                        }
                    }
                },
                "name": "获取库存列表",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [450, 300]
            })
            connections[prev_node_name] = {
                "main": [[{"node": "获取库存列表", "type": "main", "index": 0}]]
            }
            
            # 节点2: 分割数组以逐项处理
            nodes.append({
                "parameters": {
                    "options": {}
                },
                "name": "拆分为单个产品",
                "type": "n8n-nodes-base.splitInBatches",
                "typeVersion": 2,
                "position": [650, 300]
            })
            connections["获取库存列表"] = {
                "main": [[{"node": "拆分为单个产品", "type": "main", "index": 0}]]
            }
            
            # 节点3: 计算库存状态（安全/警告/危险）
            nodes.append({
                "parameters": {
                    "values": {
                        "number": [
                            {"name": "safetyStock", "value": "={{$json.minStock * 1.5}}"},
                            {"name": "dangerLevel", "value": "={{$json.minStock}}"}
                        ],
                        "string": [
                            {"name": "status", "value": "={{$json.currentStock > $json.safetyStock ? 'safe' : ($json.currentStock > $json.dangerLevel ? 'warning' : 'danger')}}"},
                            {"name": "needReorder", "value": "={{$json.currentStock <= $json.minStock ? 'yes' : 'no'}}"},
                            {"name": "reorderQuantity", "value": "={{$json.maxStock - $json.currentStock}}"}
                        ]
                    },
                    "options": {}
                },
                "name": "计算库存状态",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [850, 300]
            })
            connections["拆分为单个产品"] = {
                "main": [[{"node": "计算库存状态", "type": "main", "index": 0}]]
            }
            
            # 节点4: 判断是否需要补货
            nodes.append({
                "parameters": {
                    "conditions": {
                        "string": [
                            {"value1": "={{$json.needReorder}}", "operation": "equals", "value2": "yes"}
                        ]
                    }
                },
                "name": "判断是否需要补货",
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": [1050, 300]
            })
            connections["计算库存状态"] = {
                "main": [[{"node": "判断是否需要补货", "type": "main", "index": 0}]]
            }
            
            # 节点5: 自动创建补货订单
            nodes.append({
                "parameters": {
                    "method": "POST",
                    "url": "https://api.example.com/create-reorder",
                    "sendBody": true,
                    "specifyBody": "json",
                    "jsonBody": "={\"productId\": \"{{$json.productId}}\", \"productName\": \"{{$json.productName}}\", \"quantity\": {{$json.reorderQuantity}}, \"priority\": \"{{$json.status}}\", \"requestDate\": \"{{$now.format('YYYY-MM-DD')}}\"}",
                    "options": {}
                },
                "name": "创建自动补货单",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [1250, 200]
            })
            connections["判断是否需要补货"] = {
                "main": [
                    [{"node": "创建自动补货单", "type": "main", "index": 0}],
                    []  # 不需要补货则跳过
                ]
            }
            
            # 节点6: 记录和发送报告
            nodes.append({
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "reportType", "value": "inventory_check"},
                            {"name": "processedItems", "value": "={{$runIndex}}"},
                            {"name": "reordersCreated", "value": "={{$json.orderId ? '1' : '0'}}"},
                            {"name": "timestamp", "value": "={{$now.format('YYYY-MM-DD HH:mm:ss')}}"}
                        ]
                    },
                    "options": {}
                },
                "name": "生成库存报告",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [1450, 300]
            })
            
            # 从创建补货单和跳过补货两条路径都连接到报告
            connections["创建自动补货单"] = {
                "main": [[{"node": "生成库存报告", "type": "main", "index": 0}]]
            }
            # 不需要补货的也连接到报告（使用拆分批次节点的循环连接）
            connections["生成库存报告"] = {
                "main": [[{"node": "拆分为单个产品", "type": "main", "index": 0}]]
            }
            
        else:
            # 默认：简单的3节点流程
            nodes.append({
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "step", "value": "1"},
                            {"name": "data", "value": "处理数据"}
                        ]
                    }
                },
                "name": "数据处理",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [450, 300]
            })
            connections[prev_node_name] = {
                "main": [[{"node": "数据处理", "type": "main", "index": 0}]]
            }
            
            nodes.append({
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "step", "value": "2"},
                            {"name": "result", "value": "处理完成"}
                        ]
                    }
                },
                "name": "生成结果",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [650, 300]
            })
            connections["数据处理"] = {
                "main": [[{"node": "生成结果", "type": "main", "index": 0}]]
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
        """使用 LLM 智能生成并创建工作流"""
        try:
            self.logger.info(f"使用 LLM 生成工作流: {workflow_description}")
            
            # 1. 使用 LLM 生成工作流配置
            workflow = self._generate_workflow_with_llm(workflow_description)
            
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

