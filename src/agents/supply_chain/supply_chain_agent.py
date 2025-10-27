"""
供应链专业智能体

该智能体专门用于供应链业务流程规划、确认调整、用户引导和CrewAI团队配置生成。
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from enum import Enum
from datetime import datetime
import re

from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM

from src.storage.redis_chat_history import RedisConversationStore
from src.tools.crewai_generator import CrewAIGenerator
from src.config.config_loader import ConfigLoader
from src.prompts.prompt_loader import prompt_loader
from src.agents.shared.tools import get_tools


class ConversationState(Enum):
    """对话状态枚举"""
    INITIAL = "INITIAL"
    PLANNING = "PLANNING"
    CONFIRMATION = "CONFIRMATION"
    CREWAI_GENERATION = "CREWAI_GENERATION"
    GUIDANCE = "GUIDANCE"
    COMPLETED = "COMPLETED"


class SupplyChainAgent:
    """
    供应链专业智能体
    
    该智能体专门用于供应链业务流程规划、确认调整、用户引导和CrewAI团队配置生成。
    支持多轮对话、状态管理和Redis缓存存储。
    """
    
    def __init__(
        self,
        llm: BaseLLM,
        redis_url: str = "redis://localhost:6379",
        session_id: str = "default",
        verbose: bool = False
    ):
        """
        初始化供应链智能体
        
        Args:
            llm: 语言模型实例
            redis_url: Redis连接URL
            session_id: 会话ID
            verbose: 是否启用详细日志
        """
        self.llm = llm
        self.session_id = session_id
        self.verbose = verbose
        
        # 初始化Redis存储
        if redis_url:
            self.conversation_store = RedisConversationStore(
                redis_url=redis_url
            )
            
            # 获取会话历史
            self.conversation_history = self.conversation_store.get_history(session_id)
        else:
            # 使用内存存储
            from langchain_core.chat_history import InMemoryChatMessageHistory
            self.conversation_history = InMemoryChatMessageHistory()
            self.conversation_store = None
        
        # 初始化CrewAI生成器
        self.crewai_generator = CrewAIGenerator()
        
        # 初始化对话状态
        self.current_state = ConversationState.INITIAL
        
        # 初始化提示词模板
        self._init_prompt_templates()
        
        # 业务流程规划数据
        self.business_plan = None
        self.crewai_config = None
        
        # 加载会话历史
        self._load_session()
    
    def _init_prompt_templates(self):
        """初始化提示词模板"""
        # 从配置中加载提示词
        config_loader = ConfigLoader()
        agents_config = config_loader.get_agents_config()
        
        # 获取供应链智能体的配置
        supply_chain_config = config_loader.get_specific_agent_config("supply_chain_agent")
        
        # 获取提示词配置文件路径
        prompts_config = supply_chain_config.get("prompts_config", "config/base/prompts.yaml")
        
        # 使用提示词加载器加载提示词
        self.system_prompt = prompt_loader.get_prompt(prompts_config, supply_chain_config.get("system_prompt", "supply_chain_planning"))
        self.planning_prompt = prompt_loader.get_prompt(prompts_config, supply_chain_config.get("planning_prompt", "supply_chain_planning"))
        self.confirmation_prompt = prompt_loader.get_prompt(prompts_config, supply_chain_config.get("confirmation_prompt", "supply_chain_planning"))
        self.crewai_generation_prompt = prompt_loader.get_prompt(prompts_config, supply_chain_config.get("crewai_generation_prompt", "crewai_generation"))
        self.guidance_prompt = prompt_loader.get_prompt(prompts_config, supply_chain_config.get("guidance_prompt", "user_guidance"))
        self.execution_prompt = prompt_loader.get_prompt(prompts_config, supply_chain_config.get("execution_prompt", "supply_chain_planning"))
        
        # 加载对话状态和状态转换规则
        self.conversation_states = prompt_loader.get_conversation_states(prompts_config)
        self.state_transitions = prompt_loader.get_state_transitions(prompts_config)
        
        # 获取参数配置
        self.parameters = supply_chain_config.get("parameters", {})
        self.tools_config = supply_chain_config.get("tools", [])
        self.memory_config = supply_chain_config.get("memory", {})
        self.workflow_config = supply_chain_config.get("workflow", {})
        
        # 加载工具
        self.tools = get_tools(self.tools_config)
    
    def _load_session(self) -> None:
        """加载会话数据"""
        if self.conversation_store:
            session_data = self.conversation_store.load_session()
            if session_data:
                self.current_state = ConversationState(session_data.get("state", "INITIAL"))
                self.crew_config = session_data.get("crew_config")
                self.current_step = session_data.get("current_step", 0)
                self.workflow_context = session_data.get("workflow_context", {})
                self.generation_history = session_data.get("generation_history", [])
                
                if self.verbose:
                    print(f"已加载会话 {self.session_id}，状态: {self.current_state.value}")
        else:
            # 内存存储模式下，使用默认值
            self.current_state = ConversationState.INITIAL
            self.crew_config = None
            self.current_step = 0
            self.workflow_context = {}
            self.generation_history = []
        
        # 加载业务计划和CrewAI配置
        if self.conversation_store:
            session_data = self.conversation_store.load_session()
            if session_data:
                self.current_state = ConversationState(session_data.get("state", "INITIAL"))
                self.business_plan = session_data.get("business_plan")
                self.crewai_config = session_data.get("crewai_config")
                
                if self.verbose:
                    print(f"已加载会话 {self.session_id}，状态: {self.current_state.value}")
    
    def _save_session(self):
        """保存会话数据"""
        if self.conversation_store:
            session_data = {
                "state": self.current_state.value,
                "crew_config": self.crew_config,
                "current_step": self.current_step,
                "workflow_context": self.workflow_context,
                "generation_history": self.generation_history,
                "updated_at": datetime.now().isoformat()
            }
            
            self.conversation_store.save_session(session_data)
            
            if self.verbose:
                print(f"已保存会话 {self.session_id}，状态: {self.current_state.value}")
        # 内存存储模式下不需要保存
    
    def _transition_state(self, new_state: ConversationState) -> bool:
        """
        转换对话状态
        
        Args:
            new_state: 新状态
            
        Returns:
            是否成功转换状态
        """
        current_state_value = self.current_state.value
        new_state_value = new_state.value
        
        # 检查状态转换是否合法
        if new_state_value in self.state_transitions.get(current_state_value, []):
            self.current_state = new_state
            self._save_session()
            
            if self.verbose:
                print(f"状态转换: {current_state_value} -> {new_state_value}")
            
            return True
        
        if self.verbose:
            print(f"非法状态转换: {current_state_value} -> {new_state_value}")
        
        return False
    
    def _extract_content_from_tags(self, text: str, tag: str) -> Optional[str]:
        """
        从文本中提取指定标签的内容
        
        Args:
            text: 原始文本
            tag: 标签名
            
        Returns:
            标签内的内容，如果未找到则返回None
        """
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return None
    
    def _detect_intent(self, user_input: str) -> str:
        """
        检测用户意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            检测到的意图
        """
        user_input_lower = user_input.lower()
        
        # 检测确认意图
        if any(word in user_input_lower for word in ["确认", "同意", "好的", "可以", "没问题", "confirm", "yes", "ok"]):
            return "confirm"
        
        # 检测修改意图
        if any(word in user_input_lower for word in ["修改", "调整", "改变", "改", "modify", "change", "adjust"]):
            return "modify"
        
        # 检测生成CrewAI配置意图
        if any(word in user_input_lower for word in ["crewai", "团队", "配置", "生成", "generate", "team", "config"]):
            return "generate_crewai"
        
        # 检测引导意图
        if any(word in user_input_lower for word in ["如何", "怎么", "引导", "步骤", "操作", "how", "guide", "step"]):
            return "guidance"
        
        # 默认为规划意图
        return "planning"
    
    async def _process_planning_state(self, user_input: str) -> Dict[str, Any]:
        """处理规划状态"""
        # 获取对话历史
        if self.conversation_store:
            conversation_history = self.conversation_store.get_messages()
        else:
            # 内存存储模式下使用conversation_history
            conversation_history = self.conversation_history.messages
        
        # 生成业务流程规划
        planning_chain = LLMChain(
            llm=self.llm,
            prompt=self.planning_prompt
        )
        
        # 准备输入
        planning_examples = """
        示例1:
        <analysis>
        用户需要优化采购流程，当前采购周期长、成本高、供应商管理不规范。
        需要设计一个全面的采购流程优化方案。
        </analysis>
        
        <plan>
        {
            "name": "采购流程优化",
            "objective": "缩短采购周期30%，降低采购成本15%，提升供应商管理效率",
            "steps": [
                {
                    "step": 1,
                    "name": "供应商评估与分类",
                    "description": "建立供应商评估体系，对现有供应商进行分类管理",
                    "duration": "2周",
                    "resources": "采购团队、评估工具、供应商数据"
                },
                {
                    "step": 2,
                    "name": "采购流程数字化",
                    "description": "实施电子采购系统，实现采购流程自动化",
                    "duration": "4周",
                    "resources": "IT团队、采购系统、预算"
                },
                {
                    "step": 3,
                    "name": "采购人员培训",
                    "description": "对采购团队进行新流程和系统培训",
                    "duration": "1周",
                    "resources": "培训师、培训材料、培训场地"
                }
            ],
            "expected_outcomes": "采购周期缩短30%，成本降低15%，效率提升40%"
        }
        </plan>
        """
        
        # 获取工具信息
        tools_info = []
        if self.tools:
            for tool in self.tools:
                tools_info.append(f"- {tool.name}: {tool.description}")
        
        inputs = {
            "user_input": user_input,
            "conversation_history": "\n".join([f"{msg.type}: {msg.content}" for msg in conversation_history[-5:]]),
            "planning_examples": planning_examples,
            "available_tools": "\n".join(tools_info) if tools_info else "无可用工具"
        }
        
        # 生成规划
        result = await planning_chain.arun(inputs)
        
        # 提取规划内容
        plan_content = self._extract_content_from_tags(result, "plan")
        
        if plan_content:
            try:
                self.business_plan = json.loads(plan_content)
                self._save_session()
                
                # 转换到确认状态
                self._transition_state(ConversationState.CONFIRMATION)
                
                return {
                    "response": f"我已为您生成了供应链业务流程规划:\n\n{plan_content}\n\n请确认这个规划是否符合您的需求，或者告诉我需要调整的地方。",
                    "state": self.current_state.value,
                    "business_plan": self.business_plan
                }
            except json.JSONDecodeError:
                return {
                    "response": f"我生成了以下业务流程规划:\n\n{result}\n\n请确认这个规划是否符合您的需求，或者告诉我需要调整的地方。",
                    "state": self.current_state.value
                }
        
        return {
            "response": result,
            "state": self.current_state.value
        }
    
    async def _process_confirmation_state(self, user_input: str) -> Dict[str, Any]:
        """处理确认状态"""
        intent = self._detect_intent(user_input)
        
        if intent == "confirm":
            # 用户确认规划，转换到CrewAI配置生成状态
            self._transition_state(ConversationState.CREWAI_GENERATION)
            
            return {
                "response": "感谢您的确认！接下来我将为您生成相应的CrewAI团队配置。请稍候...",
                "state": self.current_state.value
            }
        
        elif intent == "generate_crewai":
            # 用户请求生成CrewAI配置，转换到CrewAI配置生成状态
            self._transition_state(ConversationState.CREWAI_GENERATION)
            
            return {
                "response": "好的，我将为您生成相应的CrewAI团队配置。请稍候...",
                "state": self.current_state.value
            }
        
        elif intent == "modify":
            # 用户需要修改规划，转换回规划状态
            self._transition_state(ConversationState.PLANNING)
            
            return {
                "response": "好的，请告诉我您希望如何调整这个业务流程规划？",
                "state": self.current_state.value
            }
        
        else:
            # 其他意图，保持当前状态
            return {
                "response": "请确认这个规划是否符合您的需求（回复\"确认\"或\"同意\"），或者告诉我需要调整的地方（回复\"修改\"或\"调整\"）。",
                "state": self.current_state.value
            }
    
    async def _process_crewai_generation_state(self, user_input: str) -> Dict[str, Any]:
        """处理CrewAI配置生成状态"""
        # 使用CrewAI生成器生成团队配置
        crewai_config = self.crewai_generator.generate_crew_config(
            business_process=json.dumps(self.business_plan, ensure_ascii=False) if isinstance(self.business_plan, dict) else self.business_plan
        )
        
        # 转换为字典格式以便JSON序列化
        crewai_dict = self.crewai_generator.export_to_dict(crewai_config)
        self.crewai_config = crewai_dict
        self._save_session()
        
        # 转换到引导状态
        self._transition_state(ConversationState.GUIDANCE)
        
        return {
            "response": f"我已为您生成了CrewAI团队配置:\n\n{json.dumps(crewai_dict, indent=2, ensure_ascii=False)}\n\n接下来我可以引导您如何按照业务流程执行操作。您需要了解哪个步骤的具体操作方法？",
            "state": self.current_state.value,
            "crewai_config": self.crewai_config
        }
    
    async def _process_guidance_state(self, user_input: str) -> Dict[str, Any]:
        """处理引导状态"""
        # 生成操作指导
        guidance_chain = LLMChain(
            llm=self.llm,
            prompt=self.guidance_prompt
        )
        
        # 准备输入
        guidance_examples = """
        示例1:
        <analysis>
        用户询问如何进行供应商评估与分类，这是业务流程的第一步。
        需要提供详细的操作指导和注意事项。
        </analysis>
        
        <guidance>
        ## 供应商评估与分类操作指南
        
        ### 当前步骤
        步骤1: 供应商评估与分类
        
        ### 操作方法
        1. **制定评估标准**
           - 质量能力：产品质量认证、质量控制体系
           - 交付能力：生产周期、物流能力、准时交付率
           - 成本能力：价格竞争力、成本结构、付款条件
           - 服务能力：售后服务、技术支持、响应速度
           - 风险控制：财务状况、合规性、可持续发展
        
        2. **收集供应商数据**
           - 发放供应商信息调查表
           - 进行现场审核
           - 收集第三方认证信息
           - 调查市场口碑和客户反馈
        
        3. **评估与打分**
           - 根据评估标准对供应商进行打分
           - 使用加权评分法计算综合得分
           - 建立供应商评估数据库
        
        4. **供应商分类**
           - A类供应商：战略合作伙伴，占供应商总数20%
           - B类供应商：优选供应商，占供应商总数30%
           - C类供应商：普通供应商，占供应商总数50%
        
        ### 注意事项
        - 确保评估标准的公平性和一致性
        - 定期更新供应商评估数据，建议每半年一次
        - 建立供应商绩效跟踪机制
        - 对不同类别供应商采取差异化管理策略
        
        ### 建议技巧
        - 使用数字化工具进行供应商管理，如SRM系统
        - 建立供应商激励机制，促进持续改进
        - 定期与战略供应商召开业务回顾会议
        - 建立供应商风险预警机制
        </guidance>
        """
        
        inputs = {
            "business_plan": json.dumps(self.business_plan, ensure_ascii=False),
            "current_step": user_input,
            "guidance_examples": guidance_examples
        }
        
        # 生成指导
        result = await guidance_chain.arun(inputs)
        
        # 提取指导内容
        guidance_content = self._extract_content_from_tags(result, "guidance")
        
        if guidance_content:
            return {
                "response": guidance_content,
                "state": self.current_state.value
            }
        
        return {
            "response": result,
            "state": self.current_state.value
        }
    
    async def _process_initial_state(self, user_input: str) -> Dict[str, Any]:
        """处理初始状态"""
        # 转换到规划状态
        self._transition_state(ConversationState.PLANNING)
        
        return {
            "response": "您好！我是供应链管理专家，可以帮助您规划业务流程、优化供应链操作，并生成相应的CrewAI团队配置。\n\n请告诉我您需要解决的供应链问题或需求，我将为您制定详细的业务流程规划。",
            "state": self.current_state.value
        }
    
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果
        """
        # 添加用户消息到历史
        self.conversation_history.add_message(HumanMessage(content=user_input))
        
        # 根据当前状态处理用户输入
        if self.current_state == ConversationState.INITIAL:
            result = await self._process_initial_state(user_input)
        
        elif self.current_state == ConversationState.PLANNING:
            result = await self._process_planning_state(user_input)
        
        elif self.current_state == ConversationState.CONFIRMATION:
            result = await self._process_confirmation_state(user_input)
        
        elif self.current_state == ConversationState.CREWAI_GENERATION:
            result = await self._process_crewai_generation_state(user_input)
        
        elif self.current_state == ConversationState.GUIDANCE:
            result = await self._process_guidance_state(user_input)
        
        elif self.current_state == ConversationState.COMPLETED:
            # 重置到初始状态
            self._transition_state(ConversationState.INITIAL)
            result = await self._process_initial_state(user_input)
        
        else:
            result = {
                "response": "抱歉，我遇到了一个未知的状态。让我们重新开始吧。",
                "state": ConversationState.INITIAL.value
            }
        
        # 添加AI响应到历史
        self.conversation_history.add_message(AIMessage(content=result["response"]))
        
        return result
    
    async def chat(self, user_input: str) -> str:
        """
        与智能体对话
        
        Args:
            user_input: 用户输入
            
        Returns:
            智能体响应
        """
        result = await self.process_user_input(user_input)
        return result["response"]
    
    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        运行智能体
        
        Args:
            user_input: 用户输入
            
        Returns:
            包含响应和元数据的结果
        """
        result = await self.process_user_input(user_input)
        
        return {
            "response": result["response"],
            "metadata": {
                "state": result["state"],
                "session_id": self.session_id,
                "business_plan": self.business_plan,
                "crewai_config": self.crewai_config
            }
        }
    
    async def stream(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        流式输出
        
        Args:
            user_input: 用户输入
            
        Yields:
            流式响应片段
        """
        result = await self.process_user_input(user_input)
        response = result["response"]
        
        # 简单的流式输出实现，按字符分割
        words = response.split()
        for i, word in enumerate(words):
            if i == 0:
                yield word
            else:
                yield f" {word}"
            
            # 添加小延迟以模拟流式效果
            await asyncio.sleep(0.05)
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        if self.conversation_store:
            return self.conversation_history.get_session_info()
        else:
            # 内存存储模式下的会话信息
            return {
                "session_id": self.session_id,
                "message_count": len(self.conversation_history.messages),
                "last_updated": datetime.now().isoformat(),
                "storage_type": "memory"
            }
    
    def reset_session(self):
        """重置会话"""
        if self.conversation_store:
            self.conversation_store.clear_messages()
        else:
            # 内存存储模式下清空对话历史
            self.conversation_history.clear()
            
        self.current_state = ConversationState.INITIAL
        self.business_plan = None
        self.crewai_config = None
        self._save_session()
        
        if self.verbose:
            print(f"已重置会话 {self.session_id}")