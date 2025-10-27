#!/usr/bin/env python3
"""
主程序入口文件
"""

import os
import sys
import warnings
import argparse
import logging
from typing import Optional

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()

# 在导入LangChain之前设置环境变量来抑制弃用警告
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning:langchain.*"
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.*")
warnings.filterwarnings("ignore", message="Please see the migration guide at", category=DeprecationWarning)

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.agents.unified.unified_agent import UnifiedAgent
from src.config.config_loader import config_loader


def setup_logging(debug_mode=False):
    """设置日志"""
    # 完全禁用所有弃用警告
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message="Please see the migration guide at")
    
    # 非调试模式下，过滤LangSmith警告
    if not debug_mode:
        warnings.filterwarnings("ignore", category=UserWarning, message=".*API key must be provided when using hosted LangSmith API.*")
    
    logging_config = config_loader.get_logging_config()
    level = getattr(logging, logging_config.get("level", "INFO"))
    format_str = logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file = logging_config.get("file", "logs/agent.log")
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # 获取调试配置
    debug_config = logging_config.get("debug", {})
    
    # 设置调试过滤器
    from src.shared.debug_filter import setup_debug_filters
    setup_debug_filters(debug_mode, debug_config)


def interactive_mode(agent: UnifiedAgent, stream: bool = False):
    """交互模式"""
    print("=== LangChain智能体交互模式 ===")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'clear' 清除对话历史")
    print("输入 'memory' 查看对话历史")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\n您: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("再见!")
                break
            elif user_input.lower() == 'clear':
                agent.clear_memory()
                print("对话历史已清除")
                continue
            elif user_input.lower() == 'memory':
                memory = agent.get_memory()
                if memory:
                    print("\n=== 对话历史 ===")
                    for i, msg in enumerate(memory):
                        msg_type = "用户" if msg.type == "human" else "助手"
                        print(f"{msg_type}: {msg.content}")
                    print("=" * 40)
                else:
                    print("暂无对话历史")
                continue
            
            print("\n助手: ", end="", flush=True)
            if stream:
                # 流式输出
                for chunk in agent.stream(user_input):
                    if isinstance(chunk, dict) and "response" in chunk:
                        print(chunk["response"], end="", flush=True)
                    else:
                        print(chunk, end="", flush=True)
                print()  # 换行
            else:
                # 非流式输出
                response = agent.run(user_input)
                if isinstance(response, dict) and "response" in response:
                    print(response["response"])
                else:
                    print(response)
            
        except KeyboardInterrupt:
            print("\n\n程序被中断，再见!")
            break
        except EOFError:
            # 处理EOF错误（例如管道输入结束）
            print("\n\n输入结束，再见!")
            break
        except Exception as e:
            print(f"\n错误: {str(e)}")


def single_query_mode(agent: UnifiedAgent, query: str, stream: bool = False):
    """单次查询模式"""
    try:
        if stream:
            # 流式输出
            for chunk in agent.stream(query):
                if isinstance(chunk, dict) and "response" in chunk:
                    print(chunk["response"], end="", flush=True)
                else:
                    print(chunk, end="", flush=True)
            print()  # 换行
        else:
            # 非流式输出
            response = agent.run(query)
            if isinstance(response, dict) and "response" in response:
                print(response["response"])
            else:
                print(response)
    except Exception as e:
        print(f"错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能体系统")
    parser.add_argument("--provider", choices=["openai", "anthropic", "ollama", "siliconflow"], default="siliconflow", help="选择LLM提供商")
    parser.add_argument("--query", type=str, help="单次查询模式")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    parser.add_argument("--stream", "-s", action="store_true", help="启用流式输出")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--debug", action="store_true", help="调试模式，显示详细日志")
    parser.add_argument("--no-debug", action="store_true", help="关闭调试模式，仅显示对话信息")
    
    args = parser.parse_args()
    
    # 如果指定了配置文件路径，重新加载配置
    if args.config:
        global config_loader
        from src.config.config_loader import ConfigLoader
        config_loader = ConfigLoader(args.config)
    
    # 设置日志
    debug_mode = args.debug and not args.no_debug
    setup_logging(debug_mode)
    
    try:
        # 创建智能体
        agent = UnifiedAgent(provider=args.provider)
        
        if args.query:
            # 单次查询模式
            single_query_mode(agent, args.query, args.stream)
        elif args.interactive:
            interactive_mode(agent, args.stream)
        else:
            interactive_mode(agent, args.stream)
    
    except Exception as e:
        print(f"初始化智能体失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()