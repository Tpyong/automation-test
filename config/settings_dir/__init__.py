"""
配置设置模块
"""

from .base.base import *
from .development.development import *
from .testing.testing import *
from .production.production import *

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
