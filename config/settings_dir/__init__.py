"""
配置设置模块
"""

from .base import *
from .development import *
from .testing import *
from .production import *

__all__ = [
    "BASE_URL",
    "BROWSER",
    "HEADLESS",
    "SLOW_MO",
    "TIMEOUT",
    "VIEWPORT_WIDTH",
    "VIEWPORT_HEIGHT",
    "VIDEO_ENABLED",
]
