"""
用户 API 测试示例

展示如何测试 RESTful API 接口，包括：
- GET/POST/PUT/DELETE 请求
- 请求参数和请求体
- 响应验证（状态码、字段值、响应时间）
- 错误处理
- Allure 报告集成

注意：这些测试需要真实的 API 后端。
如果没有真实 API，请运行 tests/api/test_mock_api.py 中的 Mock 测试。
"""

import allure
import pytest

from core.utils.api_client import APIAssertions, APIClient
from core.utils.logger import get_logger

logger = get_logger(__name__)


@allure.epic("API 测试")
@allure.feature("用户管理 API")
class TestUserAPI:
    """用户相关 API 测试"""

    @pytest.fixture(autouse=True)
    def setup(self, settings):
        """测试准备"""
        # 使用环境变量中的 API 基础 URL，如果没有则使用 mock 地址
        self.api_base_url = settings.api_base_url
        self.api_client = APIClient(base_url=self.api_base_url, timeout=settings.api_timeout / 1000)
        logger.info(f"API 客户端初始化完成：{self.api_base_url}")

    @pytest.mark.api
    @pytest.mark.smoke
    @allure.story("获取用户列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取用户列表 - 成功场景")
    def test_get_users_success(self):
        """测试成功获取用户列表"""
        with allure.step("发送 GET 请求获取用户列表"):
            response = self.api_client.get("/api/users", params={"page": 1, "limit": 10})

        with allure.step("验证响应状态码"):
            APIAssertions.assert_status_code(response, 200)

        with allure.step("验证响应包含用户数据"):
            APIAssertions.assert_response_has_field(response, "users")
            APIAssertions.assert_response_has_field(response, "total")

        with allure.step("验证响应时间"):
            APIAssertions.assert_response_time(response, max_time=2000)

    @pytest.mark.api
    @allure.story("创建用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试创建用户 - 成功场景")
    def test_create_user_success(self):
        """测试成功创建用户"""
        # 准备测试数据
        user_data = {
            "name": "测试用户",
            "email": "testuser@example.com",
            "age": 25,
            "role": "user",
        }

        with allure.step("准备用户数据"):
            logger.info(f"创建用户数据：{user_data}")

        with allure.step("发送 POST 请求创建用户"):
            response = self.api_client.post("/api/users", json_data=user_data)

        with allure.step("验证创建成功"):
            APIAssertions.assert_status_code(response, 201)
            APIAssertions.assert_response_has_field(response, "id")
            APIAssertions.assert_response_field_equals(response, "name", user_data["name"])
            APIAssertions.assert_response_field_equals(response, "email", user_data["email"])

        with allure.step("验证响应时间"):
            APIAssertions.assert_response_time(response, max_time=3000)

    @pytest.mark.api
    @allure.story("更新用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试更新用户信息 - 成功场景")
    def test_update_user_success(self):
        """测试成功更新用户信息"""
        # 先创建一个用户
        create_data = {"name": "原始用户", "email": "original@example.com", "age": 20}
        create_response = self.api_client.post("/api/users", json_data=create_data)
        user_id = create_response.json().get("id")

        with allure.step("准备更新数据"):
            update_data = {"name": "更新后的用户", "age": 26}

        with allure.step("发送 PUT 请求更新用户"):
            response = self.api_client.put(f"/api/users/{user_id}", json_data=update_data)

        with allure.step("验证更新成功"):
            APIAssertions.assert_status_code(response, 200)
            APIAssertions.assert_response_field_equals(response, "name", update_data["name"])
            APIAssertions.assert_response_field_equals(response, "age", update_data["age"])

    @pytest.mark.api
    @allure.story("删除用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试删除用户 - 成功场景")
    def test_delete_user_success(self):
        """测试成功删除用户"""
        # 先创建一个用户
        create_data = {"name": "待删除用户", "email": "delete@example.com"}
        create_response = self.api_client.post("/api/users", json_data=create_data)
        user_id = create_response.json().get("id")

        with allure.step("发送 DELETE 请求删除用户"):
            response = self.api_client.delete(f"/api/users/{user_id}")

        with allure.step("验证删除成功"):
            APIAssertions.assert_status_code(response, 204)

        with allure.step("验证用户已不存在"):
            get_response = self.api_client.get(f"/api/users/{user_id}")
            APIAssertions.assert_status_code(get_response, 404)

    @pytest.mark.api
    @allure.story("查询单个用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试查询用户详情 - 成功场景")
    def test_get_user_by_id(self):
        """测试查询用户详情"""
        # 先创建一个用户
        create_data = {"name": "查询用户", "email": "query@example.com"}
        create_response = self.api_client.post("/api/users", json_data=create_data)
        user_id = create_response.json().get("id")

        with allure.step("发送 GET 请求查询用户"):
            response = self.api_client.get(f"/api/users/{user_id}")

        with allure.step("验证查询成功"):
            APIAssertions.assert_status_code(response, 200)
            APIAssertions.assert_response_field_equals(response, "id", user_id)
            APIAssertions.assert_response_field_equals(response, "name", create_data["name"])

    @pytest.mark.api
    @allure.story("参数验证")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试分页参数 - 成功场景")
    def test_get_users_with_pagination(self):
        """测试分页参数"""
        with allure.step("发送带分页参数的请求"):
            response = self.api_client.get("/api/users", params={"page": 2, "limit": 5})

        with allure.step("验证响应"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            if "users" in data:
                assert len(data["users"]) <= 5, "返回的用户数量不应超过 limit 限制"

    @pytest.mark.api
    @allure.story("错误处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试查询不存在的用户 - 失败场景")
    def test_get_nonexistent_user(self):
        """测试查询不存在的用户应返回 404"""
        with allure.step("发送 GET 请求查询不存在的用户"):
            response = self.api_client.get("/api/users/999999")

        with allure.step("验证返回 404"):
            APIAssertions.assert_status_code(response, 404)

    @pytest.mark.api
    @allure.story("错误处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试创建用户时缺少必填字段 - 失败场景")
    def test_create_user_missing_required_fields(self):
        """测试创建用户时缺少必填字段应返回 400"""
        # 缺少必需的字段（如 email）
        invalid_data = {"name": "不完整的用户"}

        with allure.step("发送 POST 请求（缺少必填字段）"):
            response = self.api_client.post("/api/users", json_data=invalid_data)

        with allure.step("验证返回 400 错误"):
            APIAssertions.assert_status_code(response, 400)

    @pytest.mark.api
    @allure.story("性能测试")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("测试批量获取用户的性能")
    def test_get_users_performance(self):
        """测试批量获取用户的性能"""
        with allure.step("多次请求获取用户列表"):
            response_times = []
            for i in range(5):
                response = self.api_client.get("/api/users")
                elapsed_ms = response.elapsed.total_seconds() * 1000
                response_times.append(elapsed_ms)
                logger.info(f"第 {i + 1} 次请求耗时：{elapsed_ms:.2f}ms")

        with allure.step("计算平均响应时间"):
            avg_time = sum(response_times) / len(response_times)
            logger.info(f"平均响应时间：{avg_time:.2f}ms")
            allure.attach.body(f"平均响应时间：{avg_time:.2f}ms", attachment_type=allure.attachment_type.TEXT)

        with allure.step("验证性能指标"):
            # 注意：真实 API 的性能测试，如果 API 不可用会失败
            # CI 环境中建议跳过或使用 Mock 测试
            assert avg_time < 1000, f"平均响应时间 {avg_time:.2f}ms 超过阈值 1000ms"
