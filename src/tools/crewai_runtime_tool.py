"""
CrewAI Runtime Tool - 包装 CrewAIRuntime 为 LangChain Tool
"""

import logging
import json
from typing import Optional
from langchain.tools import BaseTool
from pydantic import Field
from src.interfaces.crewai_runtime import CrewAIRuntime as Runtime

logger = logging.getLogger(__name__)


class CrewAIRuntimeTool(BaseTool):
    """
    CrewAI 运行时工具
    
    用于运行已保存的 CrewAI 配置
    """
    
    name: str = "crewai_runtime"
    description: str = """运行 CrewAI 团队配置工具
    
    使用场景：
    - 在生成 CrewAI 配置后，运行该配置
    - 执行多智能体协作任务
    - 运行保存的 CrewAI 团队
    
    参数：
    - config_id: 配置ID（由 crewai_generator 生成）
    - query: 任务查询/描述
    
    示例：
    - query="帮我分析市场趋势", config_id="config_xxx"
    
    返回：CrewAI 执行结果
    """
    
    runtime: Optional[Runtime] = Field(default=None, description="CrewAI运行时实例")
    config_dir: str = Field(default="config/generated", description="配置目录")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, config_dir: str = "config/generated", **kwargs):
        super().__init__(**kwargs)
        self.config_dir = config_dir
        if self.runtime is None:
            self.runtime = Runtime(config_dir=config_dir)
    
    def _run(
        self,
        config_id: Optional[str] = None,
        config_path: Optional[str] = None,
        query: Optional[str] = None
    ) -> str:
        """
        运行 CrewAI 配置
        
        Args:
            config_id: 配置ID（从 config_dir 中查找）
            config_path: 配置文件路径（完整路径）
            query: 任务查询
            
        Returns:
            执行结果
        """
        try:
            # 加载配置
            if config_id:
                # 通过ID加载
                success = self.runtime.load_config_by_id(config_id)
                if not success:
                    return f"❌ 未找到配置ID: {config_id}。请先使用 crewai_generator 生成配置。"
                logger.info(f"✅ 通过ID加载配置: {config_id}")
                
            elif config_path:
                # 通过路径加载
                self.runtime.load_config(config_path)
                logger.info(f"✅ 通过路径加载配置: {config_path}")
                
            else:
                return "❌ 需要提供 config_id 或 config_path 参数"
            
            # 运行 CrewAI
            logger.info(f"🚀 开始运行 CrewAI: {query or '默认任务'}")
            result = self.runtime.run_crew(query=query)
            
            if result:
                logger.info(f"✅ CrewAI 执行成功")
                return f"✅ **CrewAI 执行完成**\n\n{result}"
            else:
                return "❌ CrewAI 执行失败或无结果返回"
                
        except Exception as e:
            logger.error(f"❌ 运行 CrewAI 失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return f"❌ 运行 CrewAI 失败: {str(e)}"
    
    async def _arun(
        self,
        config_id: Optional[str] = None,
        config_path: Optional[str] = None,
        query: Optional[str] = None
    ) -> str:
        """异步执行"""
        return self._run(config_id, config_path, query)


def create_crewai_runtime_tool(config_dir: str = "config/generated"):
    """创建 CrewAI Runtime Tool 实例"""
    return CrewAIRuntimeTool(config_dir=config_dir)
