"""
Mock API 测试示例

展示如何使用 MockServer 进行 API 测试，适用于：
- 开发环境还没有真实 API
- 测试第三方 API 集成
- 模拟各种边界和错误场景
- 性能测试和压力测试
"""

import time
import allure
import pytest
import requests

from utils.common.logger import get_logger

logger = get_logger(__name__)


@allure.epic("API 测试")
@allure.feature("Mock API 测试")
class TestMockUserAPI:
    """使用 Mock 服务器测试用户 API"""

    @pytest.mark.api
    @pytest.mark.smoke
    @allure.story("基础 Mock 端点测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试 GET 请求 Mock - 获取用户列表")
    def test_mock_get_users(self, mock_server):
        """测试 Mock 服务器的 GET 请求"""

        with allure.step("添加 Mock 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/users",
                status_code=200,
                body={
                    "users": [
                        {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
                        {"id": 2, "name": "李四", "email": "lisi@example.com"},
                        {"id": 3, "name": "王五", "email": "wangwu@example.com"},
                    ],
                    "total": 3,
                    "page": 1,
                    "limit": 10,
                },
            )
            base_url = mock_server.get_base_url()
            logger.info("Mock 服务器地址：%s", base_url)

        with allure.step("发送 GET 请求"):
            response = requests.get(f"{base_url}/api/users", timeout=10)

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"

        with allure.step("验证响应数据"):
            data = response.json()
            assert len(data["users"]) == 3, "应返回 3 个用户"
            assert data["total"] == 3, "总数应为 3"
            assert data["users"][0]["name"] == "张三", "第一个用户应为张三"

        with allure.step("验证响应时间"):
            elapsed_ms = response.elapsed.total_seconds() * 1000
            # Mock 服务器首次启动较慢，放宽时间阈值
            assert elapsed_ms < 3000, f"响应时间 {elapsed_ms}ms 超过阈值 3000ms"
            logger.info("响应时间：%.2fms", elapsed_ms)

    @pytest.mark.api
    @allure.story("POST 请求 Mock")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试 POST 请求 Mock - 创建用户")
    def test_mock_create_user(self, mock_server):
        """测试 Mock 服务器的 POST 请求"""

        with allure.step("添加 Mock 端点"):
            mock_server.add_endpoint(
                method="POST",
                path="/api/users",
                status_code=201,
                body={"id": 100, "name": "新用户", "email": "newuser@example.com", "created": True},
                headers={"Content-Type": "application/json"},
            )
            base_url = mock_server.get_base_url()

        with allure.step("准备用户数据"):
            user_data = {"name": "新用户", "email": "newuser@example.com"}

        with allure.step("发送 POST 请求"):
            response = requests.post(f"{base_url}/api/users", json=user_data, timeout=10)

        with allure.step("验证创建成功"):
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == 100
            assert data["name"] == "新用户"
            assert data["created"] is True

    @pytest.mark.api
    @allure.story("PUT 请求 Mock")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 PUT 请求 Mock - 更新用户")
    def test_mock_update_user(self, mock_server):
        """测试 Mock 服务器的 PUT 请求"""

        with allure.step("添加 Mock 端点"):
            mock_server.add_endpoint(
                method="PUT",
                path="/api/users/1",
                status_code=200,
                body={"id": 1, "name": "已更新", "email": "updated@example.com", "updated": True},
            )
            base_url = mock_server.get_base_url()

        with allure.step("准备更新数据"):
            update_data = {"name": "已更新", "email": "updated@example.com"}

        with allure.step("发送 PUT 请求"):
            response = requests.put(f"{base_url}/api/users/1", json=update_data, timeout=10)

        with allure.step("验证更新成功"):
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "已更新"
            assert data["updated"] is True

    @pytest.mark.api
    @allure.story("DELETE 请求 Mock")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 DELETE 请求 Mock - 删除用户")
    def test_mock_delete_user(self, mock_server):
        """测试 Mock 服务器的 DELETE 请求"""

        with allure.step("添加 Mock 端点"):
            mock_server.add_endpoint(
                method="DELETE",
                path="/api/users/1",
                status_code=204,
                body={},
            )
            base_url = mock_server.get_base_url()

        with allure.step("发送 DELETE 请求"):
            response = requests.delete(f"{base_url}/api/users/1", timeout=10)

        with allure.step("验证删除成功"):
            assert response.status_code == 204
            assert response.text == "" or len(response.content) == 0

    @pytest.mark.api
    @allure.story("错误场景模拟")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 404 错误 - 资源不存在")
    def test_mock_404_error(self, mock_server):
        """测试 Mock 服务器返回 404 错误"""

        with allure.step("添加返回 404 的 Mock 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/users/999",
                status_code=404,
                body={"error": "Not Found", "message": "用户不存在"},
            )
            base_url = mock_server.get_base_url()

        with allure.step("发送 GET 请求"):
            response = requests.get(f"{base_url}/api/users/999", timeout=10)

        with allure.step("验证返回 404"):
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "Not Found"

    @pytest.mark.api
    @allure.story("错误场景模拟")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 400 错误 - 参数验证失败")
    def test_mock_400_error(self, mock_server):
        """测试 Mock 服务器返回 400 错误"""

        with allure.step("添加返回 400 的 Mock 端点"):
            mock_server.add_endpoint(
                method="POST",
                path="/api/users",
                status_code=400,
                body={
                    "error": "Bad Request",
                    "message": "缺少必填字段：email",
                    "field": "email",
                },
            )
            base_url = mock_server.get_base_url()

        with allure.step("发送 POST 请求（缺少必填字段）"):
            response = requests.post(f"{base_url}/api/users", json={"name": "测试"}, timeout=10)

        with allure.step("验证返回 400"):
            assert response.status_code == 400
            data = response.json()
            assert "email" in data["message"]

    @pytest.mark.api
    @allure.story("性能测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试带延迟的 Mock 响应")
    def test_mock_delayed_response(self, mock_server):
        """测试 Mock 服务器的延迟响应功能"""

        with allure.step("添加带延迟的 Mock 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/slow-endpoint",
                status_code=200,
                body={"data": "慢速响应"},
                delay=2.0,  # 延迟 2 秒
            )
            base_url = mock_server.get_base_url()

        with allure.step("发送请求并测量时间"):
            start_time = time.time()
            response = requests.get(f"{base_url}/api/slow-endpoint", timeout=10)
            elapsed = time.time() - start_time

        with allure.step("验证响应"):
            assert response.status_code == 200
            logger.info("实际耗时：%.2f秒", elapsed)
            # 验证延迟生效（允许一定误差）
            assert elapsed >= 1.8, f"延迟应该至少 1.8 秒，实际 {elapsed:.2f}秒"

    @pytest.mark.api
    @allure.story("高级用法")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试自定义响应头")
    def test_mock_custom_headers(self, mock_server):
        """测试 Mock 服务器的自定义响应头"""

        with allure.step("添加带自定义头的 Mock 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/protected",
                status_code=200,
                body={"secret": "data"},
                headers={
                    "X-Custom-Header": "CustomValue",
                    "X-Request-ID": "12345",
                    "Cache-Control": "no-cache",
                },
            )
            base_url = mock_server.get_base_url()

        with allure.step("发送请求"):
            response = requests.get(f"{base_url}/api/protected", timeout=10)

        with allure.step("验证自定义响应头"):
            assert response.headers.get("X-Custom-Header") == "CustomValue"
            assert response.headers.get("X-Request-ID") == "12345"
            assert response.headers.get("Cache-Control") == "no-cache"

    @pytest.mark.api
    @allure.story("高级用法")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试请求验证")
    def test_mock_request_validation(self, mock_server):
        """测试 Mock 端点的请求响应"""

        with allure.step("添加 Mock 端点"):
            mock_server.add_endpoint(
                method="GET",
                path="/api/validate",
                status_code=200,
                body={"validated": True, "message": "请求已验证"},
            )

        with allure.step("多次调用端点"):
            base_url = mock_server.get_base_url()
            for i in range(3):
                response = requests.get(f"{base_url}/api/validate", timeout=10)
                assert response.status_code == 200
                data = response.json()
                assert data["validated"] is True

        with allure.step("验证成功"):
            logger.info("Mock 端点多次调用测试通过")
