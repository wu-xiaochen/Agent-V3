"""
工具模块
为智能体提供各种工具
"""

from typing import Dict, Any, List, Optional, Type
import requests
import math
import json
from datetime import datetime
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import os

# 导入供应链工具
from src.tools.supply_chain_tools import (
    DataAnalyzerTool,
    ForecastingModelTool,
    OptimizationEngineTool,
    RiskAssessmentTool
)

# 导入项目工具
from src.tools.crewai_generator import CrewAIGeneratorTool
from src.tools.crewai_runtime_tool import CrewAIRuntimeTool

# 导入动态工具加载器
from .dynamic_tool_loader import DynamicToolLoader
from .api_tool import APITool
from .mcp_tool import MCPTool

# 导入N8N工具（完整 API 版本）
from .n8n_api_tools import (
    N8NGenerateAndCreateWorkflowTool,
    N8NCreateWorkflowTool,
    N8NListWorkflowsTool,
    N8NExecuteWorkflowTool,
    N8NDeleteWorkflowTool,
    create_n8n_api_tools
)

from src.config.config_loader import config_loader


class TimeTool(BaseTool):
    """时间工具"""
    name: str = "time"
    description: str = "用于获取当前日期和时间，无需输入参数，返回当前时间信息"
    
    def _run(self, query: str = "") -> str:
        """获取当前时间"""
        try:
            now = datetime.now()
            time_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
            weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()]
            
            result = f"当前时间: {time_str} {weekday}"
            return result
        except Exception as e:
            return f"获取时间出错: {str(e)}"
    
    async def _arun(self, query: str = "") -> str:
        """异步获取当前时间"""
        return self._run(query)


