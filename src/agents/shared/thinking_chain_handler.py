"""
思维链处理器 - 完整捕获Agent的思考过程
Thinking Chain Handler - Complete capture of Agent's reasoning process

功能：
- 捕获Thought（思考）
- 捕获Planning（规划）
- 捕获Action（动作）
- 捕获Observation（观察）
- 捕获Final Thought（最终分析）
"""

import logging
import re
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    from langchain_core.callbacks import BaseCallbackHandler

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)


class ThinkingChainHandler(BaseCallbackHandler):
    """
    思维链处理器
    
    完整记录Agent的思考、规划、行动、观察全过程
    支持实时回调和数据持久化
    """
    
    def __init__(
        self,
        session_id: str,
        on_update: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        初始化思维链处理器
        
        Args:
            session_id: 会话ID
            on_update: 更新回调函数，每次有新数据时调用
        """
        super().__init__()
        self.session_id = session_id
        self.on_update = on_update
        
        # 思维链数据
        self.chain: List[Dict[str, Any]] = []
        self.current_step = 0
        self.start_time = None
        self.current_action_start = None
        
        logger.info(f"🧠 ThinkingChainHandler initialized for session: {session_id}")
    
    def _emit_update(self, step_data: Dict[str, Any]):
        """发送更新事件"""
        step_data["session_id"] = self.session_id
        step_data["timestamp"] = datetime.now().isoformat()
        
        self.chain.append(step_data)
        
        if self.on_update:
            try:
                self.on_update(step_data)
            except Exception as e:
                logger.error(f"❌ 思维链更新回调失败: {e}")
        
        logger.debug(f"🔄 思维链更新: {step_data.get('type')} - {step_data.get('content', '')[:100]}")
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Agent链开始"""
        self.start_time = datetime.now()
        self.chain = []  # 重置思维链
        
        self._emit_update({
            "type": "chain_start",
            "step": 0,
            "content": "开始处理任务",
            "input": inputs.get("input", ""),
            "status": "running"
        })
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """LLM开始思考"""
        self._emit_update({
            "type": "thinking",
            "step": self.current_step,
            "content": "正在思考和分析问题...",
            "status": "running"
        })
    
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any
    ) -> None:
        """LLM思考结束"""
        # 从响应中提取思考内容
        if response.generations and len(response.generations) > 0:
            text = response.generations[0][0].text
            thought = self._extract_thought(text)
            
            if thought:
                self._emit_update({
                    "type": "thought",
                    "step": self.current_step,
                    "content": thought,
                    "status": "complete"
                })
    
    def on_agent_action(
        self,
        action: AgentAction,
        **kwargs: Any
    ) -> None:
        """Agent执行动作"""
        self.current_step += 1
        self.current_action_start = datetime.now()
        
        # 提取并记录思考过程
        thought = self._extract_thought(action.log)
        if thought:
            self._emit_update({
                "type": "thought",
                "step": self.current_step,
                "content": thought,
                "status": "complete"
            })
        
        # 提取并记录规划
        plan = self._extract_plan(action.log)
        if plan:
            self._emit_update({
                "type": "planning",
                "step": self.current_step,
                "content": plan,
                "status": "complete"
            })
        
        # 记录动作
        self._emit_update({
            "type": "action",
            "step": self.current_step,
            "tool": action.tool,
            "tool_input": action.tool_input,
            "content": f"调用工具: {action.tool}",
            "status": "running"
        })
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any
    ) -> None:
        """工具开始执行"""
        tool_name = serialized.get("name", "unknown")
        
        self._emit_update({
            "type": "tool_start",
            "step": self.current_step,
            "tool": tool_name,
            "input": input_str,
            "content": f"开始执行: {tool_name}",
            "status": "running"
        })
    
    def on_tool_end(
        self,
        output: str,
        **kwargs: Any
    ) -> None:
        """工具执行结束"""
        execution_time = 0
        if self.current_action_start:
            execution_time = (datetime.now() - self.current_action_start).total_seconds()
        
        self._emit_update({
            "type": "observation",
            "step": self.current_step,
            "content": output,
            "execution_time": execution_time,
            "status": "success"
        })
    
    def on_tool_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """工具执行错误"""
        self._emit_update({
            "type": "observation",
            "step": self.current_step,
            "content": str(error),
            "error": str(error),
            "status": "error"
        })
    
    def on_agent_finish(
        self,
        finish: AgentFinish,
        **kwargs: Any
    ) -> None:
        """Agent完成"""
        # 提取最终思考
        final_thought = self._extract_final_thought(finish.log)
        if final_thought:
            self._emit_update({
                "type": "final_thought",
                "step": self.current_step + 1,
                "content": final_thought,
                "status": "complete"
            })
        
        # 计算总耗时
        total_time = 0
        if self.start_time:
            total_time = (datetime.now() - self.start_time).total_seconds()
        
        self._emit_update({
            "type": "chain_end",
            "step": self.current_step + 1,
            "content": "任务完成",
            "total_time": total_time,
            "status": "complete"
        })
    
    def on_chain_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """链执行错误"""
        self._emit_update({
            "type": "chain_error",
            "step": self.current_step,
            "content": str(error),
            "error": str(error),
            "status": "error"
        })
    
    def _extract_thought(self, log: str) -> str:
        """
        从日志中提取思考内容
        
        支持格式：
        - Thought: ...
        - 思考: ...
        - I need to ...
        """
        if not log:
            return ""
        
        patterns = [
            r"Thought:\s*(.*?)(?=\n(?:Action|Final Answer|$))",
            r"思考[:：]\s*(.*?)(?=\n(?:动作|最终答案|$))",
            r"I need to\s*(.*?)(?=\n|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                # 清理多余的空白
                thought = re.sub(r'\n\s*\n', '\n', thought)
                thought = re.sub(r'\s+', ' ', thought)
                return thought
        
        return ""
    
    def _extract_plan(self, log: str) -> str:
        """
        从日志中提取规划内容
        
        支持格式：
        - Plan: ...
        - 规划: ...
        - I will ...
        """
        if not log:
            return ""
        
        patterns = [
            r"Plan:\s*(.*?)(?=\n(?:Action|Thought|$))",
            r"规划[:：]\s*(.*?)(?=\n(?:动作|思考|$))",
            r"I will\s*(.*?)(?=\n|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                plan = match.group(1).strip()
                plan = re.sub(r'\n\s*\n', '\n', plan)
                plan = re.sub(r'\s+', ' ', plan)
                return plan
        
        return ""
    
    def _extract_final_thought(self, log: str) -> str:
        """提取最终思考"""
        if not log:
            return ""
        
        patterns = [
            r"(?:Final )?Thought:\s*(.*?)(?=Final Answer|$)",
            r"(?:最终)?思考[:：]\s*(.*?)(?=最终答案|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                thought = re.sub(r'\n\s*\n', '\n', thought)
                thought = re.sub(r'\s+', ' ', thought)
                return thought
        
        return ""
    
    def get_chain(self) -> List[Dict[str, Any]]:
        """获取完整的思维链"""
        return self.chain
    
    def get_summary(self) -> Dict[str, Any]:
        """获取思维链摘要"""
        thoughts = [s for s in self.chain if s["type"] == "thought"]
        actions = [s for s in self.chain if s["type"] == "action"]
        observations = [s for s in self.chain if s["type"] == "observation"]
        
        total_time = 0
        if self.chain:
            end_step = next((s for s in reversed(self.chain) if s["type"] == "chain_end"), None)
            if end_step:
                total_time = end_step.get("total_time", 0)
        
        return {
            "session_id": self.session_id,
            "total_steps": self.current_step,
            "total_time": total_time,
            "thoughts_count": len(thoughts),
            "actions_count": len(actions),
            "observations_count": len(observations),
            "status": "complete" if any(s["type"] == "chain_end" for s in self.chain) else "running"
        }

