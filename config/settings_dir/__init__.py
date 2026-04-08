"""
配置设置模块
"""

from .base.base import *
from .development.development import *
from .production.production import *
from .testing.testing import *

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
