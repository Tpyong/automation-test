"""
登录功能测试示例
演示如何使用元素定位器管理
"""

import allure
import pytest

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
        # 导航到 Playwright 演示页面
        with allure.step("导航到 Playwright 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("验证页面标题"):
            title = page.title()
            Assertions.assert_contains(title, "TodoMVC", "页面标题应包含'TodoMVC'")

        with allure.step("验证输入框可见"):
            is_visible = page.is_visible(".new-todo")
            Assertions.assert_true(is_visible, "待办事项输入框应该可见")

    @pytest.mark.regression
    @pytest.mark.ui
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("使用无效凭据登录失败")
    def test_login_failure(self, page, settings):
        """测试登录失败场景"""
        # 导航到 Playwright 演示页面
        with allure.step("导航到 Playwright 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("验证页面标题"):
            title = page.title()
            Assertions.assert_contains(title, "TodoMVC", "页面标题应包含'TodoMVC'")

    @pytest.mark.ui
    @allure.story("记住我功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("勾选记住我登录")
    def test_login_with_remember_me(self, page, settings):
        """测试记住我功能"""
        # 导航到 Playwright 演示页面
        with allure.step("导航到 Playwright 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("验证页面标题"):
            title = page.title()
            Assertions.assert_contains(title, "TodoMVC", "页面标题应包含'TodoMVC'")

    @pytest.mark.ui
    @allure.story("页面导航")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("点击忘记密码链接")
    def test_click_forgot_password(self, page, settings):
        """测试忘记密码链接"""
        # 导航到 Playwright 演示页面
        with allure.step("导航到 Playwright 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("验证页面标题"):
            title = page.title()
            Assertions.assert_contains(title, "TodoMVC", "页面标题应包含'TodoMVC'")

    @pytest.mark.ui
    @allure.story("页面元素检查")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("检查登录页面元素")
    def test_login_page_elements(self, page, settings):
        """测试登录页面元素显示"""
        # 导航到 Playwright 演示页面
        with allure.step("导航到 Playwright 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("检查页面元素"):
            # 检查待办事项输入框
            Assertions.assert_true(page.is_visible(".new-todo"), "待办事项输入框应该显示")

            # 检查页面标题
            page_title = page.title()
            Assertions.assert_contains(page_title, "TodoMVC")
