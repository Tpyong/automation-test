# API 测试指南

## 📋 概述

本项目提供完整的 API 测试解决方案，包含：

1. **内置 Mock 服务器** - 无需真实后端即可运行测试
2. **完整的 RESTful API 测试示例** - 包含 CRUD 操作、错误处理、性能测试
3. **Allure 报告集成** - 美观的测试报告
4. **缺陷分类** - 自动分类失败原因

所有测试都可以独立运行，无需外部依赖。

## 🚀 快速开始

### 前置准备

```bash
# 安装依赖
pip install -r requirements-dev.txt

# 配置环境变量（API 测试不需要特殊配置）
```

### 运行测试

```bash
# 运行所有 API 测试
pytest tests/api/ -v

# 运行特定测试文件
pytest tests/api/test_user_api.py -v

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
├── test_user_api.py          # 用户 API 测试（使用内置 Mock 服务器）
└── README.md                 # 本文档
```

---

## 🎭 内置 Mock 服务器

### 特性

- ✅ 完整的 RESTful API 端点
- ✅ 内存数据存储，支持完整的 CRUD 操作
- ✅ 自动 ID 生成
- ✅ 数据验证（如 email 必填）
- ✅ 支持分页查询
- ✅ 正确的 HTTP 状态码返回
- ✅ 无需外部依赖

### 支持的 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users` | 获取用户列表（支持分页） |
| POST | `/api/users` | 创建用户 |
| GET | `/api/users/{id}` | 获取单个用户 |
| PUT | `/api/users/{id}` | 更新用户 |
| DELETE | `/api/users/{id}` | 删除用户 |

---

## 📝 测试示例

### 查看 [`test_user_api.py`](test_user_api.py)：

```python
import allure
import pytest
import requests

from core.utils.logger import get_logger

logger = get_logger(__name__)


class UserAPIMockService:
    """用户 API Mock 服务"""
    
    def __init__(self, host: str = 'localhost', port: int = 0):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self) -> str:
        """启动 Mock 服务"""
        # 实现省略...
        pass


@allure.epic('API 测试')
@allure.feature('用户管理 API')
class TestUserAPI:
    """用户相关 API 测试"""
    
    @pytest.mark.api
    @pytest.mark.smoke
    @allure.story('获取用户列表')
    @allure.title('测试获取用户列表 - 成功场景')
    def test_get_users_success(self, user_api_mock, api_client):
        """测试成功获取用户列表"""
        base_url = f'http://{user_api_mock.host}:{user_api_mock.port}'
        
        # 先创建一些测试数据
        with allure.step('准备测试数据'):
            for i in range(5):
                user_data = {
                    'name': f'用户{i+1}',
                    'email': f'user{i+1}@example.com',
                    'age': 25 + i,
                    'role': 'user'
                }
                api_client.post(f'{base_url}/api/users', json=user_data)
        
        with allure.step('发送 GET 请求获取用户列表'):
            response = api_client.get(f'{base_url}/api/users', params={'page': 1, 'limit': 10})
        
        with allure.step('验证响应状态码'):
            assert response.status_code == 200
        
        with allure.step('验证响应包含用户数据'):
            data = response.json()
            assert 'users' in data
            assert 'total' in data
            assert data['total'] == 5
```

---

## 🎯 测试分类

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

## 📊 测试覆盖

### 包含的测试用例：

1. ✅ **获取用户列表** - 测试成功获取用户列表，支持分页
2. ✅ **创建用户** - 测试成功创建用户
3. ✅ **更新用户** - 测试成功更新用户信息
4. ✅ **删除用户** - 测试成功删除用户
5. ✅ **查询单个用户** - 测试查询用户详情
6. ✅ **分页参数验证** - 测试分页参数
7. ✅ **查询不存在用户** - 测试查询不存在的用户应返回 404
8. ✅ **缺少必填字段** - 测试创建用户时缺少必填字段应返回 400
9. ✅ **性能测试** - 测试批量获取用户的性能

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
@pytest.fixture(scope='function')
def api_client(user_api_mock):
    """API 客户端 fixture"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # 重置数据
    UserAPIMockService.reset_data()
    
    yield session
    
    session.close()
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

### Q: 如何测试真实 API？

虽然本项目的 API 测试默认使用内置 Mock 服务器。如需测试真实 API，可以：

1. 修改 `test_user_api.py`，移除 Mock 服务器相关代码
2. 配置 `API_BASE_URL` 环境变量
3. 使用真实的 API 客户端

### Q: Mock 服务器如何工作？

Mock 服务器使用 Python 内置的 `http.server` 模块创建轻量级 HTTP 服务器，在内存中存储数据，支持完整的 CRUD 操作。每次测试运行前会自动重置数据，确保测试隔离。

---

## 📚 相关文档

- [Allure Categories 配置](../../docs/core-features/ALLURE_CATEGORIES.md)
- [配置管理](../../docs/getting-started/GUIDE.md#配置管理)
- [功能特性](../../docs/core-features/FEATURES.md)

---

**最后更新**: 2026-04-04  
**维护者**: 测试团队
