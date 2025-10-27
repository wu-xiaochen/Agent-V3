#!/usr/bin/env python3
"""
CrewAI配置模板定义
定义标准化的CrewAI配置文件格式
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = field(default_factory=list)
    verbose: bool = True
    allow_delegation: bool = False
    max_iter: int = 25
    max_rpm: int = 1000


@dataclass
class TaskConfig:
    """任务配置"""
    name: str
    description: str
    agent: str  # 智能体名称或角色
    expected_output: str
    context: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)


@dataclass
class CrewAIConfig:
    """CrewAI团队配置"""
    name: str
    description: str
    agents: List[AgentConfig]
    tasks: List[TaskConfig]
    process: str = "sequential"  # sequential 或 hierarchical
    manager_role: Optional[str] = None
    verbose: bool = True
    memory: bool = True


@dataclass
class CrewAIStandardConfig:
    """标准CrewAI配置文件格式"""
    business_process: str  # 业务流程描述
    crewai_config: CrewAIConfig
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"  # 配置版本
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "business_process": self.business_process,
            "crewai_config": {
                "name": self.crewai_config.name,
                "description": self.crewai_config.description,
                "agents": [
                    {
                        "name": agent.name,
                        "role": agent.role,
                        "goal": agent.goal,
                        "backstory": agent.backstory,
                        "tools": agent.tools,
                        "verbose": agent.verbose,
                        "allow_delegation": agent.allow_delegation,
                        "max_iter": agent.max_iter,
                        "max_rpm": agent.max_rpm
                    }
                    for agent in self.crewai_config.agents
                ],
                "tasks": [
                    {
                        "name": task.name,
                        "description": task.description,
                        "agent": task.agent,
                        "expected_output": task.expected_output,
                        "context": task.context,
                        "tools": task.tools
                    }
                    for task in self.crewai_config.tasks
                ],
                "process": self.crewai_config.process,
                "manager_role": self.crewai_config.manager_role,
                "verbose": self.crewai_config.verbose,
                "memory": self.crewai_config.memory
            },
            "generated_at": self.generated_at,
            "version": self.version
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    def save_to_file(self, file_path: str):
        """保存到文件"""
        file_ext = file_path.split('.')[-1].lower()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_ext in ['yaml', 'yml']:
                import yaml
                yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False, indent=2)
            else:
                f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrewAIStandardConfig":
        """从字典创建配置对象"""
        crew_config = data["crewai_config"]
        
        agents = [
            AgentConfig(
                name=agent["name"],
                role=agent["role"],
                goal=agent["goal"],
                backstory=agent["backstory"],
                tools=agent.get("tools", []),
                verbose=agent.get("verbose", True),
                allow_delegation=agent.get("allow_delegation", False),
                max_iter=agent.get("max_iter", 25),
                max_rpm=agent.get("max_rpm", 1000)
            )
            for agent in crew_config["agents"]
        ]
        
        tasks = [
            TaskConfig(
                name=task["name"],
                description=task["description"],
                agent=task["agent"],
                expected_output=task["expected_output"],
                context=task.get("context", []),
                tools=task.get("tools", [])
            )
            for task in crew_config["tasks"]
        ]
        
        crewai_config = CrewAIConfig(
            name=crew_config["name"],
            description=crew_config["description"],
            agents=agents,
            tasks=tasks,
            process=crew_config.get("process", "sequential"),
            manager_role=crew_config.get("manager_role"),
            verbose=crew_config.get("verbose", True),
            memory=crew_config.get("memory", True)
        )
        
        return cls(
            business_process=data.get("business_process", ""),
            crewai_config=crewai_config,
            generated_at=data.get("generated_at", datetime.now().isoformat()),
            version=data.get("version", "1.0")
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> "CrewAIStandardConfig":
        """从文件加载配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            file_ext = file_path.split('.')[-1].lower()
            
            if file_ext in ['yaml', 'yml']:
                import yaml
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls.from_dict(data)