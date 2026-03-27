"""
登录页面示例
演示如何使用元素定位器管理
"""

import allure
from playwright.sync_api import Page

from core.utils.locators import LocatorManager
from core.utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage:
    """登录页面对象"""

    def __init__(self, page: Page):
        self.page = page
        # 加载定位器文件（自动识别 YAML/JSON）
        self.locators = LocatorManager("login_page")
        logger.info("登录页面对象初始化完成")

    @allure.step("导航到登录页面: {url}")
    def navigate(self, url: str):
        """导航到登录页面"""
        self.page.goto(url)
        logger.info(f"导航到登录页面: {url}")

    @allure.step("输入用户名: {username}")
    def enter_username(self, username: str):
        """输入用户名"""
        # 方式1: 使用属性访问
        self.page.fill(self.locators.username_input, username)
        logger.info(f"输入用户名: {username}")

    @allure.step("输入密码")
    def enter_password(self, password: str):
        """输入密码"""
        # 方式2: 使用字典访问
        self.page.fill(self.locators["password_input"], password)
        logger.info("输入密码: ******")

    @allure.step("点击登录按钮")
    def click_login_button(self):
        """点击登录按钮"""
        self.page.click(self.locators.login_button)
        logger.info("点击登录按钮")

    @allure.step("勾选记住我")
    def check_remember_me(self):
        """勾选记住我"""
        self.page.check(self.locators.remember_me)
        logger.info("勾选记住我")

    @allure.step("执行登录操作")
    def login(self, username: str, password: str, remember: bool = False):
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
        """获取错误提示信息"""
        # 等待错误信息显示
        self.page.wait_for_selector(self.locators.error_message, state="visible", timeout=5000)
        message = self.page.text_content(self.locators.error_message)
        logger.info(f"错误提示: {message}")
        return message.strip() if message else ""

    @allure.step("获取成功提示信息")
    def get_success_message(self) -> str:
        """获取成功提示信息"""
        self.page.wait_for_selector(self.locators.success_message, state="visible", timeout=5000)
        message = self.page.text_content(self.locators.success_message)
        logger.info(f"成功提示: {message}")
        return message.strip() if message else ""

    @allure.step("检查错误信息是否显示")
    def is_error_displayed(self) -> bool:
        """检查错误信息是否显示"""
        return self.page.is_visible(self.locators.error_message)

    @allure.step("检查成功信息是否显示")
    def is_success_displayed(self) -> bool:
        """检查成功信息是否显示"""
        return self.page.is_visible(self.locators.success_message)

    @allure.step("检查欢迎信息是否显示")
    def is_welcome_displayed(self) -> bool:
        """检查欢迎信息是否显示"""
        return self.page.is_visible(self.locators.welcome_text)

    @allure.step("获取页面标题")
    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.page.text_content(self.locators.page_title)

    @allure.step("点击忘记密码链接")
    def click_forgot_password(self):
        """点击忘记密码链接"""
        self.page.click(self.locators.forgot_password_link)
        logger.info("点击忘记密码链接")

    @allure.step("点击注册链接")
    def click_register(self):
        """点击注册链接"""
        self.page.click(self.locators.register_link)
        logger.info("点击注册链接")

    @allure.step("等待加载完成")
    def wait_for_loading(self):
        """等待加载完成"""
        # 等待加载动画消失
        self.page.wait_for_selector(self.locators.loading_spinner, state="hidden", timeout=10000)
        logger.info("加载完成")

    def get_locator_by_strategy(self, element_name: str, strategy: str = "default") -> str:
        """
        使用特定策略获取定位器

        Args:
            element_name: 元素名称
            strategy: 定位策略（default, css, xpath, text）

        Returns:
            定位器字符串
        """
        return self.locators.get_by_strategy(element_name, strategy)
