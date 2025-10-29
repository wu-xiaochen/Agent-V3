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
                except (ValueError, KeyError, AttributeError) as json_err:
                    # JSON 解析失败，使用原始错误消息
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
    description: str = """【n8n AI工作流生成工具】- 创建智能自动化工作流

⚡ 主要用途:
1. 创建 AI 对话/问答系统（支持 AI Agent 节点）
2. 创建自动化业务流程（定时、触发、数据处理）
3. 创建 webhook API 接口（接收请求、AI 处理、返回响应）

⭐ 何时使用此工具:

✅ AI 对话场景（推荐！）
- "创建一个 AI 对话"、"n8n 智能体对话"
- "创建智能客服"、"问答系统"
- "创建 AI 助手 API"
- 关键词: "对话"、"AI"、"聊天"、"问答"、"智能体"

✅ 自动化流程场景
- "创建 n8n 工作流"、"自动化流程"
- "定时任务"、"webhook 触发"
- "数据处理管道"、"集成系统"
- 关键词: "n8n"、"工作流"、"自动化"、"定时"

❌ 何时不使用:
- 用户说"运行它"（可能是 CrewAI）
- 用户要求分析或研究（使用 CrewAI）
- 用户刚生成了 CrewAI 配置
- 不涉及工作流自动化的任务

📋 输入要求:
- description: 简洁描述需求（1-2句话）
- 自动识别场景类型（AI对话/自动化/API等）

💡 正确示例:

AI 对话场景:
- "创建一个智能客服对话"
- "n8n AI Agent 对话系统"
- "问答机器人"

自动化场景:
- "每小时检查库存并发邮件"
- "接收订单webhook并存储数据库"
- "定时生成销售报告"

❌ 错误示例:
- 不要提供 JSON 配置
- 不要提供详细节点配置
- 不要提供复杂步骤说明

返回: 工作流创建结果 + 访问链接 + 使用说明
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
    
    def _generate_workflow_with_llm(self, description: str, max_retries: int = 3) -> Dict[str, Any]:
        """使用 LLM 智能生成工作流结构，支持自动重试和校正"""
        from src.infrastructure.llm.llm_factory import LLMFactory
        
        self.logger.info(f"使用 LLM 生成工作流: {description}")
        
        # 创建 LLM 实例
        llm = LLMFactory.create_llm(provider="siliconflow")
        
        last_error = None
        last_response = None
        
        for attempt in range(max_retries):
            try:
                # 根据重试次数调整 prompt
                prompt = self._build_workflow_prompt(description, attempt, last_error, last_response)
                
                self.logger.info(f"LLM 生成尝试 {attempt + 1}/{max_retries}")
                
                # 调用 LLM 生成设计
                response = llm.invoke(prompt)
                design_text = response.content if hasattr(response, 'content') else str(response)
                last_response = design_text
                
                # 清理可能的 markdown 代码块
                design_text = self._clean_json_response(design_text)
                
                # 解析 LLM 的设计
                design = json.loads(design_text)
                
                # 验证设计的有效性
                validation_error = self._validate_workflow_design(design)
                if validation_error:
                    raise ValueError(f"工作流设计验证失败: {validation_error}")
                
                # 将设计转换为 n8n 格式
                self.logger.info(f"✅ LLM 成功生成工作流（尝试 {attempt + 1}）")
                return self._convert_design_to_n8n(design, description)
                
            except json.JSONDecodeError as e:
                last_error = f"JSON 解析错误: {str(e)}"
                self.logger.warning(f"尝试 {attempt + 1} 失败: {last_error}")
                if attempt == max_retries - 1:
                    raise Exception(f"LLM 多次尝试后仍无法生成有效的 JSON: {last_error}")
                
            except ValueError as e:
                last_error = f"验证错误: {str(e)}"
                self.logger.warning(f"尝试 {attempt + 1} 失败: {last_error}")
                if attempt == max_retries - 1:
                    raise Exception(f"LLM 多次尝试后生成的工作流仍不符合要求: {last_error}")
                
            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                self.logger.error(f"尝试 {attempt + 1} 失败: {last_error}")
                if attempt == max_retries - 1:
                    raise Exception(f"LLM 生成工作流失败: {last_error}")
        
        raise Exception("LLM 生成工作流失败：超过最大重试次数")
    
    def _build_workflow_prompt(self, description: str, attempt: int, last_error: str = None, last_response: str = None) -> str:
        """根据重试次数和错误信息构建优化的 prompt"""
        
        base_prompt = f"""你是一个 n8n 工作流设计专家。根据用户需求设计一个简洁但完整的工作流。

