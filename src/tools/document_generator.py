"""
文档生成工具 - 生成文档并自动提供下载链接
"""

import logging
from typing import Optional
from langchain.tools import BaseTool
from pydantic import Field
from src.interfaces.file_manager import get_file_manager

logger = logging.getLogger(__name__)


class DocumentGeneratorTool(BaseTool):
    """
    文档生成工具
    
    生成 Markdown 文档并自动提供下载链接
    """
    
    name: str = "generate_document"
    description: str = """生成文档工具 - 创建 Markdown 格式的文档
    
    使用场景：
    - 生成报告、分析文档
    - 保存会议纪要
    - 创建知识文档
    
    参数：
    - title: 文档标题
    - content: 文档内容（Markdown格式）
    - filename: 文件名（可选，不含扩展名）
    - tags: 文档标签列表（可选）
    
    返回：包含下载链接的文档信息
    """
    
    file_manager: Optional[any] = Field(default=None, description="文件管理器实例")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.file_manager is None:
            self.file_manager = get_file_manager()
    
    def _run(
        self,
        title: str,
        content: str,
        filename: Optional[str] = None,
        tags: Optional[str] = None
    ) -> str:
        """
        生成文档
        
        Args:
            title: 文档标题
            content: 文档内容
            filename: 文件名（可选）
            tags: 标签（逗号分隔的字符串）
            
        Returns:
            文档信息（包含下载链接）
        """
        try:
            # 构建完整的 Markdown 文档
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            markdown_content = f"""# {title}

**生成时间**: {current_time}

---

{content}

---
*本文档由 AI Agent 自动生成*
"""
            
            # 处理标签
            tag_list = None
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            
            # 保存文档
            result = self.file_manager.save_document(
                content=markdown_content,
                filename=filename or title.replace(" ", "_").lower(),
                file_format="md",
                tags=tag_list,
                ttl_days=90  # 文档保留90天
            )
            
            if result["success"]:
                logger.info(f"✅ 文档生成成功: {result['filename']}")
                
                # 返回格式化的信息
                return f"""📄 **文档已生成**

**文件名**: {result['filename']}
**大小**: {result['size_human']}
**创建时间**: {result['created_at']}

**下载链接**: {result['download_url']}

💡 提示：点击上方链接即可下载文档
"""
            else:
                error_msg = result.get("error", "未知错误")
                logger.error(f"❌ 文档生成失败: {error_msg}")
                return f"❌ 文档生成失败: {error_msg}"
                
        except Exception as e:
            logger.error(f"❌ 文档生成过程出错: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return f"❌ 文档生成过程出错: {str(e)}"
    
    async def _arun(self, title: str, content: str, filename: Optional[str] = None, tags: Optional[str] = None) -> str:
        """异步执行"""
        return self._run(title, content, filename, tags)


def create_document_generator_tool():
    """创建文档生成工具实例"""
    return DocumentGeneratorTool()

