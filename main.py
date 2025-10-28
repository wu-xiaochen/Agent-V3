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
    
    # 非调试模式下，过滤各种警告
    if not debug_mode:
        warnings.filterwarnings("ignore", category=UserWarning, message=".*API key must be provided when hosted LangSmith API.*")
        warnings.filterwarnings("ignore", category=UserWarning, message=".*CrewAI执行过程.*")
        # 过滤LangChain参数警告
        warnings.filterwarnings("ignore", message=".*is not default parameter.*")
        warnings.filterwarnings("ignore", message=".*was transferred to model_kwargs.*")
    
    logging_config = config_loader.get_logging_config()
    # 在debug模式下，将日志级别设置为DEBUG
    if debug_mode:
        level = logging.DEBUG
    else:
        level = logging.INFO  # 非debug模式只显示INFO及以上级别的日志
    
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
    
    # 非调试模式下，提高第三方库的日志级别，只显示ERROR及以上
    if not debug_mode:
        logging.getLogger("langchain_community").setLevel(logging.ERROR)
        logging.getLogger("openai").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("httpcore").setLevel(logging.ERROR)
        logging.getLogger("langsmith").setLevel(logging.ERROR)


def interactive_mode(agent: UnifiedAgent, stream: bool = False):
    """交互模式"""
    print("=== LangChain智能体交互模式 ===")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'clear' 清除对话历史")
    print("输入 'memory' 查看对话历史")
    print("输入 'stats' 查看记忆统计")
    print("输入 'summary' 查看对话摘要")
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
                        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                        print(f"{msg_type}: {content}")
                    print("=" * 40)
                else:
                    print("暂无对话历史")
                continue
            elif user_input.lower() == 'stats':
                stats = agent.get_memory_stats()
                print("\n=== 记忆统计 ===")
                print(f"记忆状态: {'启用' if stats['enabled'] else '未启用'}")
                print(f"消息数量: {stats['message_count']}")
                print(f"对话轮数: {stats.get('conversation_rounds', 0)}")
                print(f"摘要数量: {stats['summary_count']}")
                print(f"存储类型: {stats.get('memory_type', 'unknown')}")
                print(f"会话ID: {stats.get('session_id', 'unknown')}")
                print("=" * 40)
                continue
            elif user_input.lower() == 'summary':
                summaries = agent.get_summary_history()
                if summaries:
                    print("\n=== 对话摘要历史 ===")
                    for i, summary in enumerate(summaries, 1):
                        print(f"\n摘要 {i}:")
                        print(summary)
                    print("\n" + "=" * 40)
                else:
                    print("暂无对话摘要（对话轮数较少，未触发自动摘要）")
                continue
            
            # 注意：streaming_style 参数已经在创建agent时设置了callbacks
            # 这些callbacks会在run()方法执行时自动触发，提供实时输出
            # 所以这里统一使用run()方法，不需要区分stream参数
            response = agent.run(user_input)
            if isinstance(response, dict) and "response" in response:
                print(f"\n助手: {response['response']}")
            else:
                print(f"\n助手: {response}")
            
        except KeyboardInterrupt:
            print("\n\n程序被中断，再见!")
            break
        except EOFError:
            # 处理EOF错误（例如管道输入结束）
            print("\n\n输入结束，再见!")
            break
        except Exception as e:
            print(f"\n错误: {str(e)}")


def single_query_mode(agent: UnifiedAgent, query: str, stream: bool = False, auto_continue: bool = False, max_retries: int = 3):
    """单次查询模式"""
    try:
        # 注意：streaming_style 参数已经在创建agent时设置了callbacks
        # 这些callbacks会在run()方法执行时自动触发，提供实时输出
        
        # 🆕 如果启用自动继续，使用 run_with_auto_continue
        if auto_continue:
            print(f"🔄 自动继续模式已启用（最大重试: {max_retries}）")
            response = agent.run_with_auto_continue(query, max_retries=max_retries)
        else:
            response = agent.run(query)
        
        if isinstance(response, dict) and "response" in response:
            print(f"\n{response['response']}")
            # 🆕 显示自动继续的统计信息
            if auto_continue and "metadata" in response:
                attempts = response["metadata"].get("auto_continue_attempts", 1)
                if attempts > 1:
                    print(f"\n📊 统计: 经过 {attempts} 次执行完成任务")
        else:
            print(f"\n{response}")
    except Exception as e:
        print(f"错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能体系统")
    parser.add_argument("--provider", choices=["openai", "anthropic", "ollama", "siliconflow"], default="siliconflow", help="选择LLM提供商")
    parser.add_argument("--query", type=str, help="单次查询模式")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    parser.add_argument("--stream", "-s", action="store_true", help="启用流式输出")
    parser.add_argument("--streaming-style", choices=["simple", "detailed", "none"], default="simple", 
                       help="流式输出样式: simple=简洁美观, detailed=详细完整, none=只显示结果")
    parser.add_argument("--auto-continue", action="store_true", help="🆕 启用自动继续执行（达到限制时自动续接）")
    parser.add_argument("--max-retries", type=int, default=3, help="🆕 自动继续的最大重试次数")
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
        # 创建智能体（传入streaming_style参数）
        agent = UnifiedAgent(
            provider=args.provider,
            streaming_style=args.streaming_style
        )
        
        if args.query:
            # 单次查询模式
            # 🆕 传递auto_continue和max_retries参数
            single_query_mode(agent, args.query, args.stream, args.auto_continue, args.max_retries)
        elif args.interactive:
            interactive_mode(agent, args.stream)
        else:
            interactive_mode(agent, args.stream)
    
    except Exception as e:
        print(f"初始化智能体失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()