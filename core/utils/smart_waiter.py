"""
智能等待策略模块

提供智能化的等待机制，优化测试执行效率和稳定性
"""

import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.utils.logger import get_logger

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
        self.config = config or WaitConfig()
        self._attempt_history: List[Dict[str, Any]] = []
        self._fibonacci_cache = [0, 1]

    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
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
        """获取斐波那契数"""
        while len(self._fibonacci_cache) <= n:
            self._fibonacci_cache.append(self._fibonacci_cache[-1] + self._fibonacci_cache[-2])
        return self._fibonacci_cache[n]

    def _calculate_adaptive_delay(self, attempt: int) -> float:
        """计算自适应延迟"""
        if not self._attempt_history:
            return self.config.initial_delay
        
        # 使用 attempt 参数调整延迟
        base_delay = self.config.initial_delay * min(attempt, 5) / 5

        # 分析历史成功率
        recent_attempts = self._attempt_history[-10:]
        success_rate = sum(1 for a in recent_attempts if a.get("success", False)) / len(
            recent_attempts
        )

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
                logger.warning(f"等待超时: {error_message or '条件未满足'}")
                return False

            # 检查条件
            try:
                if condition():
                    self._record_attempt(attempt, True)
                    logger.debug(f"条件在第 {attempt + 1} 次尝试后满足")
                    return True
            except Exception as e:
                logger.debug(f"条件检查失败: {e}")

            # 计算延迟
            delay = self.calculate_delay(attempt + 1)

            logger.debug(
                f"等待 {delay:.2f} 秒后重试（尝试 {attempt + 1}/{self.config.max_attempts}）"
            )

            # 等待
            time.sleep(delay)
            attempt += 1

        self._record_attempt(attempt, False)
        logger.warning(f"达到最大尝试次数 {self.config.max_attempts}，条件仍未满足")
        return False

    def wait_for_element(self, page: Any, selector: str, timeout: Optional[float] = None) -> bool:
        """等待元素出现"""

        def element_exists():
            return page.locator(selector).count() > 0

        return self.wait(
            condition=element_exists, timeout=timeout, error_message=f"元素未找到: {selector}"
        )

    def wait_for_text(
        self, page: Any, selector: str, text: str, timeout: Optional[float] = None
    ) -> bool:
        """等待文本出现"""

        def text_present():
            element = page.locator(selector)
            return element.count() > 0 and text in element.first.text_content()

        return self.wait(
            condition=text_present,
            timeout=timeout,
            error_message=f"文本未找到: {text} in {selector}",
        )

    def wait_for_url(self, page: Any, url_pattern: str, timeout: Optional[float] = None) -> bool:
        """等待URL匹配"""

        def url_matches():
            return url_pattern in page.url

        return self.wait(
            condition=url_matches, timeout=timeout, error_message=f"URL未匹配: {url_pattern}"
        )

    def _record_attempt(self, attempt: int, success: bool) -> None:
        """记录尝试历史"""
        self._attempt_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "attempt": attempt,
                "success": success,
                "strategy": self.config.strategy.value,
            }
        )

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
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
        """创建固定等待器"""
        config = WaitConfig(
            strategy=WaitStrategy.FIXED, initial_delay=delay, max_attempts=max_attempts
        )
        return SmartWaiter(config)

    @staticmethod
    def create_exponential_waiter(
        initial_delay: float = 1.0, max_delay: float = 60.0, max_attempts: int = 5
    ) -> SmartWaiter:
        """创建指数等待器"""
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
        """创建自适应等待器"""
        config = WaitConfig(
            strategy=WaitStrategy.ADAPTIVE,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_attempts=max_attempts,
        )
        return SmartWaiter(config)

    @staticmethod
    def create_fast_waiter() -> SmartWaiter:
        """创建快速等待器（适用于快速失败场景）"""
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
        """创建耐心等待器（适用于不稳定环境）"""
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
    """

    def decorator(func: Callable) -> Callable:
        config = WaitConfig(
            strategy=strategy, initial_delay=initial_delay, max_attempts=max_attempts
        )
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
                            f"函数 {func.__name__} 执行失败（尝试 {attempt}/{max_attempts}），"
                            f"{delay:.2f}秒后重试: {e}"
                        )
                        time.sleep(delay)

            logger.error(f"函数 {func.__name__} 达到最大重试次数 {max_attempts}")
            if last_exception:
                raise last_exception
            else:
                raise Exception(
                    f"函数 {func.__name__} 达到最大重试次数 {max_attempts}，但没有捕获到异常"
                )

        return wrapper

    return decorator