class SearchTool(BaseTool):
    """搜索工具"""
    name: str = "search"
    description: str = "用于搜索信息，输入查询内容，返回搜索结果"
    
    def _run(self, query: str) -> str:
        """执行搜索"""
        try:
            services_config = config_loader.get_services_config()
            # 修正配置获取路径
            services_data = services_config.get("services", {})
            search_config = services_data.get("tools", {}).get("search", {})
            provider = search_config.get("provider", "duckduckgo")
            max_results = search_config.get("max_results", 5)
            
            if provider == "duckduckgo":
                return self._duckduckgo_search(query, max_results)
            elif provider == "serper":
                return self._serper_search(query, max_results)
            elif provider == "serpapi":
                return self._serpapi_search(query, max_results)
            else:
                return f"不支持的搜索提供商: {provider}"
        except Exception as e:
            return f"搜索出错: {str(e)}"
    
    def _duckduckgo_search(self, query: str, max_results: int) -> str:
        """使用DuckDuckGo进行搜索"""
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append(result)
                
            if not results:
                return f"没有找到关于 '{query}' 的搜索结果"
            
            response = f"搜索 '{query}' 的结果:\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. {result['title']}\n"
                response += f"   {result['body']}\n"
                response += f"   链接: {result['href']}\n\n"
            
            return response
        except ImportError:
            return "DuckDuckGo搜索功能需要安装duckduckgo_search包，请运行: pip install duckduckgo_search"
        except Exception as e:
            return f"DuckDuckGo搜索出错: {str(e)}"
    
    def _serper_search(self, query: str, max_results: int) -> str:
        """使用Serper API进行Google搜索"""
        try:
            services_config = config_loader.get_services_config()
            # 修正配置获取路径
            services_data = services_config.get("services", {})
            search_config = services_data.get("tools", {}).get("search", {})
            serper_config = search_config.get("serper", {})
            api_key = serper_config.get("api_key")
            
            if not api_key:
                return "未配置Serper API密钥，请在配置文件中设置services.tools.search.serper.api_key"
            
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": query,
                "num": max_results
            })
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            
            if response.status_code != 200:
                return f"Serper搜索失败: {data.get('message', '未知错误')}"
            
            if "organic" not in data or not data["organic"]:
                return f"没有找到关于 '{query}' 的搜索结果"
            
            response_text = f"Google搜索 '{query}' 的结果:\n\n"
            for i, result in enumerate(data["organic"][:max_results], 1):
                response_text += f"{i}. {result['title']}\n"
                response_text += f"   {result.get('snippet', '无描述')}\n"
                response_text += f"   链接: {result['link']}\n\n"
            
            return response_text
        except Exception as e:
            return f"Serper搜索出错: {str(e)}"
    
    def _serpapi_search(self, query: str, max_results: int) -> str:
        """使用SerpApi进行Google搜索"""
        try:
            services_config = config_loader.get_services_config()
            # 修正配置获取路径
            services_data = services_config.get("services", {})
            search_config = services_data.get("tools", {}).get("search", {})
            api_key = search_config.get("serpapi", {}).get("api_key")
            
            if not api_key:
                return "未配置SerpApi API密钥，请在配置文件中设置services.tools.search.serpapi.api_key"
            
            # 根据SerpApi文档构建请求
            url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": max_results
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                error = data.get('error', '未知错误')
                return f"SerpApi搜索失败: {error}"
            
            if "organic_results" not in data or not data["organic_results"]:
                return f"没有找到关于 '{query}' 的搜索结果"
            
            response_text = f"Google搜索 '{query}' 的结果:\n\n"
            for i, result in enumerate(data["organic_results"][:max_results], 1):
                response_text += f"{i}. {result['title']}\n"
                response_text += f"   {result.get('snippet', '无描述')}\n"
                response_text += f"   链接: {result['link']}\n\n"
            
            return response_text
        except Exception as e:
            return f"SerpApi搜索出错: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """异步执行搜索"""
        return self._run(query)


class CalculatorTool(BaseTool):
    """计算器工具"""
    name: str = "calculator"
    description: str = "用于进行数学计算，输入数学表达式，返回计算结果"
    
    def _run(self, expression: str) -> str:
        """执行计算"""
        try:
            tools_config = config_loader.get_tools_config()
            calc_config = tools_config.get("calculator", {})
            precision = calc_config.get("precision", 4)
            
            # 安全评估数学表达式
            allowed_names = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e
            }
            
            # 替换常见的数学符号
            expression = expression.replace("^", "**")
            
            # 使用eval计算表达式，限制可用的函数和变量
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            # 格式化结果
            if isinstance(result, float):
                result = round(result, precision)
            
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """异步执行计算"""
        return self._run(expression)


class WeatherTool(BaseTool):
    """天气工具"""
    name: str = "weather"
    description: str = "用于查询天气信息，输入城市名称，返回当前天气情况"
    
    def _run(self, city: str) -> str:
        """查询天气"""
        try:
            tools_config = config_loader.get_tools_config()
            weather_config = tools_config.get("weather", {})
            api_key = weather_config.get("api_key")
            provider = weather_config.get("provider", "openweathermap")
            
            if not api_key:
                return "未配置天气API密钥，请在配置文件中设置weather.api_key"
            
            if provider == "openweathermap":
                return self._openweathermap_weather(city, api_key)
            else:
                return f"不支持的天气提供商: {provider}"
        except Exception as e:
            return f"查询天气出错: {str(e)}"
    
    def _openweathermap_weather(self, city: str, api_key: str) -> str:
        """使用OpenWeatherMap查询天气"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=zh_cn"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code != 200:
                return f"查询天气失败: {data.get('message', '未知错误')}"
            
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            result = f"{city}的天气情况:\n"
            result += f"天气: {weather_desc}\n"
            result += f"温度: {temp}°C (体感温度: {feels_like}°C)\n"
            result += f"湿度: {humidity}%\n"
            result += f"风速: {wind_speed} m/s"
            
            return result
        except Exception as e:
            return f"查询OpenWeatherMap天气出错: {str(e)}"
    
    async def _arun(self, city: str) -> str:
        """异步查询天气"""
        return self._run(city)


def get_builtin_tool_class(tool_name: str) -> Optional[Type[BaseTool]]:
    """
    根据工具名称获取内置工具类
    
    Args:
        tool_name: 工具名称
        
    Returns:
        工具类，如果找不到则返回None
    """
    available_tools = {
        "time": TimeTool,
        "search": SearchTool,
        "calculator": CalculatorTool,
        "weather": WeatherTool,
        "data_analyzer": DataAnalyzerTool,
        "forecasting_model": ForecastingModelTool,
        "optimization_engine": OptimizationEngineTool,
        "risk_assessment": RiskAssessmentTool,
        "crewai_generator": CrewAIGeneratorTool,
        "crewai_runtime": CrewAIRuntimeTool
    }
    
    return available_tools.get(tool_name)


