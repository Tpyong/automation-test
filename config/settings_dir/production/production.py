"""
生产环境配置
继承基础配置并覆盖特定的配置项
"""

from ..base import *

# 生产环境特定配置
BASE_URL = "https://www.example.com"
HEADLESS = True  # 生产环境使用无头模式
VIDEO_ENABLED = False  # 生产环境禁用视频录制，提高性能
