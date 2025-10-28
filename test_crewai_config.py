#!/usr/bin/env python3
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_loader import ConfigLoader
from interfaces.crewai_runtime import CrewAIRuntime

# 加载配置
config_loader = ConfigLoader()

# 创建CrewAI运行时
runtime = CrewAIRuntime()

# 创建一个简单的团队配置进行测试
crew_config = {
    'crewai_config': {
        'name': '测试团队',
        'description': '用于测试LLM配置的团队',
        'agents': [
            {
                'role': '测试智能体',
                'goal': '测试LLM配置',
                'backstory': '用于测试LLM配置的智能体',
                'tools': []
            }
        ],
        'tasks': [
            {
                'description': '测试任务',
                'expected_output': '测试输出',
                'agent': '测试智能体'
            }
        ]
    }
}

# 测试创建团队
print('测试创建CrewAI团队...')
success = runtime.load_crew_from_config(crew_config)
print(f'团队创建结果: {success}')