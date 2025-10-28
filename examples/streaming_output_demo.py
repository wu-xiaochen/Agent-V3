"""
流式输出功能演示
展示三种不同的流式输出模式
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.unified.unified_agent import UnifiedAgent


def demo_simple_mode():
    """演示简洁模式"""
    print("\n" + "=" * 80)
    print("演示1: 简洁模式 (Simple Mode)")
    print("=" * 80)
    print("特点: 清晰展示执行步骤，美观的图标和分隔线\n")
    
    agent = UnifiedAgent(
        provider="siliconflow",
        memory=False,  # 为了演示，关闭记忆
        streaming_style="simple"
    )
    
    result = agent.run("现在几点了？", session_id="demo_simple")
    print("\n最终输出:")
    print(result["response"])


def demo_detailed_mode():
    """演示详细模式"""
    print("\n" + "=" * 80)
    print("演示2: 详细模式 (Detailed Mode)")
    print("=" * 80)
    print("特点: 完整的思考过程，带颜色的层次化输出\n")
    
    agent = UnifiedAgent(
        provider="siliconflow",
        memory=False,
        streaming_style="detailed"
    )
    
    result = agent.run("计算 15 * 8", session_id="demo_detailed")
    print("\n最终输出:")
    print(result["response"])


def demo_none_mode():
    """演示无流式输出模式"""
    print("\n" + "=" * 80)
    print("演示3: 无流式输出 (None Mode)")
    print("=" * 80)
    print("特点: 只显示最终结果，适合自动化脚本\n")
    
    agent = UnifiedAgent(
        provider="siliconflow",
        memory=False,
        streaming_style="none"
    )
    
    result = agent.run("100 + 200 等于多少？", session_id="demo_none")
    print("\n最终输出:")
    print(result["response"])


def demo_with_tools():
    """演示带工具调用的流式输出"""
    print("\n" + "=" * 80)
    print("演示4: 多工具调用场景 (简洁模式)")
    print("=" * 80)
    print("特点: 展示多个工具的调用过程\n")
    
    agent = UnifiedAgent(
        provider="siliconflow",
        memory=False,
        streaming_style="simple"
    )
    
    result = agent.run(
        "请告诉我现在的时间，然后帮我计算 456 + 789",
        session_id="demo_tools"
    )
    print("\n最终输出:")
    print(result["response"])


def main():
    """主函数"""
    print("\n🌟 流式输出功能演示")
    print("=" * 80)
    print("本演示将展示Agent-V3系统的三种流式输出模式")
    print("=" * 80)
    
    demos = [
        ("1", "简洁模式", demo_simple_mode),
        ("2", "详细模式", demo_detailed_mode),
        ("3", "无流式输出", demo_none_mode),
        ("4", "多工具调用", demo_with_tools),
    ]
    
    print("\n请选择要运行的演示:")
    for num, name, _ in demos:
        print(f"  {num}. {name}")
    print("  0. 运行所有演示")
    
    choice = input("\n请输入选项 (0-4): ").strip()
    
    if choice == "0":
        # 运行所有演示
        for num, name, demo_func in demos:
            try:
                demo_func()
                input("\n按回车继续下一个演示...")
            except Exception as e:
                print(f"\n演示出错: {str(e)}")
                continue
    else:
        # 运行单个演示
        for num, name, demo_func in demos:
            if choice == num:
                try:
                    demo_func()
                except Exception as e:
                    print(f"\n演示出错: {str(e)}")
                return
        
        if choice not in [num for num, _, _ in demos]:
            print("无效的选项！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n演示已取消")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")

