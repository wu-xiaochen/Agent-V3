#!/usr/bin/env python3
"""
通用CrewAI运行时
支持加载和运行任何符合标准格式的CrewAI配置文件
"""

import sys
import os
import json
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crewai import Agent, Task, Crew, Process
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from src.config.config_loader import config_loader


class CrewAIRuntime:
    """通用CrewAI运行时类"""
    
    def __init__(self, config_path=None, config_dir="config/generated"):
        """
        初始化CrewAI运行时
        
        Args:
            config_path: 配置文件路径，支持JSON和YAML格式
            config_dir: 配置文件目录（用于配置ID查询）
        """
        self.config_path = config_path
        self.config_dir = Path(config_dir)
        self.config_data = None
        self.crew = None
        self.agents = []
        self.tasks = []
        self.logger = logging.getLogger(__name__)
        
        if config_path:
            self.load_config(config_path)
    
    def load_config_from_dict(self, config_dict):
        """
        从字典加载CrewAI配置
        
        Args:
            config_dict: CrewAI配置字典
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 验证配置
            if not self._validate_config(config_dict):
                return False
                
            # 存储配置数据
            self.config_data = config_dict
            self.config_path = "内存中的配置字典"
            
            print(f"成功从字典加载CrewAI配置")
            return True
            
        except Exception as e:
            print(f"从字典加载配置失败: {str(e)}")
            return False
    
    def load_config(self, config_path):
        """
        加载CrewAI配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            config_file = Path(config_path)
            
            if not config_file.exists():
                print(f"错误: 配置文件不存在: {config_path}")
                return False
                
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    self.config_data = yaml.safe_load(f)
                else:
                    self.config_data = json.load(f)
            
            # 验证配置格式
            if not self._validate_config():
                print(f"错误: 配置文件格式不正确: {config_path}")
                return False
                
            self.config_path = str(config_file)
            print(f"成功加载配置文件: {config_path}")
            return True
            
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return False
    
    def _validate_config(self, config_data=None):
        """验证配置文件格式"""
        # 如果没有提供配置数据，使用实例的配置数据
        if config_data is None:
            config_data = self.config_data
            
        if not config_data:
            return False
            
        if "crewai_config" not in config_data:
            logging.error("配置文件中缺少 'crewai_config' 部分")
            return False
            
        crew_config = config_data["crewai_config"]
        
        # 检查必需字段
        required_fields = ["name", "description", "agents", "tasks"]
        for field in required_fields:
            if field not in crew_config:
                logging.error(f"crewai_config 中缺少必需字段: {field}")
                return False
                
        # 检查agents和tasks是否为列表
        if not isinstance(crew_config["agents"], list) or not isinstance(crew_config["tasks"], list):
            logging.error("agents 和 tasks 必须是列表")
            return False
            
        # 检查agents和tasks是否为空
        if not crew_config["agents"] or not crew_config["tasks"]:
            logging.error("agents 和 tasks 不能为空")
            return False
            
        logging.info("CrewAI配置验证通过")
        return True
    
    def load_config_by_id(self, config_id: str) -> bool:
        """
        根据配置ID加载配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            bool: 加载是否成功
        """
        # 搜索配置目录
        if not self.config_dir.exists():
            print(f"❌ 配置目录不存在: {self.config_dir}")
            return False
        
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get("config_id") == config_id:
                        self.config_data = config
                        self.config_path = str(config_file)
                        print(f"✅ 找到配置: {config_file.name} (ID: {config_id})")
                        return True
            except Exception as e:
                continue
        
        print(f"❌ 未找到配置ID: {config_id}")
        return False
    
    def list_saved_configs(self) -> list:
        """
        列出所有保存的配置
        
        Returns:
            配置列表
        """
        configs = []
        
        if not self.config_dir.exists():
            print(f"⚠️ 配置目录不存在: {self.config_dir}")
            return configs
        
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configs.append({
                        "file": config_file.name,
                        "config_id": config.get("config_id"),
                        "name": config.get("crewai_config", {}).get("name"),
                        "created_at": config.get("generated_at"),
                        "path": str(config_file)
                    })
            except Exception as e:
                continue
        
        return configs
    
    def load_crew_from_config(self, config_data):
        """
        从配置数据加载并创建CrewAI团队
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.config_data = config_data
            
            # 验证配置格式
            if not self._validate_config():
                logging.error("错误: 配置数据格式不正确")
                return False
                
            # 创建团队
            if not self.create_crew():
                logging.error("错误: 创建团队失败")
                return False
                
            logging.info("成功从配置数据加载并创建团队")
            return True
            
        except Exception as e:
            logging.error(f"从配置数据加载团队失败: {str(e)}")
            return False
    
    def create_crew(self):
        """根据配置创建CrewAI团队"""
        if not self.config_data:
            print("错误: 尚未加载配置文件")
            return False
            
        try:
            crew_config = self.config_data["crewai_config"]
            
            # 从配置文件获取CrewAI专用LLM配置
            try:
                # 获取服务配置
                services_config = config_loader.get_services_config()
                self.logger.debug(f"完整services配置: {services_config}")
                
                # services_config包含整个services.yaml文件，需要从中获取services配置
                services = services_config.get("services", {})
                self.logger.debug(f"services键下的配置: {services}")
                
                # 获取CrewAI特定配置
                crewai_config = services.get('crewai', {})
                self.logger.debug(f"CrewAI配置: {crewai_config}")
                
                # 获取CrewAI专用LLM配置
                crewai_llm_config = crewai_config.get('llm', {})
                self.logger.debug(f"CrewAI LLM配置: {crewai_llm_config}")
                
                # 检查配置是否为空
                if not crewai_llm_config:
                    self.logger.error("未找到CrewAI LLM配置，请检查config/base/services.yaml文件中的services.crewai.llm配置")
                    return False
                
                # 🆕 获取配置参数（优先使用 EnvManager）
                from src.config.env_manager import EnvManager
                provider = crewai_llm_config.get("provider", "siliconflow")
                api_key = crewai_llm_config.get("api_key") or EnvManager.SILICONFLOW_API_KEY
                base_url = crewai_llm_config.get("base_url") or EnvManager.SILICONFLOW_BASE_URL
                model_name = crewai_llm_config.get("default_model") or "deepseek-chat"
                temperature = crewai_llm_config.get("temperature", 0.7)
                max_tokens = crewai_llm_config.get("max_tokens", 1000)
                
                if not api_key:
                    self.logger.error("未找到CrewAI LLM API密钥，请设置环境变量或在配置文件中指定")
                    return False
                    
            except Exception as e:
                self.logger.error(f"读取LLM配置失败: {str(e)}")
                return False
            
            # 使用CrewAI原生LLM创建方式
            from crewai import LLM
            
            # 创建LLM实例，使用CrewAI原生方式
            # 根据文档，模型名称格式为 provider/model-id
            # 对于硅基流动，使用 openai/ 前缀表示OpenAI兼容API
            model_with_provider = f"openai/{model_name}"
            
            llm = LLM(
                model=model_with_provider,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                base_url=base_url
            )
            
            # 存储实际使用的模型信息
            llm.__dict__['actual_model'] = model_name  # 从配置读取实际模型名称
            llm.__dict__['provider'] = provider  # 标记提供商
            
            # 打印配置信息
            self.logger.info(f"LLM提供商: {provider} - CrewAI专用LLM")
            self.logger.info(f"API端点: {base_url}")
            self.logger.info(f"使用模型: {model_with_provider}")
            self.logger.info(f"温度参数: {temperature}")
            self.logger.info(f"最大令牌数: {max_tokens}")
            
            # 获取CrewAI工具配置
            crewai_tools_config = crewai_config.get('tools', {})
            tools_enabled = crewai_tools_config.get('enabled', True)
            default_tools = crewai_tools_config.get('default_tools', ['time', 'search', 'calculator'])
            role_tools_mapping = crewai_tools_config.get('role_tools', {})
            
            # 获取角色模型映射
            role_models = crewai_llm_config.get('role_models', {})
            
            # 获取当前时间信息（用于注入到agent的上下文）
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y年%m月%d日")
            current_year = datetime.now().year
            
            time_context = f"\n\n【重要时间信息】\n当前时间: {current_datetime} (北京时间 UTC+8)\n当前年份: {current_year}\n今天日期: {current_date}\n\n在执行任务时，请注意使用当前时间信息，特别是在分析趋势、新闻、市场状况等时效性信息时。"
            
            # 创建智能体
            self.agents = []
            for agent_config in crew_config["agents"]:
                # 确定智能体角色类型（用于选择模型和工具）
                agent_role_type = agent_config.get("role_type", "default")
                agent_role = agent_config["role"]
                agent_name = agent_config.get('name', agent_role)
                
                # 根据角色类型或名称智能判断角色类型
                if agent_role_type == "default":
                    # 智能判断角色类型
                    role_lower = agent_role.lower()
                    name_lower = agent_name.lower()
                    
                    if any(keyword in role_lower or keyword in name_lower for keyword in ["coder", "代码", "开发", "程序员", "工程师"]):
                        agent_role_type = "coder"
                    elif any(keyword in role_lower or keyword in name_lower for keyword in ["analyst", "分析"]):
                        agent_role_type = "analyst"
                    elif any(keyword in role_lower or keyword in name_lower for keyword in ["planner", "规划", "设计"]):
                        agent_role_type = "planner"
                    elif any(keyword in role_lower or keyword in name_lower for keyword in ["reviewer", "审查", "评审"]):
                        agent_role_type = "reviewer"
                    elif any(keyword in role_lower or keyword in name_lower for keyword in ["coordinator", "协调"]):
                        agent_role_type = "coordinator"
                    elif any(keyword in role_lower or keyword in name_lower for keyword in ["executor", "执行"]):
                        agent_role_type = "executor"
                
                # 根据角色类型选择模型
                role_model = role_models.get(agent_role_type, role_models.get('default', model_name))
                
                # 如果角色模型与默认模型不同，创建专用LLM
                if role_model != model_name:
                    self.logger.info(f"为角色 {agent_role_type} 使用专用模型: {role_model}")
                    role_llm = LLM(
                        model=f"openai/{role_model}",
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_key=api_key,
                        base_url=base_url
                    )
                    agent_llm = role_llm
                else:
                    agent_llm = llm
                
                # 获取工具配置
                # 注意：CrewAI的Agent.tools需要CrewAI工具，不能直接使用LangChain工具
                agent_tools = []
                tool_names = []
                
                if tools_enabled:
                    # 优先使用配置中指定的工具
                    if agent_config.get("tools"):
                        tool_names = agent_config["tools"]
                    # 其次使用角色特定工具
                    elif agent_role_type in role_tools_mapping:
                        tool_names = role_tools_mapping[agent_role_type]
                    # 最后使用默认工具
                    else:
                        tool_names = default_tools
                    
                    if tool_names:
                        self.logger.info(f"智能体 {agent_name} ({agent_role_type}) 配置了工具: {tool_names}")
                        
                        # 创建CrewAI兼容的工具（传递agent_config以支持知识库工具）
                        from src.agents.shared.crewai_tools import create_crewai_tools
                        try:
                            agent_tools = create_crewai_tools(tool_names, agent_config)
                            self.logger.info(f"已为智能体创建 {len(agent_tools)} 个CrewAI工具")
                        except Exception as e:
                            self.logger.error(f"创建CrewAI工具失败: {e}")
                            agent_tools = []
                
                # 将时间信息注入到backstory中
                backstory_with_time = agent_config["backstory"] + time_context
                
                agent = Agent(
                    role=agent_role,
                    goal=agent_config["goal"],
                    backstory=backstory_with_time,  # 注入时间信息
                    verbose=agent_config.get("verbose", True),
                    allow_delegation=agent_config.get("allow_delegation", False),
                    max_iter=agent_config.get("max_iter", 25),
                    max_rpm=agent_config.get("max_rpm", 1000),
                    llm=agent_llm,  # 使用角色特定的LLM
                    tools=agent_tools if agent_tools else None  # 传递CrewAI工具
                )
                self.agents.append(agent)
                self.logger.info(f"已创建智能体: {agent_name} - {agent_role} (类型: {agent_role_type}, 模型: {role_model})")
            
            # 创建任务
            self.tasks = []
            for task_config in crew_config["tasks"]:
                # 查找对应的智能体
                agent = None
                agent_identifier = task_config.get("agent", "")
                
                # 首先尝试通过名称匹配
                for a in self.agents:
                    agent_name = next((ac.get('name', ac['role']) for ac in crew_config["agents"] 
                                     if ac['role'] == a.role), a.role)
                    if agent_identifier == agent_name or agent_identifier == a.role:
                        agent = a
                        break
                
                # 如果找不到匹配的智能体，使用第一个智能体
                if agent is None:
                    agent = self.agents[0]
                    self.logger.warning(f"未找到匹配的智能体 '{agent_identifier}'，使用默认智能体")
                
                task = Task(
                    description=task_config["description"],
                    agent=agent,
                    expected_output=task_config["expected_output"]
                )
                self.tasks.append(task)
                self.logger.info(f"已创建任务: {task_config.get('name', '未命名任务')} - {task_config['description'][:50]}...")
            
            # 确定流程类型
            process_type = Process.sequential
            if crew_config.get("process", "").lower() == "hierarchical":
                process_type = Process.hierarchical
            
            # 创建团队
            self.crew = Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=process_type,
                verbose=crew_config.get("verbose", True),
                memory=crew_config.get("memory", True),
                manager_llm=llm  # 使用硅基流动LLM作为管理器
            )
            
            self.logger.info(f"团队 '{crew_config['name']}' 创建成功!")
            self.logger.info(f"团队描述: {crew_config['description']}")
            self.logger.info(f"智能体数量: {len(self.agents)}")
            self.logger.info(f"任务数量: {len(self.tasks)}")
            self.logger.info(f"流程类型: {process_type}")
            self.logger.info(f"LLM提供商: 硅基流动 (SiliconFlow)")
            self.logger.info(f"使用模型: {model_with_provider}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"创建团队失败: {str(e)}")
            return False
    
    def run_crew(self, query, save_result=True):
        """
        运行CrewAI团队
        
        Args:
            query: 查询内容
            save_result: 是否保存结果到文件
            
        Returns:
            str: 团队执行结果，如果失败则返回None
        """
        if not self.crew:
            self.logger.error("尚未创建团队，请先调用 create_crew()")
            return None
            
        self.logger.info(f"运行CrewAI团队，查询: {query}")
        
        try:
            # 运行团队 - CrewAI现在期望字典格式的输入
            inputs = {"query": query}
            result = self.crew.kickoff(inputs=inputs)
            self.logger.info("团队执行结果:")
            self.logger.info(result)
            
            if save_result:
                self._save_result(query, result)
                
            return result
            
        except Exception as e:
            self.logger.error(f"团队执行失败: {str(e)}")
            return None
    
    def _save_result(self, query, result):
        """保存执行结果到文件"""
        try:
            # 创建结果目录
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            
            # 生成结果文件名
            crew_name = self.config_data["crewai_config"]["name"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = results_dir / f"{crew_name}_{timestamp}.txt"
            
            # 保存结果
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"配置文件: {self.config_path}\n")
                f.write(f"团队名称: {crew_name}\n")
                f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"查询: {query}\n\n")
                f.write(f"结果:\n{result}")
                
            self.logger.info(f"结果已保存到文件: {result_file}")
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="通用CrewAI运行时")
    parser.add_argument("--config", "-c", required=True, help="CrewAI配置文件路径")
    parser.add_argument("--query", "-q", help="要执行的查询")
    parser.add_argument("--no-save", action="store_true", help="不保存执行结果")
    
    args = parser.parse_args()
    
    # 创建运行时
    runtime = CrewAIRuntime()
    
    # 加载配置
    if not runtime.load_config(args.config):
        sys.exit(1)
    
    # 创建团队
    if not runtime.create_crew():
        sys.exit(1)
    
    # 获取查询
    query = args.query
    if not query:
        query = input("请输入查询内容: ")
    
    # 运行团队
    result = runtime.run_crew(query, save_result=not args.no_save)
    
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()