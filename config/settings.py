import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from config.validators import validate_config
from utils.common.logger import get_logger

logger = get_logger(__name__)


def load_env_file(env_file: str = ".env") -> None:
    """手动加载 .env 文件，自动解密加密值

    优先从项目根目录加载，如果不存在则从 config/envs/ 目录加载
    """
    decrypt_func: Callable[[str], str]
    try:
        from utils.security.secrets_manager import decrypt_value

        decrypt_func = decrypt_value
    except ImportError:
        decrypt_func = lambda x: x

    # 优先从项目根目录加载
    project_root = Path(__file__).parent.parent
    env_path = project_root / env_file

    # 如果根目录不存在，尝试从 config/envs/ 目录加载
    if not env_path.exists():
        env_path = project_root / "config" / "envs" / env_file

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # 自动解密加密的值
                    decrypted_value = decrypt_func(value)
                    os.environ[key] = decrypted_value


class ConfigValidationError(Exception):
    """配置验证错误"""

    pass


class Settings:
    def __init__(self, env: Optional[str] = None, validate: bool = True, config_mode: str = "strict"):
        """
        初始化配置

        Args:
            env: 环境名称
            validate: 是否验证配置
            config_mode: 配置模式 (strict/relaxed)
        """
        # 从环境变量获取当前环境，默认为 development
        self.env = env or os.getenv("TEST_ENV", "development")

        # 配置模式
        self.config_mode = config_mode or os.getenv("CONFIG_MODE", "strict")

        # 配置变更日志
        self.config_changes: List[str] = []

        # 加载对应环境的配置文件
        self._load_env_files()

        # 加载配置
        self._load_configs()

        # 验证配置
        if validate:
            self._validate_config()

        # 记录初始配置
        self._log_config_summary()

    def _load_env_files(self) -> None:
        """加载环境配置文件，优先级：.env.{env} > .env > .env.base"""
        # 首先加载基础配置文件（所有环境的默认值）
        load_env_file(".env.base")

        # 然后加载项目根目录的 .env 文件（项目级配置）
        load_env_file(".env")

        # 最后加载特定环境的配置文件（环境特定配置，覆盖前面的配置）
        env_file = f".env.{self.env}"
        load_env_file(env_file)

    def _load_configs(self) -> None:
        """加载所有配置项"""
        # 基础配置
        self.base_url = self._get_env("BASE_URL", "https://www.example.com")
        self.browser_type = self._get_env("BROWSER", "chromium")
        self.headless = self._get_env("HEADLESS", "false").lower() == "true"
        self.slow_mo = int(self._get_env("SLOW_MO", "0"))
        self.timeout = int(self._get_env("TIMEOUT", "30000"))

        # 视口配置
        viewport_width = int(self._get_env("VIEWPORT_WIDTH", "1920"))
        viewport_height = int(self._get_env("VIEWPORT_HEIGHT", "1080"))
        self.viewport = {"width": viewport_width, "height": viewport_height}

        # API 配置
        self.api_base_url = self._get_env("API_BASE_URL", "https://api.example.com")
        self.api_timeout = int(self._get_env("API_TIMEOUT", "30000"))

        # 录屏配置
        self.video_enabled = self._get_env("VIDEO_ENABLED", "false").lower() == "true"
        self.video_size = {"width": viewport_width, "height": viewport_height}

        # 数据库配置（可选）
        self.db_host = self._get_env("DB_HOST", "localhost")
        self.db_port = int(self._get_env("DB_PORT", "3306"))
        self.db_user = self._get_env("DB_USER", "root")
        self.db_password = self._get_env("DB_PASSWORD", "")
        self.db_name = self._get_env("DB_NAME", "test_db")

        # pytest-playwright 相关配置
        self.playwright_slowmo = int(self._get_env("PLAYWRIGHT_SLOWMO", str(self.slow_mo)))
        self.playwright_timeout = int(self._get_env("PLAYWRIGHT_TIMEOUT", str(self.timeout)))
        self.playwright_headless = self._get_env("PLAYWRIGHT_HEADLESS", str(self.headless)).lower() == "true"
        self.playwright_browser = self._get_env("PLAYWRIGHT_BROWSER", self.browser_type)

        # 截图配置
        self.screenshot_enabled = self._get_env("SCREENSHOT_ENABLED", "true").lower() == "true"
        self.screenshot_path = self._get_env("SCREENSHOT_PATH", "screenshots")

        # Allure 报告配置
        self.allure_enabled = self._get_env("ALLURE_ENABLED", "true").lower() == "true"
        self.allure_output_dir = self._get_env("ALLURE_OUTPUT_DIR", "allure-results")

    def _get_env(self, key: str, default: Any) -> Any:
        """获取环境变量，并记录配置变更

        Args:
            key: 环境变量键名
            default: 默认值

        Returns:
            环境变量值或默认值
        """
        value = os.getenv(key, default)
        # 移除注释部分
        if isinstance(value, str):
            value = value.split('#')[0].strip()
        if value != default:
            self.config_changes.append(f"{key}: {default} -> {value}")
        return value

    def _validate_config(self) -> None:
        """验证配置的正确性"""
        # 构建配置字典
        config = {
            "BASE_URL": self.base_url,
            "BROWSER": self.browser_type,
            "TIMEOUT": self.timeout,
            "VIEWPORT_WIDTH": self.viewport["width"],
            "VIEWPORT_HEIGHT": self.viewport["height"],
            "API_BASE_URL": self.api_base_url,
            "PLAYWRIGHT_BROWSER": self.playwright_browser,
        }

        # 验证环境名称
        valid_envs = ["development", "testing", "staging", "production"]
        if self.env not in valid_envs:
            error_msg = f"无效的环境名称: {self.env}，有效值: {valid_envs}"
            logger.warning(error_msg)
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError(error_msg)

        # 验证 API URL 格式
        if not self._is_valid_url(self.api_base_url):
            error_msg = f"无效的 API_BASE_URL 格式: {self.api_base_url}"
            logger.warning(error_msg)
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError(error_msg)

        # 验证数值范围
        if self.slow_mo < 0 or self.slow_mo > 10000:
            error_msg = f"SLOW_MO 应该在 0-10000 之间，当前: {self.slow_mo}"
            logger.warning(error_msg)
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError(error_msg)

        if self.api_timeout < 1000 or self.api_timeout > 300000:
            error_msg = f"API_TIMEOUT 应该在 1000-300000 之间，当前: {self.api_timeout}"
            logger.warning(error_msg)
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError(error_msg)

        # 验证数据库端口
        if self.db_port < 1 or self.db_port > 65535:
            error_msg = f"DB_PORT 应该在 1-65535 之间，当前: {self.db_port}"
            logger.warning(error_msg)
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError(error_msg)

        # 验证浏览器类型
        valid_browsers = ["chromium", "firefox", "webkit"]
        if self.playwright_browser not in valid_browsers:
            error_msg = f"无效的浏览器类型: {self.playwright_browser}，有效值: {valid_browsers}"
            logger.warning(error_msg)
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError(error_msg)

        # 验证配置模式
        valid_config_modes = ["strict", "relaxed"]
        if self.config_mode not in valid_config_modes:
            error_msg = f"无效的配置模式: {self.config_mode}，有效值: {valid_config_modes}"
            logger.warning(error_msg)
            # 强制设置为 strict 模式
            self.config_mode = "strict"
            self.config_changes.append(f"CONFIG_MODE: {self.config_mode} -> strict")

        # 使用新的配置验证器验证基本配置
        if not validate_config(config):
            if self.config_mode == "strict" and not self.is_development:
                raise ConfigValidationError("配置验证失败")

    def _is_valid_url(self, url: str) -> bool:
        """验证 URL 格式是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _log_config_summary(self) -> None:
        """记录配置摘要和变更"""
        # 记录配置摘要
        config_summary = self.get_config_summary()
        logger.info("配置加载完成，环境: %s, 模式: %s", self.env, self.config_mode)
        logger.debug("配置摘要: %s", config_summary)

        # 记录配置变更
        if self.config_changes:
            logger.info("配置变更:")
            for change in self.config_changes:
                logger.info("  - %s", change)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置项键名
            default: 默认值

        Returns:
            配置项值或默认值
        """
        return getattr(self, key, default)

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要（用于日志记录）"""
        return {
            "env": self.env,
            "config_mode": self.config_mode,
            "browser": self.browser_type,
            "playwright_browser": self.playwright_browser,
            "headless": self.headless,
            "playwright_headless": self.playwright_headless,
            "viewport": self.viewport,
            "base_url": self.base_url,
            "api_base_url": self.api_base_url,
            "video_enabled": self.video_enabled,
            "screenshot_enabled": self.screenshot_enabled,
            "allure_enabled": self.allure_enabled,
        }

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.env == "development"

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.env == "testing"

    @property
    def is_staging(self) -> bool:
        """是否为预发布环境"""
        return self.env == "staging"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.env == "production"

    @property
    def is_strict_mode(self) -> bool:
        """是否为严格配置模式"""
        return self.config_mode == "strict"

    @property
    def is_relaxed_mode(self) -> bool:
        """是否为宽松配置模式"""
        return self.config_mode == "relaxed"
