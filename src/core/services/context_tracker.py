"""
上下文追踪器 - 追踪智能体的执行历史和上下文
"""

from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContextTracker:
    """智能体上下文追踪器"""
    
    def __init__(self, max_history: int = 10):
        """
        初始化上下文追踪器
        
        Args:
            max_history: 保存的最大历史记录数
        """
        self.max_history = max_history
        self.query_history = deque(maxlen=max_history)
        self.tool_history = deque(maxlen=max_history)
        self.logger = logging.getLogger(__name__)
    
    def add_query(self, query: str):
        """
        添加查询到历史
        
        Args:
            query: 用户查询
        """
        self.query_history.append({
            "timestamp": datetime.now(),
            "query": query
        })
        self.logger.debug(f"添加查询到历史: {query[:50]}...")
    
    def add_tool_call(self, tool_name: str, result: Any):
        """
        添加工具调用到历史
        
        Args:
            tool_name: 工具名称
            result: 执行结果
        """
        # 🔥 修复: 如果result是dict类型，使用JSON序列化而非str()
        import json
        if isinstance(result, dict):
            result_str = json.dumps(result, ensure_ascii=False)
        else:
            result_str = str(result)
        
        self.tool_history.append({
            "timestamp": datetime.now(),
            "tool": tool_name,
            "result_summary": result_str[:200] if len(result_str) > 200 else result_str,  # 只保存摘要
            "result_raw": result if isinstance(result, dict) else None  # 保存原始dict对象
        })
        self.logger.debug(f"添加工具调用到历史: {tool_name}")
    
    def get_last_tool(self) -> Optional[str]:
        """
        获取最后调用的工具
        
        Returns:
            最后调用的工具名称，如果没有则返回 None
        """
        if self.tool_history:
            return self.tool_history[-1]["tool"]
        return None
    
    def get_last_query(self) -> Optional[str]:
        """
        获取最后的查询
        
        Returns:
            最后的查询内容，如果没有则返回 None
        """
        if self.query_history:
            return self.query_history[-1]["query"]
        return None
    
    def get_context_summary(self, n: int = 3) -> str:
        """
        获取最近 n 步的上下文摘要
        
        Args:
            n: 获取的历史步骤数
        
        Returns:
            上下文摘要文本
        """
        recent = list(self.tool_history)[-n:]
        if not recent:
            return "无历史操作"
        
        summary = "最近操作:\n"
        for i, item in enumerate(recent, 1):
            summary += f"{i}. {item['tool']}: {item['result_summary'][:50]}...\n"
        return summary
    
    def is_context_dependent(self, query: str) -> bool:
        """
        判断查询是否依赖上下文
        
        Args:
            query: 用户查询
        
        Returns:
            是否依赖上下文
        """
        # 上下文依赖关键词
        context_keywords = [
            "它", "他", "她", "这个", "那个",
            "刚才", "上一步", "之前", "刚刚",
            "运行", "执行", "启动",
            "继续", "接着"
        ]
        
        return any(keyword in query for keyword in context_keywords)
    
    def generate_context_hint(self, query: str) -> str:
        """
        生成上下文提示
        
        Args:
            query: 用户查询
        
        Returns:
            增强后的查询（包含上下文提示）
        """
        if not self.is_context_dependent(query):
            return query
        
        last_tool = self.get_last_tool()
        if not last_tool:
            return query
        
        # 根据最后的工具生成提示
        hints = {
            "crewai_generator": "\n[上下文提示: 上一步刚生成了 CrewAI 配置，用户可能想运行它。优先考虑使用 crewai_runtime 工具]",
            "n8n_generate_and_create_workflow": "\n[上下文提示: 上一步刚创建了 n8n 工作流，用户可能想执行或查看它]",
            "crewai_runtime": "\n[上下文提示: 上一步刚运行了 CrewAI 团队，用户可能想查看结果或继续操作]"
        }
        
        hint = hints.get(last_tool, f"\n[上下文提示: 上一步使用了 {last_tool} 工具]")
        return query + hint
    
    def clear(self):
        """清空所有历史记录"""
        self.query_history.clear()
        self.tool_history.clear()
        self.logger.info("清空上下文历史")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        tool_counts = {}
        for item in self.tool_history:
            tool = item["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        return {
            "total_queries": len(self.query_history),
            "total_tool_calls": len(self.tool_history),
            "unique_tools": len(tool_counts),
            "tool_counts": tool_counts,
            "last_tool": self.get_last_tool(),
            "last_query": self.get_last_query()
        }

