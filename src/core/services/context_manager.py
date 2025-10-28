"""
上下文管理服务
提供对话历史的摘要、压缩、检索功能
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class ContextManager:
    """
    上下文管理器
    
    负责管理对话上下文，包括：
    1. 对话历史摘要
    2. Token数量控制
    3. 关键信息保留
    4. 上下文压缩
    """
    
    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        max_tokens: int = 4000,
        summary_threshold: int = 10,  # 超过10轮对话就生成摘要
        keep_recent: int = 4,  # 保留最近4轮完整对话
    ):
        """
        初始化上下文管理器
        
        Args:
            llm: 语言模型，用于生成摘要
            max_tokens: 最大token数量
            summary_threshold: 触发摘要的对话轮数阈值
            keep_recent: 保留最近几轮完整对话
        """
        self.llm = llm
        self.max_tokens = max_tokens
        self.summary_threshold = summary_threshold
        self.keep_recent = keep_recent
        self.summary_history: List[str] = []  # 存储历史摘要
        
    def manage_context(
        self, 
        messages: List[BaseMessage],
        force_summary: bool = False
    ) -> List[BaseMessage]:
        """
        管理上下文，自动压缩和摘要
        
        Args:
            messages: 消息列表
            force_summary: 是否强制生成摘要
            
        Returns:
            处理后的消息列表
        """
        if not messages:
            return messages
        
        # 1. 检查是否需要压缩
        conversation_rounds = self._count_conversation_rounds(messages)
        
        if conversation_rounds <= self.summary_threshold and not force_summary:
            # 对话轮数未超过阈值，不需要压缩
            return messages
        
        # 2. 需要压缩：提取最近的对话和旧对话
        recent_messages = self._get_recent_messages(messages, self.keep_recent)
        old_messages = messages[:-len(recent_messages)] if len(messages) > len(recent_messages) else []
        
        # 3. 生成旧对话的摘要
        if old_messages and self.llm:
            summary = self._generate_summary(old_messages)
            if summary:
                self.summary_history.append(summary)
                # 创建摘要消息
                summary_message = SystemMessage(content=f"[对话历史摘要]: {summary}")
                return [summary_message] + recent_messages
        
        # 4. 如果没有LLM或摘要失败，使用简单压缩
        return self._simple_compression(messages)
    
    def _count_conversation_rounds(self, messages: List[BaseMessage]) -> int:
        """
        计算对话轮数（一轮 = 一个用户消息 + 一个AI消息）
        
        Args:
            messages: 消息列表
            
        Returns:
            对话轮数
        """
        human_count = sum(1 for msg in messages if isinstance(msg, HumanMessage))
        ai_count = sum(1 for msg in messages if isinstance(msg, AIMessage))
        return min(human_count, ai_count)
    
    def _get_recent_messages(
        self, 
        messages: List[BaseMessage], 
        keep_rounds: int
    ) -> List[BaseMessage]:
        """
        获取最近N轮对话
        
        Args:
            messages: 消息列表
            keep_rounds: 保留轮数
            
        Returns:
            最近的消息列表
        """
        if not messages:
            return []
        
        # 从后往前找，保留最近N轮完整对话
        kept_messages = []
        rounds_found = 0
        
        for msg in reversed(messages):
            kept_messages.insert(0, msg)
            if isinstance(msg, HumanMessage):
                rounds_found += 1
                if rounds_found >= keep_rounds:
                    break
        
        return kept_messages
    
    def _generate_summary(self, messages: List[BaseMessage]) -> Optional[str]:
        """
        生成对话摘要
        
        Args:
            messages: 消息列表
            
        Returns:
            摘要文本
        """
        if not self.llm or not messages:
            return None
        
        try:
            # 构建摘要提示词
            conversation_text = self._messages_to_text(messages)
            
            summary_prompt = f"""请总结以下对话的关键信息和上下文，保留重要的细节和决策：

{conversation_text}

