"""
统一智能体模块
结合ReAct架构、多轮对话记忆、工具调用和可配置输出格式
"""

import warnings
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from src.infrastructure.llm.llm_factory import LLMFactory
from src.agents.shared.tools import get_tools
from src.agents.shared.output_formatter import OutputFormatter, OutputFormat
from src.config.config_loader import config_loader
from src.prompts.prompt_loader import prompt_loader


class UnifiedAgent:
    """统一智能体，结合ReAct架构、多轮对话记忆、工具调用和可配置输出格式"""
    
    def __init__(
        self, 
        provider: Optional[str] = None, 
        memory: bool = True,
        redis_url: Optional[str] = None,
        session_id: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ):
        """
        初始化统一智能体
        
        Args:
            provider: LLM提供商
            memory: 是否启用记忆功能
            redis_url: Redis连接URL，如果提供则使用Redis存储
            session_id: 会话ID，用于区分不同对话
            model_name: 模型名称
            **kwargs: 额外的LLM参数
        """
        # 处理模型名称参数
        if model_name:
            kwargs["model_name"] = model_name
            
        self.llm = LLMFactory.create_llm(provider, **kwargs)
        self.agent_config = config_loader.get_agent_config()
        self.output_config = config_loader.get_output_config()
        self.memory = self._create_memory(memory, redis_url, session_id)
        
        # 使用新的动态工具加载器
        try:
            # 尝试使用智能体特定的工具配置
            self.tools = get_tools_for_agent("unified_agent")
        except Exception as e:
            print(f"使用智能体特定工具配置失败: {e}")
            # 回退到默认工具列表
            self.tools = get_tools(["calculator", "search", "time", "crewai_generator", "crewai_runtime"]) if self.agent_config.get("enable_tools", True) else []
        
        # 使用配置文件中的输出格式初始化OutputFormatter
        output_format = self.output_config.get("format", "normal")
        self.output_formatter = OutputFormatter(output_format, self.output_config)
        
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor()
        
        # 存储会话信息
        self.session_id = session_id or "default"
        self.redis_url = redis_url
    
    def _create_memory(self, memory_enabled: bool, redis_url: Optional[str], session_id: Optional[str]):
        """
        创建记忆组件
        
        Args:
            memory_enabled: 是否启用记忆
            redis_url: Redis连接URL
            session_id: 会话ID
            
        Returns:
            记忆组件实例
        """
        if not memory_enabled:
            return None
        
        # 如果提供了Redis URL，使用Redis存储
        if redis_url:
            try:
                from src.storage.redis_chat_history import RedisChatMessageHistory
                return RedisChatMessageHistory(
                    session_id=session_id or "default",
                    redis_url=redis_url
                )
            except ImportError:
                print("Redis存储不可用，回退到内存存储")
            except Exception as e:
                print(f"Redis连接失败: {e}，回退到内存存储")
        
        # 使用内存存储
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
        # 使用ReAct架构作为基础，但结合了其他智能体的特性
        # 使用LangChain内置的ReAct提示词模板
        from langchain import hub
        
        # 获取统一智能体的配置
        unified_config = config_loader.get_specific_agent_config("unified_agent")
        
        # 从配置中获取提示词文件路径，如果未配置则使用默认路径
        prompts_file = unified_config.get("prompts_file", "src/prompts/prompts.py")
        
        try:
            # 尝试使用LangChain Hub中的ReAct提示词
            prompt = hub.pull("hwchase17/react-chat")
        except Exception as e:
            print(f"无法从LangChain Hub获取提示词，使用配置的提示词: {e}")
            
            # 使用提示词加载器加载系统提示词
            system_prompt_key = unified_config.get("system_prompt_key", "UNIFIED_AGENT_SYSTEM_PROMPT")
            
            # 检查是否是Python文件，如果是则直接导入
            if prompts_file.endswith('.py'):
                try:
                    # 动态导入Python模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("prompts_module", prompts_file)
                    prompts_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(prompts_module)
                    
                    # 获取提示词
                    system_prompt = getattr(prompts_module, system_prompt_key, "")
                except Exception as import_error:
                    print(f"无法从Python文件导入提示词: {import_error}")
                    system_prompt = "你是一个功能强大的通用智能助手，能够处理各种领域的任务和问题。"
            else:
                # 使用YAML加载器
                system_prompt = prompt_loader.get_prompt(prompts_file, system_prompt_key)
                if not system_prompt:
                    system_prompt = "你是一个功能强大的通用智能助手，能够处理各种领域的任务和问题。"
            
            # 构建完整的提示词模板
            template = f"""{system_prompt}

            你可以使用以下工具:
            {{tools}}

            工具名称:
            {{tool_names}}

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

            Question: {{input}}
            Thought:{{{{agent_scratchpad}}}}"""
            
            # 获取工具名称列表
            tool_names = [tool.name for tool in self.tools]
            prompt = ChatPromptTemplate.from_template(template)
        
        return create_react_agent(self.llm, self.tools, prompt)
    
    def _create_agent_executor(self):
        """
        创建智能体执行器
        
        Returns:
            智能体执行器实例
        """
        # 创建基础的AgentExecutor
        executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={
                "tool_names": [tool.name for tool in self.tools]
            }
        )
        
        if self.memory:
            # 使用RunnableWithMessageHistory包装AgentExecutor，实现记忆功能
            agent_with_history = RunnableWithMessageHistory(
                executor,
                lambda session_id: self.memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            return agent_with_history
        else:
            # 如果不需要记忆功能，直接使用AgentExecutor
            return executor
    
    def run(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        运行智能体
        
        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            包含响应和元数据的字典
        """
        try:
            if self.memory:
                # 使用RunnableWithMessageHistory的invoke方法
                # 不需要在这里添加intermediate_steps，因为AgentExecutor会处理
                response = self.agent_executor.invoke(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}}
                )
            else:
                # 使用AgentExecutor的invoke方法
                response = self.agent_executor.invoke({"input": query})
            
            # 处理不同类型的响应
            if hasattr(response, 'get'):
                # 字典类型响应
                raw_output = response.get("output", "未收到有效响应")
            elif hasattr(response, 'return_values'):
                # AgentFinish对象类型响应
                raw_output = response.return_values.get("output", "未收到有效响应")
            else:
                # 其他类型，尝试直接转换为字符串
                raw_output = str(response)
            
            # 构建元数据
            metadata = {
                "query": query,
                "tools_used": [tool.name for tool in self.tools],
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id,
                "has_memory": self.memory is not None,
                "memory_type": "redis" if self.redis_url else "in_memory"
            }
            
            # 使用OutputFormatter格式化响应
            formatted_response = self.output_formatter.format_response(raw_output, metadata)
            
            return {
                "response": formatted_response,
                "metadata": metadata
            }
        except Exception as e:
            error_msg = f"智能体运行出错: {str(e)}"
            metadata = {
                "query": query,
                "error": str(e),
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id
            }
            return {
                "response": error_msg,
                "metadata": metadata
            }
    
    async def arun(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        异步运行智能体
        
        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            包含响应和元数据的字典
        """
        try:
            if self.memory:
                # 使用RunnableWithMessageHistory的ainvoke方法
                # 不需要在这里添加intermediate_steps，因为AgentExecutor会处理
                response = await self.agent_executor.ainvoke(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}}
                )
            else:
                # 使用AgentExecutor的ainvoke方法
                response = await self.agent_executor.ainvoke({"input": query})
            
            # 处理不同类型的响应
            if hasattr(response, 'get'):
                # 字典类型响应
                raw_output = response.get("output", "未收到有效响应")
            elif hasattr(response, 'return_values'):
                # AgentFinish对象类型响应
                raw_output = response.return_values.get("output", "未收到有效响应")
            else:
                # 其他类型，尝试直接转换为字符串
                raw_output = str(response)
            
            # 构建元数据
            metadata = {
                "query": query,
                "tools_used": [tool.name for tool in self.tools],
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id,
                "has_memory": self.memory is not None,
                "memory_type": "redis" if self.redis_url else "in_memory"
            }
            
            # 使用OutputFormatter格式化响应
            formatted_response = self.output_formatter.format_response(raw_output, metadata)
            
            return {
                "response": formatted_response,
                "metadata": metadata
            }
        except Exception as e:
            error_msg = f"智能体异步运行出错: {str(e)}"
            metadata = {
                "query": query,
                "error": str(e),
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id
            }
            return {
                "response": error_msg,
                "metadata": metadata
            }
    
    def chat(self, message: str, history: Optional[List[BaseMessage]] = None, session_id: str = "default") -> Dict[str, Any]:
        """
        对话模式
        
        Args:
            message: 用户消息
            history: 对话历史
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            包含响应和元数据的字典
        """
        try:
            if history and self.memory:
                # 如果提供了历史记录，更新记忆
                self.memory.messages = history
            
            if self.memory:
                # 使用RunnableWithMessageHistory的invoke方法
                # 不需要在这里添加intermediate_steps，因为AgentExecutor会处理
                response = self.agent_executor.invoke(
                    {"input": message},
                    config={"configurable": {"session_id": session_id}}
                )
            else:
                # 使用AgentExecutor的invoke方法
                response = self.agent_executor.invoke({"input": message})
            
            # 处理不同类型的响应
            if hasattr(response, 'get'):
                # 字典类型响应
                raw_output = response.get("output", "未收到有效响应")
            elif hasattr(response, 'return_values'):
                # AgentFinish对象类型响应
                raw_output = response.return_values.get("output", "未收到有效响应")
            else:
                # 其他类型，尝试直接转换为字符串
                raw_output = str(response)
            
            # 构建元数据
            metadata = {
                "query": message,
                "has_history": history is not None,
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id,
                "has_memory": self.memory is not None,
                "memory_type": "redis" if self.redis_url else "in_memory"
            }
            
            # 使用OutputFormatter格式化响应
            formatted_response = self.output_formatter.format_response(raw_output, metadata)
            
            return {
                "response": formatted_response,
                "metadata": metadata
            }
        except Exception as e:
            error_msg = f"对话出错: {str(e)}"
            metadata = {
                "query": message,
                "error": str(e),
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id
            }
            return {
                "response": error_msg,
                "metadata": metadata
            }
    
    def stream(self, query: str, session_id: str = "default"):
        """
        流式运行智能体
        
        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同对话
            
        Yields:
            流式输出的响应片段
        """
        try:
            if self.memory:
                # 使用RunnableWithMessageHistory的stream方法
                # 不需要在这里添加intermediate_steps，因为AgentExecutor会处理
                for chunk in self.agent_executor.stream(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}}
                ):
                    yield from self._process_stream_chunk(chunk, query)
            else:
                # 使用AgentExecutor的stream方法进行流式输出
                for chunk in self.agent_executor.stream({"input": query}):
                    yield from self._process_stream_chunk(chunk, query)
                    
        except Exception as e:
            error_msg = f"智能体流式运行出错: {str(e)}"
            metadata = {
                "query": query,
                "error": str(e),
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id
            }
            formatted_error = self.output_formatter.format_response(error_msg, metadata)
            yield {
                "response": formatted_error,
                "metadata": metadata
            }
    
    async def astream(self, query: str, session_id: str = "default"):
        """
        异步流式运行智能体
        
        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同对话
            
        Yields:
            异步流式输出的响应片段
        """
        try:
            if self.memory:
                # 使用RunnableWithMessageHistory的astream方法
                # 不需要在这里添加intermediate_steps，因为AgentExecutor会处理
                async for chunk in self.agent_executor.astream(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}}
                ):
                    for processed_chunk in self._process_stream_chunk(chunk, query):
                        yield processed_chunk
            else:
                # 使用AgentExecutor的astream方法进行异步流式输出
                async for chunk in self.agent_executor.astream({"input": query}):
                    for processed_chunk in self._process_stream_chunk(chunk, query):
                        yield processed_chunk
                    
        except Exception as e:
            error_msg = f"智能体异步流式运行出错: {str(e)}"
            metadata = {
                "query": query,
                "error": str(e),
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": session_id
            }
            formatted_error = self.output_formatter.format_response(error_msg, metadata)
            yield {
                "response": formatted_error,
                "metadata": metadata
            }
    
    def _process_stream_chunk(self, chunk: Dict[str, Any], query: str):
        """
        处理流式输出块
        
        Args:
            chunk: 流式输出块
            query: 原始查询
            
        Yields:
            处理后的输出片段
        """
        # 处理不同类型的输出块
        if isinstance(chunk, dict) and "output" in chunk:
            # 字典类型且有output键
            raw_output = chunk["output"]
            metadata = {
                "query": query,
                "tools_used": [tool.name for tool in self.tools],
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": self.session_id,
                "has_memory": self.memory is not None,
                "memory_type": "redis" if self.redis_url else "in_memory"
            }
            yield {
                "response": raw_output,
                "metadata": metadata
            }
        elif hasattr(chunk, 'return_values') and 'output' in chunk.return_values:
            # AgentFinish对象类型
            raw_output = chunk.return_values['output']
            metadata = {
                "query": query,
                "tools_used": [tool.name for tool in self.tools],
                "agent_type": "unified",
                "output_format": self.output_formatter.get_format(),
                "session_id": self.session_id,
                "has_memory": self.memory is not None,
                "memory_type": "redis" if self.redis_url else "in_memory"
            }
            yield {
                "response": raw_output,
                "metadata": metadata
            }
        elif isinstance(chunk, dict) and "steps" in chunk:
            # 中间步骤 - 修复intermediate_steps访问问题
            for step in chunk["steps"]:
                # 更安全的方式访问步骤内容
                if isinstance(step, (tuple, list)) and len(step) >= 2:
                    # 新版本可能是(action, observation)元组格式
                    action, observation = step[0], step[1]
                    
                    # 处理action
                    if hasattr(action, "tool"):
                        tool_name = action.tool
                        tool_input = getattr(action, "tool_input", str(action))
                        action_info = f"\n🔧 使用工具: {tool_name}\n📝 输入: {tool_input}\n"
                        yield {
                            "response": action_info,
                            "metadata": {
                                "query": query,
                                "agent_type": "unified",
                                "session_id": self.session_id,
                                "is_intermediate_step": True
                            }
                        }
                    else:
                        action_info = f"\n🔧 执行操作: {str(action)}\n"
                        yield {
                            "response": action_info,
                            "metadata": {
                                "query": query,
                                "agent_type": "unified",
                                "session_id": self.session_id,
                                "is_intermediate_step": True
                            }
                        }
                    
                    # 处理observation
                    obs_info = f"📊 结果: {str(observation)}\n"
                    yield {
                        "response": obs_info,
                        "metadata": {
                            "query": query,
                            "agent_type": "unified",
                            "session_id": self.session_id,
                            "is_intermediate_step": True
                        }
                    }
                elif hasattr(step, "action") and hasattr(step, "observation"):
                    # 旧版本对象格式
                    action = step.action
                    observation = step.observation
                    
                    # 输出动作信息
                    action_info = f"\n🔧 使用工具: {action.tool}\n"
                    action_info += f"📝 输入: {action.tool_input}\n"
                    yield {
                        "response": action_info,
                        "metadata": {
                            "query": query,
                            "agent_type": "unified",
                            "session_id": self.session_id,
                            "is_intermediate_step": True
                        }
                    }
                    
                    # 输出观察结果
                    obs_info = f"📊 结果: {observation}\n"
                    yield {
                        "response": obs_info,
                        "metadata": {
                            "query": query,
                            "agent_type": "unified",
                            "session_id": self.session_id,
                            "is_intermediate_step": True
                        }
                    }
                else:
                    # 其他格式，直接输出
                    yield {
                        "response": f"🔄 步骤: {str(step)}\n",
                        "metadata": {
                            "query": query,
                            "agent_type": "unified",
                            "session_id": self.session_id,
                            "is_intermediate_step": True
                        }
                    }
        elif isinstance(chunk, dict) and "messages" in chunk:
            # 消息输出
            for message in chunk["messages"]:
                if hasattr(message, "content"):
                    yield {
                        "response": message.content,
                        "metadata": {
                            "query": query,
                            "agent_type": "unified",
                            "session_id": self.session_id,
                            "is_message": True
                        }
                    }
                else:
                    yield {
                        "response": str(message),
                        "metadata": {
                            "query": query,
                            "agent_type": "unified",
                            "session_id": self.session_id,
                            "is_message": True
                        }
                    }
        else:
            # 其他类型的输出，尝试直接转换为字符串
            yield {
                "response": str(chunk),
                "metadata": {
                    "query": query,
                    "agent_type": "unified",
                    "session_id": self.session_id,
                    "is_raw": True
                }
            }

    def set_output_format(self, format_type: str) -> None:
        """
        设置输出格式
        
        Args:
            format_type: 输出格式类型 (normal, markdown, json)
        """
        self.output_formatter.set_format(format_type)
    
    def get_output_format(self) -> str:
        """
        获取当前输出格式
        
        Returns:
            当前输出格式类型
        """
        return self.output_formatter.get_format()
    
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
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        获取会话信息
        
        Returns:
            会话信息字典
        """
        info = {
            "session_id": self.session_id,
            "has_memory": self.memory is not None,
            "memory_type": "redis" if self.redis_url else "in_memory",
            "output_format": self.output_formatter.get_format(),
            "tools_count": len(self.tools)
        }
        
        # 如果使用Redis存储，获取额外信息
        if self.redis_url and self.memory:
            try:
                redis_info = self.memory.get_session_info()
                info.update(redis_info)
            except Exception as e:
                info["redis_error"] = str(e)
        
        return info