"""
调试日志过滤器模块
提供过滤调试信息的功能
"""

import logging
import warnings
from typing import Dict, Any


class DebugFilter(logging.Filter):
    """调试日志过滤器"""
    
    def __init__(self, debug_config: Dict[str, Any]):
        super().__init__()
        self.debug_config = debug_config
        self.enabled = debug_config.get("enabled", False)
        self.show_system_logs = debug_config.get("show_system_logs", True)
        self.show_agent_logs = debug_config.get("show_agent_logs", True)
        self.show_tool_logs = debug_config.get("show_tool_logs", True)
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录"""
        # 如果启用了调试模式，显示所有日志
        if self.enabled:
            return True
        
        # 非调试模式，只显示用户与智能体的对话信息
        # 过滤掉系统日志、智能体内部日志和工具调用日志
        logger_name = record.name
        
        # 过滤系统日志
        if not self.show_system_logs and any(name in logger_name for name in ["langsmith", "urllib3", "httpx", "openai", "httpcore"]):
            return False
        
        # 过滤智能体内部日志
        if not self.show_agent_logs and "src.agents" in logger_name:
            return False
        
        # 过滤工具调用日志
        if not self.show_tool_logs and "src.tools" in logger_name:
            return False
        
        # 默认显示
        return True


class ConversationFilter(logging.Filter):
    """对话日志过滤器，只显示用户与智能体的对话信息"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录，只保留对话信息"""
        logger_name = record.name
        
        # 过滤系统日志
        if any(name in logger_name for name in ["langsmith", "urllib3", "httpx", "openai", "httpcore"]):
            return False
        
        # 过滤智能体内部日志
        if "src.agents" in logger_name and record.levelno == logging.DEBUG:
            return False
        
        # 过滤工具调用日志
        if "src.tools" in logger_name:
            return False
        
        # 默认显示
        return True


class CrewAIFilter(logging.Filter):
    """CrewAI过滤器，隐藏debug信息但保留CrewAI执行过程"""
    
    def __init__(self, debug_config: Dict[str, Any]):
        super().__init__()
        self.debug_config = debug_config
        self.enabled = debug_config.get("enabled", False)
        self.show_system_logs = debug_config.get("show_system_logs", False)
        self.show_agent_logs = debug_config.get("show_agent_logs", False)
        self.show_tool_logs = debug_config.get("show_tool_logs", False)
        self.show_crewai_execution = debug_config.get("show_crewai_execution", True)
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录"""
        # 如果启用了调试模式，显示所有日志
        if self.enabled:
            return True
        
        logger_name = record.name
        message = record.getMessage()
        
        # 显示CrewAI执行过程
        if self.show_crewai_execution:
            # CrewAI运行时输出
            if "CrewAIRuntime" in logger_name or "crewai_runtime" in logger_name:
                return True
            
            # CrewAI相关输出
            if any(keyword in message for keyword in [
                "已创建智能体", "已创建任务", "团队", "创建成功", 
                "运行CrewAI团队", "团队执行结果", "配置文件", "执行时间",
                "查询", "结果", "已保存到文件"
            ]):
                return True
            
            # CrewAI工具执行过程
            if "crewai_runtime_tool" in logger_name:
                return True
            
            # CrewAI原生输出
            if "crewai" in logger_name.lower():
                return True
        
        # 过滤系统日志
        if not self.show_system_logs and any(name in logger_name for name in ["langsmith", "urllib3", "httpx", "openai", "httpcore"]):
            return False
        
        # 过滤智能体内部日志
        if not self.show_agent_logs and "src.agents" in logger_name:
            return False
        
        # 过滤工具调用日志（除了CrewAI）
        if not self.show_tool_logs and "src.tools" in logger_name and "crewai" not in logger_name:
            return False
        
        # 过滤DEBUG级别日志
        if record.levelno == logging.DEBUG:
            return False
        
        # 默认显示INFO及以上级别的日志
        return True


def setup_debug_filters(debug_mode: bool, debug_config: Dict[str, Any]) -> None:
    """设置调试过滤器"""
    root_logger = logging.getLogger()
    
    # 过滤LangSmith警告
    if not debug_mode:
        warnings.filterwarnings("ignore", category=UserWarning, message=".*API key must be provided when using hosted LangSmith API.*")
    
    if debug_mode:
        # 调试模式，使用DebugFilter
        debug_filter = DebugFilter(debug_config)
        for handler in root_logger.handlers:
            handler.addFilter(debug_filter)
    elif debug_config.get("show_crewai_execution", False):
        # CrewAI模式：隐藏debug信息但保留CrewAI执行过程
        crewai_filter = CrewAIFilter(debug_config)
        for handler in root_logger.handlers:
            handler.addFilter(crewai_filter)
    else:
        # 非调试模式，使用ConversationFilter
        conversation_filter = ConversationFilter()
        for handler in root_logger.handlers:
            handler.addFilter(conversation_filter)
    
    # 发出警告
    if not debug_mode and debug_config.get("show_crewai_execution", False):
        warnings.warn("CrewAI执行过程已启用，但debug模式未开启", UserWarning)