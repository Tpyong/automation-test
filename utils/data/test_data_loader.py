"""
测试数据加载器
支持缓存机制，避免重复加载和解析
"""

import os
from typing import Any, Dict, List

from utils.common.logger import get_logger
from utils.data.data_cache import get_data_cache

logger = get_logger(__name__)


class TestDataLoader:
    """测试数据加载器"""

    @staticmethod
    def load_yaml_file(file_path: str) -> Dict[str, Any]:
        """
        加载YAML文件（带缓存）

        Args:
            file_path: YAML文件路径

        Returns:
            解析后的数据字典
        """
        cache = get_data_cache()
        return cache.load_yaml_with_cache(file_path)

    @staticmethod
    def get_test_data(data_file: str, section: str) -> List[Dict[str, Any]]:
        """
        获取指定section的测试数据（带缓存）

        Args:
            data_file: 数据文件名称（不含路径）
            section: 数据section名称

        Returns:
            测试数据列表
        """
        data_path = os.path.join("data", "test_data", data_file)
        if not os.path.exists(data_path):
            logger.error(f"测试数据文件不存在: {data_path}")
            return []

        cache = get_data_cache()
        return cache.get_cached_data(data_path, section)

    @staticmethod
    def get_login_data(section: str) -> List[Dict[str, Any]]:
        """
        获取登录测试数据

        Args:
            section: 数据section名称 ('login_success' 或 'login_failure')

        Returns:
            登录测试数据列表
        """
        return TestDataLoader.get_test_data("login_data_example.yaml", section)

    @staticmethod
    def clear_cache():
        """清除测试数据缓存"""
        cache = get_data_cache()
        cache.clear_all_cache()
        logger.info("测试数据缓存已清除")

    @staticmethod
    def get_cache_stats() -> Dict[str, int]:
        """
        获取缓存统计信息

        Returns:
            缓存统计信息
        """
        cache = get_data_cache()
        return cache.get_cache_stats()
