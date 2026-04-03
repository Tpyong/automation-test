"""
测试用例失败示例 - 用于验证 Allure Categories 功能
"""

import allure
import pytest
from core.utils.assertions import Assertions


@allure.epic("测试验证")
@allure.feature("Categories 功能测试")
class TestCategoriesDemo:
    """演示 Allure Categories 功能的测试类"""

    @pytest.mark.ui
    @allure.story("断言失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试断言失败 - 应该归类为自动化缺陷")
    @pytest.mark.skip(reason="CI 环境中会失败，仅用于本地验证 Categories 功能")
    def test_assertion_failure(self, page):
        """这个测试会失败，用于验证 Categories 功能"""
        # 故意创建一个断言失败
        with allure.step("执行一个会失败的断言"):
            # 这个断言会失败
            Assertions().assert_equal(1, 2, "1 应该等于 2")

    @pytest.mark.ui
    @allure.story("元素未找到")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("测试元素未找到 - 应该归类为元素未找到")
    @pytest.mark.skip(reason="CI 环境中会失败，仅用于本地验证 Categories 功能")
    def test_element_not_found(self, page):
        """这个测试会失败，用于验证元素未找到的分类"""
        # 导航到页面
        page.goto("https://demo.playwright.dev/todomvc")

        # 尝试找一个不存在的元素（会超时失败）
        with allure.step("查找不存在的元素"):
            # 这个元素不存在，会超时
            non_existent = page.locator("#this-element-does-not-exist-12345")
            non_existent.click(timeout=1000)  # 设置短超时以便快速失败

    @pytest.mark.ui
    @allure.story("已知问题")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试已知问题 - 使用 TODO 标记")
    @pytest.mark.skip(reason="已知问题，测试未实现")
    def test_known_issue(self, page):
        """这个测试会失败，包含 TODO 标记"""
        # TODO: 这个功能还没实现，测试会失败
        with allure.step("TODO: 实现这个测试"):
            raise AssertionError("TODO: 这个测试还没实现")
