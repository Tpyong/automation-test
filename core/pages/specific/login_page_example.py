"""
登录页面示例
演示如何使用元素定位器管理
"""

from typing import Any, Literal, Optional, Union

import allure
from playwright.sync_api import Page, Response

from core.pages.base.base_page import BasePage
from core.pages.locators import LocatorManager
from utils.common.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """登录页面对象"""

    def __init__(self, page: Page):
        """初始化登录页面

        Args:
            page: Playwright 页面实例
        """
        super().__init__(page)
        # 加载定位器文件（自动识别 YAML/JSON）
        self.locators = LocatorManager("login_page_example")
        logger.info("登录页面对象初始化完成")

    @allure.step("导航到登录页面: {url}")
    def navigate(
        self,
        url: str,
        wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "networkidle",
        timeout: int = 30000,
    ) -> Optional[Response]:
        """导航到登录页面

        Args:
            url: 登录页面 URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle, commit)
            timeout: 超时时间（毫秒）

        Returns:
            导航响应对象
        """
        return super().navigate(url, wait_until=wait_until, timeout=timeout)

    @allure.step("输入用户名: {username}")
    def enter_username(self, username: str) -> None:
        """输入用户名

        Args:
            username: 用户名
        """
        # 方式1: 使用属性访问
        locator: Union[str, dict[Any, Any]] = self.locators.username_input
        self.fill(str(locator), username)

    @allure.step("输入密码")
    def enter_password(self, password: str) -> None:
        """输入密码

        Args:
            password: 密码
        """
        # 方式2: 使用字典访问
        locator = self.locators["password_input"]
        self.fill(str(locator), password)

    @allure.step("点击登录按钮")
    def click_login_button(self) -> None:
        """点击登录按钮"""
        locator = self.locators.login_button
        self.click(str(locator))

    @allure.step("勾选记住我")
    def check_remember_me(self) -> None:
        """勾选记住我"""
        locator = self.locators.remember_me
        self.page.check(str(locator))
        logger.info("勾选记住我")

    @allure.step("执行登录操作")
    def login(self, username: str, password: str, remember: bool = False) -> None:
        """
        执行完整的登录操作

        Args:
            username: 用户名
            password: 密码
            remember: 是否记住我
        """
        self.enter_username(username)
        self.enter_password(password)

        if remember:
            self.check_remember_me()

        self.click_login_button()

    @allure.step("获取错误提示信息")
    def get_error_message(self) -> str:
        """获取错误提示信息

        Returns:
            错误提示信息
        """
        # 等待错误信息显示
        locator = self.locators.error_message
        self.wait_for_visible(str(locator), timeout=5000)
        message: Optional[str] = self.get_text(str(locator))
        return message.strip() if message else ""

    @allure.step("获取成功提示信息")
    def get_success_message(self) -> str:
        """获取成功提示信息

        Returns:
            成功提示信息
        """
        locator = self.locators.success_message
        self.wait_for_visible(str(locator), timeout=5000)
        message: Optional[str] = self.get_text(str(locator))
        return message.strip() if message else ""

    @allure.step("检查错误信息是否显示")
    def is_error_displayed(self) -> bool:
        """检查错误信息是否显示

        Returns:
            错误信息是否显示
        """
        locator = self.locators.error_message
        return self.is_visible(str(locator))

    @allure.step("检查成功信息是否显示")
    def is_success_displayed(self) -> bool:
        """检查成功信息是否显示

        Returns:
            成功信息是否显示
        """
        locator = self.locators.success_message
        return self.is_visible(str(locator))

    @allure.step("检查欢迎信息是否显示")
    def is_welcome_displayed(self) -> bool:
        """检查欢迎信息是否显示

        Returns:
            欢迎信息是否显示
        """
        locator = self.locators.welcome_text
        return self.is_visible(str(locator))

    @allure.step("获取页面标题")
    def get_page_title(self) -> Optional[str]:
        """获取页面标题

        Returns:
            页面标题
        """
        locator = self.locators.page_title
        return self.get_text(str(locator))

    @allure.step("点击忘记密码链接")
    def click_forgot_password(self) -> None:
        """点击忘记密码链接"""
        locator = self.locators.forgot_password_link
        self.click(str(locator))

    @allure.step("点击注册链接")
    def click_register(self) -> None:
        """点击注册链接"""
        locator = self.locators.register_link
        self.click(str(locator))

    @allure.step("等待加载完成")
    def wait_for_loading(self) -> None:
        """等待加载完成"""
        # 等待加载动画消失
        locator = self.locators.loading_spinner
        self.wait_for_hidden(str(locator), timeout=10000)

    def get_locator_by_strategy(self, element_name: str, strategy: str = "default") -> Union[str, dict[Any, Any]]:
        """
        使用特定策略获取定位器

        Args:
            element_name: 元素名称
            strategy: 定位策略（default, css, xpath, text）

        Returns:
            定位器字符串或字典
        """
        return self.locators.get_by_strategy(element_name, strategy)
