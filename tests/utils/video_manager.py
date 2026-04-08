"""
视频文件管理器
负责视频文件的查找、清理和重命名
"""
import os
from datetime import datetime
from typing import List, Optional

from utils.common.logger import get_logger

logger = get_logger(__name__)


class VideoManager:
    """视频文件管理器"""

    def __init__(self, video_root_dir: Optional[str] = None):
        """
        初始化视频管理器

        Args:
            video_root_dir: 视频根目录，默认为 reports/videos/{date}
        """
        self.video_root_dir = video_root_dir or os.path.join(
            "reports", "videos", datetime.now().strftime("%Y%m%d")
        )

    def clean_empty_videos(self) -> None:
        """清理空视频文件"""
        if not os.path.exists(self.video_root_dir):
            return

        for suite_dir in os.listdir(self.video_root_dir):
            suite_path = os.path.join(self.video_root_dir, suite_dir)
            if os.path.isdir(suite_path):
                self._clean_suite_videos(suite_path)

    def _clean_suite_videos(self, suite_path: str) -> None:
        """清理套件目录中的空视频"""
        for test_dir in os.listdir(suite_path):
            test_path = os.path.join(suite_path, test_dir)
            if os.path.isdir(test_path):
                video_files = [f for f in os.listdir(test_path) if f.endswith(".webm")]
                non_empty_videos = []

                for video_file in video_files:
                    video_path = os.path.join(test_path, video_file)
                    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                        non_empty_videos.append(video_file)
                    else:
                        self._remove_video_file(video_path)

                if non_empty_videos:
                    self._rename_videos(test_path, test_dir, non_empty_videos)

    def _remove_video_file(self, video_path: str) -> None:
        """删除视频文件"""
        try:
            os.remove(video_path)
            logger.info("已删除空视频文件: %s", os.path.basename(video_path))
        except Exception as e:
            logger.warning("删除空视频文件时出错: %s", e)

    def _rename_videos(self, test_path: str, test_dir: str, video_files: List[str]) -> None:
        """重命名视频文件"""
        test_name_part = self._extract_test_name(test_dir)

        for video_file in video_files:
            original_video_path = os.path.join(test_path, video_file)
            mtime = os.path.getmtime(original_video_path)
            timestamp = datetime.fromtimestamp(mtime).strftime("%H%M%S")
            new_video_name = f"{test_name_part}_{timestamp}.webm"
            new_video_path = os.path.join(os.path.dirname(test_path), new_video_name)

            self._safe_rename_video(original_video_path, new_video_path)

    def _extract_test_name(self, test_dir: str) -> str:
        """从测试目录名提取测试名称"""
        test_name_parts = test_dir.split("_")
        timestamp_start_index = -1

        for i, part in enumerate(reversed(test_name_parts)):
            if len(part) == 6 and part.isdigit():
                timestamp_start_index = len(test_name_parts) - i - 2
                break

        if timestamp_start_index > 0:
            return "_".join(test_name_parts[:timestamp_start_index])
        else:
            last_underscore = test_dir.rfind("_")
            return test_dir[:last_underscore] if last_underscore > 0 else test_dir

    def _safe_rename_video(self, src: str, dst: str) -> None:
        """安全重命名视频文件"""
        try:
            if os.path.exists(dst):
                os.remove(dst)
                logger.info("已删除已存在的视频文件: %s", os.path.basename(dst))
            os.rename(src, dst)
            logger.info("视频文件已移动并重命名: %s", os.path.basename(dst))
        except Exception as e:
            logger.error("移动并重命名视频文件时出错: %s", e)

    def clean_empty_directories(self) -> None:
        """清理空目录"""
        if not os.path.exists(self.video_root_dir):
            return

        for suite_dir in os.listdir(self.video_root_dir):
            suite_path = os.path.join(self.video_root_dir, suite_dir)
            if os.path.isdir(suite_path):
                self._clean_test_directories(suite_path)
                self._clean_suite_directory(suite_path)

    def _clean_test_directories(self, suite_path: str) -> None:
        """清理测试目录"""
        for test_dir in os.listdir(suite_path):
            test_path = os.path.join(suite_path, test_dir)
            if os.path.isdir(test_path) and not os.listdir(test_path):
                self._remove_directory(test_path)

    def _clean_suite_directory(self, suite_path: str) -> None:
        """清理套件目录"""
        if not os.listdir(suite_path):
            self._remove_directory(suite_path)

    def _remove_directory(self, dir_path: str) -> None:
        """删除目录"""
        try:
            os.rmdir(dir_path)
            logger.info("已删除空目录: %s", os.path.basename(dir_path))
        except Exception as e:
            logger.warning("删除空目录时出错: %s", e)

    def find_video_file(self, video_dir: str, test_name: str, max_retries: int = 3) -> Optional[str]:
        """
        查找视频文件

        Args:
            video_dir: 视频目录
            test_name: 测试名称
            max_retries: 最大重试次数

        Returns:
            视频文件路径，如果未找到则返回 None
        """
        import time

        for retry in range(max_retries):
            if os.path.exists(video_dir):
                video_files = [f for f in os.listdir(video_dir) if f.endswith(".webm")]
                if video_files:
                    for video_file in video_files:
                        video_path = os.path.join(video_dir, video_file)
                        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                            return video_path

            if retry < max_retries - 1:
                time.sleep(2)

        return None

    def find_video_in_suite_dir(self, video_dir: str, test_name: str) -> Optional[str]:
        """
        在套件目录中查找视频文件

        Args:
            video_dir: 视频目录
            test_name: 测试名称

        Returns:
            视频文件路径，如果未找到则返回 None
        """
        parts = video_dir.split(os.sep)
        if len(parts) >= 4:
            suite_dir = os.path.join(parts[0], parts[1], parts[2], parts[3])

            if os.path.exists(suite_dir):
                test_name_part = test_name.split("[")[0]
                for file in os.listdir(suite_dir):
                    if file.endswith(".webm") and test_name_part in file:
                        video_path = os.path.join(suite_dir, file)
                        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                            return video_path

        return None