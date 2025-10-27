"""
CrewAI运行时工具
提供运行CrewAI团队的功能
"""

import json
import os
import sys
from typing import Dict, Any, Optional, List, Type
from pydantic import BaseModel, Field

# 导入基础工具类
from langchain.tools import BaseTool

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入CrewAI运行时
from src.interfaces.crewai_runtime import CrewAIRuntime


class CrewAIRuntimeToolInput(BaseModel):
    """CrewAI运行时工具输入参数"""
    config: str = Field(description="CrewAI团队配置，可以是JSON字符串或配置文件路径")
    query: str = Field(description="要执行的任务查询")
    process_type: Optional[str] = Field(default="sequential", description="执行流程类型 (sequential/hierarchical)")


class CrewAIRuntimeTool(BaseTool):
    """CrewAI运行时工具类"""
    
    name: str = "crewai_runtime"
    description: str = "运行CrewAI团队，执行指定的任务查询"
    args_schema: Optional[Type[BaseModel]] = CrewAIRuntimeToolInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保args_schema被正确设置
        if not hasattr(self, 'args_schema') or self.args_schema is None:
            self.args_schema = CrewAIRuntimeToolInput
    
    def _run(self, config: str, query: str, process_type: str = "sequential") -> Dict[str, Any]:
        """
        运行CrewAI团队
        
        Args:
            config: CrewAI团队配置，可以是JSON字符串或配置文件路径
            query: 要执行的任务查询
            process_type: 执行流程类型
            
        Returns:
            Dict: 执行结果
        """
        try:
            # 创建CrewAI运行时实例
            runtime = CrewAIRuntime()
            
            # 检查config是JSON字符串还是文件路径
            if config.strip().startswith('{') or config.strip().startswith('['):
                # 是JSON字符串，直接使用
                config_data = json.loads(config)
                # 加载配置
                runtime.load_config_from_dict(config_data)
            else:
                # 是文件路径，从文件加载
                if not os.path.exists(config):
                    return {
                        "error": f"配置文件不存在: {config}",
                        "success": False
                    }
                runtime.load_config(config)
            
            # 创建团队
            runtime.create_crew()
            
            # 运行团队
            result = runtime.run_crew(query)
            
            return {
                "result": result,
                "success": True,
                "config": config,
                "query": query
            }
            
        except Exception as e:
            return {
                "error": f"运行CrewAI团队时出错: {str(e)}",
                "success": False,
                "config": config,
                "query": query
            }
    
    async def _arun(self, config: str, query: str, process_type: str = "sequential") -> Dict[str, Any]:
        """异步运行CrewAI团队"""
        return self._run(config, query, process_type)