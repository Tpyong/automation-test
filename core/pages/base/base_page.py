import allure
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.utils.allure_helper import AllureHelper
from core.utils.logger import get_logger
from core.utils.path_helper import PathHelper

logger = get_logger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("导航到: {url}")
    def navigate(self, url: str) -> None:
        logger.info(f"导航到: {url}")
        self.page.goto(url)

    @allure.step("等待页面加载完成")
    def wait_for_page_load(self, timeout: int = 30000) -> None:
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        logger.info("页面加载完成")

    def get_locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    @allure.step("点击元素: {selector}")
    def click(self, selector: str, timeout: int = 30000) -> None:
        logger.info(f"点击元素: {selector}")
        self.page.click(selector, timeout=timeout)

    @allure.step("填充输入框: {selector} = {value}")
    def fill(self, selector: str, value: str, timeout: int = 30000) -> None:
        logger.info(f"填充输入框: {selector} = {value}")
        self.page.fill(selector, value, timeout=timeout)

    @allure.step("获取元素文本: {selector}")
    def get_text(self, selector: str, timeout: int = 30000) -> str:
        text = self.page.locator(selector).text_content(timeout=timeout)
        logger.info(f"获取元素文本: {selector} = {text}")
        return text or ""

    @allure.step("验证元素可见: {selector}")
    def is_visible(self, selector: str, timeout: int = 30000) -> bool:
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    @allure.step("等待元素可见: {selector}")
    def wait_for_visible(self, selector: str, timeout: int = 30000) -> None:
        logger.info(f"等待元素可见: {selector}")
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    @allure.step("等待元素不可见: {selector}")
    def wait_for_hidden(self, selector: str, timeout: int = 30000) -> None:
        logger.info(f"等待元素不可见: {selector}")
        self.page.wait_for_selector(selector, state="hidden", timeout=timeout)

    @allure.step("获取页面标题")
    def get_title(self) -> str:
        title = self.page.title()
        logger.info(f"页面标题: {title}")
        return title

    @allure.step("获取当前URL")
    def get_url(self) -> str:
        url = self.page.url
        logger.info(f"当前URL: {url}")
        return url

    @allure.step("截图: {name}")
    def screenshot(self, name: str = "screenshot") -> None:
        # 使用统一的命名格式：{name}_{timestamp}.png（目录已经按日期分类）
        screenshot_path = PathHelper.get_screenshot_path(name)
        self.page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"截图已保存: {screenshot_path}")
        AllureHelper.attach_screenshot(screenshot_path, name=name)
