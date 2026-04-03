import allure
import pytest

from core.pages.base.base_page import BasePage
from core.utils.assertions import Assertions
from core.utils.logger import get_logger

logger = get_logger(__name__)


@allure.epic("示例测试套件")
@allure.feature("基础功能测试")
class TestSample:

    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.story("页面访问测试")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("验证 Playwright 演示页面可以正常访问")
    def test_playwright_demo_page(self, page):
        logger.info("开始执行测试: test_playwright_demo_page")

        base_page = BasePage(page)

        with allure.step("导航到 Playwright 演示页面"):
            base_page.navigate("https://demo.playwright.dev/todomvc")
            base_page.wait_for_page_load()

        with allure.step("验证页面标题"):
            title = base_page.get_title()
            Assertions.assert_contains(title, "TodoMVC", "页面标题应包含'TodoMVC'")

        with allure.step("验证输入框可见"):
            is_visible = base_page.is_visible(".new-todo", timeout=10000)
            Assertions.assert_true(is_visible, "待办事项输入框应该可见")

        with allure.step("截图记录"):
            base_page.screenshot("playwright_demo_page")

        logger.info("测试执行完成: test_playwright_demo_page")

    @pytest.mark.regression
    @pytest.mark.ui
    @allure.story("待办事项功能测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("验证添加待办事项功能")
    def test_add_todo_item(self, page):
        logger.info("开始执行测试: test_add_todo_item")

        base_page = BasePage(page)

        with allure.step("导航到 Playwright 演示页面"):
            base_page.navigate("https://demo.playwright.dev/todomvc")
            base_page.wait_for_page_load()

        with allure.step("添加待办事项"):
            base_page.fill(".new-todo", "学习 Playwright 自动化测试")
            page.keyboard.press("Enter")

        with allure.step("验证待办事项已添加"):
            todo_text = base_page.get_text(".todo-list li label")
            Assertions.assert_equal(todo_text, "学习 Playwright 自动化测试")

        with allure.step("截图记录"):
            base_page.screenshot("todo_item_added")

        logger.info("测试执行完成: test_add_todo_item")
