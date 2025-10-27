"""
CrewAI 配置生成工具

这个模块提供了生成 CrewAI 团队配置的功能，根据供应链业务流程
生成相应的智能体配置。
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import os
import sys

# 导入基础工具类
from langchain.tools import BaseTool

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入标准化配置模板
from src.interfaces.crewai_config_template import (
    CrewAIStandardConfig, 
    AgentConfig, 
    TaskConfig, 
    CrewAIConfig
)


class AgentRole(str, Enum):
    """智能体角色枚举"""
    PLANNER = "planner"  # 规划师
    ANALYST = "analyst"  # 分析师
    COORDINATOR = "coordinator"  # 协调员
    EXECUTOR = "executor"  # 执行者
    REVIEWER = "reviewer"  # 审查者


class CrewAgentConfig(BaseModel):
    """CrewAI 智能体配置模型"""
    name: str = Field(..., description="智能体名称")
    role: str = Field(..., description="智能体角色")
    goal: str = Field(..., description="智能体目标")
    backstory: str = Field(..., description="智能体背景故事")
    tools: List[str] = Field(default=[], description="智能体可用的工具列表")
    verbose: bool = Field(default=True, description="是否启用详细输出")
    allow_delegation: bool = Field(default=False, description="是否允许任务委托")
    max_iter: int = Field(default=25, description="最大迭代次数")
    max_rpm: int = Field(default=1000, description="每分钟最大请求数")


class CrewTaskConfig(BaseModel):
    """CrewAI 任务配置模型"""
    name: str = Field(..., description="任务名称")
    description: str = Field(..., description="任务描述")
    agent: str = Field(..., description="负责任务的智能体")
    expected_output: str = Field(..., description="预期输出")
    context: List[str] = Field(default=[], description="依赖的任务列表")
    tools: List[str] = Field(default=[], description="任务可用的工具")


class CrewConfig(BaseModel):
    """CrewAI 团队配置模型"""
    name: str = Field(..., description="团队名称")
    description: str = Field(..., description="团队描述")
    agents: List[CrewAgentConfig] = Field(..., description="智能体列表")
    tasks: List[CrewTaskConfig] = Field(..., description="任务列表")
    process: str = Field(default="sequential", description="执行流程 (sequential/hierarchical)")
    manager_role: Optional[str] = Field(default=None, description="管理者角色（仅hierarchical流程）")
    verbose: bool = Field(default=True, description="是否启用详细输出")
    memory: bool = Field(default=True, description="是否启用记忆功能")


class CrewAIGenerator:
    """CrewAI 配置生成器"""
    
    def __init__(self):
        """初始化 CrewAI 配置生成器"""
        self.agent_templates = self._load_agent_templates()
        self.task_templates = self._load_task_templates()
    
    def _load_agent_templates(self) -> Dict[str, Dict[str, str]]:
        """加载智能体模板"""
        return {
            AgentRole.PLANNER: {
                "name": "供应链规划师",
                "role": "负责制定供应链战略和规划",
                "goal": "根据业务需求制定最优的供应链规划和策略",
                "backstory": "你是一位经验丰富的供应链规划专家，拥有超过10年的行业经验，擅长分析复杂供应链问题并制定创新解决方案。"
            },
            AgentRole.ANALYST: {
                "name": "供应链分析师",
                "role": "负责分析供应链数据和趋势",
                "goal": "深入分析供应链数据，识别问题和机会，提供数据驱动的洞察",
                "backstory": "你是一位专业的供应链数据分析师，精通各种数据分析工具和方法，能够从复杂数据中提取有价值的信息。"
            },
            AgentRole.COORDINATOR: {
                "name": "供应链协调员",
                "role": "负责协调供应链各环节的运作",
                "goal": "确保供应链各环节高效协同，优化整体运作效率",
                "backstory": "你是一位出色的供应链协调专家，擅长跨部门沟通和资源协调，能够有效解决供应链中的各种协调问题。"
            },
            AgentRole.EXECUTOR: {
                "name": "供应链执行者",
                "role": "负责执行供应链计划和任务",
                "goal": "高效执行供应链计划，确保各项任务按时完成",
                "backstory": "你是一位经验丰富的供应链执行专家，擅长将计划转化为实际行动，能够有效应对执行过程中的各种挑战。"
            },
            AgentRole.REVIEWER: {
                "name": "供应链审查者",
                "role": "负责审查供应链流程和结果",
                "goal": "全面审查供应链流程和结果，确保质量和效率",
                "backstory": "你是一位严谨的供应链审查专家，具有敏锐的洞察力，能够发现潜在问题并提出改进建议。"
            }
        }
    
    def _load_task_templates(self) -> Dict[str, Dict[str, str]]:
        """加载任务模板"""
        return {
            "analysis": {
                "name": "供应链分析",
                "description": "分析当前供应链状况，识别关键问题和机会",
                "expected_output": "详细的供应链分析报告，包括现状、问题和机会"
            },
            "planning": {
                "name": "供应链规划",
                "description": "根据分析结果制定供应链优化规划",
                "expected_output": "全面的供应链优化规划，包括目标、策略和实施步骤"
            },
            "coordination": {
                "name": "供应链协调",
                "description": "协调供应链各环节，确保规划顺利实施",
                "expected_output": "供应链协调计划，包括沟通机制和资源分配"
            },
            "execution": {
                "name": "供应链执行",
                "description": "执行供应链规划，监控实施进度",
                "expected_output": "供应链执行报告，包括进度、成果和问题"
            },
            "review": {
                "name": "供应链审查",
                "description": "审查供应链执行结果，评估效果并提出改进建议",
                "expected_output": "供应链审查报告，包括效果评估和改进建议"
            }
        }
    
    def generate_crew_config(
        self,
        business_process: str,
        crew_name: str = "供应链优化团队",
        process_type: str = "sequential",
        custom_agents: Optional[List[Dict[str, Any]]] = None,
        custom_tasks: Optional[List[Dict[str, Any]]] = None
    ) -> CrewConfig:
        """
        根据业务流程生成 CrewAI 配置
        
        Args:
            business_process: 业务流程描述
            crew_name: 团队名称
            process_type: 执行流程类型 (sequential/hierarchical)
            custom_agents: 自定义智能体配置
            custom_tasks: 自定义任务配置
            
        Returns:
            CrewConfig: 生成的团队配置
        """
        # 分析业务流程，确定需要的角色
        required_roles = self._analyze_process_for_roles(business_process)
        
        # 生成智能体配置
        agents = []
        if custom_agents:
            # 使用自定义智能体
            for agent_config in custom_agents:
                agents.append(CrewAgentConfig(**agent_config))
        else:
            # 使用模板生成智能体
            for role in required_roles:
                template = self.agent_templates.get(role, self.agent_templates[AgentRole.PLANNER])
                agent = CrewAgentConfig(
                    name=f"{template['name']}_{role}",
                    role=template["role"],
                    goal=template["goal"],
                    backstory=template["backstory"]
                )
                agents.append(agent)
        
        # 生成任务配置
        tasks = []
        if custom_tasks:
            # 使用自定义任务
            for task_config in custom_tasks:
                tasks.append(CrewTaskConfig(**task_config))
        else:
            # 根据业务流程生成任务
            task_types = self._analyze_process_for_tasks(business_process)
            for i, task_type in enumerate(task_types):
                template = self.task_templates.get(task_type, self.task_templates["planning"])
                agent_role = required_roles[min(i, len(required_roles)-1)]
                agent_name = agents[required_roles.index(agent_role)].name
                
                task = CrewTaskConfig(
                    name=f"{template['name']}_{i+1}",
                    description=template["description"],
                    agent=agent_name,
                    expected_output=template["expected_output"]
                )
                tasks.append(task)
        
        # 创建团队配置
        crew_config = CrewConfig(
            name=crew_name,
            description=f"基于业务流程 '{business_process}' 生成的供应链优化团队",
            agents=agents,
            tasks=tasks,
            process=process_type,
            manager_role="planner" if process_type == "hierarchical" else None
        )
        
        return crew_config
    
    def _analyze_process_for_roles(self, business_process: str) -> List[AgentRole]:
        """分析业务流程，确定需要的角色"""
        process_lower = business_process.lower()
        roles = []
        
        # 基于关键词分析需要的角色
        if any(keyword in process_lower for keyword in ["规划", "计划", "设计", "策略"]):
            roles.append(AgentRole.PLANNER)
        
        if any(keyword in process_lower for keyword in ["分析", "数据", "评估", "研究"]):
            roles.append(AgentRole.ANALYST)
        
        if any(keyword in process_lower for keyword in ["协调", "沟通", "合作", "整合"]):
            roles.append(AgentRole.COORDINATOR)
        
        if any(keyword in process_lower for keyword in ["执行", "实施", "操作", "落地"]):
            roles.append(AgentRole.EXECUTOR)
        
        if any(keyword in process_lower for keyword in ["审查", "检查", "验证", "评估"]):
            roles.append(AgentRole.REVIEWER)
        
        # 如果没有匹配到任何角色，默认使用规划师和执行者
        if not roles:
            roles = [AgentRole.PLANNER, AgentRole.EXECUTOR]
        
        return roles
    
    def _analyze_process_for_tasks(self, business_process: str) -> List[str]:
        """分析业务流程，确定需要的任务类型"""
        process_lower = business_process.lower()
        tasks = []
        
        # 基于关键词分析需要的任务类型
        if any(keyword in process_lower for keyword in ["分析", "数据", "评估", "研究"]):
            tasks.append("analysis")
        
        if any(keyword in process_lower for keyword in ["规划", "计划", "设计", "策略"]):
            tasks.append("planning")
        
        if any(keyword in process_lower for keyword in ["协调", "沟通", "合作", "整合"]):
            tasks.append("coordination")
        
        if any(keyword in process_lower for keyword in ["执行", "实施", "操作", "落地"]):
            tasks.append("execution")
        
        if any(keyword in process_lower for keyword in ["审查", "检查", "验证", "评估"]):
            tasks.append("review")
        
        # 如果没有匹配到任何任务，默认使用规划和执行
        if not tasks:
            tasks = ["planning", "execution"]
        
        return tasks
    
    def export_to_json(self, crew_config: CrewConfig) -> str:
        """将配置导出为 JSON 字符串"""
        return crew_config.json(indent=2)
    
    def export_to_dict(self, crew_config: CrewConfig) -> Dict[str, Any]:
        """将配置导出为字典"""
        return crew_config.dict()
    
    def save_to_file(self, crew_config: CrewConfig, file_path: str) -> bool:
        """将配置保存到文件"""
        try:
            # 转换为标准化配置
            standard_config = self._convert_to_standard_config(crew_config)
            
            # 根据文件扩展名决定保存格式
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(standard_config.to_dict(), f, default_flow_style=False, allow_unicode=True)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(standard_config.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def _convert_to_standard_config(self, crew_config: CrewConfig) -> CrewAIStandardConfig:
        """将CrewConfig转换为标准化配置"""
        # 转换智能体配置
        agents = []
        for agent in crew_config.agents:
            agent_config = AgentConfig(
                name=agent.name,
                role=agent.role,
                goal=agent.goal,
                backstory=agent.backstory,
                tools=[]  # 默认为空，可根据需要添加
            )
            agents.append(agent_config)
        
        # 转换任务配置
        tasks = []
        for task in crew_config.tasks:
            task_config = TaskConfig(
                name=task.name,
                description=task.description,
                agent=task.agent,
                expected_output=task.expected_output
            )
            tasks.append(task_config)
        
        # 创建团队配置
        crewai_config = CrewAIConfig(
            name=crew_config.name,
            description=crew_config.description,
            agents=agents,
            tasks=tasks,
            process=crew_config.process,
            verbose=True,
            memory=True
        )
        
        # 创建标准化配置
        standard_config = CrewAIStandardConfig(
            business_process="",  # 可以在调用时设置
            crewai_config=crewai_config
        )
        
        return standard_config


# 便捷函数
def generate_crew_from_process(
    business_process: str,
    crew_name: str = "供应链优化团队",
    process_type: str = "sequential",
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：从业务流程生成 CrewAI 配置
    
    Args:
        business_process: 业务流程描述
        crew_name: 团队名称
        process_type: 执行流程类型
        output_file: 输出文件路径（可选）
        
    Returns:
        Dict: 生成的配置字典
    """
    generator = CrewAIGenerator()
    crew_config = generator.generate_crew_config(
        business_process=business_process,
        crew_name=crew_name,
        process_type=process_type
    )
    
    config_dict = generator.export_to_dict(crew_config)
    
    if output_file:
        generator.save_to_file(crew_config, output_file)
    
    return config_dict


