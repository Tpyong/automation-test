import os
from typing import Any, Dict, List

import yaml

from core.utils.logger import get_logger

logger = get_logger(__name__)


class TestDataLoader:
    """测试数据加载器"""

    @staticmethod
    def load_yaml_file(file_path: str) -> Dict[str, Any]:
        """
        加载YAML文件

        Args:
            file_path: YAML文件路径

        Returns:
            解析后的数据字典
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            logger.info(f"成功加载测试数据文件: {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载测试数据文件失败: {e}")
            return {}

    @staticmethod
    def get_test_data(data_file: str, section: str) -> List[Dict[str, Any]]:
        """
        获取指定section的测试数据

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

        data = TestDataLoader.load_yaml_file(data_path)
        return data.get(section, [])

    @staticmethod
    def get_login_data(section: str) -> List[Dict[str, Any]]:
        """
        获取登录测试数据

        Args:
            section: 数据section名称 ('login_success' 或 'login_failure')

        Returns:
            登录测试数据列表
        """
        return TestDataLoader.get_test_data("login_data.yaml", section)
