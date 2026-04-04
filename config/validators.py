"""
配置验证器
用于验证配置的正确性和完整性
"""

import re
from typing import Dict, Any, List

from utils.common.logger import get_logger

logger = get_logger(__name__)


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_base_url(base_url: str) -> bool:
        """
        验证基础 URL

        Args:
            base_url: 基础 URL

        Returns:
            bool: 是否有效
        """
        if not base_url:
            logger.error("基础 URL 不能为空")
            return False
        
        # 验证 URL 格式
        url_pattern = re.compile(r'^https?://[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}([a-zA-Z0-9-._~:/?#\[\]@!$&\'()*+,;=.]+)?$')
        if not url_pattern.match(base_url):
            logger.error(f"无效的基础 URL: {base_url}")
            return False
        
        return True

    @staticmethod
    def validate_browser(browser: str) -> bool:
        """
        验证浏览器类型

        Args:
            browser: 浏览器类型

        Returns:
            bool: 是否有效
        """
        valid_browsers = ["chromium", "firefox", "webkit"]
        if browser not in valid_browsers:
            logger.error(f"无效的浏览器类型: {browser}，有效值: {valid_browsers}")
            return False
        
        return True

    @staticmethod
    def validate_timeout(timeout: int) -> bool:
        """
        验证超时时间

        Args:
            timeout: 超时时间（毫秒）

        Returns:
            bool: 是否有效
        """
        if not isinstance(timeout, int):
            logger.error("超时时间必须是整数")
            return False
        
        if timeout <= 0:
            logger.error("超时时间必须大于 0")
            return False
        
        return True

    @staticmethod
    def validate_viewport(viewport_width: int, viewport_height: int) -> bool:
        """
        验证视口大小

        Args:
            viewport_width: 视口宽度
            viewport_height: 视口高度

        Returns:
            bool: 是否有效
        """
        if not isinstance(viewport_width, int) or not isinstance(viewport_height, int):
            logger.error("视口大小必须是整数")
            return False
        
        if viewport_width <= 0 or viewport_height <= 0:
            logger.error("视口大小必须大于 0")
            return False
        
        return True

    @staticmethod
    def validate_environment(environment: str) -> bool:
        """
        验证环境类型

        Args:
            environment: 环境类型

        Returns:
            bool: 是否有效
        """
        valid_environments = ["development", "testing", "production"]
        if environment not in valid_environments:
            logger.error(f"无效的环境类型: {environment}，有效值: {valid_environments}")
            return False
        
        return True

    @staticmethod
    def validate_database_config(db_config: Dict[str, Any]) -> bool:
        """
        验证数据库配置

        Args:
            db_config: 数据库配置

        Returns:
            bool: 是否有效
        """
        if not isinstance(db_config, dict):
            logger.error("数据库配置必须是字典")
            return False
        
        required_fields = ["host", "port", "database"]
        for field in required_fields:
            if field not in db_config:
                logger.error(f"数据库配置缺少必要字段: {field}")
                return False
        
        if not isinstance(db_config.get("port"), int) or db_config.get("port") <= 0:
            logger.error("数据库端口必须是正整数")
            return False
        
        return True

    @staticmethod
    def validate_report_config(report_config: Dict[str, Any]) -> bool:
        """
        验证报告配置

        Args:
            report_config: 报告配置

        Returns:
            bool: 是否有效
        """
        if not isinstance(report_config, dict):
            logger.error("报告配置必须是字典")
            return False
        
        if "enabled" in report_config and not isinstance(report_config["enabled"], bool):
            logger.error("报告启用状态必须是布尔值")
            return False
        
        return True

    @staticmethod
    def validate_parallel_config(parallel_config: Dict[str, Any]) -> bool:
        """
        验证并行测试配置

        Args:
            parallel_config: 并行测试配置

        Returns:
            bool: 是否有效
        """
        if not isinstance(parallel_config, dict):
            logger.error("并行测试配置必须是字典")
            return False
        
        if "enabled" in parallel_config and not isinstance(parallel_config["enabled"], bool):
            logger.error("并行测试启用状态必须是布尔值")
            return False
        
        if "workers" in parallel_config:
            if not isinstance(parallel_config["workers"], int) or parallel_config["workers"] <= 0:
                logger.error("并行测试工作线程数必须是正整数")
                return False
        
        return True

    @staticmethod
    def validate_log_config(log_config: Dict[str, Any]) -> bool:
        """
        验证日志配置

        Args:
            log_config: 日志配置

        Returns:
            bool: 是否有效
        """
        if not isinstance(log_config, dict):
            logger.error("日志配置必须是字典")
            return False
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if "level" in log_config and log_config["level"] not in valid_log_levels:
            logger.error(f"无效的日志级别: {log_config['level']}，有效值: {valid_log_levels}")
            return False
        
        return True

    @staticmethod
    def validate_all(config: Dict[str, Any]) -> List[str]:
        """
        验证所有配置项

        Args:
            config: 配置字典

        Returns:
            List[str]: 错误信息列表
        """
        errors = []

        # 验证基础 URL
        if "BASE_URL" in config:
            if not ConfigValidator.validate_base_url(config["BASE_URL"]):
                errors.append("无效的基础 URL")

        # 验证浏览器类型
        if "BROWSER" in config:
            if not ConfigValidator.validate_browser(config["BROWSER"]):
                errors.append("无效的浏览器类型")

        # 验证超时时间
        if "TIMEOUT" in config:
            if not ConfigValidator.validate_timeout(config["TIMEOUT"]):
                errors.append("无效的超时时间")

        # 验证视口大小
        if "VIEWPORT_WIDTH" in config and "VIEWPORT_HEIGHT" in config:
            if not ConfigValidator.validate_viewport(
                config["VIEWPORT_WIDTH"], config["VIEWPORT_HEIGHT"]
            ):
                errors.append("无效的视口大小")

        # 验证环境类型
        if "ENVIRONMENT" in config:
            if not ConfigValidator.validate_environment(config["ENVIRONMENT"]):
                errors.append("无效的环境类型")

        # 验证数据库配置
        if "DATABASE" in config:
            if not ConfigValidator.validate_database_config(config["DATABASE"]):
                errors.append("无效的数据库配置")

        # 验证报告配置
        if "REPORT" in config:
            if not ConfigValidator.validate_report_config(config["REPORT"]):
                errors.append("无效的报告配置")

        # 验证并行测试配置
        if "PARALLEL" in config:
            if not ConfigValidator.validate_parallel_config(config["PARALLEL"]):
                errors.append("无效的并行测试配置")

        # 验证日志配置
        if "LOG" in config:
            if not ConfigValidator.validate_log_config(config["LOG"]):
                errors.append("无效的日志配置")

        return errors


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置

    Args:
        config: 配置字典

    Returns:
        bool: 是否有效
    """
    errors = ConfigValidator.validate_all(config)
    
    if errors:
        for error in errors:
            logger.error(error)
        return False
    
    logger.info("配置验证通过")
    return True
