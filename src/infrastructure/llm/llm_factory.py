"""
LLM工厂类
用于创建不同提供商的LLM实例
"""

import warnings
import os
# 在导入LangChain之前设置环境变量来抑制弃用警告
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning:langchain.*"
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.*")

from typing import Dict, Any, Optional
from langchain_openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import HuggingFaceHub
from langchain_community.chat_models import ChatAnthropic
from src.config.config_loader import config_loader


class LLMFactory:
    """LLM工厂类"""
    
    @staticmethod
    def create_llm(provider: Optional[str] = None, **kwargs) -> Any:
        """
        创建LLM实例
        
        Args:
            provider: LLM提供商，如果为None则使用默认提供商
            **kwargs: 额外的LLM参数
            
        Returns:
            LLM实例
        """
        if provider is None:
            # 获取服务配置中的默认提供商
            services_config = config_loader.get_services_config()
            services = services_config.get("services", {})
            llm_config = services.get("llm", {})
            provider = llm_config.get("provider", "openai")
        
        llm_config = config_loader.get_llm_config(provider)
        
        # 合并参数
        merged_config = {**llm_config, **kwargs}
        
        # 根据提供商创建对应的LLM实例
        if provider == "openai":
            return LLMFactory._create_openai_llm(merged_config)
        elif provider == "anthropic":
            return LLMFactory._create_anthropic_llm(merged_config)
        elif provider == "huggingface":
            return LLMFactory._create_huggingface_llm(merged_config)
        elif provider == "siliconflow":
            return LLMFactory._create_siliconflow_llm(merged_config)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
    
    @staticmethod
    def _create_openai_llm(config: Dict[str, Any]) -> Any:
        """
        创建OpenAI LLM实例
        
        Args:
            config: OpenAI配置
            
        Returns:
            OpenAI LLM实例
        """
        # 🆕 优先使用 EnvManager
        from src.config.env_manager import EnvManager
        api_key = config.get("api_key") or EnvManager.OPENAI_API_KEY
        if not api_key:
            raise ValueError("未找到OpenAI API密钥，请在配置文件中设置或设置环境变量OPENAI_API_KEY")
        
        model = config.get("model") or EnvManager.get("OPENAI_DEFAULT_MODEL", "gpt-3.5-turbo")
        base_url = config.get("base_url") or EnvManager.OPENAI_BASE_URL
        
        # 根据模型类型决定使用ChatOpenAI还是OpenAI
        if "gpt-" in model:
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name=model,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1000),
                top_p=config.get("top_p", 1.0),
                frequency_penalty=config.get("frequency_penalty", 0.0),
                presence_penalty=config.get("presence_penalty", 0.0),
                openai_api_base=base_url
            )
        else:
            return OpenAI(
                openai_api_key=api_key,
                model_name=model,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1000),
                top_p=config.get("top_p", 1.0),
                frequency_penalty=config.get("frequency_penalty", 0.0),
                presence_penalty=config.get("presence_penalty", 0.0),
                openai_api_base=base_url
            )
    
    @staticmethod
    def _create_anthropic_llm(config: Dict[str, Any]) -> Any:
        """
        创建Anthropic Claude LLM实例
        
        Args:
            config: Anthropic配置
            
        Returns:
            Anthropic Claude LLM实例
        """
        api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("未找到Anthropic API密钥，请在配置文件中设置或设置环境变量ANTHROPIC_API_KEY")
        
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model=config.get("model", "claude-3-sonnet-20240229"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 1000)
        )
    
    @staticmethod
    def _create_huggingface_llm(config: Dict[str, Any]) -> Any:
        """
        创建Hugging Face LLM实例
        
        Args:
            config: Hugging Face配置
            
        Returns:
            Hugging Face LLM实例
        """
        api_key = config.get("api_key") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            raise ValueError("未找到Hugging Face API密钥，请在配置文件中设置或设置环境变量HUGGINGFACEHUB_API_TOKEN")
        
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key
        
        return HuggingFaceHub(
            repo_id=config.get("model", "microsoft/DialoGPT-medium"),
            model_kwargs={"temperature": config.get("temperature", 0.7)},
            huggingfacehub_api_token=api_key
        )
    
    @staticmethod
    def _create_siliconflow_llm(config: Dict[str, Any]) -> Any:
        """
        创建硅基流动LLM实例
        
        Args:
            config: 硅基流动配置
            
        Returns:
            硅基流动LLM实例
        """
        # 🆕 优先使用 EnvManager
        from src.config.env_manager import EnvManager
        api_key = config.get("api_key") or EnvManager.SILICONFLOW_API_KEY
        if not api_key:
            raise ValueError("未找到硅基流动API密钥，请在配置文件中设置或设置环境变量SILICONFLOW_API_KEY")
        
        model = config.get("model", "Pro/deepseek-ai/DeepSeek-V3.1-Terminus")
        base_url = config.get("base_url", "https://api.siliconflow.cn/v1")
        
        # 使用ChatOpenAI来连接硅基流动API，因为它兼容OpenAI API格式
        # 使用实际的模型名称，而不是gpt-3.5-turbo
        llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=model,  # 使用实际的模型名称
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 1000),
            top_p=config.get("top_p", 1.0),
            frequency_penalty=config.get("frequency_penalty", 0.0),
            presence_penalty=config.get("presence_penalty", 0.0),
            openai_api_base=base_url
        )
        
        # 存储实际的模型名称，以便后续使用
        # 使用__dict__添加属性，避免Pydantic验证错误
        llm.__dict__['actual_model'] = model
        
        return llm