请提供一个简洁但完整的摘要（不超过200字）："""
            
            # 调用LLM生成摘要
            response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"生成对话摘要: {len(summary)} 字符")
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return None
    
    def _messages_to_text(self, messages: List[BaseMessage]) -> str:
        """
        将消息列表转换为文本格式
        
        Args:
            messages: 消息列表
            
        Returns:
            文本格式的对话
        """
        text_lines = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                text_lines.append(f"用户: {msg.content}")
            elif isinstance(msg, AIMessage):
                text_lines.append(f"助手: {msg.content}")
            elif isinstance(msg, SystemMessage):
                text_lines.append(f"系统: {msg.content}")
        
        return "\n".join(text_lines)
    
    def _simple_compression(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        简单压缩：保留最近的消息
        
        Args:
            messages: 消息列表
            
        Returns:
            压缩后的消息列表
        """
        # 保留最近的消息
        keep_count = self.keep_recent * 2  # 每轮对话包含用户和AI消息
        return messages[-keep_count:] if len(messages) > keep_count else messages
    
    def estimate_tokens(self, messages: List[BaseMessage]) -> int:
        """
        估算消息列表的token数量（粗略估算）
        
        Args:
            messages: 消息列表
            
        Returns:
            估算的token数量
        """
        total_chars = sum(len(msg.content) for msg in messages if hasattr(msg, 'content'))
        # 粗略估算：中文约1.5字符/token，英文约4字符/token
        # 这里使用保守估算：2字符/token
        return total_chars // 2
    
    def should_compress(self, messages: List[BaseMessage]) -> bool:
        """
        判断是否应该压缩上下文
        
        Args:
            messages: 消息列表
            
        Returns:
            是否需要压缩
        """
        # 检查对话轮数
        rounds = self._count_conversation_rounds(messages)
        if rounds > self.summary_threshold:
            return True
        
        # 检查token数量
        estimated_tokens = self.estimate_tokens(messages)
        if estimated_tokens > self.max_tokens * 0.8:  # 超过80%就压缩
            return True
        
        return False
    
    def get_summary_history(self) -> List[str]:
        """
        获取历史摘要
        
        Returns:
            历史摘要列表
        """
        return self.summary_history.copy()
    
    def clear_summary_history(self):
        """清除历史摘要"""
        self.summary_history.clear()
        logger.info("已清除历史摘要")


class ConversationBufferWithSummary:
    """
    带摘要的对话缓冲区
    结合了InMemoryChatMessageHistory和ContextManager
    """
    
    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        max_tokens: int = 4000,
        summary_threshold: int = 10,
        keep_recent: int = 4,
    ):
        """
        初始化带摘要的对话缓冲区
        
        Args:
            llm: 语言模型
            max_tokens: 最大token数
            summary_threshold: 摘要阈值
            keep_recent: 保留最近对话轮数
        """
        from langchain_core.chat_history import InMemoryChatMessageHistory
        
        self.messages_history = InMemoryChatMessageHistory()
        self.context_manager = ContextManager(
            llm=llm,
            max_tokens=max_tokens,
            summary_threshold=summary_threshold,
            keep_recent=keep_recent
        )
    
    @property
    def messages(self) -> List[BaseMessage]:
        """
        获取管理后的消息
        
        Returns:
            压缩和摘要后的消息列表
        """
        raw_messages = self.messages_history.messages
        
        # 检查是否需要压缩
        if self.context_manager.should_compress(raw_messages):
            return self.context_manager.manage_context(raw_messages)
        
        return raw_messages
    
    @messages.setter
    def messages(self, value: List[BaseMessage]):
        """设置消息"""
        self.messages_history.messages = value
    
    def add_message(self, message: BaseMessage):
        """添加消息"""
        self.messages_history.add_message(message)
    
    def add_user_message(self, message: str):
        """添加用户消息"""
        self.messages_history.add_user_message(message)
    
    def add_ai_message(self, message: str):
        """添加AI消息"""
        self.messages_history.add_ai_message(message)
    
    def add_messages(self, messages: List[BaseMessage]):
        """
        批量添加消息（用于兼容 LangChain）
        
        Args:
            messages: 消息列表
        """
        for message in messages:
            self.messages_history.add_message(message)
    
    def clear(self):
        """清除所有消息和摘要"""
        self.messages_history.clear()
        self.context_manager.clear_summary_history()
    
    def get_summary_history(self) -> List[str]:
        """获取摘要历史"""
        return self.context_manager.get_summary_history()