用户需求: {description}

🎯 设计原则：
1. 第一个节点必须是触发器（webhook/manualTrigger/scheduleTrigger）
2. 优先使用 AI Agent 处理智能任务（对话、分析、生成内容等）
3. 节点数量：3-8个（根据需求复杂度）
4. 每个节点都要有明确的作用
5. 连接要完整、逻辑清晰

📋 常用节点类型：

【触发器类】（第一个节点必须是这些之一）
- webhook: Webhook 触发器 ⭐ 推荐用于对话/API场景
- manualTrigger: 手动触发 ⭐ 推荐用于测试
- scheduleTrigger: 定时触发（Cron 表达式）
- emailTrigger: 邮件触发

【AI/智能类】⭐ 核心节点
- aiAgent: AI Agent 智能体
  * 功能：调用 LLM 执行复杂 AI 任务
  * 用途：对话、分析、决策、问答、内容生成、总结、翻译等
  * 配置：需设置 model（如 gpt-4）、prompt、tools
  * ⭐ 对话场景必选节点！
  
- chatOpenAI: OpenAI 聊天 API
- chatAnthropic: Claude 聊天 API
- embeddings: 文本向量化
- vectorStore: 向量数据库（RAG）
- memoryManager: 对话记忆管理 ⭐ 多轮对话必选

【数据处理类】
- set: 设置/转换数据 ⭐ 常用
- code: JavaScript 代码 ⭐ 灵活
- if: 条件判断
- switch: 多路分支
- filter: 过滤数据
- merge: 合并数据流
- aggregate: 聚合数据

【HTTP/API 类】
- httpRequest: HTTP API 调用 ⭐ 调用外部服务

【数据库类】
- postgres: PostgreSQL
- mongodb: MongoDB
- redis: Redis 缓存 ⭐ 存储会话

【响应类】
- respondToWebhook: Webhook 响应 ⭐ 对话场景必选
- emailSend: 发送邮件
- slack: Slack 通知

⭐⭐⭐ 场景模板 ⭐⭐⭐

场景1: AI 对话/问答系统（最常见）
流程: webhook → aiAgent（配置 prompt 和 model）→ respondToWebhook
关键点: 
  - webhook 接收用户输入
  - aiAgent 处理对话逻辑
  - respondToWebhook 返回结果

场景2: AI 对话 + 记忆（推荐）
流程: webhook → memoryManager(load) → aiAgent → memoryManager(save) → respondToWebhook
关键点: 先加载历史，AI 处理，保存记忆，返回结果

场景3: AI 分析 + 数据库
流程: webhook → set(prepare data) → aiAgent(analyze) → postgres(save) → respondToWebhook

场景4: 定时 AI 任务
流程: scheduleTrigger → httpRequest(fetch data) → aiAgent(analyze) → emailSend(report)

⚠️ 重要规则：
1. webhook 触发器后面通常接 aiAgent 或 set
2. AI 对话场景必须包含: webhook → aiAgent → respondToWebhook
3. aiAgent 节点的 parameters 需要包含：
   - model: "gpt-4" 或其他模型
   - prompt: 具体的 AI 指令
   - (可选) tools: 工具列表
4. 多轮对话要用 memoryManager
5. 所有分支最后都要有输出节点

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

⚠️ 重要提示：
- 只返回纯 JSON，不要任何其他文字说明
- 确保 JSON 格式完全正确，所有字符串必须用双引号
- 所有大括号、方括号必须正确配对
- 不要在 JSON 中使用注释"""
        
        # 如果是重试，添加错误反馈
        if attempt > 0 and last_error:
            base_prompt += f"""

❌ 上次生成失败，错误信息：
{last_error}

上次的响应：
{last_response[:500] if last_response else "无"}

请修正以上错误，重新生成正确的 JSON。"""
        
        # 根据错误类型提供具体指导
        if last_error and "JSON 解析错误" in last_error:
            base_prompt += """

🔧 JSON 格式检查清单：
1. 所有字符串必须用双引号，不能用单引号
2. 对象的最后一个属性后不能有逗号
3. 数组的最后一个元素后不能有逗号
4. 所有括号必须成对出现
5. 不要在 JSON 中添加注释
6. 确保所有中文字符都在双引号内"""
        
        if last_error and "验证错误" in last_error:
            base_prompt += """

