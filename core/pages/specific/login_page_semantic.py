"""
登录页面示例 - 使用 Playwright 官方推荐的语义化定位方式
演示如何使用 SmartPage 和语义化定位器
"""

from typing import Any, Dict, Optional

import allure
from playwright.sync_api import Page

from core.utils.locators import SmartPage
from core.utils.logger import get_logger

logger = get_logger(__name__)


class LoginPageSemantic(SmartPage):
    """
    登录页面对象 - 使用语义化定位方式
    继承 SmartPage 以支持语义化定位
    """

    def __init__(self, page: Page):
        # 使用语义化定位器文件
        super().__init__(page, page_name="login_page_semantic")
        logger.info("登录页面对象（语义化定位）初始化完成")

    @allure.step("导航到登录页面: {url}")
    def navigate(self, url: str) -> None:
        """导航到登录页面"""
        self.page.goto(url)
        logger.info(f"导航到登录页面: {url}")

    @allure.step("输入用户名: {username}")
    def enter_username(self, username: str) -> None:
        """
        输入用户名
        使用 label 定位方式（Playwright 推荐）
        """
        # 使用语义化定位 - label 方式
        self.fill("username_input", username)
        logger.info(f"输入用户名: {username}")

    @allure.step("输入密码")
    def enter_password(self, password: str) -> None:
        """
        输入密码
        使用 label 定位方式（Playwright 推荐）
        """
        self.fill("password_input", password)
        logger.info("输入密码: ******")

    @allure.step("点击登录按钮")
    def click_login_button(self) -> None:
        """
        点击登录按钮
        使用 role + name 定位方式（Playwright 最推荐）
        """
        self.click("login_button")
        logger.info("点击登录按钮")

    @allure.step("执行登录操作")
    def login(self, username: str, password: str) -> None:
        """
        执行完整的登录操作
        组合使用 label 定位和 role 定位
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
        logger.info("点击忘记密码链接")

    @allure.step("点击注册链接")
    def click_register(self) -> None:
        """
        点击注册链接
        使用 text 定位方式
        """
        self.click("register_link")
        logger.info("点击注册链接")

    @allure.step("获取错误提示信息")
    def get_error_message(self) -> str:
        """
        获取错误提示信息
        使用 CSS 选择器定位
        """
        self.wait_for_visible("error_message", timeout=5000)
        message: Optional[str] = self.get_text("error_message")
        logger.info(f"错误提示: {message}")
        return message.strip() if message else ""

    @allure.step("检查错误信息是否显示")
    def is_error_displayed(self) -> bool:
        """检查错误信息是否显示"""
        return self.is_visible("error_message")

    @allure.step("检查成功信息是否显示")
    def is_success_displayed(self) -> bool:
        """检查成功信息是否显示"""
        return self.is_visible("success_message")

    @allure.step("等待加载完成")
    def wait_for_loading(self) -> None:
        """等待加载完成"""
        self.wait_for_hidden("loading_spinner", timeout=10000)
        logger.info("加载完成")

    @allure.step("使用 test_id 定位输入用户名")
    def enter_username_by_test_id(self, username: str) -> None:
        """
        使用 test_id 定位输入用户名
        test_id 是最稳定的定位方式（需要开发配合）
        """
        self.fill("username_field", username)
        logger.info(f"使用 test_id 输入用户名: {username}")

    @allure.step("使用 placeholder 定位搜索框并输入: {text}")
    def search(self, text: str) -> None:
        """
        使用 placeholder 定位搜索框
        适用于没有 label 的输入框
        """
        self.fill("search_input", text)
        self.page.keyboard.press("Enter")
        logger.info(f"搜索: {text}")

    @allure.step("点击帮助图标")
    def click_help(self) -> None:
        """
        点击帮助图标
        使用 title 定位方式
        """
        self.click("help_icon")
        logger.info("点击帮助图标")

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
        logger.info(f"元素 '{element_name}' 的定位器配置: {config}")
        if isinstance(config, dict):
            return config
        return {}
