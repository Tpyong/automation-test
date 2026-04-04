"""
浏览器实例池管理器
实现浏览器实例的复用，提高测试执行效率
"""

import threading
from typing import Dict, List, Optional, Set

from playwright.sync_api import Browser, Playwright

from utils.common.logger import get_logger

logger = get_logger(__name__)


class BrowserPool:
    """浏览器实例池管理器"""

    def __init__(self, max_pool_size: int = 5):
        """
        初始化浏览器实例池

        Args:
            max_pool_size: 最大池大小
        """
        self.max_pool_size = max_pool_size
        self._pool: List[Browser] = []
        self._in_use: Set[int] = set()
        self._lock = threading.Lock()
        self._playwright: Optional[Playwright] = None
        self._browser_type: str = "chromium"
        self._headless: bool = True
        self._slow_mo: int = 0

        logger.info(f"浏览器实例池初始化完成，最大池大小: {max_pool_size}")

    def initialize(
        self,
        playwright: Playwright,
        browser_type: str = "chromium",
        headless: bool = True,
        slow_mo: int = 0,
    ) -> None:
        """
        初始化浏览器池

        Args:
            playwright: Playwright实例
            browser_type: 浏览器类型
            headless: 是否无头模式
            slow_mo: 慢动作延迟
        """
        self._playwright = playwright
        self._browser_type = browser_type
        self._headless = headless
        self._slow_mo = slow_mo

        # 预创建浏览器实例
        self._pre_create_browsers()

    def _pre_create_browsers(self) -> None:
        """预创建浏览器实例"""
        if not self._playwright:
            logger.error("Playwright实例未初始化")
            return

        with self._lock:
            for i in range(self.max_pool_size):
                try:
                    browser = self._create_browser()
                    if browser:
                        self._pool.append(browser)
                        logger.info(f"预创建浏览器实例 {i + 1}/{self.max_pool_size}")
                except Exception as e:
                    logger.error(f"预创建浏览器实例失败: {e}")

    def _create_browser(self) -> Optional[Browser]:
        """创建新的浏览器实例"""
        if not self._playwright:
            return None

        try:
            if self._browser_type == "chromium":
                return self._playwright.chromium.launch(headless=self._headless, slow_mo=self._slow_mo)
            elif self._browser_type == "firefox":
                return self._playwright.firefox.launch(headless=self._headless, slow_mo=self._slow_mo)
            elif self._browser_type == "webkit":
                return self._playwright.webkit.launch(headless=self._headless, slow_mo=self._slow_mo)
            else:
                raise ValueError(f"不支持的浏览器类型: {self._browser_type}")
        except Exception as e:
            logger.error(f"创建浏览器实例失败: {e}")
            return None

    def acquire_browser(self) -> Optional[Browser]:
        """
        获取一个浏览器实例

        Returns:
            浏览器实例
        """
        with self._lock:
            # 优先从池中获取
            while self._pool:
                browser = self._pool.pop(0)
                if browser.is_connected():
                    self._in_use.add(id(browser))
                    logger.debug(f"从池中获取浏览器实例: {id(browser)}")
                    return browser
                else:
                    logger.warning("池中的浏览器实例已断开连接，创建新实例")

            # 池为空，创建新实例
            new_browser: Optional[Browser] = self._create_browser()
            if new_browser:
                self._in_use.add(id(new_browser))
                logger.debug(f"创建新浏览器实例: {id(new_browser)}")
            return new_browser

    def release_browser(self, browser: Browser) -> None:
        """
        释放浏览器实例回池中

        Args:
            browser: 浏览器实例
        """
        with self._lock:
            browser_id = id(browser)
            if browser_id in self._in_use:
                self._in_use.remove(browser_id)

            if browser.is_connected() and len(self._pool) < self.max_pool_size:
                self._pool.append(browser)
                logger.debug(f"浏览器实例回收到池中: {browser_id}")
            else:
                try:
                    browser.close()
                    logger.debug(f"浏览器实例已关闭: {browser_id}")
                except Exception as e:
                    logger.error(f"关闭浏览器实例失败: {e}")

    def get_pool_status(self) -> Dict[str, int]:
        """
        获取池状态

        Returns:
            池状态信息
        """
        with self._lock:
            return {
                "pool_size": len(self._pool),
                "in_use": len(self._in_use),
                "max_size": self.max_pool_size,
            }

    def cleanup(self) -> None:
        """清理所有浏览器实例"""
        with self._lock:
            logger.info("开始清理浏览器实例池")

            # 关闭池中的实例
            for browser in self._pool:
                try:
                    if browser.is_connected():
                        browser.close()
                except Exception as e:
                    # 忽略事件循环已关闭的错误
                    if "Event loop is closed" not in str(e):
                        logger.error(f"关闭浏览器实例失败: {e}")
                    else:
                        logger.debug("浏览器实例已关闭，跳过清理")

            self._pool.clear()
            self._in_use.clear()
            logger.info("浏览器实例池清理完成")


# 全局浏览器池实例
_browser_pool: Optional[BrowserPool] = None


def get_browser_pool(max_pool_size: int = 5) -> BrowserPool:
    """
    获取全局浏览器池实例

    Args:
        max_pool_size: 最大池大小

    Returns:
        浏览器池实例
    """
    global _browser_pool
    if _browser_pool is None:
        _browser_pool = BrowserPool(max_pool_size)
    return _browser_pool
