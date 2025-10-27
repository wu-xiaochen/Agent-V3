#!/usr/bin/env python3
"""
CrewAI配置验证工具
用于验证智能体传入的配置是否正确
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.interfaces.crewai_config_template import CrewAIStandardConfig, AgentConfig, TaskConfig, CrewAIConfig
from src.config.config_loader import config_loader


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class CrewAIConfigValidator:
    """CrewAI配置验证器"""
    
    def __init__(self):
        """初始化验证器"""
        self.services_config = config_loader.get_services_config()
        self.llm_config = config_loader.get_llm_config()
    
    def validate_config_dict(self, config_dict: Dict[str, Any]) -> ValidationResult:
        """
        验证配置字典
        
        Args:
            config_dict: 配置字典
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 检查基本结构
        if not isinstance(config_dict, dict):
            result.is_valid = False
            result.errors.append("配置必须是一个字典")
            return result
        
        # 检查是否有crewai_config或crew键
        if "crewai_config" not in config_dict and "crew" not in config_dict:
            result.is_valid = False
            result.errors.append("配置中缺少 'crewai_config' 或 'crew' 键")
            return result
        
        # 获取crew配置
        crew_config = config_dict.get("crewai_config", config_dict.get("crew", {}))
        
        # 验证crew配置
        crew_result = self._validate_crew_config(crew_config)
        result.is_valid = result.is_valid and crew_result.is_valid
        result.errors.extend(crew_result.errors)
        result.warnings.extend(crew_result.warnings)
        result.suggestions.extend(crew_result.suggestions)
        
        return result
    
    def _validate_crew_config(self, crew_config: Dict[str, Any]) -> ValidationResult:
        """
        验证crew配置
        
        Args:
            crew_config: crew配置字典
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 检查必需字段
        required_fields = ["name", "description", "agents", "tasks"]
        for field in required_fields:
            if field not in crew_config:
                result.is_valid = False
                result.errors.append(f"crew配置中缺少必需字段: {field}")
        
        # 验证agents
        if "agents" in crew_config:
            agents_result = self._validate_agents(crew_config["agents"])
            result.is_valid = result.is_valid and agents_result.is_valid
            result.errors.extend(agents_result.errors)
            result.warnings.extend(agents_result.warnings)
            result.suggestions.extend(agents_result.suggestions)
        
        # 验证tasks
        if "tasks" in crew_config:
            tasks_result = self._validate_tasks(crew_config["tasks"], crew_config.get("agents", []))
            result.is_valid = result.is_valid and tasks_result.is_valid
            result.errors.extend(tasks_result.errors)
            result.warnings.extend(tasks_result.warnings)
            result.suggestions.extend(tasks_result.suggestions)
        
        # 验证process类型
        if "process" in crew_config:
            process = crew_config["process"]
            if process not in ["sequential", "hierarchical"]:
                result.warnings.append(f"未知的process类型: {process}，将使用默认值 'sequential'")
        
        # 验证manager_role（仅在hierarchical流程中需要）
        if crew_config.get("process") == "hierarchical" and "manager_role" not in crew_config:
            result.warnings.append("hierarchical流程建议设置manager_role")
        
        return result
    
    def _validate_agents(self, agents: List[Dict[str, Any]]) -> ValidationResult:
        """
        验证agents配置
        
        Args:
            agents: agents配置列表
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        if not isinstance(agents, list):
            result.is_valid = False
            result.errors.append("agents必须是一个列表")
            return result
        
        if not agents:
            result.is_valid = False
            result.errors.append("agents列表不能为空")
            return result
        
        # 验证每个agent
        for i, agent in enumerate(agents):
            agent_result = self._validate_agent(agent, i)
            result.is_valid = result.is_valid and agent_result.is_valid
            result.errors.extend(agent_result.errors)
            result.warnings.extend(agent_result.warnings)
            result.suggestions.extend(agent_result.suggestions)
        
        return result
    
    def _validate_agent(self, agent: Dict[str, Any], index: int) -> ValidationResult:
        """
        验证单个agent配置
        
        Args:
            agent: agent配置字典
            index: agent索引
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        agent_name = agent.get("name", f"agents[{index}]")
        
        # 检查必需字段
        required_fields = ["role", "goal", "backstory"]
        for field in required_fields:
            if field not in agent:
                result.is_valid = False
                result.errors.append(f"{agent_name}缺少必需字段: {field}")
        
        # 检查可选字段
        if "tools" in agent and not isinstance(agent["tools"], list):
            result.warnings.append(f"{agent_name}的tools字段应该是列表")
        
        if "max_iter" in agent:
            max_iter = agent["max_iter"]
            if not isinstance(max_iter, int) or max_iter <= 0:
                result.warnings.append(f"{agent_name}的max_iter应该是正整数")
        
        if "max_rpm" in agent:
            max_rpm = agent["max_rpm"]
            if not isinstance(max_rpm, int) or max_rpm <= 0:
                result.warnings.append(f"{agent_name}的max_rpm应该是正整数")
        
        return result
    
    def _validate_tasks(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> ValidationResult:
        """
        验证tasks配置
        
        Args:
            tasks: tasks配置列表
            agents: agents配置列表
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        if not isinstance(tasks, list):
            result.is_valid = False
            result.errors.append("tasks必须是一个列表")
            return result
        
        if not tasks:
            result.is_valid = False
            result.errors.append("tasks列表不能为空")
            return result
        
        # 获取所有agent名称和角色
        agent_names = []
        agent_roles = []
        for agent in agents:
            if "name" in agent:
                agent_names.append(agent["name"])
            if "role" in agent:
                agent_roles.append(agent["role"])
        
        # 验证每个task
        for i, task in enumerate(tasks):
            task_result = self._validate_task(task, i, agent_names, agent_roles)
            result.is_valid = result.is_valid and task_result.is_valid
            result.errors.extend(task_result.errors)
            result.warnings.extend(task_result.warnings)
            result.suggestions.extend(task_result.suggestions)
        
        return result
    
    def _validate_task(self, task: Dict[str, Any], index: int, agent_names: List[str], agent_roles: List[str]) -> ValidationResult:
        """
        验证单个task配置
        
        Args:
            task: task配置字典
            index: task索引
            agent_names: 可用的agent名称列表
            agent_roles: 可用的agent角色列表
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        task_name = task.get("name", f"tasks[{index}]")
        
        # 检查必需字段
        required_fields = ["description", "agent", "expected_output"]
        for field in required_fields:
            if field not in task:
                result.is_valid = False
                result.errors.append(f"{task_name}缺少必需字段: {field}")
        
        # 检查agent引用
        if "agent" in task:
            agent_ref = task["agent"]
            if agent_ref not in agent_names and agent_ref not in agent_roles:
                result.warnings.append(f"{task_name}引用了不存在的agent: {agent_ref}")
        
        # 检查可选字段
        if "context" in task and not isinstance(task["context"], list):
            result.warnings.append(f"{task_name}的context字段应该是列表")
        
        if "tools" in task and not isinstance(task["tools"], list):
            result.warnings.append(f"{task_name}的tools字段应该是列表")
        
        return result
    
    def validate_llm_config(self) -> ValidationResult:
        """
        验证LLM配置
        
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 检查是否有LLM配置
        if not self.llm_config:
            result.is_valid = False
            result.errors.append("未找到LLM配置，请检查config/base/services.yaml文件")
            return result
        
        # 检查API密钥
        api_key = self.llm_config.get("api_key") or os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            result.warnings.append("未找到LLM API密钥，请设置环境变量SILICONFLOW_API_KEY或在配置文件中指定")
        
        # 检查base_url
        base_url = self.llm_config.get("base_url")
        if not base_url:
            result.warnings.append("未找到LLM base_url，将使用默认值")
        
        # 检查模型名称
        model_name = self.llm_config.get("default_model")
        if not model_name:
            result.warnings.append("未找到默认模型名称，将使用默认模型")
        
        return result
    
    def validate_config_file(self, file_path: str) -> ValidationResult:
        """
        验证配置文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            result.is_valid = False
            result.errors.append(f"配置文件不存在: {file_path}")
            return result
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    import yaml
                    config_dict = yaml.safe_load(f)
                else:
                    config_dict = json.load(f)
            
            # 验证配置
            return self.validate_config_dict(config_dict)
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"读取或解析配置文件失败: {str(e)}")
            return result
    
    def suggest_improvements(self, config_dict: Dict[str, Any]) -> List[str]:
        """
        为配置提供改进建议
        
        Args:
            config_dict: 配置字典
            
        Returns:
            List[str]: 改进建议列表
        """
        suggestions = []
        
        # 获取crew配置
        crew_config = config_dict.get("crewai_config", config_dict.get("crew", {}))
        
        # 检查是否缺少description
        if "description" not in crew_config:
            suggestions.append("建议为crew添加description字段，描述团队的目的")
        
        # 检查agent是否有name字段
        for i, agent in enumerate(crew_config.get("agents", [])):
            if "name" not in agent:
                suggestions.append(f"建议为agent {i} 添加name字段，便于引用")
        
        # 检查task是否有name字段
        for i, task in enumerate(crew_config.get("tasks", [])):
            if "name" not in task:
                suggestions.append(f"建议为task {i} 添加name字段，便于识别")
        
        # 检查是否使用了合适的process类型
        process = crew_config.get("process", "sequential")
        if len(crew_config.get("agents", [])) > 3 and process == "sequential":
            suggestions.append("对于多agent团队，建议考虑使用hierarchical流程")
        
        return suggestions


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python crewai_config_validator.py <配置文件路径>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    validator = CrewAIConfigValidator()
    
    # 验证配置文件
    result = validator.validate_config_file(config_path)
    
    # 打印结果
    print(f"\n配置验证结果: {'通过' if result.is_valid else '失败'}")
    
    if result.errors:
        print("\n错误:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("\n警告:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if result.suggestions:
        print("\n建议:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")
    
    # 验证LLM配置
    llm_result = validator.validate_llm_config()
    if not llm_result.is_valid or llm_result.warnings:
        print("\nLLM配置:")
        if llm_result.errors:
            for error in llm_result.errors:
                print(f"  错误: {error}")
        if llm_result.warnings:
            for warning in llm_result.warnings:
                print(f"  警告: {warning}")
    
    # 退出码
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()