"""
数据驱动测试支持模块
支持 JSON、YAML、CSV 格式的测试数据
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from core.utils.logger import get_logger

logger = get_logger(__name__)


class DataProvider:
    """数据驱动测试数据提供者"""

    @staticmethod
    def load_json(file_path: str) -> List[Dict[str, Any]]:
        """
        从 JSON 文件加载测试数据

        Args:
            file_path: JSON 文件路径

        Returns:
            测试数据列表
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"成功加载 JSON 数据: {file_path}")
                return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"加载 JSON 文件失败: {file_path}, 错误: {e}")
            return []

    @staticmethod
    def load_yaml(file_path: str) -> List[Dict[str, Any]]:
        """
        从 YAML 文件加载测试数据

        Args:
            file_path: YAML 文件路径

        Returns:
            测试数据列表
        """
        if not HAS_YAML:
            logger.error("未安装 PyYAML，无法加载 YAML 文件")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                logger.info(f"成功加载 YAML 数据: {file_path}")
                return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"加载 YAML 文件失败: {file_path}, 错误: {e}")
            return []

    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        从 CSV 文件加载测试数据

        Args:
            file_path: CSV 文件路径

        Returns:
            测试数据列表
        """
        try:
            data = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            logger.info(f"成功加载 CSV 数据: {file_path}, 共 {len(data)} 条")
            return data
        except Exception as e:
            logger.error(f"加载 CSV 文件失败: {file_path}, 错误: {e}")
            return []

    @staticmethod
    def load_data(file_path: str) -> List[Dict[str, Any]]:
        """
        根据文件扩展名自动选择加载方式

        Args:
            file_path: 数据文件路径

        Returns:
            测试数据列表
        """
        ext = Path(file_path).suffix.lower()

        if ext == ".json":
            return DataProvider.load_json(file_path)
        if ext in [".yaml", ".yml"]:
            return DataProvider.load_yaml(file_path)
        if ext == ".csv":
            return DataProvider.load_csv(file_path)
        logger.error(f"不支持的文件格式: {ext}")
        return []

    @staticmethod
    def get_test_data(data_file: str) -> List[Dict[str, Any]]:
        """
        从 testdata 目录加载测试数据

        Args:
            data_file: 数据文件名（相对于 testdata 目录）

        Returns:
            测试数据列表
        """
        base_dir = Path(__file__).parent.parent.parent
        data_path = base_dir / "testdata" / data_file
        return DataProvider.load_data(str(data_path))


def pytest_parametrize(data_file: str):
    """
    Pytest 参数化装饰器，用于数据驱动测试

    使用示例:
        @pytest.mark.parametrize("test_data", pytest_parametrize("login_data.json"))
        def test_login(page, test_data):
            # 使用 test_data 进行测试
            pass
    """
    return DataProvider.get_test_data(data_file)
