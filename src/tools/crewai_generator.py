"""
CrewAI 配置生成工具

这个模块提供了生成 CrewAI 团队配置的功能，根据业务需求
生成相应的智能体配置。
"""

import json
import yaml
import logging
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

# 创建logger实例
logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """智能体角色枚举"""
    PLANNER = "planner"  # 规划师
    ANALYST = "analyst"  # 分析师
    COORDINATOR = "coordinator"  # 协调员
    EXECUTOR = "executor"  # 执行者
    REVIEWER = "reviewer"  # 审查者
    CODER = "coder"  # 代码生成/开发工程师


class BusinessDomain(str, Enum):
    """业务领域枚举"""
    GENERAL = "general"  # 通用领域
    SUPPLY_CHAIN = "supply_chain"  # 供应链
    TECHNOLOGY = "technology"  # 技术
    MARKETING = "marketing"  # 市场营销
    FINANCE = "finance"  # 金融
    HEALTHCARE = "healthcare"  # 医疗健康
    EDUCATION = "education"  # 教育
    RESEARCH = "research"  # 研究


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
    
    def _detect_domain(self, business_process: str) -> BusinessDomain:
        """检测业务领域"""
        process_lower = business_process.lower()
        
        # 定义领域关键词
        domain_keywords = {
            BusinessDomain.SUPPLY_CHAIN: ["供应链", "物流", "采购", "库存", "配送", "仓储"],
            BusinessDomain.TECHNOLOGY: ["技术", "软件", "开发", "编程", "系统", "架构", "ai", "人工智能", "机器学习"],
            BusinessDomain.MARKETING: ["营销", "市场", "推广", "品牌", "广告", "销售", "客户"],
            BusinessDomain.FINANCE: ["金融", "财务", "投资", "银行", "保险", "会计", "预算"],
            BusinessDomain.HEALTHCARE: ["医疗", "健康", "医院", "药品", "治疗", "护理", "疾病"],
            BusinessDomain.EDUCATION: ["教育", "学习", "培训", "学校", "课程", "教学", "学生"],
            BusinessDomain.RESEARCH: ["研究", "科研", "学术", "论文", "实验", "数据", "分析", "趋势"]
        }
        
        # 检测匹配的领域
        for domain, keywords in domain_keywords.items():
            if any(keyword in process_lower for keyword in keywords):
                return domain
        
        # 默认返回通用领域
        return BusinessDomain.GENERAL
    
    def _load_agent_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """加载智能体模板"""
        return {
            BusinessDomain.GENERAL: {
                AgentRole.PLANNER: {
                    "name": "规划师",
                    "role": "负责制定战略和规划",
                    "goal": "根据业务需求制定最优的规划和策略",
                    "backstory": "你是一位经验丰富的规划专家，拥有超过10年的行业经验，擅长分析复杂问题并制定创新解决方案。"
                },
                AgentRole.ANALYST: {
                    "name": "分析师",
                    "role": "负责分析数据和趋势",
                    "goal": "深入分析数据，识别问题和机会，提供数据驱动的洞察",
                    "backstory": "你是一位专业的数据分析师，精通各种数据分析工具和方法，能够从复杂数据中提取有价值的信息。"
                },
                AgentRole.COORDINATOR: {
                    "name": "协调员",
                    "role": "负责协调各环节的运作",
                    "goal": "确保各环节高效协同，优化整体运作效率",
                    "backstory": "你是一位出色的协调专家，擅长跨部门沟通和资源协调，能够有效解决各种协调问题。"
                },
                AgentRole.EXECUTOR: {
                    "name": "执行者",
                    "role": "负责执行计划和任务",
                    "goal": "高效执行计划，确保各项任务按时完成",
                    "backstory": "你是一位经验丰富的执行专家，擅长将计划转化为实际行动，能够有效应对执行过程中的各种挑战。"
                },
                AgentRole.REVIEWER: {
                    "name": "审查者",
                    "role": "负责审查流程和结果",
                    "goal": "全面审查流程和结果，确保质量和效率",
                    "backstory": "你是一位严谨的审查专家，具有敏锐的洞察力，能够发现潜在问题并提出改进建议。"
                },
                AgentRole.CODER: {
                    "name": "开发工程师",
                    "role": "负责代码开发和技术实现",
                    "goal": "高质量地实现功能需求，编写清晰、高效、可维护的代码",
                    "backstory": "你是一位技术精湛的开发工程师，精通多种编程语言和开发框架，拥有丰富的项目经验，能够将需求转化为高质量的代码实现。你擅长代码设计、性能优化和问题排查。"
                }
            },
            BusinessDomain.SUPPLY_CHAIN: {
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
            },
            BusinessDomain.TECHNOLOGY: {
                AgentRole.PLANNER: {
                    "name": "技术架构师",
                    "role": "负责设计技术架构和规划",
                    "goal": "根据业务需求设计最优的技术架构和实施规划",
                    "backstory": "你是一位资深的技术架构师，拥有丰富的系统设计经验，擅长创建可扩展、高性能的技术解决方案。"
                },
                AgentRole.ANALYST: {
                    "name": "技术分析师",
                    "role": "负责分析技术趋势和数据",
                    "goal": "深入分析技术趋势和数据，识别技术机会和风险",
                    "backstory": "你是一位专业的技术分析师，精通各种技术评估方法，能够准确评估技术的可行性和潜在价值。"
                },
                AgentRole.COORDINATOR: {
                    "name": "项目经理",
                    "role": "负责协调技术团队和资源",
                    "goal": "确保技术团队高效协作，优化开发流程和资源分配",
                    "backstory": "你是一位经验丰富的项目经理，擅长敏捷开发方法，能够有效协调跨职能技术团队。"
                },
                AgentRole.EXECUTOR: {
                    "name": "开发工程师",
                    "role": "负责实现技术方案和代码开发",
                    "goal": "高质量地实现技术方案，确保代码质量和项目进度",
                    "backstory": "你是一位技术精湛的开发工程师，精通多种编程语言和框架，能够高效实现复杂的技术功能。"
                },
                AgentRole.REVIEWER: {
                    "name": "质量保证工程师",
                    "role": "负责审查代码质量和系统性能",
                    "goal": "全面审查代码质量和系统性能，确保产品符合质量标准",
                    "backstory": "你是一位严谨的质量保证工程师，具有敏锐的细节洞察力，能够发现潜在的技术问题并提出改进方案。"
                }
            },
            BusinessDomain.RESEARCH: {
                AgentRole.PLANNER: {
                    "name": "研究规划师",
                    "role": "负责设计研究框架和方法论",
                    "goal": "根据研究目标设计科学的研究框架和方法论",
                    "backstory": "你是一位资深的研究规划师，拥有丰富的研究设计经验，擅长创建严谨、科学的研究方案。"
                },
                AgentRole.ANALYST: {
                    "name": "数据分析师",
                    "role": "负责收集和分析研究数据",
                    "goal": "系统性地收集和分析研究数据，提取有价值的洞察和结论",
                    "backstory": "你是一位专业的研究数据分析师，精通各种统计分析和数据可视化方法，能够从复杂数据中发现规律和趋势。"
                },
                AgentRole.COORDINATOR: {
                    "name": "研究协调员",
                    "role": "负责协调研究团队和资源",
                    "goal": "确保研究团队高效协作，优化研究流程和资源分配",
                    "backstory": "你是一位经验丰富的研究协调员，擅长跨学科研究团队的协作，能够有效管理研究项目的各个方面。"
                },
                AgentRole.EXECUTOR: {
                    "name": "研究助理",
                    "role": "负责执行研究任务和数据收集",
                    "goal": "高效执行研究任务，确保数据收集的准确性和完整性",
                    "backstory": "你是一位细致的研究助理，精通各种研究方法和数据收集技术，能够准确执行研究计划。"
                },
                AgentRole.REVIEWER: {
                    "name": "同行评议专家",
                    "role": "负责审查研究方法和结论",
                    "goal": "全面审查研究方法和结论，确保研究的科学性和可靠性",
                    "backstory": "你是一位严谨的同行评议专家，具有敏锐的批判性思维，能够识别研究中的潜在问题并提出改进建议。"
                }
            }
        }
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """加载任务模板"""
        return {
            BusinessDomain.GENERAL: {
                "analysis": {
                    "name": "分析",
                    "description": "分析当前状况，识别关键问题和机会",
                    "expected_output": "详细的分析报告，包括现状、问题和机会"
                },
                "planning": {
                    "name": "规划",
                    "description": "根据分析结果制定优化规划",
                    "expected_output": "全面的优化规划，包括目标、策略和实施步骤"
                },
                "coordination": {
                    "name": "协调",
                    "description": "协调各环节，确保规划顺利实施",
                    "expected_output": "协调计划，包括沟通机制和资源分配"
                },
                "execution": {
                    "name": "执行",
                    "description": "执行规划，监控实施进度",
                    "expected_output": "执行报告，包括进度、成果和问题"
                },
                "review": {
                    "name": "审查",
                    "description": "审查执行结果，评估效果并提出改进建议",
                    "expected_output": "审查报告，包括效果评估和改进建议"
                }
            },
            BusinessDomain.SUPPLY_CHAIN: {
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
            },
            BusinessDomain.TECHNOLOGY: {
                "analysis": {
                    "name": "技术分析",
                    "description": "分析当前技术状况，识别技术问题和机会",
                    "expected_output": "详细的技术分析报告，包括现状、问题和机会"
                },
                "planning": {
                    "name": "技术规划",
                    "description": "根据分析结果制定技术实施规划",
                    "expected_output": "全面的技术实施规划，包括架构设计、技术选型和实施步骤"
                },
                "coordination": {
                    "name": "项目协调",
                    "description": "协调技术团队和资源，确保项目顺利实施",
                    "expected_output": "项目协调计划，包括团队分工、沟通机制和资源分配"
                },
                "execution": {
                    "name": "开发执行",
                    "description": "执行技术方案，监控开发进度",
                    "expected_output": "开发执行报告，包括进度、成果和技术问题"
                },
                "review": {
                    "name": "技术审查",
                    "description": "审查技术实现和系统性能，评估质量并提出改进建议",
                    "expected_output": "技术审查报告，包括代码质量评估和性能优化建议"
                }
            },
            BusinessDomain.RESEARCH: {
                "analysis": {
                    "name": "文献综述",
                    "description": "收集和分析相关文献，确定研究现状和空白",
                    "expected_output": "详细的文献综述报告，包括研究现状、理论框架和研究空白"
                },
                "planning": {
                    "name": "研究设计",
                    "description": "根据文献综述设计研究方案和方法论",
                    "expected_output": "完整的研究设计方案，包括研究问题、假设、方法和数据收集计划"
                },
                "coordination": {
                    "name": "研究协调",
                    "description": "协调研究团队和资源，确保研究顺利进行",
                    "expected_output": "研究协调计划，包括团队分工、时间表和资源分配"
                },
                "execution": {
                    "name": "数据收集",
                    "description": "执行研究方案，收集和分析数据",
                    "expected_output": "数据收集报告，包括数据质量、初步分析结果和方法论执行情况"
                },
                "review": {
                    "name": "结果评估",
                    "description": "评估研究结果，验证假设并得出结论",
                    "expected_output": "研究评估报告，包括结果解释、假设验证和研究局限性"
                }
            }
        }
    
    def generate_crew_config(
        self,
        business_process: str,
        crew_name: str = "专业团队",
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
        # 检测业务领域
        domain = self._detect_domain(business_process)
        
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
                # 获取领域特定的模板，如果不存在则使用通用模板
                domain_templates = self.agent_templates.get(domain, self.agent_templates[BusinessDomain.GENERAL])
                template = domain_templates.get(role, domain_templates[AgentRole.PLANNER])
                
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
                # 获取领域特定的模板，如果不存在则使用通用模板
                domain_templates = self.task_templates.get(domain, self.task_templates[BusinessDomain.GENERAL])
                template = domain_templates.get(task_type, domain_templates["planning"])
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
            description=f"基于业务需求 '{business_process}' 生成的专业团队",
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
        # Pydantic v2兼容性：优先使用model_dump_json()，回退到json()
        if hasattr(crew_config, 'model_dump_json'):
            return crew_config.model_dump_json(indent=2)
        else:
            return crew_config.json(indent=2)
    
    def export_to_dict(self, crew_config: CrewConfig) -> Dict[str, Any]:
        """将配置导出为字典"""
        # Pydantic v2兼容性：优先使用model_dump()，回退到dict()
        if hasattr(crew_config, 'model_dump'):
            return crew_config.model_dump()
        else:
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
            # 根据角色添加合适的工具
            default_tools = ["search", "calculator", "time"]  # 所有角色的基础工具
            
            # 根据角色类型添加特定工具（可以根据角色名称智能判断）
            agent_tools = list(set(default_tools))  # 去重
            
            # 根据角色类型添加专用工具
            role_lower = agent.role.lower()
            name_lower = agent.name.lower()
            
            # Coder角色：添加代码相关工具
            if any(keyword in role_lower or keyword in name_lower for keyword in ["coder", "代码", "开发", "程序员", "工程师"]):
                agent_tools.extend(["search", "calculator", "n8n_mcp_generator"])
            
            # 分析类角色：增强搜索能力
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["分析", "analyst", "研究", "research"]):
                agent_tools.append("search")
            
            # 规划类角色：增强计算和搜索能力
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["规划", "planner", "设计", "design"]):
                agent_tools.extend(["search", "calculator"])
            
            # 去重并排序
            agent_tools = sorted(list(set(agent_tools)))
            
            # 确定角色类型（用于runtime选择模型）
            role_type = "default"
            if any(keyword in role_lower or keyword in name_lower for keyword in ["coder", "代码", "开发", "程序员", "工程师"]):
                role_type = "coder"
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["analyst", "分析"]):
                role_type = "analyst"
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["planner", "规划", "设计"]):
                role_type = "planner"
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["reviewer", "审查", "评审"]):
                role_type = "reviewer"
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["coordinator", "协调"]):
                role_type = "coordinator"
            elif any(keyword in role_lower or keyword in name_lower for keyword in ["executor", "执行"]):
                role_type = "executor"
            
            agent_config = AgentConfig(
                name=agent.name,
                role=agent.role,
                goal=agent.goal,
                backstory=agent.backstory,
                tools=agent_tools,  # 添加工具列表
                verbose=True,
                allow_delegation=False,
                max_iter=25,
                max_rpm=1000
            )
            # 保持AgentConfig对象，不转换成字典
            # role_type信息可以存储在agents字典中，供runtime使用
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
    crew_name: str = "专业团队",
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
    description: str = "根据业务需求生成CrewAI团队配置，支持多业务领域的专业团队创建"
    generator: CrewAIGenerator = Field(default_factory=CrewAIGenerator)
    auto_save: bool = Field(default=True, description="是否自动保存配置到文件")
    save_dir: str = Field(default="config/generated", description="配置保存目录")
    
    def _run(self, business_process: str, **kwargs) -> Dict[str, Any]:
        """
        运行CrewAI配置生成工具
        
        Args:
            business_process: 业务流程描述
            **kwargs: 其他参数，包括crew_name, process_type等
            
        Returns:
            Dict: 生成的CrewAI配置字典
        """
        crew_name = kwargs.get("crew_name", "专业团队")
        process_type = kwargs.get("process_type", "sequential")
        output_file = kwargs.get("output_file", None)
        auto_save = kwargs.get("auto_save", self.auto_save)
        
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
        
        # ✅ 自动保存配置（如果启用）
        crew_id = self._generate_config_id(crew_name)
        if auto_save or output_file:
            saved_path = self._auto_save_config(config_dict, crew_name, output_file)
            config_dict["saved_config_path"] = saved_path
            config_dict["config_id"] = crew_id
            logger.info(f"✅ CrewAI配置已保存: {saved_path} (ID: {config_dict['config_id']})")
        
        # 🆕 返回特殊标记，让前端自动打开画布
        result = {
            "success": True,
            "crew_id": crew_id,
            "crew_name": crew_name,
            "crew_config": config_dict,
            "action": "open_canvas",  # ← 前端识别此标记自动打开CrewAI画布
            "message": f"✅ 已生成Crew团队: {crew_name}\n\n包含 {len(config_dict.get('crewai_config', {}).get('agents', []))} 个Agent和 {len(config_dict.get('crewai_config', {}).get('tasks', []))} 个Task\n\n点击右上角CrewAI按钮查看详情，或等待自动打开画布"
        }
        
        return result
    
    def _auto_save_config(self, config_dict: Dict[str, Any], crew_name: str, output_file: Optional[str] = None) -> str:
        """
        自动保存配置到文件
        
        Args:
            config_dict: 配置字典
            crew_name: 团队名称
            output_file: 指定的输出文件路径（可选）
            
        Returns:
            str: 保存的文件路径
        """
        import os
        from datetime import datetime
        from pathlib import Path
        
        # 确保保存目录存在
        save_dir = Path(self.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if output_file:
            file_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = crew_name.replace(" ", "_").replace("/", "_")
            file_path = save_dir / f"{safe_name}_{timestamp}.json"
        
        # 保存配置
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        return str(file_path)
    
    def _generate_config_id(self, crew_name: str) -> str:
        """
        生成配置ID
        
        Args:
            crew_name: 团队名称
            
        Returns:
            str: 配置ID
        """
        import hashlib
        from datetime import datetime
        
        # 使用时间戳和团队名称生成唯一ID
        timestamp = datetime.now().isoformat()
        id_string = f"{crew_name}_{timestamp}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]
    
    async def _arun(self, business_process: str, **kwargs) -> Dict[str, Any]:
        """异步运行CrewAI配置生成工具"""
        return self._run(business_process, **kwargs)