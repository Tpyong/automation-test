"""
基础配置
包含所有环境的默认配置
"""

BASE_URL = "https://www.example.com"
API_BASE_URL = "https://api.example.com"
BROWSER = "chromium"
HEADLESS = True
SLOW_MO = 0
TIMEOUT = 30000
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
VIDEO_ENABLED = True

# 配置模式 (strict/relaxed)
CONFIG_MODE = "strict"

# pytest-playwright 配置
PLAYWRIGHT_BROWSER = "chromium"
PLAYWRIGHT_BROWSERS = "chromium,firefox"
PLAYWRIGHT_HEADLESS = False
PLAYWRIGHT_SLOWMO = 0
PLAYWRIGHT_TIMEOUT = 30000

# 截图配置
SCREENSHOT_ENABLED = True
SCREENSHOT_PATH = "screenshots"

# Allure 报告配置
ALLURE_ENABLED = True
ALLURE_OUTPUT_DIR = "allure-results"

# 数据库配置
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "test_db"
