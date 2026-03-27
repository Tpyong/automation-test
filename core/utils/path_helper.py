"""
路径工具模块
提供统一的路径管理和文件操作
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.utils.logger import get_logger

logger = get_logger(__name__)


class PathHelper:
    """路径辅助类"""

    @staticmethod
    def get_screenshot_path(name: str, date_str: Optional[str] = None) -> str:
        """
        获取截图文件路径

        Args:
            name: 截图名称
            date_str: 日期字符串（可选，默认今天）

        Returns:
            完整的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Path("screenshots") / f"{name}_{timestamp}.png"
        path.parent.mkdir(exist_ok=True)
        return str(path)

    @staticmethod
    def get_video_path(name: str, date_str: Optional[str] = None) -> str:
        """
        获取视频文件路径

        Args:
            name: 视频名称
            date_str: 日期字符串（可选，默认今天）

        Returns:
            完整的文件路径
        """
        date_str = date_str or datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Path("videos") / date_str / f"{name}_{timestamp}.webm"
        path.parent.mkdir(exist_ok=True, parents=True)
        return str(path)

    @staticmethod
    def get_report_dir() -> Path:
        """获取报告目录"""
        path = Path("reports")
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def safe_rename(src: str, dst: str, max_retries: int = 3, retry_delay: float = 0.5) -> bool:
        """
        安全重命名文件，支持重试

        Args:
            src: 源文件路径
            dst: 目标文件路径
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）

        Returns:
            是否成功
        """
        for attempt in range(max_retries):
            try:
                os.rename(src, dst)
                return True
            except OSError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"重命名失败（尝试 {attempt + 1}/{max_retries}）: {e}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"重命名最终失败: {e}")
                    return False
        return False
