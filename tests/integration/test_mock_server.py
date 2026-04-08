"""
Mock 服务器使用示例测试
展示如何使用 MockServer 进行 API 测试
"""

import time
from typing import Any, Dict

import allure
import pytest
import requests

from core.services.api.mock_server import MockServer
from utils.common.logger import get_logger

logger = get_logger(__name__)


@allure.epic("Mock 服务测试")
@allure.feature("API Mock 功能")
class TestMockServer:

    @pytest.mark.api
    @pytest.mark.smoke
    @allure.story("基础 Mock 端点测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试 GET 请求 Mock")
    def test_mock_get_request(self, mock_server: MockServer) -> None:
        """测试 Mock 服务器的 GET 请求

        Args:
            mock_server: Mock 服务器实例
        """

        with allure.step("添加 Mock 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/users",
                status_code=200,
                body={
                    "users": [
                        {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
                        {"id": 2, "name": "李四", "email": "lisi@example.com"},
                    ],
                    "total": 2,
                },
            )
            base_url: str = mock_server.get_base_url()
            logger.info(f"Mock 服务器地址: {base_url}")

        with allure.step("发送 GET 请求"):
            response = requests.get(f"{base_url}/api/users", timeout=10)

        with allure.step("验证响应"):
            assert response.status_code == 200
            data: Dict[str, Any] = response.json()
            assert "users" in data
            assert len(data["users"]) == 2
            assert data["total"] == 2
            logger.info(f"GET 请求成功: {data}")

    @pytest.mark.api
    @allure.story("POST 请求 Mock 测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 POST 请求 Mock")
    def test_mock_post_request(self, mock_server: MockServer) -> None:
        """测试 Mock 服务器的 POST 请求

        Args:
            mock_server: Mock 服务器实例
        """

        with allure.step("添加 POST 端点"):
            mock_server.add_endpoint(
                method="POST",
                path="/api/users",
                status_code=201,
                body={"id": 3, "name": "王五", "email": "wangwu@example.com", "created": True},
            )
            base_url: str = mock_server.get_base_url()

        with allure.step("发送 POST 请求"):
            payload: Dict[str, str] = {"name": "王五", "email": "wangwu@example.com"}
            response = requests.post(f"{base_url}/api/users", json=payload, timeout=10)

        with allure.step("验证响应和调用计数"):
            assert response.status_code == 201
            data: Dict[str, Any] = response.json()
            assert data["created"] is True
            assert data["id"] == 3

            # 验证端点被调用次数
            call_count: int = mock_server.get_call_count("POST", "/api/users")
            assert call_count == 1
            logger.info(f"POST 请求成功，调用次数: {call_count}")

    @pytest.mark.api
    @allure.story("错误响应 Mock 测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 404 错误响应")
    def test_mock_error_response(self, mock_server: MockServer) -> None:
        """测试 Mock 服务器返回错误响应

        Args:
            mock_server: Mock 服务器实例
        """

        with allure.step("添加 404 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/not-found",
                status_code=404,
                body={"error": "Not Found", "message": "资源不存在"},
            )
            base_url: str = mock_server.get_base_url()

        with allure.step("发送请求并验证 404"):
            response = requests.get(f"{base_url}/api/not-found", timeout=10)
            assert response.status_code == 404
            data: Dict[str, Any] = response.json()
            assert data["error"] == "Not Found"
            logger.info(f"404 响应正确: {data}")

    @pytest.mark.api
    @allure.story("延迟响应 Mock 测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试延迟响应")
    def test_mock_delayed_response(self, mock_server: MockServer) -> None:
        """测试 Mock 服务器的延迟响应

        Args:
            mock_server: Mock 服务器实例
        """

        with allure.step("添加延迟端点"):
            mock_server.add_endpoint(method="GET", path="/api/slow", status_code=200, body={"status": "ok"}, delay=0.5)
            base_url: str = mock_server.get_base_url()

        with allure.step("发送请求并验证延迟"):
            start_time: float = time.time()
            response = requests.get(f"{base_url}/api/slow", timeout=10)
            elapsed: float = time.time() - start_time

            assert response.status_code == 200
            assert elapsed >= 0.5
            logger.info(f"延迟响应验证成功，耗时: {elapsed:.2f}秒")

    @pytest.mark.api
    @allure.story("请求记录测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试请求记录")
    def test_mock_request_recording(self, mock_server: MockServer) -> None:
        """测试 Mock 服务器记录请求

        Args:
            mock_server: Mock 服务器实例
        """

        with allure.step("添加端点"):
            endpoint = mock_server.add_endpoint(method="POST", path="/api/echo", status_code=200, body={"echo": True})
            base_url: str = mock_server.get_base_url()

        with allure.step("发送带参数的请求"):
            test_data: Dict[str, str] = {"message": "Hello, Mock!"}
            response = requests.post(
                f"{base_url}/api/echo",
                json=test_data,
                headers={"X-Custom-Header": "test-value"},
                timeout=10,
            )
            assert response.status_code == 200

        with allure.step("验证请求记录"):
            assert endpoint.last_request is not None
            assert endpoint.last_request["method"] == "POST"

            # 验证请求头
            headers = endpoint.last_request["headers"]
            assert "X-Custom-Header" in str(headers)

            # 验证请求体
            body = endpoint.last_request["body"]
            assert "Hello, Mock!" in body
            logger.info("请求记录验证成功")
