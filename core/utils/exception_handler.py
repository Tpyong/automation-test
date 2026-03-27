import traceback
import time
from typing import Any, Optional

from core.utils.allure_helper import AllureHelper
from core.utils.logger import get_logger

logger = get_logger(__name__)


class TestException(Exception):
    """测试异常基类"""

    pass


class TestSetupException(TestException):
    """测试设置异常"""

    pass


class TestExecutionException(TestException):
    """测试执行异常"""

    pass


class TestAssertionException(TestException):
    """测试断言异常"""

    pass


class TestCleanupException(TestException):
    """测试清理异常"""

    pass


class ExceptionHandler:
    """异常处理类"""

    @staticmethod
    def handle_exception(e: Exception, context: str = "测试执行") -> None:
        """
        处理异常

        Args:
            e: 异常对象
            context: 异常上下文
        """
        # 获取异常类型和消息
        exception_type = type(e).__name__
        exception_message = str(e)

        # 获取详细的堆栈信息
        stack_trace = traceback.format_exc()

        # 记录错误日志
        logger.error(f"[{context}] 异常: {exception_type}: {exception_message}")
        logger.error(f"堆栈信息:\n{stack_trace}")

        # 添加到Allure报告
        error_details = f"异常类型: {exception_type}\n异常消息: {exception_message}\n堆栈信息:\n{stack_trace}"
        AllureHelper.attach_text(error_details, name=f"{context}错误", attachment_type="text/plain")

    @staticmethod
    def safe_execute(func, *args, **kwargs) -> Optional[Any]:
        """
        安全执行函数，捕获并处理异常

        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果，如果发生异常则返回None
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ExceptionHandler.handle_exception(e, f"执行 {func.__name__}")
            return None

    @staticmethod
    def retry_on_exception(func, max_retries: int = 3, delay: int = 1):
        """
        异常重试装饰器

        Args:
            func: 要执行的函数
            max_retries: 最大重试次数
            delay: 重试延迟（秒）

        Returns:
            装饰后的函数
        """

        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    logger.warning(f"执行 {func.__name__} 失败，{retries}/{max_retries} 重试中...")
                    time.sleep(delay)
            # 确保函数有返回值
            return None

        return wrapper
