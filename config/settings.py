import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from core.utils.logger import get_logger

logger = get_logger(__name__)


def load_env_file(env_file: str = ".env") -> None:
    """手动加载 .env 文件，自动解密加密值

    优先从项目根目录加载，如果不存在则从 config/envs/ 目录加载
    """
    decrypt_func: Callable[[str], str]
    try:
        from core.utils.secrets_manager import decrypt_value

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
    def __init__(self, env: Optional[str] = None, validate: bool = True):
        """
        初始化配置

        Args:
            env: 环境名称
            validate: 是否验证配置
        """
        # 从环境变量获取当前环境，默认为 development
        self.env = env or os.getenv("TEST_ENV", "development")

        # 加载对应环境的配置文件
        self._load_env_files()

        # 加载配置
        self.base_url = os.getenv("BASE_URL", "https://www.example.com")
        self.browser_type = os.getenv("BROWSER", "chromium")
        self.headless = os.getenv("HEADLESS", "false").lower() == "true"
        self.slow_mo = int(os.getenv("SLOW_MO", "0"))
        self.timeout = int(os.getenv("TIMEOUT", "30000"))

        viewport_width = int(os.getenv("VIEWPORT_WIDTH", "1920"))
        viewport_height = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
        self.viewport = {"width": viewport_width, "height": viewport_height}

        self.api_base_url = os.getenv("API_BASE_URL", "https://api.example.com")
        self.api_timeout = int(os.getenv("API_TIMEOUT", "30000"))

        # 录屏配置
        self.video_enabled = os.getenv("VIDEO_ENABLED", "false").lower() == "true"
        self.video_size = {"width": viewport_width, "height": viewport_height}

        # 数据库配置（可选）
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "3306"))
        self.db_user = os.getenv("DB_USER", "root")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_name = os.getenv("DB_NAME", "test_db")

        # 验证配置
        if validate:
            self._validate_config()

    def _load_env_files(self) -> None:
        """加载环境配置文件，优先级：.env.{env} > .env"""
        # 首先加载基础 .env 文件
        load_env_file(".env")

        # 然后加载特定环境的配置文件（覆盖基础配置）
        env_file = f".env.{self.env}"
        load_env_file(env_file)

    def _validate_config(self) -> None:
        """验证配置的正确性"""
        errors: List[str] = []

        # 验证环境名称
        valid_envs = ["development", "testing", "staging", "production"]
        if self.env not in valid_envs:
            errors.append(f"无效的环境名称: {self.env}，有效值: {valid_envs}")

        # 验证浏览器类型
        valid_browsers = ["chromium", "firefox", "webkit"]
        if self.browser_type not in valid_browsers:
            errors.append(f"无效的浏览器类型: {self.browser_type}，有效值: {valid_browsers}")

        # 验证 URL 格式
        if not self._is_valid_url(self.base_url):
            errors.append(f"无效的 BASE_URL 格式: {self.base_url}")

        if not self._is_valid_url(self.api_base_url):
            errors.append(f"无效的 API_BASE_URL 格式: {self.api_base_url}")

        # 验证数值范围
        if self.timeout < 1000 or self.timeout > 300000:
            errors.append(f"TIMEOUT 应该在 1000-300000 之间，当前: {self.timeout}")

        if self.slow_mo < 0 or self.slow_mo > 10000:
            errors.append(f"SLOW_MO 应该在 0-10000 之间，当前: {self.slow_mo}")

        if self.api_timeout < 1000 or self.api_timeout > 300000:
            errors.append(f"API_TIMEOUT 应该在 1000-300000 之间，当前: {self.api_timeout}")

        # 验证视口大小
        if self.viewport["width"] < 320 or self.viewport["width"] > 3840:
            errors.append(f"VIEWPORT_WIDTH 应该在 320-3840 之间，当前: {self.viewport['width']}")

        if self.viewport["height"] < 240 or self.viewport["height"] > 2160:
            errors.append(f"VIEWPORT_HEIGHT 应该在 240-2160 之间，当前: {self.viewport['height']}")

        # 验证数据库端口
        if self.db_port < 1 or self.db_port > 65535:
            errors.append(f"DB_PORT 应该在 1-65535 之间，当前: {self.db_port}")

        # 如果有错误，抛出异常或记录警告
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join([f"  - {e}" for e in errors])
            logger.warning(error_msg)

            # 如果是开发环境，继续运行；其他环境抛出异常
            if not self.is_development:
                raise ConfigValidationError(error_msg)
        else:
            logger.info("配置验证通过")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """验证 URL 格式是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要（用于日志记录）"""
        return {
            "env": self.env,
            "browser": self.browser_type,
            "headless": self.headless,
            "viewport": self.viewport,
            "base_url": self.base_url,
            "api_base_url": self.api_base_url,
            "video_enabled": self.video_enabled,
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
