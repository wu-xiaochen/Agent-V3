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
    
    def __init__(self, config_path=None):
        """
        初始化CrewAI运行时
        
        Args:
            config_path: 配置文件路径，支持JSON和YAML格式
        """
        self.config_path = config_path
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
            
            # 从配置文件获取LLM配置
            try:
                # 获取硅基流动LLM配置
                services_config = config_loader.get_services_config()
                self.logger.debug(f"完整services配置: {services_config}")
                
                # services_config包含整个services.yaml文件，需要从中获取services配置
                services = services_config.get("services", {})
                self.logger.debug(f"services键下的配置: {services}")
                
                # 获取LLM基础配置
                llm_config = services.get('llm', {})
                self.logger.debug(f"LLM基础配置: {llm_config}")
                
                # 获取CrewAI特定配置
                crewai_config = services.get('crewai', {})
                self.logger.debug(f"CrewAI配置: {crewai_config}")
                
                # 检查配置是否为空
                if not llm_config:
                    self.logger.error("未找到LLM配置，请检查config/base/services.yaml文件中的services.llm配置")
                    return False
                
                # 获取配置参数，优先使用CrewAI特定配置
                api_key = llm_config.get("api_key") or os.getenv("SILICONFLOW_API_KEY")
                base_url = llm_config.get("base_url") or "https://api.siliconflow.cn/v1"
                # 优先使用crewai配置中的模型，如果没有则使用llm配置中的默认模型
                model_name = crewai_config.get("default_model") or llm_config.get("default_model") or "deepseek-chat"
                temperature = 0.7  # 默认温度
                max_tokens = 1000  # 默认最大令牌数
                
                if not api_key:
                    self.logger.error("未找到硅基流动API密钥，请设置环境变量SILICONFLOW_API_KEY或在配置文件中指定")
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
            llm.__dict__['provider'] = "siliconflow"  # 标记提供商
            
            # 打印配置信息
            self.logger.info(f"LLM提供商: 硅基流动 (SiliconFlow) - CrewAI原生LLM")
            self.logger.info(f"API端点: {base_url}")
            self.logger.info(f"使用模型: {model_with_provider}")
            self.logger.info(f"温度参数: {temperature}")
            self.logger.info(f"最大令牌数: {max_tokens}")
            
            # 创建智能体
            self.agents = []
            for agent_config in crew_config["agents"]:
                agent = Agent(
                    role=agent_config["role"],
                    goal=agent_config["goal"],
                    backstory=agent_config["backstory"],
                    verbose=agent_config.get("verbose", True),
                    allow_delegation=agent_config.get("allow_delegation", False),
                    max_iter=agent_config.get("max_iter", 25),
                    max_rpm=agent_config.get("max_rpm", 1000),
                    llm=llm  # 使用硅基流动LLM
                )
                self.agents.append(agent)
                self.logger.info(f"已创建智能体: {agent_config.get('name', agent_config['role'])} - {agent_config['role']}")
            
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