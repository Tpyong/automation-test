# 页面对象模块
from .base.base_page import BasePage
from .specific.login_page import LoginPage
from .specific.login_page_semantic import LoginPageSemantic

__all__ = ["BasePage", "LoginPage", "LoginPageSemantic"]