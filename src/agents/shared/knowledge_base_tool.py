"""
知识库搜索工具 - 供CrewAI Agent使用
"""

import logging
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class KnowledgeBaseSearchToolSchema(BaseModel):
    """知识库搜索工具参数Schema"""
    query: str = Field(..., description="搜索查询词")
    kb_id: Optional[str] = Field(None, description="知识库ID，如果未指定则使用默认知识库")
    top_k: int = Field(5, description="返回结果数量，默认5条")


class KnowledgeBaseSearchTool(BaseTool):
    """
    知识库搜索工具
    
    允许CrewAI Agent在知识库中搜索相关信息
    """
    
    name: str = "knowledge_base_search"
    description: str = """在知识库中搜索相关信息。
    
    使用场景：
    - 需要查找已上传的文档内容
    - 需要获取特定主题的相关信息
    - 需要引用知识库中的知识来回答问题
    
    参数：
    - query: 搜索查询词（必需）
    - kb_id: 知识库ID（可选，如果未指定则使用第一个可用知识库）
    - top_k: 返回结果数量（可选，默认5条）
    
    返回：相关文档片段列表，包含内容和相似度分数
    """
    
    args_schema: Type[BaseModel] = KnowledgeBaseSearchToolSchema
    kb_id: Optional[str] = Field(default=None, description="知识库ID")
    
    def __init__(self, kb_id: Optional[str] = None, **kwargs):
        """初始化知识库搜索工具"""
        super().__init__(**kwargs)
        self.kb_id = kb_id
        if kb_id:
            # 更新工具名称以包含知识库ID
            self.name = f"knowledge_base_search_{kb_id}"
            self.description = f"""在知识库 (ID: {kb_id}) 中搜索相关信息。
            
使用场景：
- 需要查找已上传的文档内容
- 需要获取特定主题的相关信息
- 需要引用知识库中的知识来回答问题

参数：
- query: 搜索查询词（必需）
- top_k: 返回结果数量（可选，默认5条）

返回：相关文档片段列表，包含内容和相似度分数
"""
    
    def _run(self, query: str, kb_id: Optional[str] = None, top_k: int = 5) -> str:
        """
        执行知识库搜索
        
        Args:
            query: 搜索查询词
            kb_id: 知识库ID（如果工具初始化时未指定，可以使用此参数）
            top_k: 返回结果数量
            
        Returns:
            搜索结果字符串
        """
        try:
            # 导入知识库服务（延迟导入避免循环依赖）
            from src.services.knowledge_base_service import KnowledgeBaseService
            from src.models.knowledge_base import SearchRequest
            
            # 使用指定的kb_id或工具初始化时的kb_id
            target_kb_id = kb_id or self.kb_id
            
            if not target_kb_id:
                # 如果没有指定知识库，尝试使用第一个可用知识库
                kb_service = KnowledgeBaseService()
                kbs = kb_service.list_knowledge_bases()
                if not kbs:
                    return "❌ 没有可用的知识库。请先创建知识库并上传文档。"
                target_kb_id = kbs[0].id
                logger.info(f"⚠️  未指定知识库ID，使用第一个可用知识库: {target_kb_id}")
            
            # 创建搜索请求
            search_request = SearchRequest(
                kb_id=target_kb_id,
                query=query,
                top_k=top_k,
                score_threshold=0.0
            )
            
            # 执行搜索
            kb_service = KnowledgeBaseService()
            response = kb_service.search(search_request)
            
            if not response.success:
                return f"❌ 搜索失败: {response.query}"
            
            if response.total_results == 0:
                return f"📚 知识库搜索完成\n\n查询: {query}\n结果: 未找到相关文档"
            
            # 格式化搜索结果
            output = f"📚 知识库搜索结果 (知识库ID: {target_kb_id})\n\n"
            output += f"查询: {query}\n"
            output += f"找到 {response.total_results} 条相关结果:\n\n"
            
            for i, result in enumerate(response.results, 1):
                score_percent = (result.score * 100)
                output += f"**结果 {i}** (相似度: {score_percent:.1f}%)\n"
                output += f"{result.content}\n"
                
                # 显示元数据（如果有）
                if result.metadata:
                    metadata_str = ", ".join([
                        f"{k}: {v}" 
                        for k, v in result.metadata.items() 
                        if k not in ["doc_id", "chunk_index"]
                    ])
                    if metadata_str:
                        output += f"元数据: {metadata_str}\n"
                
                output += f"文档ID: {result.doc_id}\n\n"
            
            output += f"搜索耗时: {response.search_time:.3f}秒\n"
            
            logger.info(f"✅ 知识库搜索成功: 查询='{query}', 结果数={response.total_results}")
            return output
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 知识库搜索失败: {error_msg}")
            import traceback
            logger.debug(traceback.format_exc())
            return f"❌ 知识库搜索失败: {error_msg}"
    
    async def _arun(self, query: str, kb_id: Optional[str] = None, top_k: int = 5) -> str:
        """异步执行搜索（目前直接调用同步方法）"""
        return self._run(query, kb_id, top_k)


def create_knowledge_base_tool(kb_id: str, kb_name: Optional[str] = None) -> KnowledgeBaseSearchTool:
    """
    创建指定知识库的搜索工具
    
    Args:
        kb_id: 知识库ID
        kb_name: 知识库名称（用于工具描述）
        
    Returns:
        知识库搜索工具实例
    """
    tool = KnowledgeBaseSearchTool(kb_id=kb_id)
    if kb_name:
        tool.description = f"""在知识库 "{kb_name}" (ID: {kb_id}) 中搜索相关信息。

使用场景：
- 需要查找已上传的文档内容
- 需要获取特定主题的相关信息
- 需要引用知识库中的知识来回答问题

参数：
- query: 搜索查询词（必需）
- top_k: 返回结果数量（可选，默认5条）

返回：相关文档片段列表，包含内容和相似度分数
"""
    return tool

