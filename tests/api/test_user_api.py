"""
用户 API 测试示例

展示如何测试 RESTful API 接口，包括：
- GET/POST/PUT/DELETE 请求
- 请求参数和请求体
- 响应验证（状态码、字段值、响应时间）
- 错误处理
- Allure 报告集成

使用 Flask 实现的 Mock 服务器，无需真实 API 后端即可运行测试
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Generator
from urllib.parse import parse_qs, urlparse

import allure
import pytest
import requests

from utils.common.logger import get_logger

logger = get_logger(__name__)


class UserAPIHandler(BaseHTTPRequestHandler):
    """用户 API 请求处理器"""

    users: Dict[int, Dict[str, Any]] = {}
    next_id: int = 1

    def log_message(self, format, *args):
        """禁用默认日志"""
        pass

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_body(self) -> Dict[str, Any]:
        """读取请求体"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(body)
        return {}

    def do_GET(self):  # pylint: disable=invalid-name
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)

        # GET /api/users - 获取用户列表
        if path == "/api/users":
            page = int(params.get("page", ["1"])[0])
            limit = int(params.get("limit", ["10"])[0])

            all_users = list(UserAPIHandler.users.values())
            start = (page - 1) * limit
            end = start + limit
            paginated_users = all_users[start:end]

            self._send_json_response(
                200, {"users": paginated_users, "total": len(all_users), "page": page, "limit": limit}
            )
            return

        # GET /api/users/{id} - 获取单个用户
        if path.startswith("/api/users/"):
            try:
                user_id = int(path.split("/")[-1])
                if user_id in UserAPIHandler.users:
                    self._send_json_response(200, UserAPIHandler.users[user_id])
                else:
                    self._send_json_response(404, {"error": "User not found"})
            except (ValueError, IndexError):
                self._send_json_response(400, {"error": "Invalid user ID"})
            return

        self._send_json_response(404, {"error": "Not found"})

    def do_POST(self):  # pylint: disable=invalid-name
        """处理 POST 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # POST /api/users - 创建用户
        if path == "/api/users":
            try:
                body = self._read_body()

                # 验证必填字段
                if not body or "email" not in body:
                    self._send_json_response(400, {"error": "Missing required field: email"})
                    return

                user_id = UserAPIHandler.next_id
                UserAPIHandler.next_id += 1

                user = {
                    "id": user_id,
                    "name": body.get("name", ""),
                    "email": body.get("email", ""),
                    "age": body.get("age", 0),
                    "role": body.get("role", "user"),
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                UserAPIHandler.users[user_id] = user

                self._send_json_response(201, user)
            except json.JSONDecodeError:
                self._send_json_response(400, {"error": "Invalid JSON"})
            return

        self._send_json_response(404, {"error": "Not found"})

    def do_PUT(self):  # pylint: disable=invalid-name
        """处理 PUT 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # PUT /api/users/{id} - 更新用户
        if path.startswith("/api/users/"):
            try:
                user_id = int(path.split("/")[-1])
                if user_id not in UserAPIHandler.users:
                    self._send_json_response(404, {"error": "User not found"})
                    return

                body = self._read_body()
                user = UserAPIHandler.users[user_id]

                if "name" in body:
                    user["name"] = body["name"]
                if "age" in body:
                    user["age"] = body["age"]
                user["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

                self._send_json_response(200, user)
            except json.JSONDecodeError:
                self._send_json_response(400, {"error": "Invalid JSON"})
            except (ValueError, IndexError):
                self._send_json_response(400, {"error": "Invalid user ID"})
            return

        self._send_json_response(404, {"error": "Not found"})

    def do_DELETE(self):  # pylint: disable=invalid-name
        """处理 DELETE 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # DELETE /api/users/{id} - 删除用户
        if path.startswith("/api/users/"):
            try:
                user_id = int(path.split("/")[-1])
                if user_id in UserAPIHandler.users:
                    del UserAPIHandler.users[user_id]
                    self.send_response(204)
                    self.end_headers()
                else:
                    self._send_json_response(404, {"error": "User not found"})
            except (ValueError, IndexError):
                self._send_json_response(400, {"error": "Invalid user ID"})
            return

        self._send_json_response(404, {"error": "Not found"})


class UserAPIMockService:
    """用户 API Mock 服务"""

    def __init__(self, host: str = "localhost", port: int = 0):
        self.host = host
        self.port = port
        self.server: HTTPServer = None
        self.thread: threading.Thread = None

    def start(self) -> str:
        """启动 Mock 服务"""
        self.server = HTTPServer((self.host, self.port), UserAPIHandler)

        # 如果端口是 0，获取实际分配的端口
        if self.port == 0:
            self.port = self.server.server_address[1]

        # 在后台线程中运行
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        base_url = f"http://{self.host}:{self.port}"
        logger.info("用户 API Mock 服务已启动: %s", base_url)
        return base_url

    def stop(self):
        """停止 Mock 服务"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        logger.info("用户 API Mock 服务已停止")

    @staticmethod
    def reset_data():
        """重置用户数据"""
        UserAPIHandler.users.clear()
        UserAPIHandler.next_id = 1
        logger.info("用户数据已重置")


@pytest.fixture(scope="class")
def user_api_mock() -> Generator[UserAPIMockService, None, None]:
    """用户 API Mock 服务 fixture"""
    mock_service = UserAPIMockService()
    mock_service.start()
    yield mock_service
    mock_service.stop()


@pytest.fixture(scope="function")
def api_client(user_api_mock: UserAPIMockService) -> Generator[requests.Session, None, None]:
    """API 客户端 fixture"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

    # 重置数据
    UserAPIMockService.reset_data()

    yield session

    session.close()


def get_base_url(user_api_mock: UserAPIMockService) -> str:
    """获取 API 基础 URL"""
    return f"http://{user_api_mock.host}:{user_api_mock.port}"


@allure.epic("API 测试")
@allure.feature("用户管理 API")
class TestUserAPI:
    """用户相关 API 测试"""

    @pytest.mark.api
    @pytest.mark.smoke
    @allure.story("获取用户列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取用户列表 - 成功场景")
    def test_get_users_success(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试成功获取用户列表"""
        base_url = get_base_url(user_api_mock)

        # 先创建一些测试数据
        with allure.step("准备测试数据"):
            for i in range(5):
                user_data = {"name": f"用户{i + 1}", "email": f"user{i + 1}@example.com", "age": 25 + i, "role": "user"}
                api_client.post(f"{base_url}/api/users", json=user_data)

        with allure.step("发送 GET 请求获取用户列表"):
            start_time = time.time()
            response = api_client.get(f"{base_url}/api/users", params={"page": 1, "limit": 10})
            elapsed_ms = (time.time() - start_time) * 1000

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"

        with allure.step("验证响应包含用户数据"):
            data = response.json()
            assert "users" in data, "响应中缺少 users 字段"
            assert "total" in data, "响应中缺少 total 字段"
            assert data["total"] == 5, f'期望总数 5，实际 {data["total"]}'

        with allure.step("验证响应时间"):
            assert elapsed_ms < 2000, f"响应时间 {elapsed_ms:.2f}ms 超过 2000ms"
            allure.attach(f"响应时间: {elapsed_ms:.2f}ms", name="响应时间", attachment_type=allure.attachment_type.TEXT)

    @pytest.mark.api
    @allure.story("创建用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试创建用户 - 成功场景")
    def test_create_user_success(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试成功创建用户"""
        base_url = get_base_url(user_api_mock)

        user_data = {
            "name": "测试用户",
            "email": "testuser@example.com",
            "age": 25,
            "role": "user",
        }

        with allure.step("准备用户数据"):
            logger.info("创建用户数据：%s", user_data)
            allure.attach(str(user_data), name="请求数据", attachment_type=allure.attachment_type.JSON)

        with allure.step("发送 POST 请求创建用户"):
            start_time = time.time()
            response = api_client.post(f"{base_url}/api/users", json=user_data)
            elapsed_ms = (time.time() - start_time) * 1000

        with allure.step("验证创建成功"):
            assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
            data = response.json()
            assert "id" in data, "响应中缺少 id 字段"
            assert data["name"] == user_data["name"], "name 不匹配"
            assert data["email"] == user_data["email"], "email 不匹配"

        with allure.step("验证响应时间"):
            assert elapsed_ms < 3000, f"响应时间 {elapsed_ms:.2f}ms 超过 3000ms"

    @pytest.mark.api
    @allure.story("更新用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试更新用户信息 - 成功场景")
    def test_update_user_success(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试成功更新用户信息"""
        base_url = get_base_url(user_api_mock)

        # 先创建一个用户
        with allure.step("创建测试用户"):
            create_data = {"name": "原始用户", "email": "original@example.com", "age": 20}
            response = api_client.post(f"{base_url}/api/users", json=create_data)
            user_id = response.json().get("id")
            assert user_id is not None, "创建用户失败"

        with allure.step("准备更新数据"):
            update_data = {"name": "更新后的用户", "age": 26}

        with allure.step("发送 PUT 请求更新用户"):
            response = api_client.put(f"{base_url}/api/users/{user_id}", json=update_data)

        with allure.step("验证更新成功"):
            assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
            data = response.json()
            assert data["name"] == update_data["name"], "name 未更新"
            assert data["age"] == update_data["age"], "age 未更新"

    @pytest.mark.api
    @allure.story("删除用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试删除用户 - 成功场景")
    def test_delete_user_success(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试成功删除用户"""
        base_url = get_base_url(user_api_mock)

        # 先创建一个用户
        with allure.step("创建测试用户"):
            create_data = {"name": "待删除用户", "email": "delete@example.com"}
            response = api_client.post(f"{base_url}/api/users", json=create_data)
            user_id = response.json().get("id")
            assert user_id is not None, "创建用户失败"

        with allure.step("发送 DELETE 请求删除用户"):
            response = api_client.delete(f"{base_url}/api/users/{user_id}")

        with allure.step("验证删除成功"):
            assert response.status_code == 204, f"期望状态码 204，实际 {response.status_code}"

        with allure.step("验证用户已不存在"):
            get_response = api_client.get(f"{base_url}/api/users/{user_id}")
            assert get_response.status_code == 404, f"期望状态码 404，实际 {get_response.status_code}"

    @pytest.mark.api
    @allure.story("查询单个用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试查询用户详情 - 成功场景")
    def test_get_user_by_id(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试查询用户详情"""
        base_url = get_base_url(user_api_mock)

        # 先创建一个用户
        with allure.step("创建测试用户"):
            create_data = {"name": "查询用户", "email": "query@example.com"}
            response = api_client.post(f"{base_url}/api/users", json=create_data)
            user_id = response.json().get("id")
            assert user_id is not None, "创建用户失败"

        with allure.step("发送 GET 请求查询用户"):
            response = api_client.get(f"{base_url}/api/users/{user_id}")

        with allure.step("验证查询成功"):
            assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
            data = response.json()
            assert data["id"] == user_id, "id 不匹配"
            assert data["name"] == create_data["name"], "name 不匹配"

    @pytest.mark.api
    @allure.story("参数验证")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试分页参数 - 成功场景")
    def test_get_users_with_pagination(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试分页参数"""
        base_url = get_base_url(user_api_mock)

        # 创建测试数据
        with allure.step("准备测试数据"):
            for i in range(10):
                user_data = {"name": f"用户{i + 1}", "email": f"user{i + 1}@example.com", "age": 25, "role": "user"}
                api_client.post(f"{base_url}/api/users", json=user_data)

        with allure.step("发送带分页参数的请求"):
            response = api_client.get(f"{base_url}/api/users", params={"page": 2, "limit": 5})

        with allure.step("验证响应"):
            assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
            data = response.json()
            if "users" in data:
                assert len(data["users"]) <= 5, f'返回的用户数量 {len(data["users"])} 超过 limit 限制 5'
                allure.attach(
                    f'返回用户数: {len(data["users"])}', name="分页结果", attachment_type=allure.attachment_type.TEXT
                )

    @pytest.mark.api
    @allure.story("错误处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试查询不存在的用户 - 失败场景")
    def test_get_nonexistent_user(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试查询不存在的用户应返回 404"""
        base_url = get_base_url(user_api_mock)

        with allure.step("发送 GET 请求查询不存在的用户"):
            response = api_client.get(f"{base_url}/api/users/999999")

        with allure.step("验证返回 404"):
            assert response.status_code == 404, f"期望状态码 404，实际 {response.status_code}"

    @pytest.mark.api
    @allure.story("错误处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试创建用户时缺少必填字段 - 失败场景")
    def test_create_user_missing_required_fields(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试创建用户时缺少必填字段应返回 400"""
        base_url = get_base_url(user_api_mock)

        # 缺少必需的字段（如 email）
        invalid_data = {"name": "不完整的用户"}

        with allure.step("发送 POST 请求（缺少必填字段）"):
            response = api_client.post(f"{base_url}/api/users", json=invalid_data)

        with allure.step("验证返回 400 错误"):
            assert response.status_code == 400, f"期望状态码 400，实际 {response.status_code}"

    @pytest.mark.api
    @allure.story("性能测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试批量获取用户的性能")
    def test_get_users_performance(self, user_api_mock: UserAPIMockService, api_client: requests.Session):
        """测试批量获取用户的性能"""
        base_url = get_base_url(user_api_mock)

        # 创建测试数据
        with allure.step("准备测试数据"):
            for i in range(10):
                user_data = {"name": f"用户{i + 1}", "email": f"user{i + 1}@example.com", "age": 25, "role": "user"}
                api_client.post(f"{base_url}/api/users", json=user_data)

        with allure.step("多次请求获取用户列表"):
            response_times = []
            for i in range(5):
                start_time = time.time()
                api_client.get(f"{base_url}/api/users")
                elapsed_ms = (time.time() - start_time) * 1000
                response_times.append(elapsed_ms)
                logger.info("第 %d 次请求耗时：%.2fms", i + 1, elapsed_ms)

        with allure.step("计算平均响应时间"):
            avg_time = sum(response_times) / len(response_times)
            logger.info("平均响应时间：%.2fms", avg_time)
            allure.attach(
                f"平均响应时间：{avg_time:.2f}ms", name="性能指标", attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证性能指标"):
            assert avg_time < 1000, f"平均响应时间 {avg_time:.2f}ms 超过阈值 1000ms"
