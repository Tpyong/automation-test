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

from core.utils.logger import get_logger

logger = get_logger(__name__)


class LocatorManager:
    """元素定位器管理器"""

    def __init__(self, page_name: str, locators_dir: str = "locators"):
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

        logger.warning(f"未找到定位器文件: {self.page_name}")

    def _load_yaml(self, file_path: Path) -> None:
        """加载 YAML 定位器文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.locators = yaml.safe_load(f) or {}
            logger.info(f"成功加载 YAML 定位器: {file_path}")
        except Exception as e:
            logger.error(f"加载 YAML 定位器失败: {file_path}, 错误: {e}")

    def _load_json(self, file_path: Path) -> None:
        """加载 JSON 定位器文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.locators = json.load(f)
            logger.info(f"成功加载 JSON 定位器: {file_path}")
        except Exception as e:
            logger.error(f"加载 JSON 定位器失败: {file_path}, 错误: {e}")

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

    def get_by_strategy(
        self, element_name: str, strategy: str = "default"
    ) -> Union[str, Dict[str, Any]]:
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

    def __getattr__(self, element_name: str) -> Union[str, Dict[str, Any]]:
        """支持通过属性方式访问定位器"""
        return self.get(element_name)

    def __getitem__(self, element_name: str) -> Union[str, Dict[str, Any]]:
        """支持通过字典方式访问定位器"""
        return self.get(element_name)


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
            return self.page.locator(self.config)

        if isinstance(self.config, dict):
            # 语义化定位方式
            return self._get_semantic_locator(self.config)

        else:
            raise ValueError(f"不支持的定位器配置: {self.config}")

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
        # 1. get_by_role - 最推荐的方式
        if "role" in config:
            role = config["role"]
            name = config.get("name")  # 可选的 accessible name
            if name:
                return self.page.get_by_role(role, name=name)
            return self.page.get_by_role(role)

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

        # 8. CSS 选择器
        if "css" in config:
            return self.page.locator(config["css"])

        # 9. XPath 选择器
        if "xpath" in config:
            return self.page.locator(config["xpath"])

        # 默认使用第一个值作为 CSS 选择器
        first_value = list(config.values())[0]
        if isinstance(first_value, str):
            return self.page.locator(first_value)

        raise ValueError(f"无法识别的定位器配置: {config}")


class SmartPage:
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
        self.page = page
        self.locators: Optional[LocatorManager] = None

        if page_name:
            self.locators = LocatorManager(page_name)

    def get_smart_locator(self, element_name: str) -> SmartLocator:
        """获取智能定位器"""
        if not self.locators:
            raise ValueError("未设置页面名称，无法使用定位器管理")

        config = self.locators.get(element_name)
        return SmartLocator(self.page, config)

    def get_playwright_locator(self, element_name: str) -> Locator:
        """获取 Playwright Locator 对象"""
        return self.get_smart_locator(element_name).get_locator()

    def click(self, element_name: str, **kwargs: Any) -> None:
        """点击元素"""
        locator = self.get_playwright_locator(element_name)
        locator.click(**kwargs)

    def fill(self, element_name: str, value: str, **kwargs: Any) -> None:
        """填充输入框"""
        locator = self.get_playwright_locator(element_name)
        locator.fill(value, **kwargs)

    def get_text(self, element_name: str, **kwargs: Any) -> Optional[str]:
        """获取元素文本"""
        locator = self.get_playwright_locator(element_name)
        return locator.text_content(**kwargs)

    def is_visible(self, element_name: str, **kwargs: Any) -> bool:
        """检查元素是否可见"""
        locator = self.get_playwright_locator(element_name)
        return locator.is_visible(**kwargs)

    def is_enabled(self, element_name: str, **kwargs: Any) -> bool:
        """检查元素是否可用"""
        locator = self.get_playwright_locator(element_name)
        return locator.is_enabled(**kwargs)

    def is_checked(self, element_name: str, **kwargs: Any) -> bool:
        """检查复选框/单选框是否选中"""
        locator = self.get_playwright_locator(element_name)
        return locator.is_checked(**kwargs)

    def check(self, element_name: str, **kwargs: Any) -> None:
        """勾选复选框"""
        locator = self.get_playwright_locator(element_name)
        locator.check(**kwargs)

    def uncheck(self, element_name: str, **kwargs: Any) -> None:
        """取消勾选复选框"""
        locator = self.get_playwright_locator(element_name)
        locator.uncheck(**kwargs)

    def select_option(self, element_name: str, value: str, **kwargs: Any) -> None:
        """选择下拉框选项"""
        locator = self.get_playwright_locator(element_name)
        locator.select_option(value, **kwargs)

    def hover(self, element_name: str, **kwargs: Any) -> None:
        """鼠标悬停"""
        locator = self.get_playwright_locator(element_name)
        locator.hover(**kwargs)

    def scroll_into_view(self, element_name: str, **kwargs: Any) -> None:
        """滚动到元素可见"""
        locator = self.get_playwright_locator(element_name)
        locator.scroll_into_view_if_needed(**kwargs)

    def wait_for_visible(self, element_name: str, timeout: int = 30000) -> None:
        """等待元素可见"""
        locator = self.get_playwright_locator(element_name)
        locator.wait_for(state="visible", timeout=timeout)

    def wait_for_hidden(self, element_name: str, timeout: int = 30000) -> None:
        """等待元素隐藏"""
        locator = self.get_playwright_locator(element_name)
        locator.wait_for(state="hidden", timeout=timeout)


# 保持向后兼容
BasePageWithLocators = SmartPage
