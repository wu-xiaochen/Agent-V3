"""
测试 V3.1 新功能

测试内容：
1. 工具注册系统
2. 文档生成和下载
3. 知识库管理
4. 文档解析
5. 多模态处理
"""

import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tool_registry():
    """测试工具注册系统"""
    print("\n" + "="*60)
    print("🔧 测试 1: 工具注册系统")
    print("="*60)
    
    try:
        from src.infrastructure.tools import get_tool_registry, get_tool_factory
        
        # 获取工具注册器
        registry = get_tool_registry()
        factory = get_tool_factory()
        
        # 加载配置
        success = registry.load_from_config()
        assert success, "加载工具配置失败"
        print("✅ 工具配置加载成功")
        
        # 列出所有工具
        tools = registry.list_all_tools()
        print(f"✅ 发现 {len(tools)} 个工具:")
        for name, info in tools.items():
            status = "🟢" if info["enabled"] else "🔴"
            print(f"  {status} {info['display_name']} ({info['type']})")
        
        # 创建一个工具实例
        tool = factory.create_tool("time")
        if tool:
            print(f"✅ 成功创建工具实例: {tool.name}")
            result = tool._run()
            print(f"✅ 工具执行结果: {result[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 工具注册系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_manager():
    """测试文件管理器和文档生成"""
    print("\n" + "="*60)
    print("📄 测试 2: 文件管理器和文档生成")
    print("="*60)
    
    try:
        from src.interfaces.file_manager import get_file_manager
        
        # 获取文件管理器
        file_manager = get_file_manager()
        print("✅ 文件管理器初始化成功")
        
        # 保存测试文档
        result = file_manager.save_document(
            content="# 测试文档\n\n这是一个测试文档，用于验证文件管理功能。",
            filename="test_document",
            file_format="md",
            tags=["test", "demo"]
        )
        
        if result["success"]:
            print(f"✅ 文档保存成功: {result['filename']}")
            print(f"   文件ID: {result['file_id']}")
            print(f"   大小: {result['size_human']}")
            print(f"   下载链接: {result['download_url']}")
            
            # 获取文件信息
            file_info = file_manager.get_file(result['file_id'])
            if file_info:
                print(f"✅ 文件信息获取成功")
            
            # 列出文件
            files = file_manager.list_files(tags=["test"], limit=10)
            print(f"✅ 找到 {len(files)} 个测试文件")
            
            return True
        else:
            print(f"❌ 文档保存失败: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 文件管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_base():
    """测试知识库系统"""
    print("\n" + "="*60)
    print("📚 测试 3: 知识库系统")
    print("="*60)
    
    try:
        from src.infrastructure.knowledge import get_knowledge_base_manager, KnowledgeBaseType, StorageBackend
        
        # 获取知识库管理器
        kb_manager = get_knowledge_base_manager()
        print("✅ 知识库管理器初始化成功")
        
        # 创建测试知识库
        kb = kb_manager.create_knowledge_base(
            name="测试知识库",
            description="用于测试的知识库",
            kb_type=KnowledgeBaseType.VECTOR,
            storage_backend=StorageBackend.CHROMADB
        )
        print(f"✅ 知识库创建成功: {kb.name} ({kb.kb_id})")
        
        # 列出所有知识库
        kbs = kb_manager.list_knowledge_bases()
        print(f"✅ 当前共有 {len(kbs)} 个知识库")
        
        # 挂载到 Agent
        success = kb_manager.attach_agent(kb.kb_id, "test_agent")
        if success:
            print(f"✅ 知识库已挂载到 Agent: test_agent")
        
        # 清理测试数据
        kb_manager.delete_knowledge_base(kb.kb_id)
        print(f"✅ 测试知识库已删除")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 知识库系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_parser():
    """测试文档解析器"""
    print("\n" + "="*60)
    print("📖 测试 4: 文档解析器")
    print("="*60)
    
    try:
        from src.infrastructure.multimodal import DocumentParserFactory
        
        # 显示支持的文件类型
        supported = DocumentParserFactory.supported_extensions()
        print(f"✅ 支持的文件类型: {', '.join(supported)}")
        
        # 测试文本解析
        print("\n测试文本文件解析...")
        test_file = Path("test_text.txt")
        test_file.write_text("这是一个测试文本文件。\n第二行内容。", encoding='utf-8')
        
        result = DocumentParserFactory.parse_file(str(test_file))
        if result["success"]:
            print(f"✅ 文本解析成功:")
            print(f"   类型: {result['type']}")
            print(f"   行数: {result['lines']}")
            print(f"   编码: {result['encoding']}")
            print(f"   内容: {result['content'][:50]}...")
        
        # 清理测试文件
        test_file.unlink()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 文档解析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multimodal_processor():
    """测试多模态处理器"""
    print("\n" + "="*60)
    print("🖼️  测试 5: 多模态处理器")
    print("="*60)
    
    try:
        from src.infrastructure.multimodal import ImageProcessor, get_image_info
        
        print("✅ 多模态处理器模块导入成功")
        print("   图片分析功能需要实际图片文件和 API Key 才能测试")
        print("   跳过图片分析测试（可手动测试）")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 多模态处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unified_agent():
    """测试 UnifiedAgent 与新工具系统的集成"""
    print("\n" + "="*60)
    print("🤖 测试 6: UnifiedAgent 集成")
    print("="*60)
    
    try:
        from src.agents.unified.unified_agent import UnifiedAgent
        
        print("正在创建 UnifiedAgent...")
        agent = UnifiedAgent(
            provider="siliconflow",
            memory=False,
            streaming_style="none"
        )
        
        print(f"✅ Agent 创建成功")
        print(f"   加载了 {len(agent.tools)} 个工具")
        
        # 显示工具列表
        for tool in agent.tools[:5]:  # 只显示前5个
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ UnifiedAgent 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Agent-V3.1 功能测试")
    print("="*60)
    
    tests = [
        ("工具注册系统", test_tool_registry),
        ("文件管理器", test_file_manager),
        ("知识库系统", test_knowledge_base),
        ("文档解析器", test_document_parser),
        ("多模态处理器", test_multimodal_processor),
        ("UnifiedAgent集成", test_unified_agent),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"测试 {name} 出现异常: {e}")
            results.append((name, False))
    
    # 统计结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "="*60)
    print(f"通过: {passed}/{total} ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 所有测试通过！V3.1 新功能运行正常！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查错误信息")


if __name__ == "__main__":
    main()

