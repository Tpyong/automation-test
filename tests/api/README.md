# API 测试指南

## 📋 概述

本项目提供两种 API 测试方式：

1. **真实 API 测试** - 测试真实的后端服务
2. **Mock API 测试** - 使用 Mock 服务器模拟 API，无需真实后端

## 🚀 快速开始

### 前置准备

```bash
# 安装依赖
pip install -r requirements-dev.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，设置 API_BASE_URL 等参数
```

### 运行测试

```bash
# 运行所有 API 测试
pytest tests/api/ -v

# 运行特定测试文件
pytest tests/api/test_user_api.py -v

# 运行 Mock API 测试
pytest tests/api/test_mock_api.py -v

# 只运行冒烟测试
pytest tests/api/ -v -m smoke

# 生成 Allure 报告
pytest tests/api/ -v --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

---

## 📁 文件结构

```
tests/api/
├── test_user_api.py          # 真实 API 测试示例
├── test_mock_api.py          # Mock API 测试示例
└── README.md                 # 本文档
```

---

## 🔧 测试真实 API

### 配置方式

在 `.env` 文件中配置：

```bash
# API 基础 URL
API_BASE_URL=https://api.example.com

# API 超时时间（毫秒）
API_TIMEOUT=30000
```

### 测试示例

查看 [`test_user_api.py`](test_user_api.py)：

```python
import allure
import pytest
from core.utils.api_client import APIClient, APIAssertions

@allure.epic("API 测试")
@allure.feature("用户管理 API")
class TestUserAPI:
    
    @pytest.fixture(autouse=True)
    def setup(self, settings):
        """每个测试前自动执行"""
        self.api_client = APIClient(
            base_url=settings.api_base_url,
            timeout=settings.api_timeout / 1000
        )
    
    @pytest.mark.api
    @allure.story("获取用户列表")
    def test_get_users_success(self):
        """测试获取用户列表"""
        response = self.api_client.get("/api/users", params={"page": 1})
        
        # 验证状态码
        APIAssertions.assert_status_code(response, 200)
        
        # 验证响应字段
        APIAssertions.assert_response_has_field(response, "users")
        
        # 验证响应时间
        APIAssertions.assert_response_time(response, max_time=2000)
```

### 可用的断言方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `assert_status_code(response, code)` | 验证状态码 | `assert_status_code(response, 200)` |
| `assert_response_has_field(response, field)` | 验证包含字段 | `assert_response_has_field(response, "data")` |
| `assert_response_field_equals(response, field, value)` | 验证字段值 | `assert_response_field_equals(response, "id", 1)` |
| `assert_response_time(response, max_ms)` | 验证响应时间 | `assert_response_time(response, 2000)` |

---

## 🎭 Mock API 测试

### 使用场景

- ✅ 开发阶段，后端 API 还未完成
- ✅ 测试第三方 API 集成
- ✅ 模拟边界情况和错误场景
- ✅ 性能测试和压力测试

### Mock 服务器功能

| 功能 | 说明 |
|------|------|
| 自定义端点 | 添加任意 HTTP 方法的端点 |
| 自定义响应 | 设置状态码、响应体、响应头 |
| 延迟模拟 | 模拟网络延迟 |
| 调用统计 | 记录端点被调用次数 |

### 测试示例

查看 [`test_mock_api.py`](test_mock_api.py)：

```python
import pytest
import requests
import allure

@allure.epic("API 测试")
@allure.feature("Mock API 测试")
class TestMockUserAPI:
    
    @pytest.mark.api
    def test_mock_get_users(self, mock_server):
        """使用 Mock 服务器测试 GET 请求"""
        
        # 1. 添加 Mock 端点
        mock_server.add_endpoint(
            method="GET",
            path="/api/users",
            status_code=200,
            body={
                "users": [
                    {"id": 1, "name": "张三"},
                    {"id": 2, "name": "李四"}
                ],
                "total": 2
            }
        )
        
        # 2. 获取 Mock 服务器地址
        base_url = mock_server.get_base_url()
        
        # 3. 发送请求并验证
        response = requests.get(f"{base_url}/api/users")
        assert response.status_code == 200
        assert len(response.json()["users"]) == 2
