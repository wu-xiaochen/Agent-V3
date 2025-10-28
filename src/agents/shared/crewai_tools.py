"""
CrewAI兼容的工具包
将常用功能包装为CrewAI工具
"""

import logging
from typing import Optional, Type
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup


class CalculatorToolSchema(BaseModel):
    """计算器工具参数 Schema"""
    expression: str = Field(..., description="数学表达式，例如：'10 + 20 * 3'")


class CrewAICalculatorTool(BaseTool):
    """CrewAI计算器工具"""
    
    name: str = "calculator"
    description: str = "执行数学计算。输入数学表达式，返回计算结果。例如：'10 + 20 * 3'"
    args_schema: Type[BaseModel] = CalculatorToolSchema
    
    def _run(self, expression: str) -> str:
        """执行计算"""
        try:
            # 安全地执行数学表达式
            allowed_names = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"


class TimeToolSchema(BaseModel):
    """时间工具参数 Schema（空参数）"""
    pass


class CrewAITimeTool(BaseTool):
    """CrewAI时间工具"""
    
    name: str = "time"
    description: str = "获取当前日期和时间。此工具不需要任何输入参数。"
    args_schema: Type[BaseModel] = TimeToolSchema
    
    def _run(self) -> str:
        """获取当前时间"""
        now = datetime.now()
        return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"


class SearchToolSchema(BaseModel):
    """搜索工具参数 Schema"""
    query: str = Field(..., description="搜索查询词")


class CrewAISearchTool(BaseTool):
    """CrewAI搜索工具（简化版）"""
    
    name: str = "search"
    description: str = "搜索互联网信息。输入搜索查询，返回相关结果。"
    args_schema: Type[BaseModel] = SearchToolSchema
    
    def _run(self, query: str) -> str:
        """执行搜索"""
        try:
            # 使用DuckDuckGo HTML搜索（无需API密钥）
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 提取搜索结果
            for result in soup.find_all('div', class_='result')[:5]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
            
            if results:
                output = f"搜索结果 (查询: {query}):\n\n"
                for i, r in enumerate(results, 1):
                    output += f"{i}. {r['title']}\n"
                    output += f"   {r['snippet'][:150]}...\n"
                    output += f"   {r['url']}\n\n"
                return output
            else:
                return f"未找到相关结果: {query}"
                
        except Exception as e:
            logging.error(f"搜索失败: {e}")
            return f"搜索失败: {str(e)}"


class N8NGeneratorToolSchema(BaseModel):
    """N8N工作流生成工具参数 Schema"""
    workflow_description: str = Field(..., description="工作流描述（中文或英文）")


class CrewAIN8NGeneratorTool(BaseTool):
    """CrewAI N8N工作流生成工具"""
    
    name: str = "n8n_generate_workflow"
    description: str = """生成N8N工作流配置。
    输入：工作流描述（中文或英文）
    输出：n8n工作流JSON配置
    
    示例：
    - "创建一个定时任务，每小时发送邮件"
    - "创建一个HTTP请求到Slack通知的工作流"
    """
    args_schema: Type[BaseModel] = N8NGeneratorToolSchema
    
    def _run(self, workflow_description: str) -> str:
        """生成工作流"""
        # 导入N8N工具
        from .n8n_simple_tool import N8NGenerateWorkflowTool
        
        tool = N8NGenerateWorkflowTool()
        return tool._run(workflow_description=workflow_description)


def create_crewai_tools(tool_names: list = None) -> list:
    """
    创建CrewAI工具列表
    
    Args:
        tool_names: 工具名称列表，如果为None则返回所有工具
        
    Returns:
        CrewAI工具列表
    """
    all_tools = {
        "calculator": CrewAICalculatorTool(),
        "time": CrewAITimeTool(),
        "search": CrewAISearchTool(),
        "n8n_generate_workflow": CrewAIN8NGeneratorTool()
    }
    
    if tool_names is None:
        return list(all_tools.values())
    
    tools = []
    for name in tool_names:
        if name in all_tools:
            tools.append(all_tools[name])
    
    return tools

