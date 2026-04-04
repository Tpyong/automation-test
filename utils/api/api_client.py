"""
API 测试客户端基类
封装常用的 HTTP 请求操作
"""

import json
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import allure
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.api.assertions import Assertions
from utils.common.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """API 测试客户端"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        初始化 API 客户端

        Args:
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 默认请求头
        self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

        logger.info(f"API 客户端初始化完成，base_url: {base_url}")

    def _make_url(self, endpoint: str) -> str:
        """构建完整 URL"""
        return urljoin(self.base_url, endpoint)

    def _log_request(self, method: str, url: str, **kwargs):
        """记录请求信息"""
        logger.info(f"API 请求: {method} {url}")
        if "json" in kwargs:
            logger.debug(f"请求体: {kwargs['json']}")

    def _log_response(self, response: requests.Response):
        """记录响应信息"""
        logger.info(f"API 响应: {response.status_code} {response.url}")
        try:
            logger.debug(f"响应体: {response.json()}")
        except json.JSONDecodeError:
            logger.debug(f"响应体: {response.text}")

    @allure.step("发送 GET 请求: {endpoint}")
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[Any, Any]] = None,
        headers: Optional[Dict[Any, Any]] = None,
    ) -> requests.Response:
        """发送 GET 请求"""
        url = self._make_url(endpoint)
        self._log_request("GET", url, params=params)

        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)

        self._log_response(response)
        return response

    @allure.step("发送 POST 请求: {endpoint}")
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[Any, Any]] = None,
        json_data: Optional[Dict[Any, Any]] = None,
        headers: Optional[Dict[Any, Any]] = None,
    ) -> requests.Response:
        """发送 POST 请求"""
        url = self._make_url(endpoint)
        self._log_request("POST", url, json=json_data, data=data)

        response = self.session.post(url, data=data, json=json_data, headers=headers, timeout=self.timeout)

        self._log_response(response)
        return response

    @allure.step("发送 PUT 请求: {endpoint}")
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[Any, Any]] = None,
        json_data: Optional[Dict[Any, Any]] = None,
        headers: Optional[Dict[Any, Any]] = None,
    ) -> requests.Response:
        """发送 PUT 请求"""
        url = self._make_url(endpoint)
        self._log_request("PUT", url, json=json_data, data=data)

        response = self.session.put(url, data=data, json=json_data, headers=headers, timeout=self.timeout)

        self._log_response(response)
        return response

    @allure.step("发送 DELETE 请求: {endpoint}")
    def delete(self, endpoint: str, headers: Optional[Dict[Any, Any]] = None) -> requests.Response:
        """发送 DELETE 请求"""
        url = self._make_url(endpoint)
        self._log_request("DELETE", url)

        response = self.session.delete(url, headers=headers, timeout=self.timeout)

        self._log_response(response)
        return response

    def set_token(self, token: str, token_type: str = "Bearer") -> None:
        """设置认证 Token"""
        self.session.headers["Authorization"] = f"{token_type} {token}"
        logger.info(f"设置认证 Token: {token_type}")

    def clear_token(self) -> None:
        """清除认证 Token"""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
            logger.info("清除认证 Token")

    def set_header(self, key: str, value: str) -> None:
        """设置请求头"""
        self.session.headers[key] = value

    def close(self) -> None:
        """关闭会话"""
        self.session.close()
        logger.info("API 客户端会话已关闭")


class APIAssertions:
    """API 测试断言工具类"""

    @staticmethod
    @allure.step("验证状态码: {expected}")
    def assert_status_code(response: requests.Response, expected: int) -> None:
        """验证响应状态码"""
        actual = response.status_code
        Assertions.assert_equal(actual, expected, f"期望状态码: {expected}, 实际状态码: {actual}")

    @staticmethod
    @allure.step("验证响应包含字段: {field}")
    def assert_response_has_field(response: requests.Response, field: str) -> None:
        """验证响应 JSON 包含指定字段"""
        try:
            data = response.json()
            Assertions.assert_in(field, data, f"响应中应包含字段: {field}")
        except json.JSONDecodeError:
            Assertions.assert_true(False, "响应不是有效的 JSON 格式")

    @staticmethod
    @allure.step("验证响应字段值: {field} = {expected}")
    def assert_response_field_equals(response: requests.Response, field: str, expected: Any) -> None:
        """验证响应 JSON 字段值"""
        try:
            data = response.json()
            actual = data.get(field)
            Assertions.assert_equal(actual, expected, f"字段 {field} 期望值: {expected}, 实际值: {actual}")
        except json.JSONDecodeError:
            Assertions.assert_true(False, "响应不是有效的 JSON 格式")

    @staticmethod
    @allure.step("验证响应时间小于 {max_time}ms")
    def assert_response_time(response: requests.Response, max_time: int = 2000) -> None:
        """验证响应时间"""
        elapsed_ms = response.elapsed.total_seconds() * 1000
        Assertions.assert_true(elapsed_ms < max_time, f"响应时间 {elapsed_ms}ms 超过阈值 {max_time}ms")
