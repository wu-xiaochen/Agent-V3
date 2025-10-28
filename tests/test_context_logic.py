"""
测试上下文逻辑
测试场景：
1. 生成 CrewAI 配置 → "运行它" → 应调用 crewai_runtime
2. 创建 n8n 工作流 → "运行它" → 应说明已创建
3. 普通查询 → 正常处理
"""

import sys
from src.agents.unified.unified_agent import UnifiedAgent


def test_context_logic():
    """测试上下文逻辑"""
    
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                     🧪 上下文逻辑测试                                    ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    # 初始化智能体
    print("🔧 初始化智能体...")
    agent = UnifiedAgent(
        provider="siliconflow",
        memory=True,
        session_id="test_context_001",
        streaming_style="simple"
    )
    print("✅ 智能体初始化完成\n")
    
    # 测试场景 1: 生成 CrewAI 配置 → "运行它"
    print("━" * 80)
    print("📋 测试场景 1: CrewAI 配置生成 + 运行")
    print("━" * 80)
    
    print("\n步骤 1: 生成配置")
    result1 = agent.run("帮我生成一个简单的数据分析团队配置")
    print(f"\n结果: {result1['response'][:200]}...")
    
    # 检查上下文追踪器
    stats = agent.context_tracker.get_statistics()
    print(f"\n📊 上下文统计:")
    print(f"   - 查询次数: {stats['total_queries']}")
    print(f"   - 工具调用次数: {stats['total_tool_calls']}")
    print(f"   - 最后工具: {stats['last_tool']}")
    
    print("\n步骤 2: 运行它（应该调用 crewai_runtime）")
    result2 = agent.run("运行它")
    print(f"\n结果: {result2['response'][:200]}...")
    
    stats = agent.context_tracker.get_statistics()
    print(f"\n📊 上下文统计:")
    print(f"   - 查询次数: {stats['total_queries']}")
    print(f"   - 工具调用次数: {stats['total_tool_calls']}")
    print(f"   - 最后工具: {stats['last_tool']}")
    
    # 验证
    if stats['last_tool'] == 'crewai_runtime':
        print("\n✅ 测试场景 1 通过: 正确调用了 crewai_runtime")
    else:
        print(f"\n❌ 测试场景 1 失败: 调用了 {stats['last_tool']}，应该调用 crewai_runtime")
    
    # 测试场景 2: 上下文依赖检测
    print("\n\n━" * 80)
    print("📋 测试场景 2: 上下文依赖检测")
    print("━" * 80)
    
    tracker = agent.context_tracker
    
    test_queries = [
        ("运行它", True),
        ("执行它", True),
        ("刚才的结果", True),
        ("这个怎么用", True),
        ("计算 10 + 20", False),
        ("今天天气如何", False)
    ]
    
    print("\n测试各种查询的上下文依赖检测:")
    for query, expected in test_queries:
        result = tracker.is_context_dependent(query)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{query}' → {result} (预期: {expected})")
    
    # 测试场景 3: 上下文提示生成
    print("\n\n━" * 80)
    print("📋 测试场景 3: 上下文提示生成")
    print("━" * 80)
    
    # 模拟刚调用了 crewai_generator
    tracker.add_tool_call("crewai_generator", "已生成配置")
    
    hint = tracker.generate_context_hint("运行它")
    print(f"\n查询: '运行它'")
    print(f"增强后: '{hint[:100]}...'")
    
    if "crewai_runtime" in hint:
        print("\n✅ 测试场景 3 通过: 正确生成了 crewai_runtime 提示")
    else:
        print("\n❌ 测试场景 3 失败: 未生成正确提示")
    
    # 测试场景 4: 上下文摘要
    print("\n\n━" * 80)
    print("📋 测试场景 4: 上下文摘要")
    print("━" * 80)
    
    summary = tracker.get_context_summary(n=3)
    print(f"\n最近 3 步操作摘要:")
    print(summary)
    
    # 最终统计
    print("\n\n━" * 80)
    print("📊 最终统计")
    print("━" * 80)
    
    final_stats = agent.context_tracker.get_statistics()
    print(f"\n总查询次数: {final_stats['total_queries']}")
    print(f"总工具调用次数: {final_stats['total_tool_calls']}")
    print(f"使用的工具种类: {final_stats['unique_tools']}")
    print(f"工具调用统计:")
    for tool, count in final_stats['tool_counts'].items():
        print(f"   - {tool}: {count} 次")
    
    print("\n╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                     ✅ 测试完成！                                        ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    try:
        test_context_logic()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

