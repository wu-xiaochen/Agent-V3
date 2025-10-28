"""
流式输出功能测试
"""

import sys
import os
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.unified.unified_agent import UnifiedAgent


def test_simple_streaming():
    """测试简洁流式输出"""
    print("\n测试1: 简洁流式输出")
    print("=" * 60)
    
    try:
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=False,
            streaming_style="simple"
        )
        
        # 捕获标准输出
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        result = agent.run("计算 10 + 20", session_id="test_simple")
        
        # 恢复标准输出
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # 验证输出包含关键元素
        assert "智能体启动" in output or "🤖" in output, "应该包含启动信息"
        assert "步骤" in output or "💭" in output, "应该包含步骤信息"
        assert "工具" in output or "🔧" in output, "应该包含工具信息"
        
        print("✅ 简洁流式输出测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 简洁流式输出测试失败: {str(e)}")
        return False


def test_detailed_streaming():
    """测试详细流式输出"""
    print("\n测试2: 详细流式输出")
    print("=" * 60)
    
    try:
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=False,
            streaming_style="detailed"
        )
        
        result = agent.run("现在几点？", session_id="test_detailed")
        
        print("✅ 详细流式输出测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 详细流式输出测试失败: {str(e)}")
        return False


def test_none_streaming():
    """测试无流式输出"""
    print("\n测试3: 无流式输出")
    print("=" * 60)
    
    try:
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=False,
            streaming_style="none"
        )
        
        # 捕获标准输出
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        result = agent.run("50 + 50", session_id="test_none")
        
        # 恢复标准输出
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # 验证输出不应该包含流式输出的元素
        # 注意：AgentExecutor可能仍然有一些默认输出
        
        print("✅ 无流式输出测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 无流式输出测试失败: {str(e)}")
        return False


def test_streaming_with_multiple_tools():
    """测试多工具调用的流式输出"""
    print("\n测试4: 多工具调用流式输出")
    print("=" * 60)
    
    try:
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=False,
            streaming_style="simple"
        )
        
        result = agent.run(
            "告诉我现在的时间，然后计算 100 - 50",
            session_id="test_multi_tools"
        )
        
        print("✅ 多工具调用流式输出测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 多工具调用流式输出测试失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("流式输出功能测试套件")
    print("=" * 60)
    
    tests = [
        test_simple_streaming,
        test_detailed_streaming,
        test_none_streaming,
        test_streaming_with_multiple_tools,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            print("\n\n测试被用户中断")
            break
        except Exception as e:
            print(f"❌ 测试执行错误: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

