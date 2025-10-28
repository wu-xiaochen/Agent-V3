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
from src.agents.shared.tools import get_tools, get_tools_for_agent
from src.agents.shared.output_formatter import OutputFormatter, OutputFormat
from src.agents.shared.streaming_handler import StreamingDisplayHandler, SimpleStreamingHandler
from src.config.config_loader import config_loader
from src.prompts.prompt_loader import prompt_loader
from src.core.services.context_manager import ConversationBufferWithSummary, ContextManager


class UnifiedAgent:
    """统一智能体，结合ReAct架构、多轮对话记忆、工具调用和可配置输出格式"""
    
    def __init__(
        self, 
        provider: Optional[str] = None, 
        memory: bool = True,
        redis_url: Optional[str] = None,
        session_id: Optional[str] = None,
        model_name: Optional[str] = None,
        streaming_style: str = "simple",  # simple, detailed, none
        **kwargs
    ):
        """
        初始化统一智能体
        
        Args:
            provider: LLM提供商
            memory: 是否启用记忆功能
            redis_url: Redis连接URL，如果为None则从配置文件获取
            session_id: 会话ID，用于区分不同对话
            model_name: 模型名称
            streaming_style: 流式输出样式 (simple=简洁, detailed=详细, none=无)
            **kwargs: 额外的LLM参数
        """
        self.streaming_style = streaming_style
        # 处理模型名称参数
        if model_name:
            kwargs["model_name"] = model_name
            
        self.llm = LLMFactory.create_llm(provider, **kwargs)
        self.agent_config = config_loader.get_agent_config()
        self.output_config = config_loader.get_output_config()
        
        # 如果没有提供redis_url，从配置文件获取
        if redis_url is None and memory:
            redis_config = config_loader.get_redis_config()
            if redis_config:
                host = redis_config.get("host", "localhost")
                port = redis_config.get("port", 6379)
                db = redis_config.get("db", 0)
                password = redis_config.get("password", "")
                
                # 构建Redis URL
                if password:
                    redis_url = f"redis://:{password}@{host}:{port}/{db}"
                else:
                    redis_url = f"redis://{host}:{port}/{db}"
        
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
                print(f"✅ 使用Redis存储对话历史 (会话ID: {session_id or 'default'})")
                return RedisChatMessageHistory(
                    session_id=session_id or "default",
                    redis_url=redis_url
                )
            except ImportError:
                print("⚠️  Redis存储不可用，回退到内存存储（带摘要功能）")
            except Exception as e:
                print(f"⚠️  Redis连接失败: {e}，回退到内存存储（带摘要功能）")
        
        # 使用内存存储（带摘要和压缩功能）
        unified_config = config_loader.get_specific_agent_config("unified_agent")
        memory_config = unified_config.get("memory", {})
        
        max_tokens = memory_config.get("max_conversation_length", 4000)
        summary_threshold = memory_config.get("summary_interval", 10)
        
        print(f"✅ 使用内存存储对话历史（带自动摘要功能，每{summary_threshold}轮对话自动压缩）")
        
        # 使用带摘要功能的对话缓冲区
        return ConversationBufferWithSummary(
            llm=self.llm,
            max_tokens=max_tokens,
            summary_threshold=summary_threshold,
            keep_recent=4  # 保留最近4轮完整对话
        )
    
    def _create_agent(self):
        """
        创建智能体
        
        Returns:
            智能体实例
        """
        # 使用ReAct架构作为基础，但结合了其他智能体的特性
        # 获取统一智能体的配置
        unified_config = config_loader.get_specific_agent_config("unified_agent")
        
        # 从配置中获取提示词键
        system_prompt_key = unified_config.get("system_prompt", "supply_chain_planning")
        
        try:
            # 尝试从配置文件加载提示词
            prompts_config = config_loader.get_prompts_config()
            prompts = prompts_config.get("prompts", {})
            
            # 获取系统提示词
            prompt_config = prompts.get(system_prompt_key, {})
            system_prompt_template = prompt_config.get("template", "")
            
            if not system_prompt_template:
                # 回退到硬编码的提示词
                print(f"未找到配置的提示词 {system_prompt_key}，使用默认提示词")
                system_prompt_template = """你是一位专业的供应链管理专家和业务流程规划顾问。
你的主要职责是理解用户的供应链需求，提供专业的业务流程规划建议。

当用户询问关于n8n工作流或智能体对话生成时，你应该：
1. 明确告诉用户你可以使用n8n_mcp_generator工具来生成工作流
2. 询问用户需要什么类型的工作流或对话
3. 使用n8n_mcp_generator工具来完成任务

{agent_scratchpad}"""
            
            # 获取当前时间信息
            from datetime import datetime
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y年%m月%d日")
            current_year = datetime.now().year
            
            # 构建完整的React提示词模板 - 使用标准英文格式避免解析问题，包含对话历史
            template = f"""Current Date and Time: {current_datetime} (Beijing Time, UTC+8)
Current Year: {current_year}
Today is: {current_date}

IMPORTANT: When analyzing trends, news, market conditions, or any time-sensitive information, 
always consider the current date above. Use the 'time' tool if you need to verify the current time.

Answer the following questions as best you can. You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation history:
{{chat_history}}

New question: {{input}}
Thought:{{agent_scratchpad}}"""
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", template)
            ])
            
        except Exception as e:
            print(f"加载提示词配置失败: {e}，使用默认提示词")
            # 使用默认的React提示词
            from langchain import hub
            try:
                prompt = hub.pull("hwchase17/react-chat")
            except Exception as hub_error:
                print(f"无法从LangChain Hub获取提示词: {hub_error}")
                # 最后的回退方案
                template = """你是一个功能强大的通用智能助手。

你可以使用以下工具:
{tools}

工具名称:
{tool_names}

Question: {input}
Thought:{agent_scratchpad}"""
                prompt = ChatPromptTemplate.from_template(template)
        
        return create_react_agent(self.llm, self.tools, prompt)
    
    def _create_agent_executor(self):
        """
        创建智能体执行器
        
        Returns:
            智能体执行器实例
        """
        # 从配置文件读取迭代限制参数
        unified_config = config_loader.get_specific_agent_config("unified_agent")
        parameters = unified_config.get("parameters", {})
        max_iterations = parameters.get("max_iterations", 25)  # 默认25次
        max_execution_time = parameters.get("max_execution_time", 180)  # 默认3分钟
        
        # 创建流式处理器（根据配置选择）
        callbacks = []
        verbose_mode = False
        
        if self.streaming_style == "detailed":
            # 详细模式：显示完整的思考过程
            streaming_handler = StreamingDisplayHandler(verbose=True, show_colors=True)
            callbacks = [streaming_handler]
        elif self.streaming_style == "simple":
            # 简洁模式：显示简化的执行过程
            streaming_handler = SimpleStreamingHandler()
            callbacks = [streaming_handler]
        elif self.streaming_style == "none":
            # 无流式输出：只显示最终结果
            verbose_mode = False
        else:
            # 默认使用简洁模式
            streaming_handler = SimpleStreamingHandler()
            callbacks = [streaming_handler]
        
        # 创建基础的AgentExecutor
        executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose_mode,  # 根据模式决定是否verbose
            handle_parsing_errors=True,
            max_iterations=max_iterations,  # 从配置文件读取迭代次数
            max_execution_time=max_execution_time,  # 从配置文件读取执行时间
            callbacks=callbacks if callbacks else None,  # 添加流式处理器
            agent_kwargs={
                "tool_names": [tool.name for tool in self.tools]
            }
        )
        
        if self.memory:
            # 使用RunnableWithMessageHistory包装AgentExecutor，实现记忆功能
            def get_session_history(session_id: str):
                """获取会话历史，确保返回正确的 memory 对象"""
                # 对于 ConversationBufferWithSummary，它实现了 BaseChatMessageHistory 接口
                # 对于 RedisChatMessageHistory，也实现了同样的接口
                return self.memory
            
            agent_with_history = RunnableWithMessageHistory(
                executor,
                get_session_history,
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
                        "response": f"🔄 {str(step)}\n",
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
            print("✅ 对话历史已清除")
    
    def get_memory(self) -> List[BaseMessage]:
        """
        获取记忆内容
        
        Returns:
            记忆消息列表
        """
        if self.memory:
            return self.memory.messages
        return []
    
    def get_summary_history(self) -> List[str]:
        """
        获取对话摘要历史
        
        Returns:
            摘要历史列表
        """
        if self.memory and hasattr(self.memory, 'get_summary_history'):
            return self.memory.get_summary_history()
        return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            记忆统计字典
        """
        if not self.memory:
            return {
                "enabled": False,
                "message_count": 0,
                "summary_count": 0
            }
        
        from langchain_core.messages import HumanMessage as HumanMsg
        
        messages = self.memory.messages
        summaries = self.get_summary_history()
        
        return {
            "enabled": True,
            "message_count": len(messages),
            "summary_count": len(summaries),
            "conversation_rounds": len([m for m in messages if isinstance(m, HumanMsg)]),
            "memory_type": "redis" if self.redis_url else "in_memory_with_summary",
            "session_id": self.session_id
        }
    
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