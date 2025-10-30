"""
API回调处理器 - 捕获AI的完整思维链
用于在API模式下记录Agent的思考过程、工具调用和观察结果
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    from langchain_core.callbacks import BaseCallbackHandler

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)


class APICallbackHandler(BaseCallbackHandler):
    """
    API回调处理器
    
    捕获并记录AI的完整思维链：
    - 思考过程（Thought）
    - 工具调用（Action）
    - 执行结果（Observation）
    """
    
    def __init__(self, session_id: str, thinking_callback: Optional[callable] = None):
        """
        初始化回调处理器
        
        Args:
            session_id: 会话ID
            thinking_callback: 思考过程回调函数
        """
        super().__init__()
        self.session_id = session_id
        self.thinking_callback = thinking_callback
        self.step_count = 0
        self.current_step = {}
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """链开始时调用"""
        if self.thinking_callback:
            self.thinking_callback({
                "type": "chain_start",
                "session_id": self.session_id,
                "input": inputs.get("input", ""),
                "timestamp": datetime.now()
            })
            logger.info(f"🔗 Agent链启动: {self.session_id}")
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """LLM开始思考时调用"""
        if self.thinking_callback:
            self.thinking_callback({
                "type": "thinking",
                "session_id": self.session_id,
                "status": "thinking",
                "message": "正在思考...",
                "timestamp": datetime.now()
            })
            logger.info(f"🤔 开始思考: {self.session_id}")
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Agent执行动作时调用"""
        self.step_count += 1
        
        # 提取思考过程
        thought = self._extract_thought(action.log)
        
        # 记录思考过程
        if thought and self.thinking_callback:
            self.thinking_callback({
                "type": "thought",
                "session_id": self.session_id,
                "step": self.step_count,
                "content": thought,
                "timestamp": datetime.now()
            })
            logger.info(f"💭 思考步骤 {self.step_count}: {thought[:100]}...")
        
        # 记录工具调用
        if self.thinking_callback:
            self.thinking_callback({
                "type": "action",
                "session_id": self.session_id,
                "step": self.step_count,
                "tool": action.tool,
                "tool_input": action.tool_input,
                "status": "running",
                "timestamp": datetime.now()
            })
            logger.info(f"🔧 工具调用 {self.step_count}: {action.tool}")
        
        # 保存当前步骤信息（用于后续关联observation）
        self.current_step = {
            "step": self.step_count,
            "tool": action.tool,
            "tool_input": action.tool_input,
            "start_time": datetime.now()
        }
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """工具执行结束时调用"""
        if self.thinking_callback and self.current_step:
            execution_time = (datetime.now() - self.current_step.get("start_time", datetime.now())).total_seconds()
            
            self.thinking_callback({
                "type": "observation",
                "session_id": self.session_id,
                "step": self.current_step.get("step"),
                "tool": self.current_step.get("tool"),
                "output": output,
                "execution_time": execution_time,
                "status": "success",
                "timestamp": datetime.now()
            })
            logger.info(f"✅ 工具完成 {self.current_step.get('step')}: {self.current_step.get('tool')}")
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """工具执行错误时调用"""
        if self.thinking_callback and self.current_step:
            self.thinking_callback({
                "type": "observation",
                "session_id": self.session_id,
                "step": self.current_step.get("step"),
                "tool": self.current_step.get("tool"),
                "error": str(error),
                "status": "error",
                "timestamp": datetime.now()
            })
            logger.error(f"❌ 工具错误 {self.current_step.get('step')}: {str(error)}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        """Agent完成时调用"""
        # 提取最终思考
        final_thought = self._extract_final_thought(finish.log)
        
        if final_thought and self.thinking_callback:
            self.thinking_callback({
                "type": "final_thought",
                "session_id": self.session_id,
                "content": final_thought,
                "timestamp": datetime.now()
            })
            logger.info(f"💡 最终思考: {final_thought[:100]}...")
        
        if self.thinking_callback:
            self.thinking_callback({
                "type": "complete",
                "session_id": self.session_id,
                "timestamp": datetime.now()
            })
            logger.info(f"✅ Agent完成: {self.session_id}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """链结束时调用"""
        pass
    
    def _extract_thought(self, log: str) -> str:
        """提取思考过程"""
        import re
        
        # 尝试提取Thought部分
        patterns = [
            r"Thought:\s*(.*?)(?=\n(?:Action|Final Answer|$))",
            r"思考[:：]\s*(.*?)(?=\n(?:动作|最终答案|$))",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                # 清理多余的空白
                thought = re.sub(r'\n\s*\n', '\n', thought)
                return thought
        
        return ""
    
    def _extract_final_thought(self, log: str) -> str:
        """提取最终思考"""
        import re
        
        # 尝试提取Final Answer之前的Thought
        patterns = [
            r"Thought:\s*(.*?)(?=Final Answer)",
            r"思考[:：]\s*(.*?)(?=最终答案)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                thought = re.sub(r'\n\s*\n', '\n', thought)
                return thought
        
        return ""

