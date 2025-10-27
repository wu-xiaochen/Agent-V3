"""
共享工具函数
"""
import os
import uuid
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator
from functools import wraps
from dotenv import load_dotenv
from src.shared.exceptions.exceptions import AgentException
from src.shared.types.types import JSONDict, SessionID

# 加载 .env 文件
load_dotenv()


def generate_session_id() -> SessionID:
    """生成会话ID"""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().isoformat()


def load_json_file(file_path: str) -> JSONDict:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise AgentException(f"无法加载JSON文件 {file_path}: {str(e)}")


def save_json_file(file_path: str, data: JSONDict) -> None:
    """保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise AgentException(f"无法保存JSON文件 {file_path}: {str(e)}")


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """获取环境变量"""
    value = os.getenv(key, default)
    if value is None and default is None:
        raise AgentException(f"环境变量 {key} 未设置")
    return value


def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """异步重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """安全执行函数"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"执行函数 {func.__name__} 时出错: {str(e)}")
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并字典"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """验证必填字段"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise AgentException(f"缺少必填字段: {', '.join(missing_fields)}")


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """分块列表"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def async_generator_to_list(generator: AsyncGenerator) -> List[Any]:
    """将异步生成器转换为列表"""
    result = []
    async for item in generator:
        result.append(item)
    return result


def format_bytes(size: int) -> str:
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def sanitize_string(text: str) -> str:
    """清理字符串，移除潜在危险字符"""
    # 移除控制字符
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    # 移除潜在的脚本标签
    text = text.replace('<script>', '').replace('</script>', '')
    return text


def deep_copy_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """深拷贝字典"""
    return json.loads(json.dumps(d))


def is_valid_json(text: str) -> bool:
    """检查文本是否为有效JSON"""
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """从文本中提取JSON"""
    try:
        # 尝试直接解析整个文本
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试查找JSON片段
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                return None
        return None