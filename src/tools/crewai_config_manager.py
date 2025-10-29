#!/usr/bin/env python3
"""
CrewAI配置管理器
提供配置的CRUD和查询功能，支持SQLite索引和文件存储
"""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class CrewAIConfigManager:
    """CrewAI配置管理器 - 提供配置的CRUD和查询功能"""
    
    def __init__(self, config_dir: str = "config/generated", db_path: str = "data/crewai_configs.db"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件保存目录
            db_path: SQLite数据库路径（用于索引）
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
        logger.info(f"✅ CrewAIConfigManager 初始化完成 (配置目录: {self.config_dir}, 数据库: {self.db_path})")
    
    def _init_db(self):
        """初始化配置索引数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crewai_configs (
                config_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                business_process TEXT,
                file_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.debug("配置索引数据库初始化完成")
    
    def save_config(self, config_dict: Dict[str, Any], tags: List[str] = None) -> str:
        """
        保存配置并建立索引
        
        Args:
            config_dict: 配置字典
            tags: 配置标签列表
            
        Returns:
            配置ID
        """
        import hashlib
        
        # 生成配置ID（如果没有）
        if "config_id" not in config_dict:
            timestamp = datetime.now().isoformat()
            crew_name = config_dict.get("crewai_config", {}).get("name", "unnamed")
            config_id = hashlib.md5(f"{crew_name}_{timestamp}".encode()).hexdigest()[:12]
            config_dict["config_id"] = config_id
        else:
            config_id = config_dict["config_id"]
        
        # 生成文件名
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        crew_name = config_dict.get("crewai_config", {}).get("name", "unnamed")
        safe_name = crew_name.replace(" ", "_").replace("/", "_")
        file_path = self.config_dir / f"{safe_name}_{timestamp_str}.json"
        
        # 设置生成时间
        if "generated_at" not in config_dict:
            config_dict["generated_at"] = datetime.now().isoformat()
        
        # 保存配置文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        # 保存到索引数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO crewai_configs 
            (config_id, name, description, business_process, file_path, created_at, updated_at, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config_id,
            crew_name,
            config_dict.get("crewai_config", {}).get("description", ""),
            config_dict.get("business_process", ""),
            str(file_path),
            timestamp,
            timestamp,
            json.dumps(tags or []),
            json.dumps({"version": config_dict.get("version", "1.0")})
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ 配置已保存: {file_path.name} (ID: {config_id})")
        return config_id
    
    def get_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            配置字典，如果不存在则返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_path FROM crewai_configs WHERE config_id = ?", (config_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            logger.warning(f"❌ 未找到配置ID: {config_id}")
            return None
        
        file_path = Path(result[0])
        if not file_path.exists():
            logger.error(f"❌ 配置文件不存在: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.debug(f"✅ 加载配置: {file_path.name} (ID: {config_id})")
        return config
    
    def delete_config(self, config_id: str) -> bool:
        """
        删除配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            是否成功删除
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取文件路径
        cursor.execute("SELECT file_path FROM crewai_configs WHERE config_id = ?", (config_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            logger.warning(f"❌ 未找到配置ID: {config_id}")
            return False
        
        file_path = Path(result[0])
        
        # 删除索引记录
        cursor.execute("DELETE FROM crewai_configs WHERE config_id = ?", (config_id,))
        conn.commit()
        conn.close()
        
        # 删除文件
        if file_path.exists():
            file_path.unlink()
        
        logger.info(f"✅ 配置已删除: {config_id}")
        return True
    
    def search_configs(self, 
                      name_pattern: Optional[str] = None,
                      tags: Optional[List[str]] = None,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索配置
        
        Args:
            name_pattern: 名称模糊匹配模式
            tags: 标签列表
            date_from: 开始日期（ISO格式）
            date_to: 结束日期（ISO格式）
            
        Returns:
            配置列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM crewai_configs WHERE 1=1"
        params = []
        
        if name_pattern:
            query += " AND name LIKE ?"
            params.append(f"%{name_pattern}%")
        
        if date_from:
            query += " AND created_at >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND created_at <= ?"
            params.append(date_to)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        configs = []
        for row in results:
            config = {
                "config_id": row[0],
                "name": row[1],
                "description": row[2],
                "business_process": row[3],
                "file_path": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "tags": json.loads(row[7] or "[]"),
                "metadata": json.loads(row[8] or "{}")
            }
            configs.append(config)
        
        logger.debug(f"🔍 搜索到 {len(configs)} 个配置")
        return configs
    
    def list_all_configs(self) -> List[Dict[str, Any]]:
        """
        列出所有配置
        
        Returns:
            配置列表
        """
        return self.search_configs()
    
    def update_config_tags(self, config_id: str, tags: List[str]) -> bool:
        """
        更新配置标签
        
        Args:
            config_id: 配置ID
            tags: 新的标签列表
            
        Returns:
            是否成功更新
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE crewai_configs 
            SET tags = ?, updated_at = ?
            WHERE config_id = ?
        """, (json.dumps(tags), timestamp, config_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"✅ 配置标签已更新: {config_id}")
        else:
            logger.warning(f"❌ 未找到配置ID: {config_id}")
        
        return success
    
    def get_config_stats(self) -> Dict[str, Any]:
        """
        获取配置统计信息
        
        Returns:
            统计信息字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总配置数
        cursor.execute("SELECT COUNT(*) FROM crewai_configs")
        total_count = cursor.fetchone()[0]
        
        # 今日新增
        today = datetime.now().date().isoformat()
        cursor.execute("SELECT COUNT(*) FROM crewai_configs WHERE DATE(created_at) = ?", (today,))
        today_count = cursor.fetchone()[0]
        
        # 最近配置
        cursor.execute("SELECT name, created_at FROM crewai_configs ORDER BY created_at DESC LIMIT 5")
        recent = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_configs": total_count,
            "today_new": today_count,
            "recent_configs": [{"name": r[0], "created_at": r[1]} for r in recent]
        }


# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> CrewAIConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = CrewAIConfigManager()
    return _config_manager


if __name__ == "__main__":
    # 测试代码
    manager = CrewAIConfigManager()
    
    # 测试保存配置
    test_config = {
        "crewai_config": {
            "name": "测试团队",
            "description": "这是一个测试团队",
            "agents": [{"name": "测试Agent", "role": "测试员"}],
            "tasks": [{"name": "测试任务", "description": "执行测试"}]
        },
        "business_process": "测试业务流程",
        "version": "1.0"
    }
    
    config_id = manager.save_config(test_config, tags=["test", "demo"])
    print(f"保存配置ID: {config_id}")
    
    # 测试获取配置
    loaded_config = manager.get_config(config_id)
    print(f"加载配置: {loaded_config['crewai_config']['name']}")
    
    # 测试搜索
    results = manager.search_configs(name_pattern="测试")
    print(f"搜索结果: {len(results)} 个配置")
    
    # 测试统计
    stats = manager.get_config_stats()
    print(f"统计信息: {stats}")