class CrewAIGeneratorTool(BaseTool):
    """CrewAI配置生成工具类"""
    
    name: str = "crewai_generator"
    description: str = "根据业务流程生成CrewAI团队配置，用于创建供应链优化团队"
    generator: CrewAIGenerator = Field(default_factory=CrewAIGenerator)
    
    def _run(self, business_process: str, **kwargs) -> Dict[str, Any]:
        """
        运行CrewAI配置生成工具
        
        Args:
            business_process: 业务流程描述
            **kwargs: 其他参数，包括crew_name, process_type等
            
        Returns:
            Dict: 生成的CrewAI配置字典
        """
        crew_name = kwargs.get("crew_name", "供应链优化团队")
        process_type = kwargs.get("process_type", "sequential")
        output_file = kwargs.get("output_file", None)
        
        crew_config = self.generator.generate_crew_config(
            business_process=business_process,
            crew_name=crew_name,
            process_type=process_type
        )
        
        # 转换为标准化配置
        standard_config = self.generator._convert_to_standard_config(crew_config)
        # 设置业务流程
        standard_config.business_process = business_process
        
        config_dict = standard_config.to_dict()
        
        if output_file:
            self.generator.save_to_file(crew_config, output_file)
            config_dict["output_file"] = output_file
        
        return config_dict
    
    async def _arun(self, business_process: str, **kwargs) -> Dict[str, Any]:
        """异步运行CrewAI配置生成工具"""
        return self._run(business_process, **kwargs)