from typing import Any, Optional

import allure

from utils.common.logger import get_logger

logger = get_logger(__name__)


class Assertions:

    @staticmethod
    @allure.step("断言相等: {actual} == {expected}")
    def assert_equal(actual: Any, expected: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望: {expected}, 实际: {actual}"
        logger.info(f"断言相等: {msg}")
        assert actual == expected, msg

    @staticmethod
    @allure.step("断言不相等: {actual} != {expected}")
    def assert_not_equal(actual: Any, expected: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望不相等: {expected}, 实际: {actual}"
        logger.info(f"断言不相等: {msg}")
        assert actual != expected, msg

    @staticmethod
    @allure.step("断言为真: {condition}")
    def assert_true(condition: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望为真, 实际: {condition}"
        logger.info(f"断言为真: {msg}")
        assert condition, msg

    @staticmethod
    @allure.step("断言为假: {condition}")
    def assert_false(condition: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望为假, 实际: {condition}"
        logger.info(f"断言为假: {msg}")
        assert not condition, msg

    @staticmethod
    @allure.step("断言包含: {container} 包含 {element}")
    def assert_in(element: Any, container: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望 {container} 包含 {element}"
        logger.info(f"断言包含: {msg}")
        assert element in container, msg

    @staticmethod
    @allure.step("断言不包含: {container} 不包含 {element}")
    def assert_not_in(element: Any, container: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望 {container} 不包含 {element}"
        logger.info(f"断言不包含: {msg}")
        assert element not in container, msg

    @staticmethod
    @allure.step("断言不为空: {obj}")
    def assert_not_none(obj: Any, message: Optional[str] = None) -> None:
        msg = message or "期望不为 None"
        logger.info(f"断言不为空: {msg}")
        assert obj is not None, msg

    @staticmethod
    @allure.step("断言为空: {obj}")
    def assert_none(obj: Any, message: Optional[str] = None) -> None:
        msg = message or f"期望为 None, 实际: {obj}"
        logger.info(f"断言为空: {msg}")
        assert obj is None, msg

    @staticmethod
    @allure.step("断言字符串包含: {text} 包含 {substring}")
    def assert_contains(text: str, substring: str, message: Optional[str] = None) -> None:
        msg = message or f"期望 '{text}' 包含 '{substring}'"
        logger.info(f"断言字符串包含: {msg}")
        assert substring in text, msg