```

### Mock 端点高级用法

#### 1. 模拟错误响应

```python
mock_server.add_endpoint(
    method="POST",
    path="/api/users",
    status_code=400,
    body={
        "error": "Bad Request",
        "message": "缺少必填字段：email"
    }
)
```

#### 2. 模拟延迟响应

```python
mock_server.add_endpoint(
    method="GET",
    path="/api/slow-endpoint",
    status_code=200,
    body={"data": "slow"},
    delay=2.0  # 延迟 2 秒
)
```

#### 3. 自定义响应头

```python
mock_server.add_endpoint(
    method="GET",
    path="/api/protected",
    status_code=200,
    body={"secret": "data"},
    headers={
        "X-Custom-Header": "CustomValue",
        "Cache-Control": "no-cache"
    }
)
```

#### 4. 检查调用次数

```python
# 调用端点 5 次后检查
endpoint = mock_server.endpoints.get(("GET", "/api/stats"))
assert endpoint.call_count == 5
```

---

## 📊 测试分类

### 按测试类型标记

```python
@pytest.mark.api      # API 测试
@pytest.mark.smoke    # 冒烟测试
@pytest.mark.regression  # 回归测试
```

### 按严重程度标记

```python
@allure.severity(allure.severity_level.CRITICAL)   # 关键
@allure.severity(allure.severity_level.NORMAL)     # 普通
@allure.severity(allure.severity_level.MINOR)      # 次要
```

### 运行特定类型的测试

```bash
# 只运行冒烟测试
pytest tests/api/ -v -m smoke

# 只运行关键测试
pytest tests/api/ -v -k "CRITICAL"

# 排除慢速测试
pytest tests/api/ -v -m "not slow"
```

---

## 🎯 最佳实践

### 1. 测试命名规范

```python
def test_<方法>_<场景>_<预期结果>():
    # 好的命名
    def test_get_users_success():
    def test_create_user_missing_fields_should_fail():
    def test_delete_nonexistent_user_returns_404():
```

### 2. 使用 Allure 注解

```python
@allure.epic("API 测试")           # 史诗：大的功能模块
@allure.feature("用户管理")         # 特性：具体功能
@allure.story("创建用户")           # 故事：用户场景
@allure.title("测试创建成功")       # 标题：友好的显示名称
@allure.severity(BLOCKER)         # 严重程度
```

### 3. 分步骤组织测试

```python
def test_example(self):
    with allure.step("步骤 1: 准备数据"):
        # ...
    
    with allure.step("步骤 2: 发送请求"):
        # ...
    
    with allure.step("步骤 3: 验证响应"):
        # ...
```

### 4. 清理测试数据

```python
@pytest.fixture
def cleanup():
    created_ids = []
    yield created_ids
    # 清理创建的测试数据
    for id in created_ids:
        api_client.delete(f"/api/items/{id}")
```

---

## 🔍 调试技巧

### 查看详细日志

```bash
pytest tests/api/ -v -s
```

### 只运行单个测试

```bash
pytest tests/api/test_user_api.py::TestUserAPI::test_get_users_success -v -s
```

### 失败后重跑

```bash
pytest tests/api/ -v --lf  # --lf: last failed
```

### 超时调试

```python
# 在测试中打印响应时间
response = api_client.get("/api/users")
print(f"响应时间：{response.elapsed.total_seconds() * 1000:.2f}ms")
print(f"响应状态码：{response.status_code}")
print(f"响应体：{response.json()}")
```

---

## 📈 报告分析

### 查看 Allure 报告

```bash
# 生成报告
allure generate reports/allure-results -o reports/allure-report --clean

# 打开报告
allure open reports/allure-report
```

### 报告中的关键信息

1. **Categories（缺陷分类）** - 自动分类失败原因
2. **Behaviors（行为）** - 按 Epic/Feature/Story 分组
3. **Suites（套件）** - 按测试文件分组
4. **Graphs（图表）** - 可视化测试结果

---

## 🐛 常见问题

### Q: 如何跳过某些测试？

```python
@pytest.mark.skip(reason="功能未实现")
def test_future_feature():
    pass

@pytest.mark.skipif(condition, reason="条件不满足")
def test_conditional():
    pass
```

### Q: 如何处理认证？

```python
# 方式 1：在客户端中添加认证头
self.api_client.session.headers.update({
    "Authorization": f"Bearer {token}"
})

# 方式 2：使用 fixture 登录获取 token
@pytest.fixture
def auth_token():
    response = requests.post("/api/login", json={...})
    return response.json()["token"]
```

### Q: 如何测试需要数据库的 API？

```python
@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

def test_api_with_db(self, db_session):
    # 使用 db_session 准备测试数据
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    # 调用 API 测试
    response = self.api_client.get(f"/api/users/{user.id}")
    # ...
```

---

## 📚 相关文档

- [Allure Categories 配置](../../docs/core-features/ALLURE_CATEGORIES.md)
- [Mock Server 使用示例](../integration/test_mock_server.py)
- [API Client 源码](../../core/utils/api_client.py)

---

**最后更新**: 2026-04-03  
**维护者**: 测试团队
