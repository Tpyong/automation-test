"""
TodoMVC 功能测试示例
演示如何使用元素定位器管理
"""

import allure
import pytest

from core.utils.assertions import Assertions


@allure.epic("TodoMVC")
@allure.feature("待办事项管理")
class TestTodoMVC:
    """TodoMVC 功能测试"""

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.story("页面加载")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("TodoMVC 页面加载成功")
    def test_page_load(self, page):
        """测试 TodoMVC 页面加载场景"""
        # 导航到 Playwright 演示页面
        with allure.step("导航到 TodoMVC 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("验证页面标题"):
            title = page.title()
            Assertions.assert_contains(title, "TodoMVC", "页面标题应包含'TodoMVC'")

        with allure.step("验证输入框可见"):
            is_visible = page.is_visible(".new-todo")
            Assertions.assert_true(is_visible, "待办事项输入框应该可见")

    @pytest.mark.regression
    @pytest.mark.ui
    @allure.story("添加待办事项")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("添加新的待办事项")
    def test_add_todo(self, page):
        """测试添加待办事项场景"""
        # 导航到 TodoMVC 演示页面
        with allure.step("导航到 TodoMVC 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("添加待办事项"):
            page.fill(".new-todo", "测试待办事项")
            page.press(".new-todo", "Enter")

        with allure.step("验证待办事项已添加"):
            todo_item = page.locator(".todo-list li")
            Assertions.assert_true(todo_item.is_visible(), "待办事项应该显示")
            Assertions.assert_contains(todo_item.text_content(), "测试待办事项", "待办事项文本应该匹配")

    @pytest.mark.ui
    @allure.story("标记完成")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("标记待办事项为已完成")
    def test_mark_todo_completed(self, page):
        """测试标记待办事项为已完成"""
        # 导航到 TodoMVC 演示页面
        with allure.step("导航到 TodoMVC 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("添加待办事项"):
            page.fill(".new-todo", "测试待办事项")
            page.press(".new-todo", "Enter")

        with allure.step("标记待办事项为已完成"):
            page.click(".todo-list li .toggle")

        with allure.step("验证待办事项已标记为完成"):
            todo_item = page.locator(".todo-list li.completed")
            Assertions.assert_true(todo_item.is_visible(), "待办事项应该标记为已完成")

    @pytest.mark.ui
    @allure.story("删除待办事项")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("删除待办事项")
    def test_delete_todo(self, page):
        """测试删除待办事项"""
        # 导航到 TodoMVC 演示页面
        with allure.step("导航到 TodoMVC 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("添加待办事项"):
            page.fill(".new-todo", "测试待办事项")
            page.press(".new-todo", "Enter")

        with allure.step("删除待办事项"):
            todo_item = page.locator(".todo-list li")
            todo_item.hover()
            page.click(".todo-list li .destroy")

        with allure.step("验证待办事项已删除"):
            todo_items = page.locator(".todo-list li")
            Assertions.assert_false(todo_items.is_visible(), "待办事项应该已删除")

    @pytest.mark.ui
    @allure.story("页面元素检查")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("检查 TodoMVC 页面元素")
    def test_todo_page_elements(self, page):
        """测试 TodoMVC 页面元素显示"""
        # 导航到 TodoMVC 演示页面
        with allure.step("导航到 TodoMVC 演示页面"):
            page.goto("https://demo.playwright.dev/todomvc")

        with allure.step("检查页面元素"):
            # 检查待办事项输入框
            Assertions.assert_true(page.is_visible(".new-todo"), "待办事项输入框应该显示")

            # 检查页面标题
            page_title = page.title()
            Assertions.assert_contains(page_title, "TodoMVC")

            # 添加一个待办事项，使过滤器显示
            page.fill(".new-todo", "测试待办事项")
            page.press(".new-todo", "Enter")

            # 检查过滤器
            Assertions.assert_true(page.is_visible(".filters"), "过滤器应该显示")

            # 检查清除完成按钮（可能需要标记完成后才显示）
            page.click(".todo-list li .toggle")
            Assertions.assert_true(page.is_visible(".clear-completed"), "清除完成按钮应该显示")
