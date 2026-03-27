# 完整使用指南

本文档提供框架的详细使用指南。

## 目录

- [配置管理](#配置管理)
- [编写测试](#编写测试)
- [页面对象](#页面对象)
- [数据驱动](#数据驱动)
- [API 测试](#api-测试)
- [Mock 服务](#mock-服务)
- [敏感信息加密](#敏感信息加密)
- [新增功能](#新增功能)

## 配置管理

### 多环境配置

框架支持多环境配置：

```bash
# 开发环境
TEST_ENV=development pytest

# 测试环境
TEST_ENV=testing pytest

# 预发布环境
TEST_ENV=staging pytest
```

配置文件优先级：`.env.{env}` > `.env`

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| BASE_URL | 测试网站地址 | https://www.example.com |
| BROWSER | 浏览器类型 | chromium |
| HEADLESS | 无头模式 | false |
| SLOW_MO | 操作延迟 | 0 |
| TIMEOUT | 超时时间 | 30000 |
| VIEWPORT_WIDTH | 浏览器宽度 | 1920 |
| VIEWPORT_HEIGHT | 浏览器高度 | 1080 |
| VIDEO_ENABLED | 启用录屏 | false |

## 编写测试

### 基础测试示例

```python
import allure
import pytest
from core.pages.base_page import BasePage
from core.utils.assertions import Assertions

@allure.epic("测试套件")
@allure.feature("功能模块")
class TestExample:
    
    @pytest.mark.smoke
    @pytest.mark.ui
    @allure.story("测试场景")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("测试用例标题")
    def test_example(self, page, settings):
        base_page = BasePage(page)
        
        with allure.step("导航到页面"):
            base_page.navigate(settings.base_url)
        
        with allure.step("验证页面标题"):
            title = base_page.get_title()
            Assertions.assert_contains(title, "期望标题")
```

### 使用标记

```python
@pytest.mark.smoke      # 冒烟测试
@pytest.mark.regression # 回归测试
@pytest.mark.ui         # UI测试
@pytest.mark.api        # API测试
@pytest.mark.slow       # 慢速测试
```

## 页面对象

### 创建页面对象

```python
from core.pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "button[type='submit']"
    
    def login(self, username, password):
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)
```

### 使用语义化定位器

```python
from core.utils.locators import SmartPage

class LoginPage(SmartPage):
    def __init__(self, page):
        super().__init__(page, page_name="login_page_semantic")
    
    def login(self, username, password):
        self.fill("username_input", username)  # 使用 label 定位
        self.click("login_button")             # 使用 role 定位
```

## 数据驱动

### 使用数据工厂

```python
from core.utils.data_factory import get_data_factory

def test_with_factory():
    factory = get_data_factory()
    
    # 生成用户数据
    user = factory.generate_user()
    print(user['username'], user['email'])
    
    # 生成多个用户
    users = factory.generate_users(count=5)
```

### 使用数据提供者

```python
from core.utils.data_provider import DataProvider

# 从 JSON 文件加载数据
test_data = DataProvider.get_test_data("login_data.json")

@pytest.mark.parametrize("data", test_data)
def test_login(page, data):
    # 使用 data 进行测试
    pass
```

## API 测试

### 基础 API 测试

```python
from core.utils.api_client import APIClient, APIAssertions

def test_api():
    api = APIClient("https://api.example.com")
    
    # GET 请求
    response = api.get("/users")
    APIAssertions.assert_status_code(response, 200)
    
    # POST 请求
    response = api.post("/users", json_data={"name": "test"})
    APIAssertions.assert_status_code(response, 201)
```

## Mock 服务

### 使用 Mock 服务器

```python
def test_with_mock(mock_server):
    # 添加 Mock 端点
    mock_server.add_endpoint(
        method='GET',
        path='/api/users',
        status_code=200,
        body={'users': [{'id': 1, 'name': '张三'}]}
    )
    
    # 获取服务器地址
    base_url = mock_server.get_base_url()
    
    # 发送请求
    response = requests.get(f"{base_url}/api/users")
    
    # 验证调用次数
    assert mock_server.get_call_count('GET', '/api/users') == 1
```

### Mock 功能特性

- 支持所有 HTTP 方法
- 自定义状态码和响应体
- 响应延迟模拟
- 请求记录和调用计数

## 敏感信息加密

### 加密配置文件

```bash
# 加密 .env 文件
python scripts/secrets_tool.py encrypt .env

# 加密单个值
python scripts/secrets_tool.py encrypt-value "my-password"

# 解密 .env 文件
python scripts/secrets_tool.py decrypt .env
```

### 自动解密

配置加载时会自动解密加密值，无需手动处理。

**注意：** 请妥善保管 `.secrets.key` 和 `.secrets.salt` 文件！

## 测试数据清理

```python
def test_with_cleanup(page, test_data_cleanup):
    # 创建测试数据
    user_id = create_user("test_user")
    
    # 注册清理函数
    test_data_cleanup['cleanup_funcs'].append(lambda: delete_user(user_id))
    
    # 测试代码...
```

## 录屏功能

1. 修改 `.env` 文件，设置 `VIDEO_ENABLED=true`
2. 运行测试，录屏自动保存到 `videos/YYYYMMDD/` 目录
3. 视频文件格式：`{测试名称}_{日期}_{时间}.webm`

## 并行测试

```bash
# 自动检测 CPU 核心数
pytest -n auto

# 指定并行数
pytest -n 4
```

## 测试重试

在 `pytest.ini` 中配置：

```ini
[pytest]
addopts = --reruns=2 --reruns-delay=1
```

## 新增功能

### 测试数据管理

#### 创建测试数据文件

在 `data/test_data` 目录下创建 YAML 文件，例如 `login_data.yaml`：

```yaml
# 登录测试数据
login_success:
  - username: admin
    password: password123
    expected: 登录成功
  - username: testuser
    password: testpass
    expected: 登录成功

login_failure:
  - username: wronguser
    password: wrongpass
    expected: 用户名或密码错误
```

#### 使用测试数据

```python
from core.utils.test_data_loader import TestDataLoader

# 加载登录测试数据
login_data = TestDataLoader.get_login_data('login_success')

@pytest.mark.parametrize("data", login_data)
def test_login_success(page, data):
    username = data['username']
    password = data['password']
    expected = data['expected']
    
    # 测试代码...
```

### 统一异常处理

#### 安全执行函数

```python
from core.utils.exception_handler import ExceptionHandler

def test_with_safe_execute(page):
    # 安全执行可能失败的操作
    result = ExceptionHandler.safe_execute(
        page.click, "#submit-button", timeout=10000
    )
    
    # 处理结果
    if result is not None:
        # 操作成功
        pass
    else:
        # 操作失败，但测试继续执行
        pass
```

#### 使用异常重试装饰器

```python
from core.utils.exception_handler import retry_on_exception

@retry_on_exception(max_retries=3, delay=1)
def test_flaky_operation(page):
    # 可能失败的操作
    page.click("#flaky-button")
    page.wait_for_selector("#success-message", timeout=5000)
```

#### 自定义异常

```python
from core.utils.exception_handler import TestExecutionException

def test_custom_exception(page):
    if not page.is_visible("#element"):
        raise TestExecutionException("元素未找到")
```

### 增强的 Allure 报告

#### 添加测试参数

```python
from core.utils.allure_helper import AllureHelper

def test_with_parameters(page, settings):
    # 添加测试参数
    AllureHelper.add_parameters({
        "browser": settings.browser_type,
        "environment": settings.env,
        "viewport": f"{settings.viewport['width']}x{settings.viewport['height']}"
    })
    
    # 测试代码...
```

#### 添加链接和问题

```python
from core.utils.allure_helper import AllureHelper

def test_with_links():
    # 添加问题链接
    AllureHelper.add_issue("https://example.com/issue/123", "Bug #123")
    
    # 添加测试用例链接
    AllureHelper.add_test_case("https://example.com/testcase/456", "测试用例 #456")
    
    # 添加普通链接
    AllureHelper.add_link("https://example.com/docs", "文档")
```

#### 添加 HTML 描述

```python
from core.utils.allure_helper import AllureHelper

def test_with_html_description():
    html_desc = """
    <h3>测试描述</h3>
    <p>这是一个 <strong>HTML 格式</strong> 的测试描述。</p>
    <ul>
        <li>测试步骤 1</li>
        <li>测试步骤 2</li>
        <li>测试步骤 3</li>
    </ul>
    """
    AllureHelper.add_description_html(html_desc)
    
    # 测试代码...
```

#### 附加 JSON 数据

```python
from core.utils.allure_helper import AllureHelper

def test_with_json_data():
    test_data = {
        "user": "admin",
        "roles": ["admin", "user"],
        "permissions": {
            "read": True,
            "write": True
        }
    }
    AllureHelper.attach_json(test_data, "测试数据")
    
    # 测试代码...
```

### 依赖管理优化

#### 安装依赖

```bash
# 安装锁定版本依赖
pip install -r requirements.lock

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 更新依赖

```bash
# 更新依赖版本
pip-compile requirements.in -o requirements.lock

# 升级所有依赖
pip-compile --upgrade requirements.in -o requirements.lock
```

### 代码质量工具

#### 代码检查

```bash
# 使用 pylint 检查代码
pylint core/

# 使用 flake8 检查代码
flake8 core/
```

#### 代码格式化

```bash
# 使用 black 格式化代码
black core/ tests/

# 使用 isort 排序导入
isort core/ tests/

# 同时使用 black 和 isort
black core/ tests/ && isort core/ tests/
```

#### 配置文件

- `.pylintrc`：pylint 配置
- `.flake8`：flake8 配置
- `pyproject.toml`：black 和 isort 配置
