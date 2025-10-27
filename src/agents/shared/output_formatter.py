"""
输出格式化模块
支持多种输出格式：JSON、Markdown、正常格式
"""

import json
from typing import Dict, Any, Optional
from enum import Enum


class OutputFormat(Enum):
    """输出格式枚举"""
    NORMAL = "normal"
    MARKDOWN = "markdown"
    JSON = "json"


class OutputFormatter:
    """输出格式化器"""
    
    def __init__(self, format_type: str = OutputFormat.NORMAL.value, config: Optional[Dict[str, Any]] = None):
        """
        初始化输出格式化器
        
        Args:
            format_type: 输出格式类型
            config: 输出格式配置，包含选项和自定义模板
        """
        self.format_type = format_type.lower()
        self.config = config or {}
        self.options = self.config.get("options", {})
        self.custom_templates = self.config.get("custom_templates", {})
    
    def format_response(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        格式化响应
        
        Args:
            response: 原始响应
            metadata: 元数据（可选）
            
        Returns:
            格式化后的响应
        """
        if self.format_type == OutputFormat.JSON.value:
            return self._format_as_json(response, metadata)
        elif self.format_type == OutputFormat.MARKDOWN.value:
            return self._format_as_markdown(response, metadata)
        else:
            return self._format_as_normal(response, metadata)
    
    def _format_as_json(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        格式化为JSON
        
        Args:
            response: 原始响应
            metadata: 元数据
            
        Returns:
            JSON格式的响应
        """
        # 检查是否有自定义JSON模板
        if "json" in self.custom_templates:
            template = self.custom_templates["json"]
            import datetime
            formatted_data = {
                "response": response,
                "timestamp": datetime.datetime.now().isoformat(),
                "agent": metadata.get("agent_name", "AI助手") if metadata else "AI助手"
            }
            
            # 如果有额外元数据，添加到formatted_data中
            if metadata:
                for key, value in metadata.items():
                    if key != "agent_name":
                        formatted_data[key] = value
            
            # 使用模板格式化
            try:
                return template.format(**formatted_data)
            except KeyError as e:
                # 如果模板中有未定义的变量，使用默认格式
                pass
        
        # 默认JSON格式
        data = {
            "response": response
        }
        
        if metadata:
            data["metadata"] = metadata
        
        # 根据配置决定是否美化输出
        indent = self.options.get("indent", 2) if self.options.get("pretty_print", True) else None
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    def _format_as_markdown(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        格式化为Markdown
        
        Args:
            response: 原始响应
            metadata: 元数据
            
        Returns:
            Markdown格式的响应
        """
        # 检查是否有自定义Markdown模板
        if "markdown" in self.custom_templates:
            template = self.custom_templates["markdown"]
            import datetime
            formatted_data = {
                "response": response,
                "timestamp": datetime.datetime.now().isoformat(),
                "agent": metadata.get("agent_name", "AI助手") if metadata else "AI助手"
            }
            
            # 如果有额外元数据，添加到formatted_data中
            if metadata:
                for key, value in metadata.items():
                    if key != "agent_name":
                        formatted_data[key] = value
            
            # 使用模板格式化
            try:
                return template.format(**formatted_data)
            except KeyError as e:
                # 如果模板中有未定义的变量，使用默认格式
                pass
        
        # 默认Markdown格式
        formatted = "# AI助手响应\n\n"
        formatted += f"{response}\n"
        
        if metadata and self.options.get("include_metadata", False):
            formatted += "\n---\n\n## 元数据\n\n"
            for key, value in metadata.items():
                formatted += f"- **{key}**: {value}\n"
        
        return formatted
    
    def _format_as_normal(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        格式为正常格式
        
        Args:
            response: 原始响应
            metadata: 元数据
            
        Returns:
            正常格式的响应
        """
        # 检查是否有自定义Normal模板
        if "normal" in self.custom_templates:
            template = self.custom_templates["normal"]
            import datetime
            formatted_data = {
                "response": response,
                "timestamp": datetime.datetime.now().isoformat(),
                "agent": metadata.get("agent_name", "AI助手") if metadata else "AI助手"
            }
            
            # 如果有额外元数据，添加到formatted_data中
            if metadata:
                for key, value in metadata.items():
                    if key != "agent_name":
                        formatted_data[key] = value
            
            # 使用模板格式化
            try:
                return template.format(**formatted_data)
            except KeyError as e:
                # 如果模板中有未定义的变量，使用默认格式
                pass
        
        # 默认正常格式
        return response
    
    def set_format(self, format_type: str) -> None:
        """
        设置输出格式
        
        Args:
            format_type: 输出格式类型
        """
        self.format_type = format_type.lower()
    
    def get_format(self) -> str:
        """
        获取当前输出格式
        
        Returns:
            当前输出格式类型
        """
        return self.format_type