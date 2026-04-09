"""
登录页面示例 - 使用 Playwright 官方推荐的语义化定位方式
演示如何使用 SmartPage 和语义化定位器
"""

from typing import Any, Dict, Literal, Optional

import allure
from playwright.sync_api import Page, Response

from core.pages.locators import SmartPage
from utils.common.logger import get_logger

logger = get_logger(__name__)


class LoginPageSemantic(SmartPage):
    """
    登录页面对象 - 使用语义化定位方式
    继承 SmartPage 以支持语义化定位
    """

    def __init__(self, page: Page):
        """初始化登录页面（语义化定位）

        Args:
            page: Playwright 页面实例
        """
        # 使用语义化定位器文件
        super().__init__(page, page_name="login_page_semantic_example")
        logger.info("登录页面对象（语义化定位）初始化完成")

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
        """
        输入用户名
        使用 label 定位方式（Playwright 推荐）

        Args:
            username: 用户名
        """
        # 使用语义化定位 - label 方式
        self.fill("username_input", username)

    @allure.step("输入密码")
    def enter_password(self, password: str) -> None:
        """
        输入密码
        使用 label 定位方式（Playwright 推荐）

        Args:
            password: 密码
        """
        self.fill("password_input", password)

    @allure.step("点击登录按钮")
    def click_login_button(self) -> None:
        """
        点击登录按钮
        使用 role + name 定位方式（Playwright 最推荐）
        """
        self.click("login_button")

    @allure.step("执行登录操作")
    def login(self, username: str, password: str) -> None:
        """
        执行完整的登录操作
        组合使用 label 定位和 role 定位

        Args:
            username: 用户名
            password: 密码
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    @allure.step("点击忘记密码链接")
    def click_forgot_password(self) -> None:
        """
        点击忘记密码链接
        使用 text 定位方式
        """
        self.click("forgot_password_link")

    @allure.step("点击注册链接")
    def click_register(self) -> None:
        """
        点击注册链接
        使用 text 定位方式
        """
        self.click("register_link")

    @allure.step("获取错误提示信息")
    def get_error_message(self) -> str:
        """
        获取错误提示信息
        使用 CSS 选择器定位

        Returns:
            错误提示信息
        """
        self.wait_for_visible("error_message", timeout=5000)
        message: Optional[str] = self.get_text("error_message")
        return message.strip() if message else ""

    @allure.step("检查错误信息是否显示")
    def is_error_displayed(self) -> bool:
        """检查错误信息是否显示

        Returns:
            错误信息是否显示
        """
        return self.is_visible("error_message")

    @allure.step("检查成功信息是否显示")
    def is_success_displayed(self) -> bool:
        """检查成功信息是否显示

        Returns:
            成功信息是否显示
        """
        return self.is_visible("success_message")

    @allure.step("等待加载完成")
    def wait_for_loading(self) -> None:
        """等待加载完成"""
        self.wait_for_hidden("loading_spinner", timeout=10000)

    @allure.step("使用 test_id 定位输入用户名")
    def enter_username_by_test_id(self, username: str) -> None:
        """
        使用 test_id 定位输入用户名
        test_id 是最稳定的定位方式（需要开发配合）

        Args:
            username: 用户名
        """
        self.fill("username_field", username)

    @allure.step("使用 placeholder 定位搜索框并输入: {text}")
    def search(self, text: str) -> None:
        """
        使用 placeholder 定位搜索框
        适用于没有 label 的输入框

        Args:
            text: 搜索文本
        """
        self.fill("search_input", text)
        self.page.keyboard.press("Enter")

    @allure.step("点击帮助图标")
    def click_help(self) -> None:
        """
        点击帮助图标
        使用 title 定位方式
        """
        self.click("help_icon")

    def get_locator_info(self, element_name: str) -> Dict[str, Any]:
        """
        获取元素的定位器信息（调试用）

        Args:
            element_name: 元素名称

        Returns:
            定位器配置字典
        """
        if self.locators is None:
            return {}
        config: Any = self.locators.get(element_name)
        logger.info("元素 '%s' 的定位器配置: %s", element_name, config)
        if isinstance(config, dict):
            return config
        return {}
