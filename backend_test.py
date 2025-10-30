#!/usr/bin/env python3
"""
后端自动化测试脚本
验证API端点、数据库连接、工具功能
"""

import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

class BackendAutoTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
        
    def log(self, emoji: str, title: str, status: str, detail: str = "") -> bool:
        """记录测试结果"""
        result = {
            "title": title,
            "status": status,
            "detail": detail
        }
        self.results.append(result)
        print(f"{emoji} [{status}] {title}{': ' + detail if detail else ''}")
        return status == "PASS"
    
    async def test_api_health(self) -> bool:
        """测试1: API健康检查"""
        print("\n━━━ 测试1: API健康检查 ━━━")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self.log("✅", "API健康检查", "PASS", f"状态: {data.get('status', 'unknown')}")
                    else:
                        return self.log("❌", "API健康检查", "FAIL", f"HTTP {resp.status}")
        except Exception as e:
            return self.log("❌", "API健康检查", "FAIL", str(e))
    
    async def test_crewai_endpoints(self) -> bool:
        """测试2: CrewAI端点"""
        print("\n━━━ 测试2: CrewAI端点 ━━━")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 测试获取crews列表
                async with session.get(f"{self.base_url}/api/crewai/crews") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        crew_count = len(data.get("crews", []))
                        return self.log("✅", "CrewAI端点", "PASS", f"获取到{crew_count}个crew")
                    else:
                        return self.log("❌", "CrewAI端点", "FAIL", f"HTTP {resp.status}")
        except Exception as e:
            return self.log("❌", "CrewAI端点", "FAIL", str(e))
    
    async def test_thinking_chain_api(self) -> bool:
        """测试3: 思维链API"""
        print("\n━━━ 测试3: 思维链API ━━━")
        
        try:
            # 创建测试消息ID
            test_msg_id = "test-msg-123"
            
            async with aiohttp.ClientSession() as session:
                # 测试获取思维链
                async with session.get(
                    f"{self.base_url}/api/thinking-chain/{test_msg_id}"
                ) as resp:
                    if resp.status in [200, 404]:  # 404也是正常的（没有数据）
                        if resp.status == 200:
                            data = await resp.json()
                            step_count = len(data.get("thinking_chain", []))
                            return self.log("✅", "思维链API", "PASS", f"{step_count}个步骤")
                        else:
                            return self.log("✅", "思维链API", "PASS", "API正常（无数据）")
                    else:
                        return self.log("❌", "思维链API", "FAIL", f"HTTP {resp.status}")
        except Exception as e:
            return self.log("❌", "思维链API", "FAIL", str(e))
    
    def test_project_structure(self) -> bool:
        """测试4: 项目结构"""
        print("\n━━━ 测试4: 项目结构 ━━━")
        
        required_dirs = [
            "src/agents",
            "src/tools",
            "frontend/components",
            "frontend/lib",
            "data",
            "config"
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing.append(dir_path)
        
        if missing:
            return self.log("❌", "项目结构", "FAIL", f"缺少目录: {', '.join(missing)}")
        else:
            return self.log("✅", "项目结构", "PASS", f"{len(required_dirs)}个关键目录存在")
    
    def test_data_persistence(self) -> bool:
        """测试5: 数据持久化"""
        print("\n━━━ 测试5: 数据持久化 ━━━")
        
        data_dir = Path("data")
        if not data_dir.exists():
            return self.log("❌", "数据持久化", "FAIL", "data目录不存在")
        
        # 检查关键数据文件
        db_file = data_dir / "crewai_configs.db"
        kb_dir = data_dir / "knowledge_bases"
        crews_dir = data_dir / "crews"
        
        files_found = []
        if db_file.exists():
            files_found.append("数据库")
        if kb_dir.exists():
            files_found.append("知识库")
        if crews_dir.exists():
            crew_files = list(crews_dir.glob("*.json"))
            files_found.append(f"{len(crew_files)}个crew配置")
        
        if files_found:
            return self.log("✅", "数据持久化", "PASS", ", ".join(files_found))
        else:
            return self.log("⚠️", "数据持久化", "SKIP", "没有数据文件")
    
    async def run_all(self):
        """运行所有测试"""
        print("🚀 开始后端自动化测试...\n")
        print("=" * 50)
        
        self.results = []
        
        # API测试（异步）
        await self.test_api_health()
        await asyncio.sleep(0.5)
        
        await self.test_crewai_endpoints()
        await asyncio.sleep(0.5)
        
        await self.test_thinking_chain_api()
        await asyncio.sleep(0.5)
        
        # 本地测试（同步）
        self.test_project_structure()
        await asyncio.sleep(0.5)
        
        self.test_data_persistence()
        
        # 汇总报告
        print("\n" + "=" * 50)
        print("📊 测试汇总报告\n")
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")
        
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⚠️ 跳过: {skipped}")
        print(f"📝 总计: {len(self.results)}")
        
        if passed + failed > 0:
            success_rate = (passed / (passed + failed)) * 100
            print(f"\n成功率: {success_rate:.1f}%")
        
        print("\n" + "=" * 50)
        
        return {
            "summary": {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": len(self.results)
            },
            "details": self.results
        }

if __name__ == "__main__":
    tester = BackendAutoTest()
    result = asyncio.run(tester.run_all())
    
    # 如果有失败，退出码为1
    sys.exit(0 if result["summary"]["failed"] == 0 else 1)

