#!/usr/bin/env python3
"""
Agent-V3 前端功能自动化测试脚本

测试所有前端功能和后端API集成
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime


class Color:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class FrontendTester:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        self.failed_tests = []
    
    def print_header(self, text: str):
        """打印测试头部"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{text:^60}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}\n")
    
    def print_test(self, name: str, passed: bool, message: str = ""):
        """打印测试结果"""
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            symbol = f"{Color.GREEN}✓{Color.RESET}"
            status = f"{Color.GREEN}PASS{Color.RESET}"
        else:
            self.results["failed"] += 1
            symbol = f"{Color.RED}✗{Color.RESET}"
            status = f"{Color.RED}FAIL{Color.RESET}"
            self.failed_tests.append((name, message))
        
        print(f"{symbol} [{status}] {name}")
        if message:
            print(f"  └─ {message}")
    
    def test_backend_health(self) -> bool:
        """测试后端健康状态"""
        self.print_header("后端健康检查")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            data = response.json()
            
            # 检查状态
            health_ok = data.get("status") == "healthy"
            self.print_test(
                "后端服务状态",
                health_ok,
                f"状态: {data.get('status')}"
            )
            
            # 检查文件管理器
            fm_ok = data.get("file_manager") == "ok"
            self.print_test(
                "文件管理器状态",
                fm_ok,
                f"文件管理器: {data.get('file_manager')}"
            )
            
            # 显示会话信息
            print(f"\n  📊 活动会话: {data.get('active_sessions', 0)}")
            print(f"  📊 WebSocket连接: {data.get('active_websockets', 0)}")
            
            return health_ok and fm_ok
            
        except Exception as e:
            self.print_test("后端健康检查", False, str(e))
            return False
    
    def test_session_management(self):
        """测试会话管理功能"""
        self.print_header("会话管理测试")
        
        # 1. 列出会话
        try:
            response = requests.get(f"{self.backend_url}/api/chat/sessions")
            data = response.json()
            
            self.print_test(
                "获取会话列表",
                data.get("success", False),
                f"会话数: {data.get('count', 0)}"
            )
            
            initial_count = data.get("count", 0)
            
        except Exception as e:
            self.print_test("获取会话列表", False, str(e))
            return
        
        # 2. 创建新会话（通过发送消息）
        test_session_id = f"test-session-{int(time.time())}"
        try:
            response = requests.post(
                f"{self.backend_url}/api/chat/message",
                json={
                    "session_id": test_session_id,
                    "message": "测试消息",
                    "provider": "siliconflow",
                    "memory": True,
                    "streaming": False
                },
                timeout=30
            )
            data = response.json()
            
            create_ok = data.get("success", False)
            self.print_test(
                "创建新会话",
                create_ok,
                f"会话ID: {test_session_id}" if create_ok else data.get("response", "")
            )
            
            if create_ok:
                # 验证消息响应
                has_response = bool(data.get("response"))
                self.print_test(
                    "AI消息响应",
                    has_response,
                    f"响应长度: {len(data.get('response', ''))} 字符"
                )
            
        except Exception as e:
            self.print_test("创建新会话", False, str(e))
            test_session_id = None
        
        # 3. 再次列出会话，验证新会话
        try:
            response = requests.get(f"{self.backend_url}/api/chat/sessions")
            data = response.json()
            
            new_count = data.get("count", 0)
            increased = new_count > initial_count
            
            self.print_test(
                "会话列表更新",
                increased,
                f"会话数从 {initial_count} 增加到 {new_count}"
            )
            
        except Exception as e:
            self.print_test("验证会话列表", False, str(e))
        
        # 4. 删除测试会话
        if test_session_id:
            try:
                response = requests.delete(
                    f"{self.backend_url}/api/chat/sessions/{test_session_id}"
                )
                data = response.json()
                
                delete_ok = data.get("success", False)
                self.print_test(
                    "删除会话",
                    delete_ok,
                    data.get("message", "")
                )
                
            except Exception as e:
                self.print_test("删除会话", False, str(e))
    
    def test_tools_api(self):
        """测试工具API"""
        self.print_header("工具配置测试")
        
        try:
            response = requests.get(f"{self.backend_url}/api/tools/list")
            data = response.json()
            
            # 检查基本响应
            self.print_test(
                "获取工具列表",
                data.get("success", False),
                f"工具数: {data.get('count', 0)}"
            )
            
            if data.get("success"):
                tools = data.get("tools", {})
                
                # 统计工具类型
                types = {}
                enabled_count = 0
                disabled_count = 0
                
                for name, tool in tools.items():
                    tool_type = tool.get("type", "unknown")
                    types[tool_type] = types.get(tool_type, 0) + 1
                    
                    if tool.get("enabled"):
                        enabled_count += 1
                    else:
                        disabled_count += 1
                
                # 显示统计
                print(f"\n  📊 工具统计:")
                print(f"    - 总数: {len(tools)}")
                print(f"    - 启用: {enabled_count}")
                print(f"    - 禁用: {disabled_count}")
                print(f"\n  📊 工具类型分布:")
                for t, count in types.items():
                    print(f"    - {t}: {count}")
                
                # 验证每个工具的必要字段
                all_valid = True
                for name, tool in tools.items():
                    required_fields = ["display_name", "type", "enabled", "description"]
                    missing = [f for f in required_fields if f not in tool]
                    if missing:
                        all_valid = False
                        print(f"  ⚠️  工具 '{name}' 缺少字段: {', '.join(missing)}")
                
                self.print_test(
                    "工具数据完整性",
                    all_valid,
                    "所有工具包含必要字段" if all_valid else "部分工具数据不完整"
                )
                
        except Exception as e:
            self.print_test("获取工具列表", False, str(e))
    
    def test_file_operations(self):
        """测试文件操作"""
        self.print_header("文件管理测试")
        
        # 1. 创建测试文件
        test_content = f"测试文件内容\n创建时间: {datetime.now()}"
        
        try:
            files = {
                'file': ('test.txt', test_content, 'text/plain')
            }
            data = {
                'file_type': 'data'
            }
            
            response = requests.post(
                f"{self.backend_url}/api/files/upload",
                files=files,
                data=data,
                timeout=10
            )
            result = response.json()
            
            upload_ok = result.get("success", False)
            self.print_test(
                "文件上传",
                upload_ok,
                f"文件ID: {result.get('file_id', 'N/A')}, 大小: {result.get('size', 0)} 字节"
            )
            
            if upload_ok:
                file_id = result.get("file_id")
                download_url = result.get("download_url")
                
                # 验证下载链接
                has_download = bool(download_url)
                self.print_test(
                    "下载链接生成",
                    has_download,
                    f"URL: {download_url}"
                )
                
                # 2. 测试文件列表
                try:
                    response = requests.get(f"{self.backend_url}/api/files/list")
                    list_data = response.json()
                    
                    list_ok = list_data.get("success", False)
                    self.print_test(
                        "获取文件列表",
                        list_ok,
                        f"文件数: {list_data.get('count', 0)}"
                    )
                    
                except Exception as e:
                    self.print_test("获取文件列表", False, str(e))
                
                # 3. 测试文件删除
                if file_id:
                    try:
                        response = requests.delete(
                            f"{self.backend_url}/api/files/{file_id}"
                        )
                        delete_data = response.json()
                        
                        delete_ok = delete_data.get("success", False)
                        self.print_test(
                            "删除文件",
                            delete_ok,
                            delete_data.get("message", "")
                        )
                        
                    except Exception as e:
                        self.print_test("删除文件", False, str(e))
            
        except Exception as e:
            self.print_test("文件上传", False, str(e))
    
    def test_api_endpoints(self):
        """测试所有API端点"""
        self.print_header("API端点测试")
        
        endpoints = [
            ("GET", "/api/health", "健康检查"),
            ("GET", "/api/chat/sessions", "会话列表"),
            ("GET", "/api/tools/list", "工具列表"),
            ("GET", "/api/files/list", "文件列表"),
        ]
        
        for method, path, name in endpoints:
            try:
                url = f"{self.backend_url}{path}"
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.request(method, url, timeout=5)
                
                ok = response.status_code == 200
                self.print_test(
                    f"{name} ({method} {path})",
                    ok,
                    f"状态码: {response.status_code}"
                )
                
            except Exception as e:
                self.print_test(f"{name}", False, str(e))
    
    def test_cors_headers(self):
        """测试CORS配置"""
        self.print_header("CORS配置测试")
        
        try:
            response = requests.options(
                f"{self.backend_url}/api/health",
                headers={"Origin": "http://localhost:3000"}
            )
            
            has_cors = "access-control-allow-origin" in [
                h.lower() for h in response.headers.keys()
            ]
            
            self.print_test(
                "CORS头部配置",
                has_cors,
                "允许跨域访问" if has_cors else "未配置CORS"
            )
            
        except Exception as e:
            self.print_test("CORS配置", False, str(e))
    
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"{Color.GREEN}通过: {passed}{Color.RESET}")
        print(f"{Color.RED}失败: {failed}{Color.RESET}")
        print(f"通过率: {pass_rate:.1f}%")
        
        if failed > 0:
            print(f"\n{Color.RED}{Color.BOLD}失败的测试:{Color.RESET}")
            for name, message in self.failed_tests:
                print(f"  {Color.RED}✗{Color.RESET} {name}")
                if message:
                    print(f"    {message}")
        
        print(f"\n{Color.BLUE}{'='*60}{Color.RESET}\n")
        
        # 返回是否全部通过
        return failed == 0


def main():
    """主函数"""
    print(f"\n{Color.BOLD}{Color.BLUE}Agent-V3 前端功能自动化测试{Color.RESET}")
    print(f"{Color.BLUE}测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.RESET}\n")
    
    tester = FrontendTester()
    
    # 1. 检查后端健康状态
    if not tester.test_backend_health():
        print(f"\n{Color.RED}错误: 后端服务未运行或不健康{Color.RESET}")
        print(f"{Color.YELLOW}请确保后端服务已启动: python api_server.py{Color.RESET}\n")
        return False
    
    # 2. 运行所有测试
    tester.test_session_management()
    tester.test_tools_api()
    tester.test_file_operations()
    tester.test_api_endpoints()
    tester.test_cors_headers()
    
    # 3. 打印总结
    all_passed = tester.print_summary()
    
    if all_passed:
        print(f"{Color.GREEN}{Color.BOLD}🎉 所有测试通过！{Color.RESET}\n")
        return True
    else:
        print(f"{Color.YELLOW}⚠️  部分测试失败，请检查上述错误信息{Color.RESET}\n")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

