"""
智能等待策略模块

提供智能化的等待机制，优化测试执行效率和稳定性
与 pytest-playwright 集成，提供更可靠的等待方法
"""

import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from playwright.sync_api import Locator, Page

from utils.common.logger import get_logger

logger = get_logger(__name__)


class WaitStrategy(Enum):
    """等待策略类型"""

    FIXED = "fixed"  # 固定等待
    LINEAR = "linear"  # 线性递增
    EXPONENTIAL = "exponential"  # 指数递增
    POLYNOMIAL = "polynomial"  # 多项式递增
    FIBONACCI = "fibonacci"  # 斐波那契递增
    RANDOM = "random"  # 随机等待
    ADAPTIVE = "adaptive"  # 自适应等待


@dataclass
class WaitConfig:
    """等待配置"""

    strategy: WaitStrategy = WaitStrategy.EXPONENTIAL
    initial_delay: float = 1.0  # 初始延迟（秒）
    max_delay: float = 60.0  # 最大延迟（秒）
    max_attempts: int = 3  # 最大尝试次数
    multiplier: float = 2.0  # 递增倍数
    jitter: bool = True  # 是否添加随机抖动
    jitter_range: Tuple[float, float] = (0.8, 1.2)  # 抖动范围


class SmartWaiter:
    """智能等待器"""

    def __init__(self, config: Optional[WaitConfig] = None):
        """
        初始化智能等待器

        Args:
            config: 等待配置
        """
        self.config = config or WaitConfig()
        self._attempt_history: List[Dict[str, Any]] = []
        self._fibonacci_cache = [0, 1]

    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间

        Args:
            attempt: 尝试次数

        Returns:
            延迟时间（秒）
        """
        delay = self.config.initial_delay  # 默认值

        if self.config.strategy == WaitStrategy.FIXED:
            delay = self.config.initial_delay
        elif self.config.strategy == WaitStrategy.LINEAR:
            delay = self.config.initial_delay * attempt
        elif self.config.strategy == WaitStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (self.config.multiplier ** (attempt - 1))
        elif self.config.strategy == WaitStrategy.POLYNOMIAL:
            delay = self.config.initial_delay * (attempt**self.config.multiplier)
        elif self.config.strategy == WaitStrategy.FIBONACCI:
            delay = self.config.initial_delay * self._get_fibonacci(attempt)
        elif self.config.strategy == WaitStrategy.RANDOM:
            delay = random.uniform(self.config.initial_delay, self.config.max_delay)
        elif self.config.strategy == WaitStrategy.ADAPTIVE:
            delay = self._calculate_adaptive_delay(attempt)

        # 应用最大延迟限制
        delay = min(delay, self.config.max_delay)

        # 添加随机抖动
        if self.config.jitter:
            jitter_factor = random.uniform(*self.config.jitter_range)
            delay *= jitter_factor

        return delay

    def _get_fibonacci(self, n: int) -> int:
        """获取斐波那契数

        Args:
            n: 斐波那契数列的索引

        Returns:
            斐波那契数
        """
        while len(self._fibonacci_cache) <= n:
            self._fibonacci_cache.append(self._fibonacci_cache[-1] + self._fibonacci_cache[-2])
        return self._fibonacci_cache[n]

    def _calculate_adaptive_delay(self, attempt: int) -> float:
        """计算自适应延迟

        Args:
            attempt: 尝试次数

        Returns:
            延迟时间（秒）
        """
        if not self._attempt_history:
            return self.config.initial_delay

        # 使用 attempt 参数调整延迟
        base_delay = self.config.initial_delay * min(attempt, 5) / 5

        # 分析历史成功率
        recent_attempts = self._attempt_history[-10:]
        success_rate = sum(1 for a in recent_attempts if a.get("success", False)) / len(recent_attempts)

        # 根据成功率调整延迟
        if success_rate > 0.8:
            # 成功率高，减少等待时间
            return base_delay * 0.5
        elif success_rate > 0.5:
            # 成功率中等，使用标准延迟
            return base_delay
        else:
            # 成功率低，增加等待时间
            return base_delay * 2.0

    def wait(
        self,
        condition: Callable[[], bool],
        timeout: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        等待条件满足

        Args:
            condition: 条件函数
            timeout: 超时时间（秒）
            error_message: 错误消息

        Returns:
            条件是否满足
        """
        start_time = time.time()
        attempt = 0

        while attempt < self.config.max_attempts:
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                logger.warning("等待超时: %s", error_message or "条件未满足")
                return False

            # 检查条件
            try:
                if condition():
                    self._record_attempt(attempt, True)
                    logger.debug("条件在第 %d 次尝试后满足", attempt + 1)
                    return True
            except Exception as e:
                logger.debug("条件检查失败: %s", e)

            # 计算延迟
            delay = self.calculate_delay(attempt + 1)

            logger.debug("等待 %.2f 秒后重试（尝试 %d/%d）", delay, attempt + 1, self.config.max_attempts)

            # 等待
            time.sleep(delay)
            attempt += 1

        self._record_attempt(attempt, False)
        logger.warning("达到最大尝试次数 %d，条件仍未满足", self.config.max_attempts)
        return False

    def _get_locator(self, page: Page, selector: Union[str, Dict[str, Any]]) -> Locator:
        """获取 Playwright 定位器

        Args:
            page: Playwright 页面实例
            selector: CSS 选择器字符串或定位策略字典

        Returns:
            Playwright 定位器对象
        """
        if isinstance(selector, dict):
            # 支持不同的定位策略
            if "css" in selector:
                return page.locator(selector["css"])
            elif "xpath" in selector:
                return page.locator(selector["xpath"])
            elif "text" in selector:
                return page.get_by_text(selector["text"])
            elif "placeholder" in selector:
                return page.get_by_placeholder(selector["placeholder"])
            elif "role" in selector:
                role = selector["role"]
                options = selector.get("options", {})
                if isinstance(options, dict):
                    return page.get_by_role(role, **options)
                else:
                    return page.get_by_role(role)
            else:
                raise ValueError(f"不支持的定位策略: {selector}")
        return page.locator(selector)

    def wait_for_element(
        self, page: Page, selector: Union[str, Dict[str, Any]], timeout: Optional[float] = None
    ) -> bool:
        """等待元素出现

        Args:
            page: Playwright 页面实例
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（秒）

        Returns:
            元素是否出现
        """

        def element_exists():
            return self._get_locator(page, selector).count() > 0

        return self.wait(condition=element_exists, timeout=timeout, error_message=f"元素未找到: {selector}")

    def wait_for_text(
        self, page: Page, selector: Union[str, Dict[str, Any]], text: str, timeout: Optional[float] = None
    ) -> bool:
        """等待文本出现

        Args:
            page: Playwright 页面实例
            selector: CSS 选择器字符串或定位策略字典
            text: 要等待的文本
            timeout: 超时时间（秒）

        Returns:
            文本是否出现
        """

        def text_present():
            element = self._get_locator(page, selector)
            return element.count() > 0 and text in (element.first.text_content() or "")

        return self.wait(
            condition=text_present,
            timeout=timeout,
            error_message=f"文本未找到: {text} in {selector}",
        )

    def wait_for_url(self, page: Page, url_pattern: str, timeout: Optional[float] = None) -> bool:
        """等待URL匹配

        Args:
            page: Playwright 页面实例
            url_pattern: URL 模式
            timeout: 超时时间（秒）

        Returns:
            URL 是否匹配
        """

        def url_matches():
            return url_pattern in page.url

        return self.wait(condition=url_matches, timeout=timeout, error_message=f"URL未匹配: {url_pattern}")

    def wait_for_element_visible(
        self, page: Page, selector: Union[str, Dict[str, Any]], timeout: Optional[float] = None
    ) -> bool:
        """等待元素可见

        Args:
            page: Playwright 页面实例
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（秒）

        Returns:
            元素是否可见
        """

        def element_visible():
            try:
                return self._get_locator(page, selector).is_visible()
            except Exception:
                return False

        return self.wait(condition=element_visible, timeout=timeout, error_message=f"元素不可见: {selector}")

    def wait_for_element_hidden(
        self, page: Page, selector: Union[str, Dict[str, Any]], timeout: Optional[float] = None
    ) -> bool:
        """等待元素隐藏

        Args:
            page: Playwright 页面实例
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（秒）

        Returns:
            元素是否隐藏
        """

        def element_hidden():
            try:
                return not self._get_locator(page, selector).is_visible()
            except Exception:
                return True

        return self.wait(condition=element_hidden, timeout=timeout, error_message=f"元素未隐藏: {selector}")

    def wait_for_load_state(
        self,
        page: Page,
        state: Literal["domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: Optional[float] = None,
    ) -> bool:
        """等待页面加载状态

        Args:
            page: Playwright 页面实例
            state: 加载状态 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）

        Returns:
            加载状态是否完成
        """

        def load_state_completed():
            try:
                page.wait_for_load_state(state, timeout=1000)
                return True
            except Exception:
                return False

        return self.wait(condition=load_state_completed, timeout=timeout, error_message=f"页面加载状态未完成: {state}")

    def _record_attempt(self, attempt: int, success: bool) -> None:
        """记录尝试历史

        Args:
            attempt: 尝试次数
            success: 是否成功
        """
        self._attempt_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "attempt": attempt,
                "success": success,
                "strategy": self.config.strategy.value,
            }
        )

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            统计信息字典
        """
        if not self._attempt_history:
            return {"total_attempts": 0}

        total = len(self._attempt_history)
        successful = sum(1 for a in self._attempt_history if a["success"])

        return {
            "total_attempts": total,
            "successful_attempts": successful,
            "success_rate": successful / total if total > 0 else 0,
            "average_attempts": sum(a["attempt"] for a in self._attempt_history) / total,
        }


class WaitStrategyFactory:
    """等待策略工厂"""

    @staticmethod
    def create_fixed_waiter(delay: float = 1.0, max_attempts: int = 3) -> SmartWaiter:
        """创建固定等待器

        Args:
            delay: 固定延迟时间（秒）
            max_attempts: 最大尝试次数

        Returns:
            智能等待器实例
        """
        config = WaitConfig(strategy=WaitStrategy.FIXED, initial_delay=delay, max_attempts=max_attempts)
        return SmartWaiter(config)

    @staticmethod
    def create_exponential_waiter(
        initial_delay: float = 1.0, max_delay: float = 60.0, max_attempts: int = 5
    ) -> SmartWaiter:
        """创建指数等待器

        Args:
            initial_delay: 初始延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            max_attempts: 最大尝试次数

        Returns:
            智能等待器实例
        """
        config = WaitConfig(
            strategy=WaitStrategy.EXPONENTIAL,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_attempts=max_attempts,
        )
        return SmartWaiter(config)

    @staticmethod
    def create_adaptive_waiter(
        initial_delay: float = 1.0, max_delay: float = 30.0, max_attempts: int = 5
    ) -> SmartWaiter:
        """创建自适应等待器

        Args:
            initial_delay: 初始延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            max_attempts: 最大尝试次数

        Returns:
            智能等待器实例
        """
        config = WaitConfig(
            strategy=WaitStrategy.ADAPTIVE,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_attempts=max_attempts,
        )
        return SmartWaiter(config)

    @staticmethod
    def create_fast_waiter() -> SmartWaiter:
        """创建快速等待器（适用于快速失败场景）

        Returns:
            智能等待器实例
        """
        config = WaitConfig(
            strategy=WaitStrategy.LINEAR,
            initial_delay=0.5,
            max_delay=5.0,
            max_attempts=3,
            jitter=False,
        )
        return SmartWaiter(config)

    @staticmethod
    def create_patient_waiter() -> SmartWaiter:
        """创建耐心等待器（适用于不稳定环境）

        Returns:
            智能等待器实例
        """
        config = WaitConfig(
            strategy=WaitStrategy.EXPONENTIAL,
            initial_delay=2.0,
            max_delay=120.0,
            max_attempts=10,
            jitter=True,
        )
        return SmartWaiter(config)


# 装饰器：自动重试
def smart_retry(
    max_attempts: int = 3,
    strategy: WaitStrategy = WaitStrategy.EXPONENTIAL,
    initial_delay: float = 1.0,
    exceptions: Tuple = (Exception,),
):
    """
    智能重试装饰器

    使用示例:
        @smart_retry(max_attempts=3, strategy=WaitStrategy.EXPONENTIAL)
        def unstable_function():
            # 可能失败的代码
            pass

    Args:
        max_attempts: 最大尝试次数
        strategy: 等待策略
        initial_delay: 初始延迟时间（秒）
        exceptions: 要捕获的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        config = WaitConfig(strategy=strategy, initial_delay=initial_delay, max_attempts=max_attempts)
        waiter = SmartWaiter(config)

        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    attempt += 1

                    if attempt < max_attempts:
                        delay = waiter.calculate_delay(attempt)
                        logger.warning(
                            "函数 %s 执行失败（尝试 %d/%d），%.2f秒后重试: %s",
                            func.__name__,
                            attempt,
                            max_attempts,
                            delay,
                            e,
                        )
                        time.sleep(delay)

            logger.error("函数 %s 达到最大重试次数 %d", func.__name__, max_attempts)
            if last_exception:
                raise last_exception
            else:
                raise Exception(f"函数 {func.__name__} 达到最大重试次数 {max_attempts}，但没有捕获到异常")

        return wrapper

    return decorator
