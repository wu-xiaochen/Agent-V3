"""
嵌入服务
提供文本嵌入生成的统一接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import logging
import numpy as np
from datetime import datetime

from src.shared.exceptions.exceptions import EmbeddingError
from src.infrastructure.external.external_service import LLMService


class EmbeddingService(ABC):
    """嵌入服务抽象基类"""
    
    def __init__(
        self,
        model: str,
        dimension: int,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化嵌入服务
        
        Args:
            model: 模型名称
            dimension: 嵌入维度
            logger: 日志记录器
        """
        self.model = model
        self.dimension = dimension
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        生成单个文本的嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        生成多个文本的嵌入向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            嵌入向量列表
        """
        pass
    
    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """
        生成查询的嵌入向量
        
        Args:
            query: 查询文本
            
        Returns:
            嵌入向量
        """
        pass
    
    @abstractmethod
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        生成文档的嵌入向量
        
        Args:
            documents: 文档列表
            
        Returns:
            嵌入向量列表
        """
        pass
    
    async def compute_similarity(
        self,
        vector1: List[float],
        vector2: List[float],
        metric: str = "cosine"
    ) -> float:
        """
        计算两个向量之间的相似度
        
        Args:
            vector1: 第一个向量
            vector2: 第二个向量
            metric: 相似度度量 (cosine, euclidean, dot_product)
            
        Returns:
            相似度分数
        """
        if len(vector1) != len(vector2):
            raise EmbeddingError("向量维度不匹配")
        
        if metric == "cosine":
            return self._cosine_similarity(vector1, vector2)
        elif metric == "euclidean":
            return self._euclidean_distance(vector1, vector2)
        elif metric == "dot_product":
            return self._dot_product(vector1, vector2)
        else:
            raise EmbeddingError(f"不支持的相似度度量: {metric}")
    
    def _cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vector1)
        vec2 = np.array(vector2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _euclidean_distance(self, vector1: List[float], vector2: List[float]) -> float:
        """计算欧氏距离"""
        vec1 = np.array(vector1)
        vec2 = np.array(vector2)
        
        return float(np.linalg.norm(vec1 - vec2))
    
    def _dot_product(self, vector1: List[float], vector2: List[float]) -> float:
        """计算点积"""
        vec1 = np.array(vector1)
        vec2 = np.array(vector2)
        
        return float(np.dot(vec1, vec2))


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI嵌入服务实现"""
    
    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化OpenAI嵌入服务
        
        Args:
            model: 模型名称
            api_key: API密钥
            logger: 日志记录器
        """
        dimension = 1536 if model == "text-embedding-ada-002" else 3072  # text-embedding-3-large
        super().__init__(model, dimension, logger)
        
        self.api_key = api_key
        self._llm_service = None
    
    async def _get_llm_service(self) -> LLMService:
        """获取LLM服务实例"""
        if not self._llm_service:
            self._llm_service = LLMService(
                provider="openai",
                model=self.model,
                api_key=self.api_key,
                logger=self.logger
            )
            await self._llm_service.connect()
        
        return self._llm_service
    
    async def embed_text(self, text: str) -> List[float]:
        """生成单个文本的嵌入向量"""
        llm_service = await self._get_llm_service()
        return await llm_service.get_embedding(text, self.model)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的嵌入向量"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """生成查询的嵌入向量"""
        return await self.embed_text(query)
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """生成文档的嵌入向量"""
        return await self.embed_texts(documents)


class SentenceTransformerEmbeddingService(EmbeddingService):
    """SentenceTransformer嵌入服务实现"""
    
    def __init__(
        self,
        model: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化SentenceTransformer嵌入服务
        
        Args:
            model: 模型名称
            device: 设备 (cpu, cuda)
            logger: 日志记录器
        """
        # 获取模型维度
        dimension_map = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "multi-qa-mpnet-base-dot-v1": 768,
            "paraphrase-multilingual-mpnet-base-v2": 768,
        }
        
        dimension = dimension_map.get(model, 768)  # 默认768维
        super().__init__(model, dimension, logger)
        
        self.device = device
        self._model = None
    
    async def _get_model(self):
        """获取模型实例"""
        if not self._model:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model, device=self.device)
                self.logger.info(f"已加载SentenceTransformer模型: {self.model}")
            except ImportError:
                raise EmbeddingError("未安装sentence-transformers库，请使用 pip install sentence-transformers")
            except Exception as e:
                raise EmbeddingError(f"加载模型失败: {str(e)}")
        
        return self._model
    
    async def embed_text(self, text: str) -> List[float]:
        """生成单个文本的嵌入向量"""
        model = await self._get_model()
        embedding = model.encode(text)
        return embedding.tolist()
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的嵌入向量"""
        model = await self._get_model()
        embeddings = model.encode(texts)
        return [embedding.tolist() for embedding in embeddings]
    
    async def embed_query(self, query: str) -> List[float]:
        """生成查询的嵌入向量"""
        return await self.embed_text(query)
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """生成文档的嵌入向量"""
        return await self.embed_texts(documents)


class HuggingFaceEmbeddingService(EmbeddingService):
    """HuggingFace嵌入服务实现"""
    
    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        api_key: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化HuggingFace嵌入服务
        
        Args:
            model: 模型名称
            device: 设备 (cpu, cuda)
            api_key: API密钥
            logger: 日志记录器
        """
        # 获取模型维度
        dimension_map = {
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-mpnet-base-v2": 768,
            "sentence-transformers/multi-qa-mpnet-base-dot-v1": 768,
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2": 768,
        }
        
        dimension = dimension_map.get(model, 768)  # 默认768维
        super().__init__(model, dimension, logger)
        
        self.device = device
        self.api_key = api_key
        self._model = None
        self._tokenizer = None
    
    async def _get_model_and_tokenizer(self):
        """获取模型和分词器实例"""
        if not self._model or not self._tokenizer:
            try:
                from transformers import AutoTokenizer, AutoModel
                import torch
                
                self._tokenizer = AutoTokenizer.from_pretrained(self.model, use_auth_token=self.api_key)
                self._model = AutoModel.from_pretrained(self.model, use_auth_token=self.api_key)
                
                if self.device == "cuda" and torch.cuda.is_available():
                    self._model = self._model.to("cuda")
                
                self.logger.info(f"已加载HuggingFace模型: {self.model}")
            except ImportError:
                raise EmbeddingError("未安装transformers库，请使用 pip install transformers")
            except Exception as e:
                raise EmbeddingError(f"加载模型失败: {str(e)}")
        
        return self._model, self._tokenizer
    
    async def _mean_pooling(self, model_output, attention_mask):
        """平均池化"""
        import torch
        
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    async def embed_text(self, text: str) -> List[float]:
        """生成单个文本的嵌入向量"""
        model, tokenizer = await self._get_model_and_tokenizer()
        
        import torch
        
        # 分词
        encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        
        # 移动到指定设备
        if self.device == "cuda" and torch.cuda.is_available():
            encoded_input = {k: v.to("cuda") for k, v in encoded_input.items()}
        
        # 获取模型输出
        with torch.no_grad():
            model_output = model(**encoded_input)
        
        # 池化
        embedding = await self._mean_pooling(model_output, encoded_input["attention_mask"])
        
        # 移回CPU并转换为列表
        if self.device == "cuda" and torch.cuda.is_available():
            embedding = embedding.cpu()
        
        return embedding.numpy().flatten().tolist()
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的嵌入向量"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """生成查询的嵌入向量"""
        return await self.embed_text(query)
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """生成文档的嵌入向量"""
        return await self.embed_texts(documents)


class CohereEmbeddingService(EmbeddingService):
    """Cohere嵌入服务实现"""
    
    def __init__(
        self,
        model: str = "embed-english-v3.0",
        api_key: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化Cohere嵌入服务
        
        Args:
            model: 模型名称
            api_key: API密钥
            logger: 日志记录器
        """
        # 获取模型维度
        dimension_map = {
            "embed-english-v3.0": 1024,
            "embed-english-light-v3.0": 384,
            "embed-multilingual-v3.0": 1024,
            "embed-multilingual-light-v3.0": 384,
        }
        
        dimension = dimension_map.get(model, 1024)  # 默认1024维
        super().__init__(model, dimension, logger)
        
        self.api_key = api_key
        self._client = None
    
    async def _get_client(self):
        """获取Cohere客户端"""
        if not self._client:
            try:
                import cohere
                self._client = cohere.Client(self.api_key)
                self.logger.info(f"已初始化Cohere客户端")
            except ImportError:
                raise EmbeddingError("未安装cohere库，请使用 pip install cohere")
            except Exception as e:
                raise EmbeddingError(f"初始化Cohere客户端失败: {str(e)}")
        
        return self._client
    
    async def embed_text(self, text: str) -> List[float]:
        """生成单个文本的嵌入向量"""
        client = await self._get_client()
        response = client.embed(texts=[text], model=self.model, input_type="search_document")
        return response.embeddings[0]
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的嵌入向量"""
        client = await self._get_client()
        response = client.embed(texts=texts, model=self.model, input_type="search_document")
        return response.embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """生成查询的嵌入向量"""
        client = await self._get_client()
        response = client.embed(texts=[query], model=self.model, input_type="search_query")
        return response.embeddings[0]
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """生成文档的嵌入向量"""
        return await self.embed_texts(documents)


class EmbeddingServiceFactory:
    """嵌入服务工厂"""
    
    @staticmethod
    def create_embedding_service(
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        device: str = "cpu",
        logger: Optional[logging.Logger] = None,
        **kwargs
    ) -> EmbeddingService:
        """
        创建嵌入服务实例
        
        Args:
            provider: 提供商 (openai, sentence_transformers, huggingface, cohere)
            model: 模型名称
            api_key: API密钥
            device: 设备 (cpu, cuda)
            logger: 日志记录器
            **kwargs: 其他参数
            
        Returns:
            嵌入服务实例
        """
        provider = provider.lower()
        
        if provider == "openai":
            return OpenAIEmbeddingService(
                model=model or "text-embedding-ada-002",
                api_key=api_key,
                logger=logger
            )
        elif provider in ["sentence_transformers", "sentence-transformers"]:
            return SentenceTransformerEmbeddingService(
                model=model or "all-MiniLM-L6-v2",
                device=device,
                logger=logger
            )
        elif provider == "huggingface":
            return HuggingFaceEmbeddingService(
                model=model or "sentence-transformers/all-MiniLM-L6-v2",
                device=device,
                api_key=api_key,
                logger=logger
            )
        elif provider == "cohere":
            return CohereEmbeddingService(
                model=model or "embed-english-v3.0",
                api_key=api_key,
                logger=logger
            )
        else:
            raise EmbeddingError(f"不支持的嵌入服务提供商: {provider}")