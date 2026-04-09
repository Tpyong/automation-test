# 页面对象模块
from .base.base_page import BasePage
from .locators import LocatorManager, SmartLocator, SmartPage
from .specific.login_page_example import LoginPage
from .specific.login_page_semantic_example import LoginPageSemantic

__all__ = [
    "BasePage",
    "LoginPage",
    "LoginPageSemantic",
    "LocatorManager",
    "SmartLocator",
    "SmartPage",
]
