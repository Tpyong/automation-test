"""
测试环境配置
继承基础配置并覆盖特定的配置项
"""

from ..base import *

# 测试环境特定配置
BASE_URL = "https://test.example.com"
HEADLESS = True  # 测试环境使用无头模式
VIDEO_ENABLED = True  # 测试环境启用视频录制