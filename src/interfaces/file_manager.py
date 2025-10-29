"""
文件管理器 - 管理文件的存储、访问和下载

功能：
1. 保存文件（文档、图片、数据等）
2. 生成下载链接
3. 文件元数据管理
4. 文件清理和过期管理
"""

import os
import json
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FileMetadata:
    """文件元数据"""
    
    def __init__(
        self,
        file_id: str,
        filename: str,
        filepath: str,
        size: int,
        mime_type: str,
        created_at: str,
        expires_at: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        self.file_id = file_id
        self.filename = filename
        self.filepath = filepath
        self.size = size
        self.mime_type = mime_type
        self.created_at = created_at
        self.expires_at = expires_at
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "filepath": self.filepath,
            "size": self.size,
            "size_human": self._format_size(self.size),
            "mime_type": self.mime_type,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "tags": self.tags
        }
    
    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"


class FileManager:
    """
    文件管理器
    
    管理所有由 Agent 生成或处理的文件
    """
    
    def __init__(
        self,
        base_dir: str = "outputs",
        base_url: str = "http://localhost:8000",
        max_file_age_days: int = 30
    ):
        """
        初始化文件管理器
        
        Args:
            base_dir: 文件存储的基础目录
            base_url: API 服务的基础 URL
            max_file_age_days: 文件最大保留天数
        """
        self.base_dir = Path(base_dir)
        self.base_url = base_url.rstrip("/")
        self.max_file_age_days = max_file_age_days
        
        # 创建子目录
        self.documents_dir = self.base_dir / "documents"
        self.images_dir = self.base_dir / "images"
        self.data_dir = self.base_dir / "data"
        self.temp_dir = self.base_dir / "temp"
        
        # 创建元数据目录
        self.metadata_dir = self.base_dir / ".metadata"
        
        # 确保目录存在
        for dir_path in [self.documents_dir, self.images_dir, self.data_dir, self.temp_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 文件管理器已初始化，存储目录: {self.base_dir}")
    
    def save_document(
        self,
        content: str,
        filename: Optional[str] = None,
        file_format: str = "md",
        tags: Optional[List[str]] = None,
        ttl_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        保存文档并返回下载信息
        
        Args:
            content: 文档内容
            filename: 文件名（不含扩展名），如果为None则自动生成
            file_format: 文件格式 (md, txt, json, html等)
            tags: 文件标签
            ttl_days: 文件保留天数，None表示使用默认值
            
        Returns:
            文件信息字典
        """
        try:
            # 生成文件名
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"document_{timestamp}"
            
            # 确保文件名安全
            filename = self._sanitize_filename(filename)
            full_filename = f"{filename}.{file_format}"
            
            # 保存文件
            filepath = self.documents_dir / full_filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 创建文件元数据
            file_id = self._generate_file_id(str(filepath))
            file_size = filepath.stat().st_size
            mime_type = mimetypes.guess_type(str(filepath))[0] or "text/plain"
            created_at = datetime.now().isoformat()
            
            # 计算过期时间
            ttl = ttl_days if ttl_days is not None else self.max_file_age_days
            expires_at = (datetime.now() + timedelta(days=ttl)).isoformat() if ttl > 0 else None
            
            metadata = FileMetadata(
                file_id=file_id,
                filename=full_filename,
                filepath=str(filepath.relative_to(self.base_dir)),
                size=file_size,
                mime_type=mime_type,
                created_at=created_at,
                expires_at=expires_at,
                tags=tags
            )
            
            # 保存元数据
            self._save_metadata(file_id, metadata)
            
            # 生成下载URL
            download_url = f"{self.base_url}/api/files/download/{file_id}"
            
            logger.info(f"✅ 文档已保存: {full_filename} ({metadata._format_size(file_size)})")
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": full_filename,
                "path": str(filepath),
                "download_url": download_url,
                "size": file_size,
                "size_human": metadata._format_size(file_size),
                "created_at": created_at,
                "expires_at": expires_at,
                "mime_type": mime_type
            }
            
        except (IOError, OSError) as e:
            logger.error(f"❌ 保存文档失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_binary_file(
        self,
        data: bytes,
        filename: str,
        file_type: str = "data",
        tags: Optional[List[str]] = None,
        ttl_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        保存二进制文件（图片、PDF等）
        
        Args:
            data: 二进制数据
            filename: 文件名
            file_type: 文件类型 (image, data, temp)
            tags: 文件标签
            ttl_days: 文件保留天数
            
        Returns:
            文件信息字典
        """
        try:
            # 选择存储目录
            if file_type == "image":
                target_dir = self.images_dir
            elif file_type == "temp":
                target_dir = self.temp_dir
            else:
                target_dir = self.data_dir
            
            # 确保文件名安全
            filename = self._sanitize_filename(filename)
            filepath = target_dir / filename
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(data)
            
            # 创建文件元数据
            file_id = self._generate_file_id(str(filepath))
            file_size = filepath.stat().st_size
            mime_type = mimetypes.guess_type(str(filepath))[0] or "application/octet-stream"
            created_at = datetime.now().isoformat()
            
            # 计算过期时间
            ttl = ttl_days if ttl_days is not None else self.max_file_age_days
            expires_at = (datetime.now() + timedelta(days=ttl)).isoformat() if ttl > 0 else None
            
            metadata = FileMetadata(
                file_id=file_id,
                filename=filename,
                filepath=str(filepath.relative_to(self.base_dir)),
                size=file_size,
                mime_type=mime_type,
                created_at=created_at,
                expires_at=expires_at,
                tags=tags
            )
            
            # 保存元数据
            self._save_metadata(file_id, metadata)
            
            # 生成下载URL
            download_url = f"{self.base_url}/api/files/download/{file_id}"
            
            logger.info(f"✅ 文件已保存: {filename} ({metadata._format_size(file_size)})")
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "path": str(filepath),
                "download_url": download_url,
                "size": file_size,
                "size_human": metadata._format_size(file_size),
                "created_at": created_at,
                "expires_at": expires_at,
                "mime_type": mime_type
            }
            
        except (IOError, OSError) as e:
            logger.error(f"❌ 保存文件失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息字典，如果不存在返回None
        """
        metadata = self._load_metadata(file_id)
        if metadata is None:
            return None
        
        filepath = self.base_dir / metadata.filepath
        if not filepath.exists():
            logger.warning(f"⚠️  文件不存在: {filepath}")
            return None
        
        download_url = f"{self.base_url}/api/files/download/{file_id}"
        
        result = metadata.to_dict()
        result["download_url"] = download_url
        result["full_path"] = str(filepath)
        
        return result
    
    def delete_file(self, file_id: str) -> bool:
        """
        删除文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否成功删除
        """
        try:
            metadata = self._load_metadata(file_id)
            if metadata is None:
                logger.warning(f"⚠️  文件元数据不存在: {file_id}")
                return False
            
            filepath = self.base_dir / metadata.filepath
            if filepath.exists():
                filepath.unlink()
            
            # 删除元数据
            metadata_file = self.metadata_dir / f"{file_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info(f"🗑️  文件已删除: {metadata.filename}")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"❌ 删除文件失败: {e}")
            return False
    
    def list_files(
        self,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出文件
        
        Args:
            file_type: 文件类型过滤
            tags: 标签过滤
            limit: 最大返回数量
            
        Returns:
            文件列表
        """
        files = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)
                
                metadata = FileMetadata(**metadata_dict)
                
                # 应用过滤
                if tags and not any(tag in metadata.tags for tag in tags):
                    continue
                
                file_info = metadata.to_dict()
                file_info["download_url"] = f"{self.base_url}/api/files/download/{metadata.file_id}"
                
                files.append(file_info)
                
                if len(files) >= limit:
                    break
                    
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"⚠️  读取元数据失败: {metadata_file}, {e}")
                continue
        
        # 按创建时间倒序排序
        files.sort(key=lambda x: x["created_at"], reverse=True)
        
        return files
    
    def cleanup_expired_files(self) -> int:
        """
        清理过期文件
        
        Returns:
            清理的文件数量
        """
        cleaned_count = 0
        now = datetime.now()
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)
                
                expires_at = metadata_dict.get("expires_at")
                if expires_at:
                    expires_dt = datetime.fromisoformat(expires_at)
                    if now > expires_dt:
                        file_id = metadata_dict["file_id"]
                        if self.delete_file(file_id):
                            cleaned_count += 1
                            
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"⚠️  读取元数据失败: {metadata_file}, {e}")
                continue
        
        if cleaned_count > 0:
            logger.info(f"🗑️  已清理 {cleaned_count} 个过期文件")
        
        return cleaned_count
    
    def _generate_file_id(self, filepath: str) -> str:
        """生成文件ID"""
        content = f"{filepath}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不安全字符"""
        # 移除路径分隔符和其他危险字符
        unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def _save_metadata(self, file_id: str, metadata: FileMetadata):
        """保存文件元数据"""
        metadata_file = self.metadata_dir / f"{file_id}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """加载文件元数据"""
        metadata_file = self.metadata_dir / f"{file_id}.json"
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            return FileMetadata(**metadata_dict)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"❌ 加载元数据失败: {e}")
            return None


# 全局单例
_file_manager = None


def get_file_manager(
    base_dir: str = "outputs",
    base_url: str = "http://localhost:8000",
    max_file_age_days: int = 30
) -> FileManager:
    """获取文件管理器单例"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager(base_dir, base_url, max_file_age_days)
    return _file_manager

