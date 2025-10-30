"""
系统配置数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SystemConfig(BaseModel):
    """系统配置模型"""
    id: str = "default"
    llm_provider: str = Field(default="siliconflow", description="LLM提供商")
    api_key: str = Field(default="", description="API密钥（存储时加密）")
    base_url: str = Field(default="https://api.siliconflow.cn/v1", description="API基础URL")
    default_model: str = Field(default="Qwen/Qwen2.5-7B-Instruct", description="默认模型")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, le=100000, description="最大token数")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "default",
                "llm_provider": "siliconflow",
                "api_key": "sk-xxx",
                "base_url": "https://api.siliconflow.cn/v1",
                "default_model": "Qwen/Qwen2.5-7B-Instruct",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }


class SystemConfigUpdate(BaseModel):
    """系统配置更新模型"""
    llm_provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=100000)


class SystemConfigResponse(BaseModel):
    """系统配置响应模型（API Key脱敏）"""
    id: str
    llm_provider: str
    api_key_masked: str  # 脱敏后的API Key
    base_url: str
    default_model: str
    temperature: float
    max_tokens: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_system_config(cls, config: SystemConfig):
        """从SystemConfig创建响应对象"""
        # 脱敏API Key (只显示前4位和后4位)
        masked_key = ""
        if config.api_key:
            key_len = len(config.api_key)
            if key_len > 8:
                masked_key = config.api_key[:4] + "****" + config.api_key[-4:]
            elif key_len > 0:
                masked_key = "****" + config.api_key[-min(4, key_len):]
        
        return cls(
            id=config.id,
            llm_provider=config.llm_provider,
            api_key_masked=masked_key,
            base_url=config.base_url,
            default_model=config.default_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

