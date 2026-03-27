"""
登录功能测试示例
演示如何使用元素定位器管理
"""

import allure
import pytest

from core.pages.login_page import LoginPage
from core.utils.assertions import Assertions


@allure.epic("用户认证")
@allure.feature("登录功能")
class TestLogin:
    """登录功能测试"""

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.story("成功登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("使用有效凭据登录成功")
    def test_login_success(self, page, settings):
        """测试成功登录场景"""
        # 创建登录页面对象
        login_page = LoginPage(page)

        with allure.step("导航到登录页面"):
            login_page.navigate(f"{settings.base_url}/login")

        with allure.step("输入有效的用户名和密码"):
            login_page.login("admin", "password123")

        with allure.step("验证登录成功"):
            Assertions.assert_true(login_page.is_welcome_displayed(), "欢迎信息应该显示")

            welcome_text = login_page.page.text_content(login_page.locators.welcome_text)
            Assertions.assert_contains(welcome_text, "欢迎")

    @pytest.mark.regression
    @pytest.mark.ui
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("使用无效凭据登录失败")
    def test_login_failure(self, page, settings):
        """测试登录失败场景"""
        login_page = LoginPage(page)

        with allure.step("导航到登录页面"):
            login_page.navigate(f"{settings.base_url}/login")

        with allure.step("输入无效的用户名和密码"):
            login_page.login("wrong_user", "wrong_password")

        with allure.step("验证错误提示"):
            Assertions.assert_true(login_page.is_error_displayed(), "错误提示应该显示")

            error_message = login_page.get_error_message()
            Assertions.assert_contains(error_message, "用户名或密码错误")

    @pytest.mark.ui
    @allure.story("记住我功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("勾选记住我登录")
    def test_login_with_remember_me(self, page, settings):
        """测试记住我功能"""
        login_page = LoginPage(page)

        with allure.step("导航到登录页面"):
            login_page.navigate(f"{settings.base_url}/login")

        with allure.step("输入凭据并勾选记住我"):
            login_page.login("admin", "password123", remember=True)

        with allure.step("验证登录成功"):
            Assertions.assert_true(login_page.is_welcome_displayed(), "欢迎信息应该显示")

    @pytest.mark.ui
    @allure.story("页面导航")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("点击忘记密码链接")
    def test_click_forgot_password(self, page, settings):
        """测试忘记密码链接"""
        login_page = LoginPage(page)

        with allure.step("导航到登录页面"):
            login_page.navigate(f"{settings.base_url}/login")

        with allure.step("点击忘记密码链接"):
            login_page.click_forgot_password()

        with allure.step("验证跳转到忘记密码页面"):
            Assertions.assert_contains(page.url, "/forgot-password", "应该跳转到忘记密码页面")

    @pytest.mark.ui
    @allure.story("页面元素检查")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("检查登录页面元素")
    def test_login_page_elements(self, page, settings):
        """测试登录页面元素显示"""
        login_page = LoginPage(page)

        with allure.step("导航到登录页面"):
            login_page.navigate(f"{settings.base_url}/login")

        with allure.step("检查页面元素"):
            # 检查用户名输入框
            Assertions.assert_true(page.is_visible(login_page.locators.username_input), "用户名输入框应该显示")

            # 检查密码输入框
            Assertions.assert_true(page.is_visible(login_page.locators.password_input), "密码输入框应该显示")

            # 检查登录按钮
            Assertions.assert_true(page.is_visible(login_page.locators.login_button), "登录按钮应该显示")

            # 检查页面标题
            page_title = login_page.get_page_title()
            Assertions.assert_contains(page_title, "登录")
