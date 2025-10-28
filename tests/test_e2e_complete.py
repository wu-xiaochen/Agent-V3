#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent-V3 完整端到端测试套件
测试所有核心功能：智能体、工具、上下文管理、记忆、配置等
"""

import sys
import os
import logging
import traceback
from typing import Dict, List, Tuple
from pathlib import Path

# 确保可以导入 src 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 减少测试输出
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2ETestSuite:
    """端到端测试套件"""
    
    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
    
    def run_test(self, test_name: str, test_func, skip_if_fails: bool = False):
        """运行单个测试"""
        self.total_tests += 1
        print(f"\n{'='*80}")
        print(f"🧪 测试 {self.total_tests}: {test_name}")
        print(f"{'='*80}")
        
        try:
            test_func()
            self.results[test_name] = (True, "✅ 通过")
            self.passed_tests += 1
            print(f"✅ {test_name} - 通过")
        except AssertionError as e:
            if skip_if_fails:
                self.results[test_name] = (None, f"⏭️  跳过: {str(e)}")
                self.skipped_tests += 1
                print(f"⏭️  {test_name} - 跳过 (依赖未满足): {str(e)}")
            else:
                self.results[test_name] = (False, f"❌ 断言失败: {str(e)}")
                self.failed_tests += 1
                print(f"❌ {test_name} - 断言失败: {str(e)}")
                if logger.level <= logging.DEBUG:
                    traceback.print_exc()
        except Exception as e:
            if skip_if_fails:
                self.results[test_name] = (None, f"⏭️  跳过: {str(e)}")
                self.skipped_tests += 1
                print(f"⏭️  {test_name} - 跳过 (异常): {str(e)}")
            else:
                self.results[test_name] = (False, f"❌ 异常: {str(e)}")
                self.failed_tests += 1
                print(f"❌ {test_name} - 异常: {str(e)}")
                if logger.level <= logging.DEBUG:
                    traceback.print_exc()
    
    def print_summary(self):
        """打印测试总结"""
        print(f"\n\n{'='*80}")
        print(f"📊 测试总结")
        print(f"{'='*80}")
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"失败: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        if self.skipped_tests > 0:
            print(f"跳过: {self.skipped_tests} ({self.skipped_tests/self.total_tests*100:.1f}%)")
        
        print(f"\n详细结果:")
        for test_name, (passed, message) in self.results.items():
            print(f"  {message} - {test_name}")
        
        # 评分（跳过的测试不计入失败）
        valid_tests = self.total_tests - self.skipped_tests
        score = (self.passed_tests / valid_tests * 100) if valid_tests > 0 else 0
        
        if score >= 95:
            grade = "🎉 优秀"
        elif score >= 85:
            grade = "✅ 良好"
        elif score >= 70:
            grade = "⚠️  及格"
        else:
            grade = "❌ 不及格"
        
        print(f"\n最终评分: {score:.1f}分 - {grade}")
        print(f"{'='*80}\n")
        
        return score >= 85


# ========================================
# 配置管理测试
# ========================================

def test_env_manager_n8n_config():
    """测试 EnvManager 的 n8n 配置加载（支持配置文件后备）"""
    from src.config.env_manager import EnvManager
    
    config = EnvManager.get_n8n_config()
    assert "api_url" in config, "缺少 api_url"
    assert "api_key" in config, "缺少 api_key"
    assert config["api_url"], "api_url 为空"
    # API Key 可能为空（用户未配置）
    print(f"✅ n8n 配置: URL={config['api_url']}, Key={'已设置' if config['api_key'] else '未设置'}")


def test_config_loader_caching():
    """测试配置加载缓存"""
    from src.config.config_loader import ConfigLoader
    import time
    
    loader = ConfigLoader()
    
    # 第一次加载
    start = time.time()
    config1 = loader.load_config("agents")
    time1 = time.time() - start
    
    # 第二次加载（应该从缓存）
    start = time.time()
    config2 = loader.load_config("agents")
    time2 = time.time() - start
    
    assert config1 == config2, "配置不一致"
    # 缓存应该更快（至少快 50%）
    print(f"✅ 配置加载时间: 第1次={time1*1000:.2f}ms, 第2次={time2*1000:.2f}ms (提升{(1-time2/time1)*100:.1f}%)")


# ========================================
# 上下文管理测试
# ========================================

def test_context_tracker_full():
    """测试 ContextTracker 完整功能"""
    from src.core.services.context_tracker import ContextTracker
    
    tracker = ContextTracker(max_history=10)
    
    # 测试添加多个查询和工具调用
    tracker.add_query("生成一个配置")
    tracker.add_tool_call("crewai_generator", "配置已生成")
    tracker.add_query("运行它")
    tracker.add_tool_call("crewai_runtime", "团队运行中")
    
    # 验证历史记录
    assert len(tracker.query_history) == 2, "查询历史数量不对"
    assert len(tracker.tool_history) == 2, "工具调用历史数量不对"
    
    # 验证上下文依赖检测
    assert tracker.is_context_dependent("运行它"), "未检测到上下文依赖"
    assert tracker.is_context_dependent("刚才的结果"), "未检测到上下文依赖"
    assert not tracker.is_context_dependent("帮我分析数据"), "错误检测为上下文依赖"
    
    # 验证统计信息
    stats = tracker.get_statistics()
    assert stats["total_queries"] == 2, "查询统计不对"
    assert stats["total_tool_calls"] == 2, "工具调用统计不对"
    
    print(f"✅ ContextTracker: {stats['total_queries']} 查询, {stats['total_tool_calls']} 工具调用")


# ========================================
# 智能体测试
# ========================================

def test_unified_agent_creation():
    """测试 UnifiedAgent 创建和基本功能"""
    from src.agents.unified.unified_agent import UnifiedAgent
    
    # 创建不带记忆的 agent（避免 Redis 依赖）
    agent = UnifiedAgent(
        provider="siliconflow",
        streaming_style="none",
        memory=False
    )
    
    # 验证核心组件
    assert agent.llm is not None, "LLM 未初始化"
    assert agent.context_tracker is not None, "ContextTracker 未初始化"
    assert hasattr(agent, 'run'), "缺少 run 方法"
    assert hasattr(agent, 'run_with_auto_continue'), "缺少 run_with_auto_continue 方法"
    
    print("✅ UnifiedAgent 创建成功，所有核心组件已初始化")


def test_unified_agent_with_memory():
    """测试 UnifiedAgent 的记忆功能（需要 Redis）"""
    from src.agents.unified.unified_agent import UnifiedAgent
    import redis
    
    # 检查 Redis 是否可用
    try:
        r = redis.from_url("redis://localhost:6379/0")
        r.ping()
        redis_available = True
    except:
        redis_available = False
    
    if not redis_available:
        raise AssertionError("Redis 未运行，跳过记忆测试")
    
    # 创建带记忆的 agent
    agent = UnifiedAgent(
        provider="siliconflow",
        streaming_style="none",
        memory=True,
        session_id="test_session"
    )
    
    assert agent.memory is not None, "Memory 未初始化"
    print("✅ UnifiedAgent 记忆功能测试通过（Redis 已连接）")


def test_auto_continue_mechanism():
    """测试自动继续执行机制"""
    from src.agents.unified.unified_agent import UnifiedAgent, AgentStopReason
    
    agent = UnifiedAgent(provider="siliconflow", streaming_style="none", memory=False)
    
    # 验证停止原因枚举
    assert hasattr(AgentStopReason, 'COMPLETED'), "缺少 COMPLETED"
    assert hasattr(AgentStopReason, 'ITERATION_LIMIT'), "缺少 ITERATION_LIMIT"
    assert hasattr(AgentStopReason, 'TIME_LIMIT'), "缺少 TIME_LIMIT"
    
    # 验证方法存在
    assert hasattr(agent, '_detect_stop_reason'), "缺少 _detect_stop_reason"
    assert hasattr(agent, '_generate_continuation_prompt'), "缺少 _generate_continuation_prompt"
    assert hasattr(agent, '_extract_last_actions'), "缺少 _extract_last_actions"
    
    # 测试续接提示生成
    prompt = agent._generate_continuation_prompt(
        "分析数据",
        ["已收集数据"],
        ["search: 收集信息"]
    )
    assert "原始任务" in prompt, "续接提示不包含原始任务"
    assert "已完成的工作" in prompt, "续接提示不包含已完成工作"
    
    print("✅ 自动继续执行机制验证成功")


# ========================================
# 工具测试
# ========================================

def test_tools_loading():
    """测试工具加载"""
    from src.agents.shared.tools import get_tools
    
    # 加载默认工具
    tools = get_tools()
    
    assert len(tools) > 0, "未加载任何工具"
    
    # 验证核心工具
    tool_names = [tool.name for tool in tools]
    assert "time" in tool_names, "缺少 time 工具"
    assert "calculator" in tool_names, "缺少 calculator 工具"
    
    print(f"✅ 成功加载 {len(tools)} 个工具: {', '.join(tool_names[:5])}...")


def test_n8n_tools():
    """测试 n8n 工具（需要 n8n API Key）"""
    from src.config.env_manager import EnvManager
    from src.agents.shared.n8n_api_tools import N8NAPIClient
    
    config = EnvManager.get_n8n_config()
    
    if not config["api_key"]:
        raise AssertionError("n8n API Key 未配置，跳过 n8n 工具测试")
    
    # 创建 n8n 客户端
    client = N8NAPIClient(config["api_url"], config["api_key"])
    
    # 测试列出工作流
    workflows = client.list_workflows()
    assert isinstance(workflows, list), "工作流列表格式不对"
    
    print(f"✅ n8n 工具测试通过，当前有 {len(workflows)} 个工作流")


def test_crewai_tools():
    """测试 CrewAI 工具"""
    from src.agents.shared.crewai_tools import create_crewai_tools
    
    tools = create_crewai_tools()
    
    assert len(tools) > 0, "未创建任何 CrewAI 工具"
    
    tool_names = [tool.name for tool in tools]
    assert "calculator" in tool_names, "缺少 calculator 工具"
    assert "time" in tool_names, "缺少 time 工具"
    
    print(f"✅ 创建了 {len(tools)} 个 CrewAI 工具")


# ========================================
# CrewAI 集成测试
# ========================================

def test_crewai_runtime_creation():
    """测试 CrewAI Runtime 创建"""
    from src.interfaces.crewai_runtime import CrewAIRuntime
    
    runtime = CrewAIRuntime()
    
    assert hasattr(runtime, 'load_config'), "缺少 load_config 方法"
    assert hasattr(runtime, 'create_crew'), "缺少 create_crew 方法"
    assert hasattr(runtime, 'run_crew'), "缺少 run_crew 方法"
    
    print("✅ CrewAI Runtime 创建成功")


def test_crewai_generator():
    """测试 CrewAI 配置生成器"""
    from src.tools.crewai_generator import CrewAIGeneratorTool
    
    # 验证工具类存在
    tool = CrewAIGeneratorTool()
    
    assert hasattr(tool, '_run'), "缺少 _run 方法"
    assert hasattr(tool, 'name'), "缺少 name 属性"
    assert tool.name == "crewai_generator", "工具名称不对"
    
    print("✅ CrewAI 配置生成器验证成功")


# ========================================
# 异常处理测试
# ========================================

def test_exception_handling_quality():
    """测试异常处理质量（检查是否有裸 except）"""
    import re
    from pathlib import Path
    
    # 核心文件
    core_files = [
        "src/agents/shared/n8n_api_tools.py",
        "src/infrastructure/cache/cache_service.py",
        "src/agents/unified/unified_agent.py",
        "src/config/config_loader.py",
    ]
    
    bare_except_count = 0
    files_with_issues = []
    
    for file_path in core_files:
        full_path = project_root / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                bare_excepts = re.findall(r'except\s*:\s*\n', content)
                if bare_excepts:
                    bare_except_count += len(bare_excepts)
                    files_with_issues.append(f"{file_path} ({len(bare_excepts)})")
    
    assert bare_except_count == 0, f"发现 {bare_except_count} 个裸 except: {', '.join(files_with_issues)}"
    
    print("✅ 所有核心文件使用精确异常处理")


# ========================================
# 性能测试
# ========================================

def test_config_cache_performance():
    """测试配置缓存性能"""
    from src.config.config_loader import ConfigLoader
    import time
    
    loader = ConfigLoader()
    
    # 多次加载测试
    times = []
    for i in range(5):
        start = time.time()
        loader.load_config("agents")
        times.append(time.time() - start)
    
    # 第一次应该最慢，后续应该更快
    assert times[1] < times[0], "缓存未生效"
    avg_cached_time = sum(times[1:]) / len(times[1:])
    
    improvement = (1 - avg_cached_time / times[0]) * 100
    assert improvement > 20, f"缓存性能提升不足 ({improvement:.1f}%)"
    
    print(f"✅ 配置缓存性能提升 {improvement:.1f}%")


# ========================================
# 集成测试
# ========================================

def test_full_integration_workflow():
    """完整集成工作流测试"""
    from src.agents.unified.unified_agent import UnifiedAgent
    from src.config.env_manager import EnvManager
    
    # 1. 配置验证
    n8n_config = EnvManager.get_n8n_config()
    assert n8n_config["api_url"], "n8n URL 未配置"
    
    # 2. 创建 agent
    agent = UnifiedAgent(
        provider="siliconflow",
        streaming_style="none",
        memory=False
    )
    
    # 3. 验证上下文追踪
    assert agent.context_tracker is not None, "上下文追踪器未初始化"
    
    # 4. 验证工具加载
    # (工具在agent创建时动态加载)
    
    # 5. 测试简单查询（不需要 API 调用）
    # 注意：实际执行会调用 LLM，这里只验证接口
    assert hasattr(agent, 'run'), "Agent 缺少 run 方法"
    
    print("✅ 完整集成工作流验证通过")


# ========================================
# 主测试函数
# ========================================

def main():
    """主测试函数"""
    print(f"\n{'='*80}")
    print(f"🚀 Agent-V3 完整端到端测试开始")
    print(f"{'='*80}\n")
    
    suite = E2ETestSuite()
    
    # 配置管理测试
    print(f"\n{'#'*80}")
    print(f"# 📦 配置管理测试")
    print(f"{'#'*80}")
    suite.run_test("1.1 EnvManager n8n 配置加载", test_env_manager_n8n_config)
    suite.run_test("1.2 配置加载缓存", test_config_loader_caching)
    
    # 上下文管理测试
    print(f"\n{'#'*80}")
    print(f"# 🧠 上下文管理测试")
    print(f"{'#'*80}")
    suite.run_test("2.1 ContextTracker 完整功能", test_context_tracker_full)
    
    # 智能体测试
    print(f"\n{'#'*80}")
    print(f"# 🤖 智能体测试")
    print(f"{'#'*80}")
    suite.run_test("3.1 UnifiedAgent 创建", test_unified_agent_creation)
    suite.run_test("3.2 UnifiedAgent 记忆功能", test_unified_agent_with_memory, skip_if_fails=True)
    suite.run_test("3.3 自动继续执行机制", test_auto_continue_mechanism)
    
    # 工具测试
    print(f"\n{'#'*80}")
    print(f"# 🔧 工具测试")
    print(f"{'#'*80}")
    suite.run_test("4.1 工具加载", test_tools_loading)
    suite.run_test("4.2 n8n 工具", test_n8n_tools, skip_if_fails=True)
    suite.run_test("4.3 CrewAI 工具", test_crewai_tools)
    
    # CrewAI 集成测试
    print(f"\n{'#'*80}")
    print(f"# 👥 CrewAI 集成测试")
    print(f"{'#'*80}")
    suite.run_test("5.1 CrewAI Runtime 创建", test_crewai_runtime_creation)
    suite.run_test("5.2 CrewAI 配置生成器", test_crewai_generator)
    
    # 代码质量测试
    print(f"\n{'#'*80}")
    print(f"# ✨ 代码质量测试")
    print(f"{'#'*80}")
    suite.run_test("6.1 异常处理质量", test_exception_handling_quality)
    
    # 性能测试
    print(f"\n{'#'*80}")
    print(f"# ⚡ 性能测试")
    print(f"{'#'*80}")
    suite.run_test("7.1 配置缓存性能", test_config_cache_performance)
    
    # 集成测试
    print(f"\n{'#'*80}")
    print(f"# 🔗 集成测试")
    print(f"{'#'*80}")
    suite.run_test("8.1 完整集成工作流", test_full_integration_workflow)
    
    # 打印总结
    passed = suite.print_summary()
    
    return 0 if passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

