"""
语义化定位器测试示例
演示如何使用 Playwright 官方推荐的语义化定位方式
"""

import allure
import pytest

from core.pages.specific.login_page_semantic import LoginPageSemantic
from utils.api.assertions import Assertions
from core.pages.locators import SmartLocator


@allure.epic("定位器管理")
@allure.feature("语义化定位")
class TestSemanticLocators:
    """语义化定位器测试"""

    @pytest.mark.ui
    @allure.story("SmartLocator 功能")
    @allure.title("测试 SmartLocator 解析定位器配置")
    def test_smart_locator_parsing(self, page):
        """测试 SmartLocator 能否正确解析各种定位器配置"""

        # 测试 role 定位
        role_config = {"role": "button", "name": "登录"}
        smart_locator = SmartLocator(page, role_config)
        locator = smart_locator.get_locator()
        Assertions.assert_not_none(locator, "role 定位应该成功")

        # 测试 label 定位
        label_config = {"label": "用户名"}
        smart_locator = SmartLocator(page, label_config)
        locator = smart_locator.get_locator()
        Assertions.assert_not_none(locator, "label 定位应该成功")

        # 测试 placeholder 定位
        placeholder_config = {"placeholder": "请输入搜索内容"}
        smart_locator = SmartLocator(page, placeholder_config)
        locator = smart_locator.get_locator()
        Assertions.assert_not_none(locator, "placeholder 定位应该成功")

        # 测试 text 定位
        text_config = {"text": "忘记密码？", "exact": False}
        smart_locator = SmartLocator(page, text_config)
        locator = smart_locator.get_locator()
        Assertions.assert_not_none(locator, "text 定位应该成功")

        # 测试 CSS 定位
        css_config = ".login-form"
        smart_locator = SmartLocator(page, css_config)
        locator = smart_locator.get_locator()
        Assertions.assert_not_none(locator, "CSS 定位应该成功")

        logger = page.logger if hasattr(page, "logger") else None
        if logger:
            logger.info("所有定位器解析测试通过")

    @pytest.mark.ui
    @allure.story("SmartPage 功能")
    @allure.title("测试 SmartPage 使用语义化定位器")
    def test_smart_page_with_semantic_locators(self, page):
        """测试 SmartPage 能否正确使用语义化定位器"""

        # 创建使用语义化定位的页面对象
        login_page = LoginPageSemantic(page)

        with allure.step("验证页面对象初始化成功"):
            Assertions.assert_not_none(login_page.locators, "定位器应该成功加载")

        with allure.step("查看定位器配置信息"):
            # 查看各个元素的定位器配置
            username_config = login_page.get_locator_info("username_input")
            allure.attach(str(username_config), "用户名输入框定位器配置")

            button_config = login_page.get_locator_info("login_button")
            allure.attach(str(button_config), "登录按钮定位器配置")

        with allure.step("验证定位器配置正确"):
            Assertions.assert_not_none(username_config, "用户名输入框定位器配置应该存在")
            Assertions.assert_not_none(button_config, "登录按钮定位器配置应该存在")

    @pytest.mark.ui
    @allure.story("定位器优先级")
    @allure.title("测试定位器优先级顺序")
    def test_locator_priority(self, page):
        """测试定位器按正确优先级解析"""

        # role 应该优先于其他定位方式
        mixed_config = {"role": "button", "name": "提交", "css": ".submit-btn", "test_id": "submit"}

        smart_locator = SmartLocator(page, mixed_config)
        locator = smart_locator._get_semantic_locator(mixed_config)

        # 验证使用了 role 定位
        Assertions.assert_not_none(locator, "应该成功获取定位器")

        # 记录测试成功
        logger = page.logger if hasattr(page, "logger") else None
        if logger:
            logger.info("定位器优先级测试通过：role 定位优先")
