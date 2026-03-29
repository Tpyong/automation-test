"""
断路器模式模块

实现断路器模式，防止级联故障，提供故障隔离和快速失败机制
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.utils.logger import get_logger

logger = get_logger(__name__)


class CircuitState(Enum):
    """断路器状态"""
    CLOSED = "closed"      # 关闭状态（正常）
    OPEN = "open"          # 打开状态（熔断）
    HALF_OPEN = "half_open"  # 半开状态（尝试恢复）


@dataclass
class CircuitStats:
    """断路器统计信息"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreaker:
    """断路器"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: float = 60.0,
        expected_exceptions: tuple = (Exception,)
    ):
        """
        初始化断路器
        
        Args:
            name: 断路器名称
            failure_threshold: 失败次数阈值（达到后熔断）
            success_threshold: 成功次数阈值（半开状态下达到后恢复）
            timeout: 熔断超时时间（秒）
            expected_exceptions: 预期的异常类型
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exceptions = expected_exceptions
        
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._last_state_change_time = time.time()
        self._listeners: List[Callable[[str, CircuitState, CircuitState], None]] = []
    
    @property
    def state(self) -> CircuitState:
        """获取当前状态"""
        return self._state
    
    @property
    def stats(self) -> CircuitStats:
        """获取统计信息"""
        return self._stats
    
    @property
    def is_closed(self) -> bool:
        """是否处于关闭状态"""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """是否处于打开状态"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """是否处于半开状态"""
        return self._state == CircuitState.HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过断路器调用函数
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数执行结果
        
        Raises:
            Exception: 断路器打开时抛出异常
        """
        if self.is_open:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise Exception(f"断路器 [{self.name}] 处于打开状态，拒绝调用")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        return time.time() - self._last_state_change_time >= self.timeout
    
    def _on_success(self) -> None:
        """成功回调"""
        self._stats.total_calls += 1
        self._stats.successful_calls += 1
        self._stats.last_success_time = time.time()
        self._stats.consecutive_successes += 1
        self._stats.consecutive_failures = 0
        
        if self.is_half_open:
            if self._stats.consecutive_successes >= self.success_threshold:
                self._transition_to_closed()
    
    def _on_failure(self) -> None:
        """失败回调"""
        self._stats.total_calls += 1
        self._stats.failed_calls += 1
        self._stats.last_failure_time = time.time()
        self._stats.consecutive_failures += 1
        self._stats.consecutive_successes = 0
        
        if self.is_closed:
            if self._stats.consecutive_failures >= self.failure_threshold:
                self._transition_to_open()
        elif self.is_half_open:
            self._transition_to_open()
    
    def _transition_to_closed(self) -> None:
        """转换到关闭状态"""
        old_state = self._state
        self._state = CircuitState.CLOSED
        self._last_state_change_time = time.time()
        self._stats.consecutive_failures = 0
        self._stats.consecutive_successes = 0
        
        logger.info(f"断路器 [{self.name}] 状态变更: {old_state.value} -> CLOSED")
        self._notify_state_change(old_state, CircuitState.CLOSED)
    
    def _transition_to_open(self) -> None:
        """转换到打开状态"""
        old_state = self._state
        self._state = CircuitState.OPEN
        self._last_state_change_time = time.time()
        
        logger.warning(f"断路器 [{self.name}] 状态变更: {old_state.value} -> OPEN (熔断)")
        self._notify_state_change(old_state, CircuitState.OPEN)
    
    def _transition_to_half_open(self) -> None:
        """转换到半开状态"""
        old_state = self._state
        self._state = CircuitState.HALF_OPEN
        self._last_state_change_time = time.time()
        self._stats.consecutive_successes = 0
        
        logger.info(f"断路器 [{self.name}] 状态变更: {old_state.value} -> HALF_OPEN (尝试恢复)")
        self._notify_state_change(old_state, CircuitState.HALF_OPEN)
    
    def add_state_change_listener(
        self,
        listener: Callable[[str, CircuitState, CircuitState], None]
    ) -> None:
        """添加状态变更监听器"""
        self._listeners.append(listener)
    
    def _notify_state_change(
        self,
        old_state: CircuitState,
        new_state: CircuitState
    ) -> None:
        """通知状态变更"""
        for listener in self._listeners:
            try:
                listener(self.name, old_state, new_state)
            except Exception as e:
                logger.error(f"状态变更监听器执行失败: {e}")
    
    def reset(self) -> None:
        """重置断路器"""
        self._transition_to_closed()
        self._stats = CircuitStats()
        logger.info(f"断路器 [{self.name}] 已重置")
    
    def force_open(self) -> None:
        """强制打开断路器"""
        self._transition_to_open()
        logger.warning(f"断路器 [{self.name}] 已强制打开")
    
    def get_status(self) -> Dict[str, Any]:
        """获取断路器状态"""
        return {
            "name": self.name,
            "state": self._state.value,
            "stats": {
                "total_calls": self._stats.total_calls,
                "successful_calls": self._stats.successful_calls,
                "failed_calls": self._stats.failed_calls,
                "success_rate": (
                    self._stats.successful_calls / self._stats.total_calls * 100
                    if self._stats.total_calls > 0 else 0
                ),
                "consecutive_failures": self._stats.consecutive_failures,
                "consecutive_successes": self._stats.consecutive_successes,
                "last_failure_time": (
                    datetime.fromtimestamp(self._stats.last_failure_time).isoformat()
                    if self._stats.last_failure_time else None
                ),
                "last_success_time": (
                    datetime.fromtimestamp(self._stats.last_success_time).isoformat()
                    if self._stats.last_success_time else None
                ),
            },
            "config": {
                "failure_threshold": self.failure_threshold,
                "success_threshold": self.success_threshold,
                "timeout": self.timeout,
            }
        }


class CircuitBreakerManager:
    """断路器管理器"""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: float = 60.0
    ) -> CircuitBreaker:
        """获取或创建断路器"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                timeout=timeout
            )
        return self._breakers[name]
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有断路器状态"""
        return {
            name: breaker.get_status()
            for name, breaker in self._breakers.items()
        }
    
    def reset_all(self) -> None:
        """重置所有断路器"""
        for breaker in self._breakers.values():
            breaker.reset()
        logger.info("所有断路器已重置")


# 全局断路器管理器
_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """获取全局断路器管理器"""
    global _circuit_breaker_manager
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager()
    return _circuit_breaker_manager


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    success_threshold: int = 3,
    timeout: float = 60.0
):
    """
    断路器装饰器
    
    使用示例:
        @circuit_breaker("api_call", failure_threshold=3, timeout=30)
        def call_api():
            # API 调用逻辑
            pass
    """
    def decorator(func: Callable) -> Callable:
        manager = get_circuit_breaker_manager()
        breaker = manager.get_breaker(name, failure_threshold, success_threshold, timeout)
        
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator
