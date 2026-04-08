"""
元素定位器管理模块
支持 YAML/JSON 格式的定位器文件
支持 Playwright 官方推荐的语义化定位方式
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from playwright.sync_api import Locator, Page

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import toml  # type: ignore

    HAS_TOML = True
except ImportError:
    HAS_TOML = False

# 导入基础页面类
from core.pages.base.base_page import BasePage
from utils.common.logger import get_logger

logger = get_logger(__name__)


class LocatorManager:
    """元素定位器管理器"""

    def __init__(self, page_name: str, locators_dir: str = "resources/locators/web"):
        """
        初始化定位器管理器

        Args:
            page_name: 页面名称（对应定位器文件名）
            locators_dir: 定位器文件目录
        """
        self.page_name = page_name
        self.locators_dir = Path(__file__).parent.parent.parent / locators_dir
        self.locators: Dict[str, Any] = {}
        self._load_locators()

    def _load_locators(self) -> None:
        """加载定位器文件"""
        # 尝试加载 YAML 文件
        yaml_file = self.locators_dir / f"{self.page_name}.yaml"
        if yaml_file.exists() and HAS_YAML:
            self._load_yaml(yaml_file)
            return

        # 尝试加载 YML 文件
        yml_file = self.locators_dir / f"{self.page_name}.yml"
        if yml_file.exists() and HAS_YAML:
            self._load_yaml(yml_file)
            return

        # 尝试加载 JSON 文件
        json_file = self.locators_dir / f"{self.page_name}.json"
        if json_file.exists():
            self._load_json(json_file)
            return

        # 尝试加载 TOML 文件（如果支持）
        if HAS_TOML:
            toml_file = self.locators_dir / f"{self.page_name}.toml"
            if toml_file.exists():
                self._load_toml(toml_file)
                return

        logger.warning("未找到定位器文件: %s", self.page_name)

    def _load_yaml(self, file_path: Path) -> None:
        """加载 YAML 定位器文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.locators = yaml.safe_load(f) or {}
            logger.info("成功加载 YAML 定位器: %s", file_path)
        except Exception as e:
            logger.error("加载 YAML 定位器失败: %s, 错误: %s", file_path, e)

    def _load_json(self, file_path: Path) -> None:
        """加载 JSON 定位器文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.locators = json.load(f)
            logger.info("成功加载 JSON 定位器: %s", file_path)
        except Exception as e:
            logger.error("加载 JSON 定位器失败: %s, 错误: %s", file_path, e)

    def _load_toml(self, file_path: Path) -> None:
        """加载 TOML 定位器文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.locators = toml.load(f)
            logger.info("成功加载 TOML 定位器: %s", file_path)
        except Exception as e:
            logger.error("加载 TOML 定位器失败: %s, 错误: %s", file_path, e)

    def get(self, element_name: str) -> Union[str, Dict[str, Any]]:
        """
        获取元素定位器

        Args:
            element_name: 元素名称

        Returns:
            定位器字符串或字典（语义化定位）

        Raises:
            KeyError: 如果元素不存在
        """
        if element_name not in self.locators:
            raise KeyError(f"元素 '{element_name}' 在 '{self.page_name}' 中未定义")

        locator: Any = self.locators[element_name]
        if isinstance(locator, (str, dict)):
            return locator
        raise TypeError(f"定位器类型错误: {type(locator)}")

    def get_by_strategy(self, element_name: str, strategy: str = "default") -> Union[str, Dict[str, Any]]:
        """
        按策略获取元素定位器

        Args:
            element_name: 元素名称
            strategy: 定位策略（default, css, xpath, role, label 等）

        Returns:
            定位器字符串或字典
        """
        if element_name not in self.locators:
            raise KeyError(f"元素 '{element_name}' 在 '{self.page_name}' 中未定义")

        locator: Any = self.locators[element_name]

        if isinstance(locator, str):
            return locator
        if isinstance(locator, dict):
            if strategy in locator:
                result: Any = locator[strategy]
                if isinstance(result, (str, dict)):
                    return result
            if "default" in locator:
                result = locator["default"]
                if isinstance(result, (str, dict)):
                    return result
            return locator
        raise ValueError(f"不支持的定位器格式: {locator}")

    def get_all_elements(self) -> Dict[str, Union[str, Dict[str, Any]]]:
        """
        获取所有元素定位器

        Returns:
            所有元素定位器的字典
        """
        return self.locators

    def has_element(self, element_name: str) -> bool:
        """
        检查元素是否存在

        Args:
            element_name: 元素名称

        Returns:
            元素是否存在
        """
        return element_name in self.locators

    def add_element(self, element_name: str, locator: Union[str, Dict[str, Any]]) -> None:
        """
        添加元素定位器

        Args:
            element_name: 元素名称
            locator: 定位器字符串或字典
        """
        if not isinstance(locator, (str, dict)):
            raise TypeError(f"定位器类型错误: {type(locator)}")
        self.locators[element_name] = locator
        logger.info("添加元素定位器: %s = %s", element_name, locator)

    def remove_element(self, element_name: str) -> None:
        """
        移除元素定位器

        Args:
            element_name: 元素名称
        """
        if element_name in self.locators:
            del self.locators[element_name]
            logger.info("移除元素定位器: %s", element_name)

    def __getattr__(self, element_name: str) -> Union[str, Dict[str, Any]]:
        """支持通过属性方式访问定位器"""
        return self.get(element_name)

    def __getitem__(self, element_name: str) -> Union[str, Dict[str, Any]]:
        """支持通过字典方式访问定位器"""
        return self.get(element_name)

    def __contains__(self, element_name: str) -> bool:
        """支持通过 in 操作符检查元素是否存在"""
        return element_name in self.locators

    def __len__(self) -> int:
        """返回元素定位器的数量"""
        return len(self.locators)


class SmartLocator:
    """
    智能定位器类
    支持 Playwright 官方推荐的语义化定位方式
    """

    def __init__(self, page: Page, locator_config: Union[str, Dict[str, Any]]):
        """
        初始化智能定位器

        Args:
            page: Playwright page 对象
            locator_config: 定位器配置（字符串或字典）
        """
        self.page = page
        self.config = locator_config

    def get_locator(self) -> Locator:
        """
        根据配置获取 Playwright Locator 对象

        Returns:
            Playwright Locator 对象
        """
        if isinstance(self.config, str):
            # 传统 CSS/XPath 选择器
            try:
                return self.page.locator(self.config)
            except Exception as e:
                raise TypeError(f"Failed to create Locator from string config: {self.config}, error: {e}")

        if isinstance(self.config, dict):
            # 语义化定位方式
            try:
                return self._get_semantic_locator(self.config)
            except Exception as e:
                raise TypeError(f"Failed to create Locator from dict config: {self.config}, error: {e}")

        else:
            raise ValueError(f"不支持的定位器配置：{self.config}")

    def _get_semantic_locator(self, config: Dict[str, Any]) -> Locator:
        """
        根据语义化配置获取 Locator

        支持的定位方式（按 Playwright 官方推荐顺序）:
        1. role - 按 ARIA 角色定位
        2. label - 按标签文本定位
        3. placeholder - 按 placeholder 定位
        4. text - 按文本内容定位
        5. title - 按 title 属性定位
        6. alt - 按 alt 属性定位
        7. test_id - 按 test id 定位
        8. css - CSS 选择器
        9. xpath - XPath 选择器
        """
        try:
            # 1. get_by_role - 最推荐的方式
            if "role" in config:
                role = config["role"]
                name = config.get("name")  # 可选的 accessible name
                exact = config.get("exact", False)
                include_hidden = config.get("include_hidden", False)
                if name:
                    return self.page.get_by_role(role, name=name, exact=exact, include_hidden=include_hidden)
                return self.page.get_by_role(role, include_hidden=include_hidden)

            # 2. get_by_label - 表单元素推荐
            if "label" in config:
                label = config["label"]
                exact = config.get("exact", False)
                return self.page.get_by_label(label, exact=exact)

            # 3. get_by_placeholder
            if "placeholder" in config:
                placeholder = config["placeholder"]
                exact = config.get("exact", False)
                return self.page.get_by_placeholder(placeholder, exact=exact)

            # 4. get_by_text
            if "text" in config:
                text = config["text"]
                exact = config.get("exact", False)
                return self.page.get_by_text(text, exact=exact)

            # 5. get_by_title
            if "title" in config:
                title = config["title"]
                exact = config.get("exact", False)
                return self.page.get_by_title(title, exact=exact)

            # 6. get_by_alt_text
            if "alt" in config:
                alt = config["alt"]
                exact = config.get("exact", False)
                return self.page.get_by_alt_text(alt, exact=exact)

            # 7. get_by_test_id
            if "test_id" in config:
                test_id = config["test_id"]
                return self.page.get_by_test_id(test_id)

            # 8. get_by_selector - 通用选择器
            if "selector" in config:
                return self.page.locator(config["selector"])

            # 9. CSS 选择器
            if "css" in config:
                return self.page.locator(config["css"])

            # 10. XPath 选择器
            if "xpath" in config:
                return self.page.locator(config["xpath"])

            # 11. get_by_name - 按 name 属性定位
            if "name" in config:
                name = config["name"]
                return self.page.locator(f"[name='{name}']")

            # 12. get_by_id - 按 id 属性定位
            if "id" in config:
                element_id = config["id"]
                return self.page.locator(f"#{element_id}")

            # 13. get_by_class - 按 class 属性定位
            if "class" in config:
                class_name = config["class"]
                return self.page.locator(f".{class_name}")

            # 默认使用第一个值作为 CSS 选择器
            first_value = list(config.values())[0]
            if isinstance(first_value, str):
                return self.page.locator(first_value)

            raise ValueError(f"无法识别的定位器配置：{config}")
        except Exception as e:
            raise TypeError(f"Failed to create semantic Locator from config: {config}, error: {e}")

    def __str__(self) -> str:
        """返回定位器配置的字符串表示"""
        return f"SmartLocator({self.config})"

    def __repr__(self) -> str:
        """返回定位器配置的详细表示"""
        return f"SmartLocator(page={self.page}, config={self.config})"


class SmartPage(BasePage):
    """
    智能页面对象基类
    支持语义化定位方式
    """

    def __init__(self, page: Page, page_name: Optional[str] = None):
        """
        初始化智能页面对象

        Args:
            page: Playwright page 对象
            page_name: 页面名称（用于加载定位器文件）
        """
        super().__init__(page)
        self.locators: Optional[LocatorManager] = None

        if page_name:
            self.locators = LocatorManager(page_name)

    def get_smart_locator(self, element_name: str) -> SmartLocator:
        """获取智能定位器

        Args:
            element_name: 元素名称

        Returns:
            智能定位器对象
        """
        if not self.locators:
            raise ValueError("未设置页面名称，无法使用定位器管理")

        config = self.locators.get(element_name)
        return SmartLocator(self.page, config)

    def get_playwright_locator(self, selector: Union[str, Dict[str, Any]]) -> Locator:
        """获取 Playwright Locator 对象

        Args:
            selector: 元素名称或定位策略字典

        Returns:
            Playwright Locator 对象
        """
        try:
            if isinstance(selector, dict):
                # 直接使用基类的 get_locator 方法处理定位策略字典
                return self.get_locator(selector)
            else:
                # 使用 SmartLocator 处理元素名称
                return self.get_smart_locator(selector).get_locator()
        except Exception as e:
            raise TypeError(f"Failed to get Playwright Locator for selector '{selector}', error: {e}")

    def click(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """点击元素

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.click(timeout=timeout)

    def fill(self, selector: Union[str, Dict[str, Any]], value: str, timeout: int = 30000) -> None:
        """填充输入框

        Args:
            selector: 元素名称或定位策略字典
            value: 要填充的值
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.fill(value, timeout=timeout)

    def get_text(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> str:
        """获取元素文本

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）

        Returns:
            元素文本内容
        """
        locator = self.get_playwright_locator(selector)
        return locator.text_content(timeout=timeout) or ""

    def is_visible(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> bool:
        """检查元素是否可见

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）

        Returns:
            元素是否可见
        """
        locator = self.get_playwright_locator(selector)
        return locator.is_visible(timeout=timeout)

    def is_enabled(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> bool:
        """检查元素是否可用

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）

        Returns:
            元素是否可用
        """
        locator = self.get_playwright_locator(selector)
        return locator.is_enabled(timeout=timeout)

    def is_checked(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> bool:
        """检查复选框/单选框是否选中

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）

        Returns:
            复选框/单选框是否选中
        """
        locator = self.get_playwright_locator(selector)
        return locator.is_checked(timeout=timeout)

    def check(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """勾选复选框

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.check(timeout=timeout)

    def uncheck(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """取消勾选复选框

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.uncheck(timeout=timeout)

    def select_option(self, selector: Union[str, Dict[str, Any]], value: str, timeout: int = 30000) -> None:
        """选择下拉框选项

        Args:
            selector: 元素名称或定位策略字典
            value: 选项值
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.select_option(value, timeout=timeout)

    def hover(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """鼠标悬停

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.hover(timeout=timeout)

    def scroll_into_view(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """滚动到元素可见

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.scroll_into_view_if_needed(timeout=timeout)

    def wait_for_visible(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """等待元素可见

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.wait_for(state="visible", timeout=timeout)

    def wait_for_hidden(self, selector: Union[str, Dict[str, Any]], timeout: int = 30000) -> None:
        """等待元素隐藏

        Args:
            selector: 元素名称或定位策略字典
            timeout: 超时时间（毫秒）
        """
        locator = self.get_playwright_locator(selector)
        locator.wait_for(state="hidden", timeout=timeout)


# 保持向后兼容
BasePageWithLocators = SmartPage
