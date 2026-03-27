"""
测试数据缓存管理器
实现测试数据的缓存机制，避免重复加载和解析
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from core.utils.logger import get_logger

logger = get_logger(__name__)


class DataCache:
    """测试数据缓存管理器"""

    def __init__(self, cache_dir: str = ".cache", cache_ttl: int = 3600):
        """
        初始化数据缓存

        Args:
            cache_dir: 缓存目录
            cache_ttl: 缓存过期时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = cache_ttl
        self._memory_cache: Dict[str, Any] = {}
        self._file_hashes: Dict[str, str] = {}

        logger.info(f"数据缓存初始化完成，缓存目录: {cache_dir}")

    def _get_file_hash(self, file_path: str) -> str:
        """
        获取文件哈希值

        Args:
            file_path: 文件路径

        Returns:
            文件哈希值
        """
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"计算文件哈希失败: {e}")
            return ""

    def _get_cache_key(self, file_path: str) -> str:
        """
        获取缓存键

        Args:
            file_path: 文件路径

        Returns:
            缓存键
        """
        return hashlib.md5(file_path.encode()).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径

        Args:
            cache_key: 缓存键

        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{cache_key}.json"

    def _is_cache_valid(self, cache_file: Path, source_file: str) -> bool:
        """
        检查缓存是否有效

        Args:
            cache_file: 缓存文件路径
            source_file: 源文件路径

        Returns:
            缓存是否有效
        """
        if not cache_file.exists():
            return False

        # 检查缓存是否过期
        cache_mtime = cache_file.stat().st_mtime
        if time.time() - cache_mtime > self.cache_ttl:
            return False

        # 检查源文件是否修改
        current_hash = self._get_file_hash(source_file)
        cached_hash = self._file_hashes.get(source_file, "")

        if cached_hash and current_hash != cached_hash:
            return False

        return True

    def load_yaml_with_cache(self, file_path: str) -> Dict[str, Any]:
        """
        带缓存的YAML文件加载

        Args:
            file_path: YAML文件路径

        Returns:
            解析后的数据字典
        """
        cache_key = self._get_cache_key(file_path)

        # 检查内存缓存
        if cache_key in self._memory_cache:
            logger.debug(f"从内存缓存加载: {file_path}")
            return self._memory_cache[cache_key]

        # 检查文件缓存
        cache_file = self._get_cache_file_path(cache_key)
        if self._is_cache_valid(cache_file, file_path):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._memory_cache[cache_key] = data
                logger.debug(f"从文件缓存加载: {file_path}")
                return data
            except Exception as e:
                logger.warning(f"加载缓存文件失败: {e}")

        # 加载源文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # 更新缓存
            self._memory_cache[cache_key] = data
            self._file_hashes[file_path] = self._get_file_hash(file_path)

            # 保存到文件缓存
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"保存缓存文件失败: {e}")

            logger.info(f"成功加载并缓存测试数据文件: {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载测试数据文件失败: {e}")
            return {}

    def get_cached_data(self, file_path: str, section: str) -> List[Dict[str, Any]]:
        """
        获取缓存的测试数据

        Args:
            file_path: 数据文件路径
            section: 数据section名称

        Returns:
            测试数据列表
        """
        data = self.load_yaml_with_cache(file_path)
        return data.get(section, [])

    def clear_memory_cache(self):
        """清除内存缓存"""
        self._memory_cache.clear()
        logger.info("内存缓存已清除")

    def clear_file_cache(self):
        """清除文件缓存"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("文件缓存已清除")
        except Exception as e:
            logger.error(f"清除文件缓存失败: {e}")

    def clear_all_cache(self):
        """清除所有缓存"""
        self.clear_memory_cache()
        self.clear_file_cache()
        logger.info("所有缓存已清除")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        获取缓存统计信息

        Returns:
            缓存统计信息
        """
        return {
            "memory_cache_size": len(self._memory_cache),
            "file_cache_count": len(list(self.cache_dir.glob("*.json"))),
            "cache_ttl": self.cache_ttl
        }


# 全局数据缓存实例
_data_cache: Optional[DataCache] = None


def get_data_cache(cache_dir: str = ".cache", cache_ttl: int = 3600) -> DataCache:
    """
    获取全局数据缓存实例

    Args:
        cache_dir: 缓存目录
        cache_ttl: 缓存过期时间（秒）

    Returns:
        数据缓存实例
    """
    global _data_cache
    if _data_cache is None:
        _data_cache = DataCache(cache_dir, cache_ttl)
    return _data_cache
