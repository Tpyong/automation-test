"""
基础页面类
为所有页面对象提供通用的 Playwright 操作方法
"""

from typing import Any, Dict, Literal, Optional, Union

import allure
from playwright.sync_api import Locator, Page, Response
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.common.logger import get_logger
from utils.common.path_helper import PathHelper
from utils.reporting.allure_helper import AllureHelper

logger = get_logger(__name__)


class BasePage:
    """基础页面类，提供通用的 Playwright 操作方法"""

    def __init__(self, page: Page):
        """初始化基础页面

        Args:
            page: Playwright 页面实例
        """
        self.page = page

    @allure.step("导航到: {url}")
    def navigate(self, url: str, wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "networkidle", timeout: int = 30000) -> Optional[Response]:
        """导航到指定 URL
        
        Args:
            url: 目标 URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle, commit)
            timeout: 超时时间（毫秒）
            
        Returns:
            导航响应对象
        """
        logger.info("导航到: %s", url)
        response = self.page.goto(url, wait_until=wait_until, timeout=timeout)
        logger.info("导航完成，状态码: %s", response.status if response else "无响应")
        return response

    @allure.step("等待页面加载完成")
    def wait_for_page_load(self, state: Literal["load", "domcontentloaded", "networkidle"] = "networkidle", timeout: int = 30000) -> None:
        """等待页面加载完成
        
        Args:
            state: 等待状态 (load, domcontentloaded, networkidle)
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_load_state(state, timeout=timeout)
        logger.info("页面加载完成，状态: %s", state)

    def get_locator(self, selector: Union[str, Dict[str, Any]]) -> Locator:
        """获取元素定位器
        
        Args:
            selector: CSS 选择器字符串或定位策略字典
            
        Returns:
            Playwright 定位器对象
        """
        if isinstance(selector, dict):
            # 支持不同的定位策略
            if "css" in selector:
                return self.page.locator(selector["css"])
            if "xpath" in selector:
                return self.page.locator(selector["xpath"])
            if "text" in selector:
                return self.page.get_by_text(selector["text"])
            if "placeholder" in selector:
                return self.page.get_by_placeholder(selector["placeholder"])
            if "role" in selector:
                role = selector["role"]
                options = selector.get("options", {})
                return self.page.get_by_role(role, **options)
            raise ValueError(f"不支持的定位策略: {selector}")
        return self.page.locator(selector)

    @allure.step("点击元素: {selector}")
    def click(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """点击指定元素

        Args:
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（毫秒）
        """
        logger.info("点击元素: %s", selector)
        locator = self.get_locator(selector)
        locator.click(timeout=timeout)

    @allure.step("填充输入框: {selector} = {value}")
    def fill(self, selector: Union[str, Dict[str, Any]], value: str, timeout: int = 30000) -> None:
        """填充输入框

        Args:
            selector: CSS 选择器字符串或定位策略字典
            value: 要填充的值
            timeout: 超时时间（毫秒）
        """
        logger.info("填充输入框: %s = %s", selector, value)
        locator = self.get_locator(selector)
        locator.fill(value, timeout=timeout)

    @allure.step("获取元素文本: {selector}")
    def get_text(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> str:
        """获取元素文本

        Args:
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（毫秒）

        Returns:
            元素文本内容
        """
        locator = self.get_locator(selector)
        text = locator.text_content(timeout=timeout)
        logger.info("获取元素文本: %s = %s", selector, text)
        return text or ""

    @allure.step("验证元素可见: {selector}")
    def is_visible(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> bool:
        """验证元素是否可见

        Args:
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（毫秒）

        Returns:
            元素是否可见
        """
        try:
            locator = self.get_locator(selector)
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    @allure.step("等待元素可见: {selector}")
    def wait_for_visible(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """等待元素可见

        Args:
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（毫秒）
        """
        logger.info("等待元素可见: %s", selector)
        locator = self.get_locator(selector)
        locator.wait_for(state="visible", timeout=timeout)

    @allure.step("等待元素不可见: {selector}")
    def wait_for_hidden(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """等待元素不可见

        Args:
            selector: CSS 选择器字符串或定位策略字典
            timeout: 超时时间（毫秒）
        """
        logger.info("等待元素不可见: %s", selector)
        locator = self.get_locator(selector)
        locator.wait_for(state="hidden", timeout=timeout)

    @allure.step("获取页面标题")
    def get_title(self) -> str:
        """获取页面标题

        Returns:
            页面标题
        """
        title = self.page.title()
        logger.info("页面标题: %s", title)
        return title

    @allure.step("获取当前URL")
    def get_url(self) -> str:
        """获取当前URL

        Returns:
            当前页面的 URL
        """
        url = self.page.url
        logger.info("当前URL: %s", url)
        return url

    @allure.step("截图: {name}")
    def screenshot(self, name: str = "screenshot") -> None:
        """截取页面截图

        Args:
            name: 截图名称
        """
        # 使用统一的命名格式：{name}_{timestamp}.png（目录已经按日期分类）
        screenshot_path = PathHelper.get_screenshot_path(name)
        self.page.screenshot(path=screenshot_path, full_page=True)
        logger.info("截图已保存: %s", screenshot_path)
        AllureHelper.attach_screenshot(screenshot_path, name=name)

    @allure.step("等待网络空闲")
    def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """等待网络空闲

        Args:
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        logger.info("网络空闲")

    @allure.step("刷新页面")
    def refresh(self, wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "networkidle", timeout: int = 30000) -> Optional[Response]:
        """刷新页面
        
        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle, commit)
            timeout: 超时时间（毫秒）
            
        Returns:
            刷新响应对象
        """
        logger.info("刷新页面")
        response = self.page.reload(wait_until=wait_until, timeout=timeout)
        logger.info("页面刷新完成")
        return response

    @allure.step("返回上一页")
    def go_back(self, wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "networkidle", timeout: int = 30000) -> Optional[Response]:
        """返回上一页
        
        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle, commit)
            timeout: 超时时间（毫秒）
            
        Returns:
            导航响应对象
        """
        logger.info("返回上一页")
        response = self.page.go_back(wait_until=wait_until, timeout=timeout)
        logger.info("返回上一页完成")
        return response

    @allure.step("前进到下一页")
    def go_forward(self, wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "networkidle", timeout: int = 30000) -> Optional[Response]:
        """前进到下一页
        
        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle, commit)
            timeout: 超时时间（毫秒）
            
        Returns:
            导航响应对象
        """
        logger.info("前进到下一页")
        response = self.page.go_forward(wait_until=wait_until, timeout=timeout)
        logger.info("前进到下一页完成")
        return response

    @allure.step("执行 JavaScript: {script}")
    def execute_script(self, script: str, *args: Any) -> Any:
        """执行 JavaScript 脚本

        Args:
            script: JavaScript 脚本
            *args: 脚本参数

        Returns:
            脚本执行结果
        """
        logger.info("执行 JavaScript: %s", script)
        result = self.page.evaluate(script, *args)
        logger.info("JavaScript 执行完成，结果: %s", result)
        return result
