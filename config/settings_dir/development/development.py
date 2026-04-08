"""
开发环境配置
继承基础配置并覆盖特定的配置项
"""

from ..base import *

# 开发环境特定配置
BASE_URL = "https://dev.example.com"
HEADLESS = False  # 开发环境不使用无头模式
SLOW_MO = 100  # 开发环境添加操作延迟，便于调试