🔧 设计验证清单：
1. 必须包含 workflow_name 字段
2. 必须包含 nodes 数组，且至少有 2 个节点
3. 必须包含 connections 数组
4. 第一个节点必须是触发器类型
5. 每个节点必须有 name 和 type 字段
6. connections 中的节点名称必须在 nodes 中存在"""
        
        return base_prompt
    
    def _clean_json_response(self, text: str) -> str:
        """清理 LLM 响应中的非 JSON 内容"""
        text = text.strip()
        
        # 移除 markdown 代码块
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        # 移除可能的前后说明文字
        # 查找第一个 { 和最后一个 }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
        
        return text.strip()
    
    def _validate_workflow_design(self, design: Dict) -> str:
        """验证工作流设计的有效性，返回错误信息或 None"""
        
        # 检查必需字段
        if "workflow_name" not in design:
            return "缺少 workflow_name 字段"
        
        if "nodes" not in design or not isinstance(design["nodes"], list):
            return "缺少 nodes 数组或格式错误"
        
        if len(design["nodes"]) < 2:
            return "至少需要 2 个节点（触发器 + 处理节点）"
        
        if "connections" not in design or not isinstance(design["connections"], list):
            return "缺少 connections 数组或格式错误"
        
        # 检查第一个节点是否为触发器
        first_node = design["nodes"][0]
        if "type" not in first_node:
            return "第一个节点缺少 type 字段"
        
        first_node_type = first_node["type"].lower()
        # webhook、manualTrigger、scheduleTrigger 等都是触发器类型
        trigger_keywords = ["trigger", "manual", "webhook", "schedule", "cron"]
        is_trigger = any(keyword in first_node_type for keyword in trigger_keywords)
        
        if not is_trigger:
            return f"第一个节点必须是触发器类型（trigger/webhook/manual），但得到: {first_node['type']}"
        
        # 检查所有节点是否有必需字段
        node_names = set()
        for i, node in enumerate(design["nodes"]):
            if "name" not in node:
                return f"节点 {i} 缺少 name 字段"
            if "type" not in node:
                return f"节点 {i} ({node.get('name')}) 缺少 type 字段"
            node_names.add(node["name"])
        
        # 检查 connections 是否引用了存在的节点
        for conn in design["connections"]:
            if "from" not in conn or "to" not in conn:
                return f"连接缺少 from 或 to 字段: {conn}"
            if conn["from"] not in node_names:
                return f"连接引用了不存在的节点: {conn['from']}"
            if conn["to"] not in node_names:
                return f"连接引用了不存在的节点: {conn['to']}"
        
        return None  # 验证通过
    
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
        desc = node_design.get("description", "")
        node_lower = node_type.lower()
        
        # 触发器类
        if "trigger" in node_lower:
            if "schedule" in node_lower:
                return {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}}
            elif "webhook" in node_lower:
                return {"path": "webhook", "responseMode": "onReceived"}
            elif "email" in node_lower:
                return {"pollTime": 60000}
            else:
                return {}
        
        # AI/智能类节点
        elif "aiagent" in node_lower or ("agent" in node_lower and "langchain" in node_type):
            return {"text": f"={{{{ $json.input || '{desc}' }}}}", "options": {}}
        
        elif "chatopenai" in node_lower or "chatanthropic" in node_lower:
            return {"messages": [{"role": "user", "content": f"={{{{ $json.input || '{desc}' }}}}"}]}
        
        elif "embedding" in node_lower:
            return {"text": "={{$json.text}}"}
        
        elif "vectorstore" in node_lower:
            return {"operation": "insert", "text": "={{$json.text}}"}
        
        elif "memory" in node_lower:
            return {"operation": "get", "key": "conversation"}
        
        # HTTP/API类
        elif "httprequest" in node_lower:
            return {
                "method": "POST",
                "url": "https://api.example.com/endpoint",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={}",
                "options": {}
            }
        
        # 数据处理类
        elif node_type == "n8n-nodes-base.set" or "set" in node_lower:
            return {
                "values": {
                    "string": [
                        {"name": "data", "value": desc or "处理数据"},
                        {"name": "timestamp", "value": "={{$now.format('YYYY-MM-DD HH:mm:ss')}}"}
                    ]
                },
                "options": {}
            }
        
        elif node_type == "n8n-nodes-base.if" or (node_lower == "if"):
            return {
                "conditions": {
                    "string": [
                        {"value1": "={{$json.status}}", "operation": "equals", "value2": "active"}
                    ]
                }
            }
        
        elif "switch" in node_lower:
            return {
                "mode": "expression",
                "rules": {
                    "rules": [
                        {"value": "={{$json.value}}", "output": 0}
                    ]
                }
            }
        
        elif "filter" in node_lower:
            return {"conditions": {"string": [{"value1": "={{$json.field}}", "operation": "notEmpty"}]}}
        
        # 数据库类
        elif "postgres" in node_lower or "mysql" in node_lower:
            return {"operation": "select", "query": "SELECT * FROM table_name"}
        
        elif "mongodb" in node_lower:
            return {"operation": "find", "collection": "collection_name"}
        
        elif "redis" in node_lower:
            return {"operation": "get", "key": "key_name"}
        
        # 通知类
        elif "emailsend" in node_lower or "email" in node_lower:
            return {
                "fromEmail": "noreply@example.com",
                "toEmail": "={{$json.email}}",
                "subject": desc or "通知",
                "message": "={{$json.message}}"
            }
        
        elif "slack" in node_lower:
            return {"channelId": "", "text": "={{$json.message}}"}
        
        elif "telegram" in node_lower:
            return {"chatId": "", "text": "={{$json.message}}"}
        
        # 工具类
        elif "code" in node_lower:
            return {"mode": "runOnceForAllItems", "jsCode": "// 处理数据\nreturn items;"}
        
        elif "wait" in node_lower:
            return {"amount": 1, "unit": "seconds"}
        
        else:
            return {}
    
    def _get_type_version(self, node_type: str) -> int:
        """获取节点类型版本"""
        version_map = {
            # 触发器类
            "n8n-nodes-base.manualTrigger": 1,
            "n8n-nodes-base.webhook": 1,
            "n8n-nodes-base.scheduleTrigger": 1,
            "n8n-nodes-base.emailTrigger": 1,
            
            # 数据处理类
            "n8n-nodes-base.set": 3,
            "n8n-nodes-base.if": 1,
            "n8n-nodes-base.switch": 3,
            "n8n-nodes-base.merge": 2,
            "n8n-nodes-base.splitInBatches": 2,
            "n8n-nodes-base.itemLists": 2,
            "n8n-nodes-base.filter": 1,
            
            # AI/智能类
            "@n8n/n8n-nodes-langchain.agent": 1,
            "@n8n/n8n-nodes-langchain.chatOpenAI": 1,
            "@n8n/n8n-nodes-langchain.chatAnthropic": 1,
            "@n8n/n8n-nodes-langchain.embeddings": 1,
            "@n8n/n8n-nodes-langchain.vectorStore": 1,
            "@n8n/n8n-nodes-langchain.memoryManager": 1,
            
            # HTTP/API类
            "n8n-nodes-base.httpRequest": 4,
            
            # 数据库类
            "n8n-nodes-base.postgres": 2,
            "n8n-nodes-base.mysql": 2,
            "n8n-nodes-base.mongodb": 1,
            "n8n-nodes-base.redis": 1,
            
            # 通知类
            "n8n-nodes-base.emailSend": 2,
            "n8n-nodes-base.slack": 2,
            "n8n-nodes-base.telegram": 1,
            "n8n-nodes-base.discord": 1,
            
            # 文件处理类
            "n8n-nodes-base.readBinaryFile": 1,
            "n8n-nodes-base.writeBinaryFile": 1,
            "n8n-nodes-base.spreadsheet": 2,
            
            # 工具类
            "n8n-nodes-base.code": 2,
            "n8n-nodes-base.function": 1,
            "n8n-nodes-base.executeCommand": 1,
            "n8n-nodes-base.wait": 1,
            "n8n-nodes-base.noOp": 1,
        }
        return version_map.get(node_type, 1)
    
    def _generate_simple_fallback_workflow_DEPRECATED(self, description: str) -> Dict[str, Any]:
        """已废弃：使用 LLM 自动重试机制代替硬编码备用方案"""
        raise NotImplementedError("此方法已废弃，LLM 应通过自动重试来修正错误")
    
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
                except (json.JSONDecodeError, TypeError, ValueError) as json_err:
                    # JSON 解析失败，使用字符串包装
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

