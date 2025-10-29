"""
多模态处理器 - 处理图片、视频等多模态数据

功能：
1. 图片分析 (GPT-4V, Claude 3)
2. 图片处理和转换
3. OCR 文字识别
"""

import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO

logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理器"""
    
    @staticmethod
    def load_image(file_path: str) -> Optional[bytes]:
        """加载图片文件"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except (IOError, OSError) as e:
            logger.error(f"❌ 加载图片失败: {e}")
            return None
    
    @staticmethod
    def image_to_base64(image_data: bytes) -> str:
        """将图片转换为 base64"""
        return base64.b64encode(image_data).decode('utf-8')
    
    @staticmethod
    def get_image_info(file_path: str) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                return {
                    "success": True,
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "size": f"{img.width}x{img.height}"
                }
        except ImportError:
            logger.error("❌ Pillow 未安装，请运行: pip install pillow")
            return {"success": False, "error": "Pillow 未安装"}
        except Exception as e:
            logger.error(f"❌ 获取图片信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def resize_image(file_path: str, max_size: int = 1024) -> Optional[bytes]:
        """
        调整图片大小
        
        Args:
            file_path: 文件路径
            max_size: 最大尺寸（宽或高）
            
        Returns:
            调整后的图片数据
        """
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                # 计算新尺寸
                ratio = min(max_size / img.width, max_size / img.height)
                if ratio < 1:
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # 转换为 bytes
                buffer = BytesIO()
                img.save(buffer, format=img.format or 'PNG')
                return buffer.getvalue()
                
        except Exception as e:
            logger.error(f"❌ 调整图片大小失败: {e}")
            return None


class VisionAnalyzer:
    """
    视觉分析器 - 使用 Vision API 分析图片
    
    支持：
    - GPT-4V (OpenAI)
    - Claude 3 Vision (Anthropic)
    """
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化视觉分析器
        
        Args:
            provider: 提供商 (openai, anthropic)
            api_key: API密钥
            base_url: API基础URL
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.base_url = base_url
        
        if not api_key:
            import os
            if self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == "anthropic":
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
    
    def analyze_image(
        self,
        image_path: str,
        prompt: str = "请详细描述这张图片的内容",
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        分析图片
        
        Args:
            image_path: 图片路径
            prompt: 分析提示词
            max_tokens: 最大 token 数
            
        Returns:
            分析结果
        """
        try:
            if self.provider == "openai":
                return self._analyze_with_openai(image_path, prompt, max_tokens)
            elif self.provider == "anthropic":
                return self._analyze_with_anthropic(image_path, prompt, max_tokens)
            else:
                return {
                    "success": False,
                    "error": f"不支持的提供商: {self.provider}"
                }
        except Exception as e:
            logger.error(f"❌ 图片分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_with_openai(
        self,
        image_path: str,
        prompt: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """使用 OpenAI GPT-4V 分析图片"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            # 加载图片
            image_data = ImageProcessor.load_image(image_path)
            if not image_data:
                return {"success": False, "error": "加载图片失败"}
            
            # 转换为 base64
            base64_image = ImageProcessor.image_to_base64(image_data)
            
            # 调用 API
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            
            return {
                "success": True,
                "provider": "openai",
                "model": "gpt-4-vision-preview",
                "analysis": result,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except ImportError:
            logger.error("❌ openai 未安装，请运行: pip install openai")
            return {"success": False, "error": "openai 未安装"}
        except Exception as e:
            logger.error(f"❌ OpenAI Vision 分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_with_anthropic(
        self,
        image_path: str,
        prompt: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """使用 Anthropic Claude 3 分析图片"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            # 加载图片
            image_data = ImageProcessor.load_image(image_path)
            if not image_data:
                return {"success": False, "error": "加载图片失败"}
            
            # 转换为 base64
            base64_image = ImageProcessor.image_to_base64(image_data)
            
            # 调用 API
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            result = message.content[0].text
            
            return {
                "success": True,
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "analysis": result,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }
            
        except ImportError:
            logger.error("❌ anthropic 未安装，请运行: pip install anthropic")
            return {"success": False, "error": "anthropic 未安装"}
        except Exception as e:
            logger.error(f"❌ Anthropic Vision 分析失败: {e}")
            return {"success": False, "error": str(e)}


class MultimodalProcessor:
    """
    多模态处理器 - 统一接口
    
    功能：
    1. 自动识别文件类型
    2. 调用相应的处理器
    3. 返回统一格式的结果
    """
    
    def __init__(self, vision_provider: str = "openai"):
        """
        初始化多模态处理器
        
        Args:
            vision_provider: 视觉分析提供商
        """
        self.vision_provider = vision_provider
        self.image_processor = ImageProcessor()
        self.vision_analyzer = VisionAnalyzer(provider=vision_provider)
    
    def process_file(
        self,
        file_path: str,
        task: str = "analyze",
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理文件
        
        Args:
            file_path: 文件路径
            task: 任务类型 (analyze, info, resize)
            prompt: 自定义提示词（用于图片分析）
            
        Returns:
            处理结果
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # 判断文件类型
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        if extension in image_extensions:
            return self._process_image(file_path, task, prompt)
        else:
            return {
                "success": False,
                "error": f"不支持的文件类型: {extension}"
            }
    
    def _process_image(
        self,
        file_path: str,
        task: str,
        prompt: Optional[str]
    ) -> Dict[str, Any]:
        """处理图片"""
        if task == "info":
            return self.image_processor.get_image_info(file_path)
        elif task == "analyze":
            if not prompt:
                prompt = "请详细描述这张图片的内容，包括场景、物体、文字、颜色等所有你能观察到的信息。"
            return self.vision_analyzer.analyze_image(file_path, prompt)
        elif task == "resize":
            resized_data = self.image_processor.resize_image(file_path)
            if resized_data:
                return {
                    "success": True,
                    "message": "图片已调整大小",
                    "data_size": len(resized_data)
                }
            else:
                return {"success": False, "error": "调整图片大小失败"}
        else:
            return {"success": False, "error": f"不支持的任务类型: {task}"}


# 便捷函数
def analyze_image(
    image_path: str,
    prompt: str = "请详细描述这张图片",
    provider: str = "openai"
) -> Dict[str, Any]:
    """
    分析图片
    
    Args:
        image_path: 图片路径
        prompt: 分析提示词
        provider: 提供商
        
    Returns:
        分析结果
    """
    processor = MultimodalProcessor(vision_provider=provider)
    return processor.process_file(image_path, task="analyze", prompt=prompt)


def get_image_info(image_path: str) -> Dict[str, Any]:
    """获取图片信息"""
    processor = MultimodalProcessor()
    return processor.process_file(image_path, task="info")

