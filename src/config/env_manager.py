"""
环境变量管理器
集中管理所有环境变量和配置
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EnvManager:
    """环境变量管理器 - 集中管理所有配置"""
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    # ========== N8N 配置 ==========
    N8N_API_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
    N8N_API_KEY = os.getenv("N8N_API_KEY", "")
    
    # ========== Redis 配置 ==========
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_TTL = int(os.getenv("REDIS_TTL", "86400"))  # 24小时
    
    # ========== LLM 配置 ==========
    # SiliconFlow
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    SILICONFLOW_DEFAULT_MODEL = os.getenv("SILICONFLOW_DEFAULT_MODEL", "Pro/deepseek-ai/DeepSeek-V3.1-Terminus")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # ========== 执行限制 ==========
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "25"))
    MAX_EXECUTION_TIME = int(os.getenv("MAX_EXECUTION_TIME", "180"))  # 秒
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TIMEOUT = int(os.getenv("TIMEOUT", "120"))  # 秒
    
    # ========== CrewAI 配置 ==========
    CREWAI_MAX_TOKENS = int(os.getenv("CREWAI_MAX_TOKENS", "8000"))
    CREWAI_TIMEOUT = int(os.getenv("CREWAI_TIMEOUT", "60"))
    CREWAI_TEMPERATURE = float(os.getenv("CREWAI_TEMPERATURE", "0.7"))
    
    # ========== 日志配置 ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    
    # ========== 其他配置 ==========
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取环境变量
        
        Args:
            key: 变量名
            default: 默认值
            
        Returns:
            变量值
        """
        return os.getenv(key, default)
    
    @classmethod
    def get_redis_url(cls) -> str:
        """
        获取 Redis 连接 URL
        
        Returns:
            Redis URL
        """
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        else:
            return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    @classmethod
    def get_llm_config(cls, provider: str = "siliconflow") -> Dict[str, Any]:
        """
        获取 LLM 配置
        
        Args:
            provider: LLM 提供商 (siliconflow, openai, anthropic, ollama)
            
        Returns:
            配置字典
        """
        if provider == "siliconflow":
            return {
                "api_key": cls.SILICONFLOW_API_KEY,
                "base_url": cls.SILICONFLOW_BASE_URL,
                "model_name": cls.SILICONFLOW_DEFAULT_MODEL,
                "max_tokens": cls.MAX_TOKENS,
                "timeout": cls.TIMEOUT
            }
        elif provider == "openai":
            return {
                "api_key": cls.OPENAI_API_KEY,
                "base_url": cls.OPENAI_BASE_URL,
                "max_tokens": cls.MAX_TOKENS,
                "timeout": cls.TIMEOUT
            }
        elif provider == "anthropic":
            return {
                "api_key": cls.ANTHROPIC_API_KEY,
                "max_tokens": cls.MAX_TOKENS,
                "timeout": cls.TIMEOUT
            }
        elif provider == "ollama":
            return {
                "base_url": cls.OLLAMA_BASE_URL,
                "max_tokens": cls.MAX_TOKENS,
                "timeout": cls.TIMEOUT
            }
        else:
            logger.warning(f"未知的 LLM 提供商: {provider}，使用默认配置")
            return {
                "max_tokens": cls.MAX_TOKENS,
                "timeout": cls.TIMEOUT
            }
    
    @classmethod
    def get_n8n_config(cls) -> Dict[str, str]:
        """
        获取 n8n 配置
        
        Returns:
            n8n 配置字典
        """
        return {
            "api_url": cls.N8N_API_URL,
            "api_key": cls.N8N_API_KEY
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        验证配置完整性
        
        Returns:
            验证结果字典
        """
        results = {
            "redis": bool(cls.REDIS_HOST),
            "n8n": bool(cls.N8N_API_URL and cls.N8N_API_KEY),
            "siliconflow": bool(cls.SILICONFLOW_API_KEY),
            "openai": bool(cls.OPENAI_API_KEY),
            "anthropic": bool(cls.ANTHROPIC_API_KEY),
        }
        
        # 记录验证结果
        for service, is_valid in results.items():
            if not is_valid:
                logger.warning(f"⚠️  {service} 配置不完整或缺失")
            else:
                logger.info(f"✅ {service} 配置完整")
        
        return results
    
    @classmethod
    def print_config_summary(cls):
        """打印配置摘要"""
        print("\n" + "="*70)
        print("📋 环境配置摘要")
        print("="*70)
        
        print(f"\n🌍 环境: {cls.ENVIRONMENT}")
        print(f"🐛 调试模式: {'开启' if cls.DEBUG else '关闭'}")
        
        print(f"\n📊 Redis:")
        print(f"   - 主机: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
        print(f"   - 数据库: {cls.REDIS_DB}")
        print(f"   - 密码: {'已设置' if cls.REDIS_PASSWORD else '未设置'}")
        
        print(f"\n🔧 n8n:")
        print(f"   - API URL: {cls.N8N_API_URL}")
        print(f"   - API Key: {'已设置' if cls.N8N_API_KEY else '⚠️  未设置'}")
        
        print(f"\n🤖 LLM:")
        print(f"   - SiliconFlow: {'✅' if cls.SILICONFLOW_API_KEY else '❌'}")
        print(f"   - OpenAI: {'✅' if cls.OPENAI_API_KEY else '❌'}")
        print(f"   - Anthropic: {'✅' if cls.ANTHROPIC_API_KEY else '❌'}")
        
        print(f"\n⚙️  执行限制:")
        print(f"   - 最大迭代: {cls.MAX_ITERATIONS}")
        print(f"   - 最大执行时间: {cls.MAX_EXECUTION_TIME}s")
        print(f"   - 最大 Tokens: {cls.MAX_TOKENS}")
        print(f"   - 超时: {cls.TIMEOUT}s")
        
        print(f"\n📝 日志:")
        print(f"   - 级别: {cls.LOG_LEVEL}")
        print(f"   - 格式: {cls.LOG_FORMAT}")
        
        print("="*70 + "\n")


# 加载 .env 文件（如果存在）
def load_dotenv():
    """加载 .env 文件"""
    env_file = EnvManager.PROJECT_ROOT / ".env"
    
    if env_file.exists():
        logger.info(f"📄 加载 .env 文件: {env_file}")
        
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                
                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # 只设置尚未设置的环境变量
                    if key not in os.environ:
                        os.environ[key] = value
                        logger.debug(f"设置环境变量: {key}")
        
        logger.info("✅ .env 文件加载完成")
    else:
        logger.warning(f"⚠️  .env 文件不存在: {env_file}")
        logger.info("💡 提示: 可以创建 .env 文件来配置环境变量")


# 自动加载 .env 文件
load_dotenv()

