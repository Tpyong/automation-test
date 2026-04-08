"""
附件管理器
负责将测试附件（截图、视频等）附加到 Allure 报告
"""
import os
from typing import Any, Optional

import allure

from tests.utils.video_manager import VideoManager
from utils.common.logger import get_logger

logger = get_logger(__name__)


class AttachmentManager:
    """附件管理器"""

    def __init__(self, video_manager: Optional[VideoManager] = None):
        """
        初始化附件管理器

        Args:
            video_manager: 视频管理器实例
        """
        self.video_manager = video_manager or VideoManager()

    def attach_screenshot(self, screenshot_path: Optional[str], test_name: str) -> None:
        """
        附加截图到 Allure 报告

        Args:
            screenshot_path: 截图文件路径
            test_name: 测试名称
        """
        if not screenshot_path or not os.path.exists(screenshot_path):
            logger.debug("截图路径不存在或为空: %s", screenshot_path)
            return

        try:
            file_size = os.path.getsize(screenshot_path)
            logger.debug("截图文件存在，大小: %s bytes", file_size)
            allure.attach.file(
                screenshot_path,
                name=f"{test_name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.debug("截图已附加到 Allure 报告: %s", screenshot_path)
        except Exception as e:
            logger.debug("附加截图到 Allure 报告时出错: %s", e)

    def attach_video(self, video_dir: Optional[str], test_name: str, video_enabled: bool) -> None:
        """
        附加视频到 Allure 报告

        Args:
            video_dir: 视频目录
            test_name: 测试名称
            video_enabled: 是否启用视频功能
        """
        if not video_enabled:
            logger.info("视频功能未启用")
            return

        if not video_dir:
            logger.warning("视频目录为空")
            return

        video_path = self._find_video(video_dir, test_name)

        if video_path:
            self._attach_video_file(video_path, test_name)
        else:
            logger.warning("未找到视频文件")

    def _find_video(self, video_dir: str, test_name: str) -> Optional[str]:
        """
        查找视频文件

        Args:
            video_dir: 视频目录
            test_name: 测试名称

        Returns:
            视频文件路径，如果未找到则返回 None
        """
        # 首先在原始视频目录中查找
        video_path = self.video_manager.find_video_file(video_dir, test_name)
        if video_path:
            return video_path

        # 如果未找到，尝试在套件目录中查找
        return self.video_manager.find_video_in_suite_dir(video_dir, test_name)

    def _attach_video_file(self, video_path: str, test_name: str) -> None:
        """
        附加视频文件到 Allure 报告

        Args:
            video_path: 视频文件路径
            test_name: 测试名称
        """
        try:
            file_size = os.path.getsize(video_path)
            logger.info("视频文件存在，大小: %s bytes", file_size)
            allure.attach.file(
                video_path,
                name=f"{test_name}_video",
                attachment_type=allure.attachment_type.WEBM,
            )
            logger.info("视频文件已附加到 Allure 报告: %s", video_path)
        except Exception as e:
            logger.error("附加视频文件到 Allure 报告时出错: %s", e)

    def attach_all_artifacts(self, item: Any) -> None:
        """
        附加所有测试附件到 Allure 报告

        Args:
            item: pytest 测试项
        """
        test_name = self._get_test_name(item)

        # 附加截图
        screenshot_path = getattr(item, "screenshot_path", None)
        self.attach_screenshot(screenshot_path, test_name)

        # 附加视频
        from config.settings import Settings

        settings = Settings()
        video_dir = getattr(item, "video_dir", None)
        self.attach_video(video_dir, test_name, settings.video_enabled)

    def _get_test_name(self, item: Any) -> str:
        """
        获取测试名称

        Args:
            item: pytest 测试项

        Returns:
            测试名称
        """
        try:
            return getattr(item, "test_name", item.nodeid.split("::")[-1].replace("/", "_").replace("\\", "_"))
        except Exception as e:
            logger.debug("获取测试名称时出错: %s", e)
            return "unknown_test"