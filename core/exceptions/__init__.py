"""
异常模块
定义测试中使用的异常类
"""

from typing import Any, Dict, Optional


class TestError(Exception):
    """测试错误基类"""

    def __init__(self, message: str, details: Optional[Dict[Any, Any]] = None):
        """
        初始化测试错误

        Args:
            message: 错误消息
            details: 错误详情
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """返回错误的字符串表示"""
        if self.details:
            return f"{self.__class__.__name__}: {self.message} (详情: {self.details})"
        return f"{self.__class__.__name__}: {self.message}"


class PageError(TestError):
    """页面错误"""

    pass


class LocatorError(TestError):
    """定位器错误"""

    pass


class APIError(TestError):
    """API 错误"""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[Any, Any]] = None, details: Optional[Dict[Any, Any]] = None):
        """
        初始化 API 错误

        Args:
            message: 错误消息
            status_code: HTTP 状态码
            response: API 响应
            details: 错误详情
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        """返回错误的字符串表示"""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.status_code:
            parts.append(f"状态码: {self.status_code}")
        if self.response:
            parts.append(f"响应: {self.response}")
        if self.details:
            parts.append(f"详情: {self.details}")
        return " (".join(parts)


class AuthenticationError(APIError):
    """认证错误"""

    pass


class AuthorizationError(APIError):
    """授权错误"""

    pass


class ValidationError(TestError):
    """验证错误"""

    def __init__(self, message: str, errors: Optional[Dict[Any, Any]] = None, details: Optional[Dict[Any, Any]] = None):
        """
        初始化验证错误

        Args:
            message: 错误消息
            errors: 验证错误详情
            details: 错误详情
        """
        super().__init__(message, details)
        self.errors = errors or {}

    def __str__(self) -> str:
        """返回错误的字符串表示"""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.errors:
            parts.append(f"验证错误: {self.errors}")
        if self.details:
            parts.append(f"详情: {self.details}")
        return " (".join(parts)


class TimeoutError(TestError):
    """超时错误"""

    def __init__(self, message: str, timeout: Optional[int] = None, details: Optional[Dict[Any, Any]] = None):
        """
        初始化超时错误

        Args:
            message: 错误消息
            timeout: 超时时间（秒）
            details: 错误详情
        """
        super().__init__(message, details)
        self.timeout = timeout

    def __str__(self) -> str:
        """返回错误的字符串表示"""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.timeout:
            parts.append(f"超时时间: {self.timeout}秒")
        if self.details:
            parts.append(f"详情: {self.details}")
        return " (".join(parts)


class ConfigurationError(TestError):
    """配置错误"""

    pass


class DatabaseError(TestError):
    """数据库错误"""

    pass


class NetworkError(TestError):
    """网络错误"""

    pass


class MockServerError(TestError):
    """Mock 服务器错误"""

    pass
