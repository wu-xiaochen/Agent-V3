"""
流式输出处理器
提供美观的、层次分明的智能体执行过程展示
"""

import sys
import re
from typing import Any, Dict, List, Optional
# LangChain 1.0+ 导入路径
try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult


class StreamingDisplayHandler(BaseCallbackHandler):
    """流式显示处理器 - 美观的输出格式"""
    
    # 颜色代码
    COLORS = {
        'header': '\033[95m',      # 紫色 - 标题
        'blue': '\033[94m',        # 蓝色 - 思考
        'cyan': '\033[96m',        # 青色 - 工具
        'green': '\033[92m',       # 绿色 - 成功
        'yellow': '\033[93m',      # 黄色 - 观察
        'red': '\033[91m',         # 红色 - 错误
        'bold': '\033[1m',         # 粗体
        'underline': '\033[4m',    # 下划线
        'end': '\033[0m',          # 结束
        'gray': '\033[90m',        # 灰色 - 辅助信息
    }
    
    # 图标
    ICONS = {
        'think': '🤔',
        'tool': '🔧',
        'search': '🔍',
        'observe': '👁️',
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
        'arrow': '→',
        'bullet': '•',
        'chain': '⛓️',
        'robot': '🤖',
        'output': '📤',
    }
    
    def __init__(self, verbose: bool = True, show_colors: bool = True):
        """
        初始化流式显示处理器
        
        Args:
            verbose: 是否显示详细信息
            show_colors: 是否使用颜色
        """
        super().__init__()
        self.verbose = verbose
        self.show_colors = show_colors
        self.step_count = 0
        
    def _color(self, text: str, color: str) -> str:
        """给文本添加颜色"""
        if not self.show_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['end']}"
    
    def _print_box(self, title: str, content: str = "", icon: str = "info", color: str = "blue"):
        """打印带边框的内容"""
        width = 80
        title_line = f"{self.ICONS.get(icon, '')} {title}"
        
        print("\n" + "─" * width)
        print(self._color(f"  {title_line}", color))
        if content:
            print("─" * width)
            # 处理多行内容
            for line in content.split('\n'):
                if line.strip():
                    print(f"  {line}")
        print("─" * width + "\n")
    
    def _print_section(self, title: str, content: str, icon: str = "bullet", indent: int = 0):
        """打印分段内容"""
        prefix = "  " * indent
        icon_str = self.ICONS.get(icon, self.ICONS['bullet'])
        
        print(f"{prefix}{self._color(icon_str, 'cyan')} {self._color(title, 'bold')}")
        
        if content:
            # 处理多行内容
            for line in content.split('\n'):
                if line.strip():
                    print(f"{prefix}  {line}")
        print()
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Agent链开始时调用"""
        if not self.verbose:
            return
        
        chain_name = serialized.get("name", "Agent")
        user_input = inputs.get("input", inputs.get("question", ""))
        
        self._print_box(
            "智能体启动",
            f"问题: {user_input}",
            icon="chain",
            color="header"
        )
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Agent链结束时调用"""
        if not self.verbose:
            return
        
        output = outputs.get("output", "")
        self._print_box(
            "执行完成",
            "",
            icon="success",
            color="green"
        )
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Agent执行动作时调用"""
        if not self.verbose:
            return
        
        self.step_count += 1
        
        # 解析思考过程
        thought = self._extract_thought(action.log)
        
        # 显示分隔线
        print(self._color(f"\n{'═' * 80}", "blue"))
        print(self._color(f"{'═' * 80}\n", "blue"))
        
        # 显示思考过程
        if thought:
            self._print_section(
                "💭 思考过程",
                thought,
                icon="think",
                indent=0
            )
        
        # 显示工具调用
        tool_icon = self._get_tool_icon(action.tool)
        self._print_section(
            f"工具调用: {action.tool}",
            f"参数: {self._format_input(action.tool_input)}",
            icon="tool",
            indent=0
        )
        
        # 显示进度指示
        sys.stdout.write(self._color(f"  ⏳ 执行中", "gray"))
        sys.stdout.flush()
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """工具执行结束时调用"""
        if not self.verbose:
            return
        
        # 清除"执行中"提示
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        
        # 显示工具结果
        formatted_output = self._format_tool_output(output)
        self._print_section(
            "观察结果",
            formatted_output,
            icon="observe",
            indent=0
        )
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """工具执行错误时调用"""
        if not self.verbose:
            return
        
        self._print_section(
            "错误",
            str(error),
            icon="error",
            indent=0
        )
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        """Agent完成时调用"""
        if not self.verbose:
            return
        
        # 解析最终思考
        final_thought = self._extract_final_thought(finish.log)
        
        if final_thought:
            print(self._color(f"\n{'═' * 80}", "green"))
            print(self._color(f"  最终分析", "bold"))
            print(self._color(f"{'═' * 80}\n", "green"))
            
            self._print_section(
                "💡 结论",
                final_thought,
                icon="success",
                indent=0
            )
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """LLM开始时调用"""
        # 不显示LLM开始，避免过于冗长
        pass
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """LLM结束时调用"""
        # 不显示LLM结束，避免过于冗长
        pass
    
    def _extract_thought(self, log: str) -> str:
        """提取思考过程"""
        # 尝试提取Thought部分
        patterns = [
            r"Thought:\s*(.*?)(?=\n(?:Action|Final Answer|$))",
            r"思考[:：]\s*(.*?)(?=\n(?:动作|最终答案|$))",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                # 清理多余的空白
                thought = re.sub(r'\n\s*\n', '\n', thought)
                return thought
        
        return ""
    
    def _extract_final_thought(self, log: str) -> str:
        """提取最终思考"""
        # 尝试提取Final Answer之前的Thought
        patterns = [
            r"Thought:\s*(.*?)(?=Final Answer)",
            r"思考[:：]\s*(.*?)(?=最终答案)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                thought = re.sub(r'\n\s*\n', '\n', thought)
                return thought
        
        return ""
    
    def _format_input(self, tool_input: Any) -> str:
        """格式化工具输入"""
        if isinstance(tool_input, dict):
            # 格式化字典
            items = []
            for key, value in tool_input.items():
                if len(str(value)) > 100:
                    value = str(value)[:100] + "..."
                items.append(f"{key}={value}")
            return ", ".join(items)
        else:
            input_str = str(tool_input)
            if len(input_str) > 150:
                return input_str[:150] + "..."
            return input_str
    
    def _format_tool_output(self, output: str) -> str:
        """格式化工具输出"""
        # 限制输出长度
        max_length = 500
        if len(output) > max_length:
            return output[:max_length] + f"\n  ... (共 {len(output)} 字符，已截断)"
        return output
    
    def _get_tool_icon(self, tool_name: str) -> str:
        """根据工具名称获取图标"""
        tool_icons = {
            'search': '🔍',
            'calculator': '🔢',
            'time': '⏰',
            'crewai': '👥',
            'n8n': '⚙️',
        }
        
        for key, icon in tool_icons.items():
            if key in tool_name.lower():
                return icon
        
        return '🔧'


class SimpleStreamingHandler(BaseCallbackHandler):
    """简化版流式处理器 - 更简洁的输出"""
    
    def __init__(self):
        super().__init__()
        self.step_count = 0
        self.current_tool = None
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Agent执行动作时调用"""
        self.step_count += 1
        self.current_tool = action.tool
        
        print(f"\n{'─' * 60}")
        
        # 显示工具
        tool_icon = self._get_tool_icon(action.tool)
        print(f"{tool_icon} 工具: {action.tool}")
        
        # 显示参数
        if action.tool_input:
            if isinstance(action.tool_input, dict):
                params = ", ".join([f"{k}={v}" for k, v in action.tool_input.items()])
            else:
                params = str(action.tool_input)
            
            if len(params) > 150:
                params = params[:150] + "..."
            print(f"📝 参数: {params}")
        
        sys.stdout.write("⏳ 执行中...")
        sys.stdout.flush()
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """工具开始执行"""
        # 工具开始执行时的回调
        pass
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """工具执行结束时调用"""
        # 清除"执行中"提示
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        
        print("✅ 完成")
        
        # 显示结果摘要
        if output:
            summary = output[:200] + "..." if len(output) > 200 else output
            # 处理多行输出
            lines = summary.split('\n')
            print(f"📊 结果:")
            for line in lines[:3]:  # 只显示前3行
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 3:
                print(f"   ... (共{len(lines)}行)")
        print()
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """工具执行错误时调用"""
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        print(f"❌ 错误: {str(error)}\n")
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """链开始"""
        user_input = inputs.get("input", "")
        print(f"\n{'═' * 60}")
        print(f"🤖 智能体启动")
        print(f"{'═' * 60}")
        print(f"📥 问题: {user_input}")
        print(f"{'═' * 60}\n")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """链结束"""
        print(f"\n{'═' * 60}")
        print(f"✅ 执行完成")
        print(f"{'═' * 60}\n")
    
    def _get_tool_icon(self, tool_name: str) -> str:
        """根据工具名称获取图标"""
        tool_icons = {
            'search': '🔍',
            'calculator': '🔢',
            'time': '⏰',
            'crewai': '👥',
            'n8n': '⚙️',
        }
        
        for key, icon in tool_icons.items():
            if key in tool_name.lower():
                return icon
        
        return '🔧'

