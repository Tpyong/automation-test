# 页面对象模块
from .base.base_page import BasePage
from .locators import LocatorManager, SmartLocator, SmartPage
from .specific.login_page import LoginPage
from .specific.login_page_semantic import LoginPageSemantic

__all__ = [
    "BasePage",
    "LoginPage",
    "LoginPageSemantic",
    "LocatorManager",
    "SmartLocator",
    "SmartPage",
]
