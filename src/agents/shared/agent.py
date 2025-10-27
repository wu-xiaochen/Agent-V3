"""
智能体核心模块
基于LangChain的智能体实现
"""

import warnings
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_react_agent, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from src.infrastructure.llm.llm_factory import LLMFactory
from src.agents.shared.tools import get_tools
from src.config.config_loader import config_loader


class LangChainAgent:
    """基于LangChain的智能体"""
    
    def __init__(self, provider: Optional[str] = None, agent_type: Optional[str] = None, **kwargs):
        """
        初始化智能体
        
        Args:
            provider: LLM提供商
            agent_type: 智能体类型，如果不提供则从配置文件获取
            **kwargs: 额外的LLM参数
        """
        self.llm = LLMFactory.create_llm(provider, **kwargs)
        self.agent_config = config_loader.get_agent_config()
        
        # 如果提供了agent_type参数，使用它；否则从配置文件获取
        if agent_type:
            self.agent_config["type"] = agent_type
            
        self.memory = self._create_memory()
        
        # 使用新的动态工具加载器
        try:
            # 尝试使用智能体特定的工具配置
            agent_name = self.agent_config.get("name", "default_agent")
            self.tools = get_tools_for_agent(agent_name) if self.agent_config.get("enable_tools", True) else []
        except Exception as e:
            print(f"使用智能体特定工具配置失败: {e}")
            # 回退到默认工具列表
            self.tools = get_tools() if self.agent_config.get("enable_tools", True) else []
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor()
    
    def _create_memory(self):
        """
        创建记忆组件
        
        Returns:
            记忆组件实例
        """
        if not self.agent_config.get("memory", True):
            return None
        
        memory_type = self.agent_config.get("memory_type", "buffer")
        max_tokens = self.agent_config.get("max_memory_tokens", 2000)
        
        # 使用新的记忆实现
        if memory_type == "buffer":
            # 使用InMemoryChatMessageHistory替代ConversationBufferMemory
            return InMemoryChatMessageHistory()
        elif memory_type == "summary":
            # 对于摘要记忆，我们需要使用更复杂的实现
            # 这里暂时使用InMemoryChatMessageHistory，实际应用中可以添加摘要逻辑
            return InMemoryChatMessageHistory()
        elif memory_type == "token_buffer":
            # 对于token限制记忆，我们需要使用更复杂的实现
            # 这里暂时使用InMemoryChatMessageHistory，实际应用中可以添加token限制逻辑
            return InMemoryChatMessageHistory()
        else:
            raise ValueError(f"不支持的记忆类型: {memory_type}")
    
    def _create_agent(self):
        """
        创建智能体
        
        Returns:
            智能体实例
        """
        agent_type = self.agent_config.get("type", "react")
        
        if agent_type == "react":
            return self._create_react_agent()
        elif agent_type == "conversational":
            return self._create_conversational_agent()
        elif agent_type == "structured-chat":
            return self._create_structured_chat_agent()
        else:
            raise ValueError(f"不支持的智能体类型: {agent_type}")
    
    def _create_react_agent(self):
        """创建ReAct智能体"""
        # 从配置文件获取提示词模板
        template = config_loader.get_prompt_config("react_agent.template", """
        你是一个有帮助的AI助手。使用以下工具来回答用户的问题:

        {tools}

        工具名称:
        {tool_names}

        使用以下格式:

        Question: 输入的问题
        Thought: 你应该思考要做什么
        Action: 要使用的工具名称
        Action Input: 工具的输入
        Observation: 工具的输出
        ... (这个思考/行动/观察可以重复多次)
        Thought: 我现在知道最终答案了
        Final Answer: 对原始问题的最终答案

        开始!

        Question: {input}
        Thought: {agent_scratchpad}""")
        
        # 获取工具名称列表
        tool_names = [tool.name for tool in self.tools]
        prompt = ChatPromptTemplate.from_template(template)
        return create_react_agent(self.llm, self.tools, prompt)
    
    def _create_conversational_agent(self):
        """创建对话智能体"""
        # 从配置文件获取提示词模板
        template = config_loader.get_prompt_config("conversational_agent.template", """
        你是一个有帮助的AI助手。使用以下工具来回答用户的问题:

        {tools}

        工具名称:
        {tool_names}

        使用以下格式:

        Question: 输入的问题
        Thought: 你应该思考要做什么
        Action: 要使用的工具名称
        Action Input: 工具的输入
        Observation: 工具的输出
        ... (这个思考/行动/观察可以重复多次)
        Thought: 我现在知道最终答案了
        Final Answer: 对原始问题的最终答案

        开始!

        Question: {input}
        Thought: {agent_scratchpad}""")
        
        # 获取工具名称列表
        tool_names = [tool.name for tool in self.tools]
        prompt = ChatPromptTemplate.from_template(template)
        return create_react_agent(self.llm, self.tools, prompt)
    
    def _create_structured_chat_agent(self):
        """创建结构化聊天智能体"""
        # 从配置文件获取提示词模板
        template = config_loader.get_prompt_config("structured_chat_agent.template", """
        你是一个有帮助的AI助手。使用以下工具来回答用户的问题。

        你可以使用以下工具:
        {tools}

        工具名称:
        {tool_names}

        使用以下格式进行响应:
        ```
        Thought: 你应该思考要做什么
        Action: 要使用的工具名称
        Action Input: 工具的输入参数（必须是有效的JSON格式）
        ```
        然后你会得到工具的输出结果，继续这个过程直到你能够回答用户的问题。

        最后，使用以下格式提供最终答案:
        ```
        Thought: 我现在知道最终答案了
        Final Answer: 对原始问题的最终答案
        ```

        重要提示:
        1. Action Input必须是有效的JSON格式
        2. 只使用提供的工具名称
        3. 确保JSON格式正确，特别是字符串要用双引号

        开始!

        Question: {input}
        {agent_scratchpad}""")
        
        # 获取工具名称列表
        tool_names = [tool.name for tool in self.tools]
        prompt = ChatPromptTemplate.from_template(template)
        return create_structured_chat_agent(self.llm, self.tools, prompt)
    
    def _create_agent_executor(self):
        """
        创建智能体执行器
        
        Returns:
            智能体执行器实例
        """
        if self.memory:
            # 使用RunnableWithMessageHistory包装智能体，实现记忆功能
            agent_with_history = RunnableWithMessageHistory(
                self.agent,
                lambda session_id: self.memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            return agent_with_history
        else:
            # 如果不需要记忆功能，直接使用AgentExecutor
            return AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                agent_kwargs={
                    "tool_names": [tool.name for tool in self.tools]
                }
            )
    
    def run(self, query: str, session_id: str = "default") -> str:
        """
        运行智能体
        
        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            智能体响应
        """
        try:
            if self.memory:
                # 使用RunnableWithMessageHistory的invoke方法
                response = self.agent_executor.invoke(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}}
                )
                return response.get("output", "未收到有效响应")
            else:
                # 使用AgentExecutor的invoke方法
                response = self.agent_executor.invoke({"input": query})
                return response.get("output", "未收到有效响应")
        except Exception as e:
            return f"智能体运行出错: {str(e)}"
    
    async def arun(self, query: str, session_id: str = "default") -> str:
        """
        异步运行智能体
        
        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            智能体响应
        """
        try:
            if self.memory:
                # 使用RunnableWithMessageHistory的ainvoke方法
                response = await self.agent_executor.ainvoke(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}}
                )
                return response.get("output", "未收到有效响应")
            else:
                # 使用AgentExecutor的ainvoke方法
                response = await self.agent_executor.ainvoke({"input": query})
                return response.get("output", "未收到有效响应")
        except Exception as e:
            return f"智能体运行出错: {str(e)}"
    
    def chat(self, message: str, history: Optional[List[BaseMessage]] = None, session_id: str = "default") -> str:
        """
        对话模式
        
        Args:
            message: 用户消息
            history: 对话历史
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            智能体响应
        """
        try:
            if history and self.memory:
                # 如果提供了历史记录，更新记忆
                self.memory.messages = history
            
            if self.memory:
                # 使用RunnableWithMessageHistory的invoke方法
                response = self.agent_executor.invoke(
                    {"input": message},
                    config={"configurable": {"session_id": session_id}}
                )
                return response.get("output", "未收到有效响应")
            else:
                # 使用AgentExecutor的invoke方法
                response = self.agent_executor.invoke({"input": message})
                return response.get("output", "未收到有效响应")
        except Exception as e:
            return f"对话出错: {str(e)}"
    
    def clear_memory(self) -> None:
        """清除记忆"""
        if self.memory:
            self.memory.clear()
    
    def get_memory(self) -> List[BaseMessage]:
        """
        获取记忆内容
        
        Returns:
            记忆消息列表
        """
        if self.memory:
            return self.memory.messages
        return []