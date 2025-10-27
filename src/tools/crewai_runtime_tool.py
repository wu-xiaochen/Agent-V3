#!/usr/bin/env python3
"""
CrewAI运行时工具 - 支持从配置文件或JSON字符串创建CrewAI团队
"""

import os
import json
import sys
from typing import Dict, Any, Optional, Union
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from src.interfaces.crewai_runtime import CrewAIRuntime


class CrewAIRuntimeToolInput(BaseModel):
    """CrewAI运行时工具输入"""
    config: Union[str, Dict[str, Any]] = Field(
        description="CrewAI团队配置，可以是JSON字符串、配置文件路径或配置字典"
    )
    query: str = Field(
        description="要执行的任务或查询"
    )
    validate_config: bool = Field(
        default=True,
        description="是否验证配置（默认为True）"
    )


class CrewAIRuntimeTool(BaseTool):
    """CrewAI运行时工具"""
    name: str = "CrewAI运行时工具"
    description: str = "使用CrewAI创建和管理智能体团队，支持从配置文件或JSON字符串创建团队并执行任务"
    args_schema: type[BaseModel] = CrewAIRuntimeToolInput
    runtime: CrewAIRuntime = Field(default=None, init=False)
    
    def __init__(self, **kwargs):
        """初始化工具"""
        super().__init__(**kwargs)
        self.runtime = CrewAIRuntime()
    
    def _parse_input(self, tool_input: Union[str, Dict[str, Any]], tool_call_id: Optional[str] = None) -> Dict[str, Any]:
        """
        解析工具输入，支持多种格式
        
        Args:
            tool_input: 工具输入，可以是字符串或字典
            tool_call_id: 工具调用ID（可选）
            
        Returns:
            Dict[str, Any]: 解析后的参数字典
        """
        # 如果输入已经是字典，直接返回
        if isinstance(tool_input, dict):
            return tool_input
            
        # 如果输入是字符串，尝试解析
        if isinstance(tool_input, str):
            try:
                # 尝试解析为JSON
                parsed_input = json.loads(tool_input)
                
                # 如果解析成功，检查是否包含所需的字段
                if isinstance(parsed_input, dict):
                    # 确保所有必需字段都存在
                    if "query" not in parsed_input:
                        # 如果没有query字段，尝试从config中提取或使用默认值
                        if "config" in parsed_input and isinstance(parsed_input["config"], str):
                            # 如果config是字符串，使用它作为query
                            parsed_input["query"] = parsed_input["config"]
                        else:
                            # 否则使用默认查询
                            parsed_input["query"] = "请执行任务"
                    
                    if "config" not in parsed_input:
                        # 如果没有config字段，使用默认配置
                        parsed_input["config"] = "{}"
                    
                    if "validate_config" not in parsed_input:
                        # 如果没有validate_config字段，默认为True
                        parsed_input["validate_config"] = True
                    
                    return parsed_input
                else:
                    # 如果解析结果不是字典，创建默认参数
                    return {
                        "config": "{}",
                        "query": str(parsed_input),
                        "validate_config": True
                    }
            except json.JSONDecodeError:
                # 如果不是有效的JSON，将整个字符串作为query
                return {
                    "config": "{}",
                    "query": tool_input,
                    "validate_config": True
                }
        
        # 如果输入是其他类型，转换为字符串作为query
        return {
            "config": "{}",
            "query": str(tool_input),
            "validate_config": True
        }
    
    def _validate_config(self, config: Union[str, Dict[str, Any]]) -> bool:
        """
        验证配置
        
        Args:
            config: 配置内容，可以是JSON字符串、文件路径或配置字典
            
        Returns:
            bool: 验证是否通过
        """
        try:
            # 导入验证器
            from src.tools.crewai_config_validator import CrewAIConfigValidator
            
            # 创建验证器
            validator = CrewAIConfigValidator()
            
            # 根据配置类型进行验证
            if isinstance(config, str):
                # 检查是否是文件路径
                if os.path.exists(config):
                    result = validator.validate_config_file(config)
                else:
                    # 尝试解析为JSON
                    try:
                        config_dict = json.loads(config)
                        # 检查是否已经是包含crewai_config或crew的配置
                        if "crewai_config" in config_dict or "crew" in config_dict:
                            result = validator.validate_config_dict(config_dict)
                        else:
                            # 如果不是，包装成crewai_config格式
                            wrapped_config = {"crewai_config": config_dict}
                            result = validator.validate_config_dict(wrapped_config)
                            
                            # 如果包装后仍然验证失败，使用默认配置
                            if not result.is_valid:
                                default_config = self._get_default_config("默认任务")
                                result = validator.validate_config_dict(default_config)
                    except json.JSONDecodeError:
                        # 如果不是有效JSON，假设是简单字符串，创建默认配置
                        config_dict = self._get_default_config(config)
                        result = validator.validate_config_dict(config_dict)
            else:
                # 直接验证字典
                # 检查是否已经是包含crewai_config或crew的配置
                if "crewai_config" in config or "crew" in config:
                    result = validator.validate_config_dict(config)
                    
                    # 如果验证失败，使用默认配置
                    if not result.is_valid:
                        default_config = self._get_default_config("默认任务")
                        result = validator.validate_config_dict(default_config)
                else:
                    # 如果不是，包装成crewai_config格式
                    wrapped_config = {"crewai_config": config}
                    result = validator.validate_config_dict(wrapped_config)
                    
                    # 如果包装后仍然验证失败，使用默认配置
                    if not result.is_valid:
                        default_config = self._get_default_config("默认任务")
                        result = validator.validate_config_dict(default_config)
            
            # 输出验证结果
            if not result.is_valid:
                print("配置验证失败:")
                for error in result.errors:
                    print(f"  - {error}")
            
            if result.warnings:
                print("配置警告:")
                for warning in result.warnings:
                    print(f"  - {warning}")
            
            return result.is_valid
            
        except Exception as e:
            print(f"配置验证过程中出错: {str(e)}")
            return False
    
    def _get_default_config(self, task_description: str) -> Dict[str, Any]:
        """
        获取默认配置
        
        Args:
            task_description: 任务描述
            
        Returns:
            Dict: 默认配置字典
        """
        return {
            "crewai_config": {
                "name": "AI分析团队",
                "description": "专门用于分析问题和提供专业见解的AI团队",
                "agents": [
                    {
                        "name": "AI分析师",
                        "role": "专业分析师",
                        "goal": "提供深入、准确、有见地的分析",
                        "backstory": "你是一位经验丰富的专业分析师，擅长从多个角度分析复杂问题，并提供清晰、有条理的见解。"
                    }
                ],
                "tasks": [
                    {
                        "name": "分析任务",
                        "description": task_description,
                        "agent": "AI分析师",
                        "expected_output": "详细的分析报告，包含关键发现和建议"
                    }
                ]
            }
        }
    
    def _run(self, *args, **kwargs) -> str:
        """
        运行CrewAI工具
        
        Returns:
            str: 执行结果
        """
        # 解析参数
        if args:
            # 如果有位置参数，第一个参数应该是tool_input
            tool_input = args[0]
            parsed_input = self._parse_input(tool_input)
            
            # 提取参数
            query = parsed_input['query']
            config = parsed_input['config']
            validate_config = parsed_input.get('validate_config', True)
        elif 'tool_input' in kwargs:
            tool_input = kwargs['tool_input']
            parsed_input = self._parse_input(tool_input)
            
            # 提取参数
            query = parsed_input['query']
            config = parsed_input['config']
            validate_config = parsed_input.get('validate_config', True)
        elif 'query' in kwargs and 'config' in kwargs:
            # 如果参数已经解包为query和config
            query = kwargs['query']
            config = kwargs['config']
            validate_config = kwargs.get('validate_config', True)
        else:
            raise ValueError("无法识别的参数格式")
        
        # 创建运行时实例
        runtime = CrewAIRuntime()
        
        # 处理配置并加载
        final_config = self._process_config(config, query)
        runtime.load_config_from_dict(final_config)
        
        # 创建团队
        if not runtime.create_crew():
            return "创建CrewAI团队失败"
        
        # 从配置中获取任务描述
        task_description = query
        if "crewai_config" in final_config and "tasks" in final_config["crewai_config"] and final_config["crewai_config"]["tasks"]:
            task_description = final_config["crewai_config"]["tasks"][0].get("description", query)
        
        # 运行团队 - 使用正确的方法名和任务描述
        result = runtime.run_crew(task_description)
        
        if result is None:
            return "运行CrewAI团队时出错"
        
        return str(result)
    
    def _process_config(self, config: Union[str, Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        处理配置，确保配置有效
        
        Args:
            config: 原始配置
            query: 用户查询
            
        Returns:
            Dict: 处理后的配置
        """
        from .crewai_config_validator import CrewAIConfigValidator
        validator = CrewAIConfigValidator()
        
        if isinstance(config, str):
            # 如果是字符串，尝试解析为JSON
            try:
                config_dict = json.loads(config)
                # 检查是否已经是包含crewai_config或crew的配置
                if "crewai_config" in config_dict or "crew" in config_dict:
                    result = validator.validate_config_dict(config_dict)
                    if result.is_valid:
                        return config_dict
                else:
                    # 如果不是，包装成crewai_config格式
                    wrapped_config = {"crewai_config": config_dict}
                    result = validator.validate_config_dict(wrapped_config)
                    if result.is_valid:
                        return wrapped_config
            except json.JSONDecodeError:
                # 如果不是有效JSON，使用默认配置
                pass
        else:
            # 如果是字典
            # 检查是否已经是包含crewai_config或crew的配置
            if "crewai_config" in config or "crew" in config:
                result = validator.validate_config_dict(config)
                if result.is_valid:
                    return config
            else:
                # 如果不是，包装成crewai_config格式
                wrapped_config = {"crewai_config": config}
                result = validator.validate_config_dict(wrapped_config)
                if result.is_valid:
                    return wrapped_config
        
        # 如果所有尝试都失败，使用默认配置
        return self._get_default_config(query)
    
    async def _arun(
        self,
        config: Union[str, Dict[str, Any]],
        query: str,
        validate_config: bool = True,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """异步运行工具"""
        # 对于这个简单的实现，我们直接调用同步版本
        return self._run(config, query, validate_config, run_manager)


# 便捷函数
def create_crewai_tool():
    """创建CrewAI运行时工具实例"""
    return CrewAIRuntimeTool()


if __name__ == "__main__":
    # 示例用法
    tool = create_crewai_tool()
    
    # 使用JSON字符串配置
    json_config = json.dumps({
        "crewai_config": {
            "name": "示例团队",
            "description": "这是一个示例团队",
            "agents": [
                {
                    "name": "研究员",
                    "role": "研究员",
                    "goal": "收集和分析信息",
                    "backstory": "你是一个专业的研究员"
                }
            ],
            "tasks": [
                {
                    "name": "研究任务",
                    "description": "研究人工智能",
                    "agent": "研究员",
                    "expected_output": "研究报告"
                }
            ]
        }
    })
    
    result = tool._run(config=json_config, query="请研究人工智能的最新发展")
    print(f"结果: {result}")