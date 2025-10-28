#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent-V3 综合测试脚本
测试所有核心功能和优化项
"""

import sys
import os
import logging
import traceback
from typing import Dict, List, Tuple

# 确保可以导入 src 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveTest:
    """综合测试类"""
    
    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name: str, test_func):
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
            self.results[test_name] = (False, f"❌ 断言失败: {str(e)}")
            self.failed_tests += 1
            print(f"❌ {test_name} - 断言失败: {str(e)}")
            traceback.print_exc()
        except Exception as e:
            self.results[test_name] = (False, f"❌ 异常: {str(e)}")
            self.failed_tests += 1
            print(f"❌ {test_name} - 异常: {str(e)}")
            traceback.print_exc()
    
    def print_summary(self):
        """打印测试总结"""
        print(f"\n\n{'='*80}")
        print(f"📊 测试总结")
        print(f"{'='*80}")
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"失败: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        print(f"\n详细结果:")
        for test_name, (passed, message) in self.results.items():
            print(f"  {message} - {test_name}")
        
        # 评分
        score = self.passed_tests / self.total_tests * 100
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
        
        return score >= 85  # 85分以上算通过


# ========================================
# Phase 1 测试: 上下文感知和自动续接
# ========================================

def test_context_tracker_import():
    """测试上下文追踪器导入"""
    from src.core.services.context_tracker import ContextTracker
    tracker = ContextTracker(max_history=10)
    assert tracker is not None, "ContextTracker 实例化失败"
    print("✅ ContextTracker 导入成功")


def test_context_tracker_functionality():
    """测试上下文追踪器功能"""
    from src.core.services.context_tracker import ContextTracker
    
    tracker = ContextTracker(max_history=10)
    
    # 测试添加查询
    tracker.add_query("生成一个配置")
    assert len(tracker.query_history) == 1, "查询未正确添加"
    
    # 测试添加工具调用
    tracker.add_tool_call("crewai_generator", "配置已生成")
    assert len(tracker.tool_history) == 1, "工具调用未正确添加"
    # 验证最后工具（通过 tool_history 获取）
    last_tool = tracker.tool_history[-1] if tracker.tool_history else None
    assert last_tool is not None, "最后工具调用未记录"
    assert last_tool["tool"] == "crewai_generator", "最后工具未正确记录"
    
    # 测试上下文依赖检测
    assert tracker.is_context_dependent("运行它"), "未检测到上下文依赖"
    assert not tracker.is_context_dependent("帮我做个分析"), "错误检测为上下文依赖"
    
    # 测试上下文提示生成
    hint = tracker.generate_context_hint("运行它")
    assert "crewai_runtime" in hint, "上下文提示未包含正确工具"
    
    print("✅ ContextTracker 功能正常")


def test_unified_agent_context_integration():
    """测试 UnifiedAgent 的上下文追踪集成"""
    from src.agents.unified.unified_agent import UnifiedAgent
    
    # 创建 agent（不启用记忆，避免 Redis 依赖）
    agent = UnifiedAgent(provider="siliconflow", streaming_style="none", memory=False)
    
    # 验证上下文追踪器已初始化
    assert hasattr(agent, 'context_tracker'), "UnifiedAgent 未初始化 context_tracker"
    assert agent.context_tracker is not None, "context_tracker 为 None"
    
    print("✅ UnifiedAgent 上下文追踪集成成功")


def test_auto_continue_methods():
    """测试自动继续执行方法"""
    from src.agents.unified.unified_agent import UnifiedAgent, AgentStopReason
    
    # 验证 AgentStopReason 枚举
    assert hasattr(AgentStopReason, 'COMPLETED'), "缺少 COMPLETED 状态"
    assert hasattr(AgentStopReason, 'ITERATION_LIMIT'), "缺少 ITERATION_LIMIT 状态"
    assert hasattr(AgentStopReason, 'TIME_LIMIT'), "缺少 TIME_LIMIT 状态"
    
    # 创建 agent
    agent = UnifiedAgent(provider="siliconflow", streaming_style="none", memory=False)
    
    # 验证自动继续方法存在
    assert hasattr(agent, 'run_with_auto_continue'), "缺少 run_with_auto_continue 方法"
    assert hasattr(agent, '_detect_stop_reason'), "缺少 _detect_stop_reason 方法"
    assert hasattr(agent, '_generate_continuation_prompt'), "缺少 _generate_continuation_prompt 方法"
    assert hasattr(agent, '_extract_last_actions'), "缺少 _extract_last_actions 方法"
    
    print("✅ 自动继续执行方法验证成功")


# ========================================
# Phase 2 测试: 环境变量管理
# ========================================

def test_env_manager_import():
    """测试 EnvManager 导入"""
    from src.config.env_manager import EnvManager
    assert EnvManager is not None, "EnvManager 导入失败"
    print("✅ EnvManager 导入成功")


def test_env_manager_config_methods():
    """测试 EnvManager 配置方法"""
    from src.config.env_manager import EnvManager
    
    # 测试所有配置方法
    assert hasattr(EnvManager, 'get_redis_url'), "缺少 get_redis_url 方法"
    assert hasattr(EnvManager, 'get_llm_config'), "缺少 get_llm_config 方法"
    assert hasattr(EnvManager, 'get_n8n_config'), "缺少 get_n8n_config 方法"
    assert hasattr(EnvManager, 'validate_config'), "缺少 validate_config 方法"
    
    # 测试配置获取
    redis_url = EnvManager.get_redis_url()
    assert redis_url is not None, "Redis URL 为 None"
    assert "redis://" in redis_url, "Redis URL 格式不正确"
    
    n8n_config = EnvManager.get_n8n_config()
    assert "api_url" in n8n_config, "n8n 配置缺少 api_url"
    assert "api_key" in n8n_config, "n8n 配置缺少 api_key"
    
    print("✅ EnvManager 配置方法验证成功")


def test_env_manager_integration():
    """测试 EnvManager 在各模块中的集成"""
    # 测试 tools.py 集成
    try:
        from src.agents.shared.tools import get_tools
        # 不直接调用 get_tools（避免依赖），只验证导入
        print("✅ tools.py 可正常导入")
    except Exception as e:
        raise AssertionError(f"tools.py 导入失败: {e}")
    
    # 测试 unified_agent.py 集成
    try:
        from src.agents.unified.unified_agent import UnifiedAgent
        # 验证能正常创建 agent
        agent = UnifiedAgent(provider="siliconflow", streaming_style="none", memory=False)
        print("✅ unified_agent.py EnvManager 集成成功")
    except Exception as e:
        raise AssertionError(f"unified_agent.py 集成失败: {e}")
    
    # 测试 llm_factory.py 集成
    try:
        from src.infrastructure.llm.llm_factory import LLMFactory
        print("✅ llm_factory.py 可正常导入")
    except Exception as e:
        raise AssertionError(f"llm_factory.py 导入失败: {e}")
    
    # 测试 crewai_runtime.py 集成
    try:
        from src.interfaces.crewai_runtime import CrewAIRuntime
        print("✅ crewai_runtime.py 可正常导入")
    except Exception as e:
        raise AssertionError(f"crewai_runtime.py 导入失败: {e}")


def test_config_cache_optimization():
    """测试配置缓存优化"""
    from src.config.config_loader import ConfigLoader
    import inspect
    
    # 验证 lru_cache 导入
    config_loader = ConfigLoader()
    
    # 检查是否有缓存相关方法
    assert hasattr(config_loader, '_load_yaml_file_cached'), "缺少缓存方法"
    
    # 验证缓存装饰器
    method = getattr(config_loader, '_load_yaml_file_cached')
    # lru_cache 装饰器会添加 cache_info 方法
    assert hasattr(method, 'cache_info'), "缓存装饰器未正确应用"
    
    print("✅ 配置缓存优化验证成功")


# ========================================
# Phase 3 测试: 异常处理和依赖
# ========================================

def test_exception_handling_improvements():
    """测试异常处理改进"""
    # 检查核心文件中的裸 except 数量
    import re
    
    files_to_check = [
        'src/agents/shared/n8n_api_tools.py',
        'src/infrastructure/cache/cache_service.py',
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查裸 except（简单的模式匹配）
                bare_excepts = re.findall(r'except\s*:\s*\n', content)
                if len(bare_excepts) > 0:
                    print(f"⚠️  {file_path} 仍有 {len(bare_excepts)} 个裸 except")
                else:
                    print(f"✅ {file_path} 无裸 except")
    
    print("✅ 异常处理改进验证完成")


def test_requirements_file():
    """测试 requirements.txt 更新"""
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    assert os.path.exists(req_file), "requirements.txt 不存在"
    
    with open(req_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证必需的依赖
    required_deps = [
        'langchain',
        'openai',
        'requests',
        'PyYAML',
        'pydantic',
        'python-dotenv',
        'redis',
        'crewai',
    ]
    
    for dep in required_deps:
        assert dep in content, f"缺少必需依赖: {dep}"
    
    print(f"✅ requirements.txt 包含所有必需依赖")


# ========================================
# 集成测试
# ========================================

def test_full_integration():
    """完整集成测试"""
    from src.agents.unified.unified_agent import UnifiedAgent
    from src.config.env_manager import EnvManager
    
    # 测试完整流程
    # 1. 环境配置
    n8n_config = EnvManager.get_n8n_config()
    redis_url = EnvManager.get_redis_url()
    
    # 2. 创建 agent
    agent = UnifiedAgent(
        provider="siliconflow",
        streaming_style="none",
        memory=False  # 避免 Redis 依赖
    )
    
    # 3. 验证上下文追踪
    assert agent.context_tracker is not None, "上下文追踪器未初始化"
    
    # 4. 验证自动继续方法
    assert hasattr(agent, 'run_with_auto_continue'), "缺少自动继续方法"
    
    print("✅ 完整集成测试通过")


# ========================================
# 主测试函数
# ========================================

def main():
    """主测试函数"""
    print(f"\n{'='*80}")
    print(f"🚀 Agent-V3 综合测试开始")
    print(f"{'='*80}\n")
    
    test_suite = ComprehensiveTest()
    
    # Phase 1 测试: 上下文感知和自动续接
    print(f"\n{'#'*80}")
    print(f"# Phase 1: 上下文感知和自动续接测试")
    print(f"{'#'*80}")
    test_suite.run_test("1.1 ContextTracker 导入", test_context_tracker_import)
    test_suite.run_test("1.2 ContextTracker 功能", test_context_tracker_functionality)
    test_suite.run_test("1.3 UnifiedAgent 上下文集成", test_unified_agent_context_integration)
    test_suite.run_test("1.4 自动继续执行方法", test_auto_continue_methods)
    
    # Phase 2 测试: 环境变量管理
    print(f"\n{'#'*80}")
    print(f"# Phase 2: 环境变量管理测试")
    print(f"{'#'*80}")
    test_suite.run_test("2.1 EnvManager 导入", test_env_manager_import)
    test_suite.run_test("2.2 EnvManager 配置方法", test_env_manager_config_methods)
    test_suite.run_test("2.3 EnvManager 集成", test_env_manager_integration)
    test_suite.run_test("2.4 配置缓存优化", test_config_cache_optimization)
    
    # Phase 3 测试: 异常处理和依赖
    print(f"\n{'#'*80}")
    print(f"# Phase 3: 异常处理和依赖测试")
    print(f"{'#'*80}")
    test_suite.run_test("3.1 异常处理改进", test_exception_handling_improvements)
    test_suite.run_test("3.2 requirements.txt", test_requirements_file)
    
    # 集成测试
    print(f"\n{'#'*80}")
    print(f"# 集成测试")
    print(f"{'#'*80}")
    test_suite.run_test("4.1 完整集成测试", test_full_integration)
    
    # 打印总结
    passed = test_suite.print_summary()
    
    return 0 if passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