def get_tools(tool_names: Optional[List[str]] = None, config_path: Optional[str] = None) -> List[BaseTool]:
    """
    获取工具列表
    
    Args:
        tool_names: 工具名称列表，如果为None则使用配置文件中的工具列表
        config_path: 工具配置文件路径，如果为None则使用默认路径
        
    Returns:
        工具实例列表
    """
    # 首先尝试使用动态工具加载器
    try:
        # 确定配置文件路径
        if config_path is None:
            # 尝试从环境变量获取配置路径
            config_path = os.environ.get("TOOLS_CONFIG_PATH")
            
            if config_path is None:
                # 根据环境确定默认配置文件
                env = os.environ.get("ENVIRONMENT", "development")
                config_path = f"config/tools/{env}.json"
                
                # 检查文件是否存在
                if not os.path.exists(config_path):
                    # 回退到示例配置
                    config_path = "config/tools/tools_config_example.json"
        
        # 检查配置文件是否存在
        if os.path.exists(config_path):
            # 使用动态工具加载器加载工具
            from .dynamic_tool_loader import DynamicToolLoader
            loader = DynamicToolLoader()
            
            # 如果指定了工具名称，则只加载指定的工具
            if tool_names:
                return loader.load_tools_from_config(config_path)
            else:
                # 否则加载所有启用的工具
                return loader.load_tools_from_config(config_path)
    except Exception as e:
        print(f"使用动态工具加载器失败: {str(e)}")
        print("回退到静态工具加载方式")
    
    # 回退到静态工具加载方式
    if tool_names is None:
        # 从agents配置中获取工具列表
        agent_config = config_loader.get_agent_config()
        tool_names = agent_config.get("tools", [])
        
        # 如果工具列表为空，则使用默认工具
        if not tool_names:
            tool_names = ["search", "calculator", "time", "crewai_generator", "crewai_runtime"]
    
    available_tools = {
        "time": TimeTool,
        "search": SearchTool,
        "calculator": CalculatorTool,
        "weather": WeatherTool,
        "data_analyzer": DataAnalyzerTool,
        "forecasting_model": ForecastingModelTool,
        "optimization_engine": OptimizationEngineTool,
        "risk_assessment": RiskAssessmentTool,
        "crewai_generator": CrewAIGeneratorTool,
        "crewai_runtime": CrewAIRuntimeTool,
        # N8N工具（完整 API 版本）
        "n8n_generate_and_create_workflow": N8NGenerateAndCreateWorkflowTool,
        "n8n_create_workflow": N8NCreateWorkflowTool,
        "n8n_list_workflows": N8NListWorkflowsTool,
        "n8n_execute_workflow": N8NExecuteWorkflowTool,
        "n8n_delete_workflow": N8NDeleteWorkflowTool
    }
    
    tools = []
    for tool_name in tool_names:
        if tool_name in available_tools:
            # 实例化工具类
            tool_class = available_tools[tool_name]
            tools.append(tool_class())
        elif tool_name == "n8n_mcp_generator":
            # n8n_mcp_generator是一个工具包，包含完整的N8N API工具
            # 从配置文件读取 API 配置
            try:
                import json
                with open("config/tools/tools_config.json", "r") as f:
                    tools_config = json.load(f)
                    for tool_config in tools_config.get("tools", []):
                        if tool_config.get("name") == "n8n_mcp_generator":
                            # 🆕 使用 EnvManager 获取配置
                            from src.config.env_manager import EnvManager
                            n8n_config = EnvManager.get_n8n_config()
                            n8n_tools = create_n8n_api_tools(
                                api_url=n8n_config["api_url"],
                                api_key=n8n_config["api_key"]
                            )
                            tools.extend(n8n_tools)
                            break
            except Exception as e:
                print(f"加载n8n API工具失败: {e}")
                # 🆕 使用 EnvManager 的默认配置
                from src.config.env_manager import EnvManager
                n8n_config = EnvManager.get_n8n_config()
                tools.extend(create_n8n_api_tools(
                    api_url=n8n_config["api_url"],
                    api_key=n8n_config["api_key"]
                ))
    
    return tools


def get_tools_for_agent(agent_name: str, config_path: Optional[str] = None) -> List[BaseTool]:
    """
    根据智能体名称获取对应的工具列表
    
    Args:
        agent_name: 智能体名称
        config_path: 工具配置文件路径，如果为None则使用默认路径
        
    Returns:
        工具实例列表
    """
    try:
        # 确定配置文件路径
        if config_path is None:
            # 尝试从环境变量获取配置路径
            config_path = os.environ.get("TOOLS_CONFIG_PATH")
            
            if config_path is None:
                # 根据环境确定默认配置文件
                env = os.environ.get("ENVIRONMENT", "development")
                config_path = f"config/tools/{env}.json"
                
                # 检查文件是否存在
                if not os.path.exists(config_path):
                    # 回退到示例配置
                    config_path = "config/tools/tools_config_example.json"
        
        # 检查配置文件是否存在
        if os.path.exists(config_path):
            # 使用动态工具加载器获取智能体工具
            from .dynamic_tool_loader import DynamicToolLoader
            loader = DynamicToolLoader()
            return loader.load_tools_from_config(config_path, agent_name)
    except Exception as e:
        print(f"使用动态工具加载器获取智能体工具失败: {str(e)}")
        print("回退到静态工具加载方式")
    
    # 回退到静态工具加载方式
    return get_tools()