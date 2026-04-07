# 完整使用指南

本文档提供框架的详细使用指南。

## 目录

- [配置管理](#配置管理)
- [编写测试](#编写测试)
- [测试分层](#测试分层)
- [页面对象](#页面对象)
- [数据驱动](#数据驱动)
- [API 测试](#api-测试)
- [数据库测试](#数据库测试)
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

### 配置继承机制

框架实现了三层配置继承机制，优先级从高到低：

1. `.env.{env}` - 环境特定配置（最高优先级）
2. `.env` - 项目级配置
3. `.env.base` - 基础配置（所有环境的默认值）

这种机制减少了配置重复，确保所有环境都有统一的默认配置，同时允许在特定环境中覆盖需要修改的配置项。

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| BASE_URL | 测试网站地址 | https://www.example.com |
| BROWSER | 浏览器类型 | chromium |
| HEADLESS | 无头模式 | true |
| SLOW_MO | 操作延迟 | 0 |
| TIMEOUT | 超时时间 | 30000 |
| VIEWPORT_WIDTH | 浏览器宽度 | 1920 |
| VIEWPORT_HEIGHT | 浏览器高度 | 1080 |
| VIDEO_ENABLED | 启用录屏 | true |
| PLAYWRIGHT_BROWSER | 单个浏览器配置 | chromium |
| PLAYWRIGHT_BROWSERS | 多个浏览器配置（逗号分隔） | chromium,firefox |
| PLAYWRIGHT_HEADLESS | Playwright 无头模式 | 1 |
| PLAYWRIGHT_SLOWMO | Playwright 慢速执行（毫秒） | 0 |

### 配置验证

框架内置配置验证功能，会在测试启动时自动验证配置的正确性：
- 验证环境配置的完整性
- 检查数据库连接配置
- 验证报告配置
- 检查并行测试配置
- 验证日志配置

## 编写测试

### 基础测试示例

```python
import allure
import pytest
from core.pages.base_page import BasePage
from utils.api.assertions import Assertions

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

## 测试分层

框架支持企业级测试分层架构，按测试类型组织测试用例。

### 测试分层结构

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── api/            # API 测试
└── e2e/            # 端到端测试
```

### 单元测试

测试单个函数/方法，不依赖外部服务。

```python
# tests/unit/test_utils.py
import pytest
from utils.data.data_factory import DataFactory

class TestDataFactory:
    """DataFactory 单元测试"""
    
    def test_generate_user(self):
        """测试生成用户数据"""
        user = DataFactory.generate_user()
        assert "username" in user
        assert "email" in user
        assert "@" in user["email"]
```

### 集成测试

测试多个模块协作，包括数据库、缓存等。

```python
# tests/integration/test_database.py
import pytest

class TestDatabaseOperations:
    """数据库操作集成测试"""
    
    def test_user_crud(self, db_session):
        """测试用户增删改查"""
        # 创建用户
        db_session.execute(
            "INSERT INTO users (name, email) VALUES (:name, :email)",
            {"name": "test", "email": "test@example.com"}
        )
        
        # 查询用户
        result = db_session.execute(
            "SELECT * FROM users WHERE name = :name",
            {"name": "test"}
        )
        assert len(result) == 1
        assert result[0]["email"] == "test@example.com"
```

### API 测试

测试 RESTful API 接口。

```python
# tests/api/test_users_api.py
import pytest
from utils.api.api_client import APIClient

class TestUsersAPI:
    """用户 API 测试"""
    
    def test_get_users(self, api_client):
        """测试获取用户列表"""
        response = api_client.get("/api/users")
        assert response.status_code == 200
        assert "users" in response.json()
    
    def test_create_user(self, api_client):
        """测试创建用户"""
        data = {"name": "test", "email": "test@example.com"}
        response = api_client.post("/api/users", json=data)
        assert response.status_code == 201
```

### E2E 测试

测试完整业务流程。

```python
# tests/e2e/test_order_flow.py
import pytest
from core.pages.login_page import LoginPage
from core.pages.order_page import OrderPage

class TestOrderFlow:
    """订单流程 E2E 测试"""
    
    def test_complete_order(self, page, settings):
        """测试完整订单流程"""
        # 登录
        login_page = LoginPage(page)
        login_page.navigate(settings.base_url)
        login_page.login("user@example.com", "password")
        
        # 创建订单
        order_page = OrderPage(page)
        order_page.create_order(product_id=1, quantity=2)
        
        # 验证订单
        assert order_page.get_order_status() == "created"
```

### 运行指定层级的测试

```bash
# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行 API 测试
pytest tests/api/ -v

# 运行 E2E 测试
pytest tests/e2e/ -v

# 运行所有测试
pytest tests/ -v
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
from core.pages.locators import SmartPage

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
from utils.data.data_factory import get_data_factory

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
from utils.data.data_provider import DataProvider

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
from utils.api.api_client import APIClient, APIAssertions

def test_api():
    api = APIClient("https://api.example.com")
    
    # GET 请求
    response = api.get("/users")
    APIAssertions.assert_status_code(response, 200)
    
    # POST 请求
    response = api.post("/users", json_data={"name": "test"})
    APIAssertions.assert_status_code(response, 201)
```

### API 契约测试

```python
from utils.api.api_contract_tester import APIContractTester

def test_api_contract():
    """测试 API 是否符合 OpenAPI 规范"""
    tester = APIContractTester("https://api.example.com")
    
    # 从 OpenAPI 规范加载契约
    tester.load_openapi_spec("api/openapi.json")
    
    # 运行所有契约测试
    results = tester.run_all_contract_tests()
    
    # 验证所有测试通过
    assert len(results['failed']) == 0, f"契约测试失败: {results['failed']}"
```

### API 性能测试

```python
from utils.api.api_contract_tester import APIPerformanceTester

def test_api_load():
    """API 负载测试"""
    tester = APIPerformanceTester("https://api.example.com")
    
    # 负载测试：100 次请求，10 并发
    results = tester.load_test(
        path="/api/users",
        method="GET",
        iterations=100,
        concurrency=10
    )
    
    # 验证性能指标
    assert results['avg_response_time'] < 1.0  # 平均响应时间小于 1 秒
    assert results['error_rate'] < 1.0  # 错误率小于 1%
    assert results['p95_response_time'] < 2.0  # P95 响应时间小于 2 秒

def test_api_stress():
    """API 压力测试"""
    tester = APIPerformanceTester("https://api.example.com")
    
    # 压力测试：持续 60 秒，目标 100 RPS
    results = tester.stress_test(
        path="/api/users",
        method="GET",
        duration=60,
        target_rps=100
    )
    
    # 验证压力测试结果
    assert results['success_rate'] > 99.0  # 成功率大于 99%
    assert results['actual_rps'] >= 90  # 实际 RPS 接近目标
```

## 数据库测试

### 配置数据库连接

在 `.env` 文件中添加数据库配置：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=test_db
```

### 使用数据库会话（自动事务回滚）

```python
# tests/integration/test_database.py
import pytest

class TestDatabaseOperations:
    """数据库操作集成测试"""
    
    def test_user_crud(self, db_session):
        """测试用户增删改查（自动回滚）"""
        # 插入数据
        db_session.execute(
            "INSERT INTO users (name, email) VALUES (:name, :email)",
            {"name": "test", "email": "test@example.com"}
        )
        
        # 查询数据
        result = db_session.execute(
            "SELECT * FROM users WHERE name = :name",
            {"name": "test"}
        )
        assert len(result) == 1
        assert result[0]["email"] == "test@example.com"
        
        # 测试结束后自动回滚，数据库保持干净
```

### 使用测试数据管理器

```python
# tests/integration/test_data_management.py
import pytest
from utils.data.test_data_manager import TestDataBuilder

class TestDataManagement:
    """测试数据管理"""
    
    def test_with_test_data(self, test_data_manager):
        """使用测试数据管理器创建和清理数据"""
        # 创建测试数据
        builder = TestDataBuilder()
        user_id = (builder
                  .with_defaults("users")
                  .with_field("email", "test@example.com")
                  .insert("users"))
        
        # 跟踪记录用于清理
        test_data_manager.track_record("users", user_id)
        
        # 执行业务逻辑测试
        # ...
        
        # 测试结束后自动清理创建的数据
```

### 数据快照和恢复

```python
# tests/integration/test_snapshot.py
import pytest

class TestDataSnapshot:
    """数据快照测试"""
    
    def test_with_snapshot(self, test_data_manager, db_manager):
        """使用数据快照"""
        # 创建数据快照
        snapshot_file = test_data_manager.create_snapshot(
            tables=["users", "orders"],
            snapshot_name="before_test"
        )
        
        try:
            # 执行测试（会修改数据）
            # ...
            
            # 验证结果
            # ...
        finally:
            # 恢复数据快照
            test_data_manager.restore_snapshot("before_test")
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

**注意：** 请妥善保管 `config/secrets/.secrets.key` 和 `config/secrets/.secrets.salt` 文件！

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
2. 运行测试，录屏自动保存到 `reports/videos/YYYYMMDD/` 目录
3. 视频文件格式：`{测试名称}_{时间戳}.webm`（目录已按日期分类）
4. 智能录屏控制：仅为使用浏览器 fixture 的测试启用录屏
5. 空视频文件过滤：自动检测并删除 0B 的视频文件
6. 视频文件与测试用例关联：确保视频正确附加到对应的测试用例
7. 集成测试优化：使用 mock_server 的集成测试不会生成视频文件
8. 自动附加到 Allure 报告：视频文件会自动附加到 Allure 测试报告中

## 并行测试

```bash
# 自动检测 CPU 核心数
pytest -n auto

# 指定并行数
pytest -n 4
```

## 多浏览器测试

### 环境变量配置

在 `.env` 文件中配置多浏览器：

```bash
# 设置单个浏览器
PLAYWRIGHT_BROWSER=chromium

# 设置多个浏览器（逗号分隔）
PLAYWRIGHT_BROWSERS=chromium,firefox

# 禁用无头模式（查看浏览器执行过程）
PLAYWRIGHT_HEADLESS=0

# 慢速执行（毫秒）
PLAYWRIGHT_SLOWMO=100
```

### 运行多浏览器测试

```bash
# 使用环境变量中配置的浏览器
pytest -v tests/e2e/test_todomvc.py

# 命令行参数覆盖环境变量
pytest -v tests/e2e/test_todomvc.py --browser=chromium --browser=firefox

# 多浏览器并行测试
pytest -n auto -v tests/e2e/test_todomvc.py --browser=chromium --browser=firefox
```

### 查看多浏览器测试结果

多浏览器测试结果会在 Allure 报告中清晰展示，每个浏览器的测试结果都会单独显示，便于分析不同浏览器的兼容性问题。

## 附件功能

框架会自动为每个测试用例生成截图和视频，并附加到 Allure 报告中：

### 功能特点

- **自动截图**：测试完成后自动生成，保存在 `reports/screenshots/` 目录
- **自动录屏**：测试过程中自动录制，保存在 `reports/videos/` 目录
- **视频尺寸**：与视口大小匹配（默认 1920x1080），确保录制整个浏览器窗口
- **附件附加**：在测试拆卸阶段附加到 Allure 报告，确保截图和视频在生成后再附加
- **视频文件处理**：改进了视频文件的处理逻辑，确保 Firefox 浏览器的视频文件正确生成

### 配置选项

在 `.env` 文件中配置附件功能：

```bash
# 启用视频录制
VIDEO_ENABLED=true

# 视口大小（影响视频录制尺寸）
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
```

### 查看附件

1. 运行测试后，截图和视频会自动保存到 `reports/` 目录
2. Allure 报告中会显示每个测试用例的截图和视频
3. 点击测试用例详情，在 "Attachments" 部分查看附件

### 注意事项

- **浏览器兼容性**：Chrome 和 Firefox 浏览器都支持截图和视频录制
- **性能影响**：视频录制会增加测试执行时间，建议在 CI/CD 环境中使用无头模式
- **存储空间**：视频文件可能较大，建议定期清理 `reports/videos/` 目录

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
from utils.data.test_data_loader import TestDataLoader

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
from utils.common.exception_handler import ExceptionHandler

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
from utils.common.exception_handler import retry_on_exception

@retry_on_exception(max_retries=3, delay=1)
def test_flaky_operation(page):
    # 可能失败的操作
    page.click("#flaky-button")
    page.wait_for_selector("#success-message", timeout=5000)
```

#### 自定义异常

```python
from utils.common.exception_handler import TestExecutionException

def test_custom_exception(page):
    if not page.is_visible("#element"):
        raise TestExecutionException("元素未找到")
```

### 增强的 Allure 报告

#### 添加测试参数

```python
from utils.reporting.allure_helper import AllureHelper

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
from utils.reporting.allure_helper import AllureHelper

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
from utils.reporting.allure_helper import AllureHelper

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
from utils.reporting.allure_helper import AllureHelper

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

所有代码质量工具配置已统一至 `pyproject.toml`，便于集中管理。

#### 代码检查

```bash
# 使用 pylint 检查代码
pylint core/ tests/

# 使用 flake8 检查代码
flake8 core/ tests/

# 使用 mypy 进行类型检查
mypy core/
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

#### 统一配置文件

所有代码质量工具配置已迁移至 `pyproject.toml`：

```toml
[tool.black]
line-length = 120
target-version = ['py312']

[tool.isort]
profile = "black"
line_length = 120

[tool.flake8]
max-line-length = 120
ignore = "E203, W503"

[tool.pylint.main]
max-line-length = 120

[tool.mypy]
python_version = "3.10"
strict = true
```

#### 预提交钩子

使用 pre-commit 自动检查代码质量：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

## 用户体验增强功能

### 交互式测试运行器

交互式测试运行器提供友好的命令行界面，支持选择测试类别、模块和用例。

#### 使用方法

```bash
# 运行交互式测试运行器
python scripts/interactive_runner.py
```

#### 操作流程

1. 选择测试类别（unit/integration/api/e2e）
2. 选择测试模块
3. 选择运行所有用例或特定用例
4. 查看测试结果
5. 可以选择继续运行其他测试

### 测试配置向导

测试配置向导通过问答式界面引导用户配置测试环境，提供智能默认值和配置验证。

#### 使用方法

```bash
# 运行测试配置向导
python scripts/config_wizard.py
```

#### 配置内容

- **基础配置**：测试网站地址、浏览器类型、无头模式、操作延迟、超时时间
- **视口配置**：浏览器宽度、高度
- **API 配置**：API基础URL、API超时时间
- **录屏配置**：是否启用录屏功能
- **数据库配置**：数据库主机、端口、用户名、密码、数据库名称
- **测试环境配置**：测试环境（development/staging/production）

### 增强的测试结果可视化

增强的测试结果可视化提供丰富的图表和统计分析，包括通过率趋势、测试数量趋势、执行时长趋势和测试状态分布。

#### 查看报告

运行测试后，在 `reports/test-trend.html` 文件中查看详细的趋势分析。

#### 功能特性

- **丰富的图表**：多种类型的图表展示测试数据
- **模块级分析**：按模块查看测试性能和趋势
- **交互式标签**：通过标签切换查看不同模块的分析数据
- **响应式设计**：适配不同屏幕尺寸

### 智能测试建议

智能测试建议基于历史测试结果分析测试性能，提供针对性的优化建议。

#### 使用方法

```bash
# 生成智能测试建议报告
python -c "from utils.reporting.test_advisor import get_test_advisor; advisor = get_test_advisor(); advisor.generate_advisor_report()"
```

#### 分析内容

- **性能分析**：识别执行时间较长的测试
- **可靠性分析**：识别频繁失败的测试
- **模块分析**：识别表现不佳的模块
- **趋势分析**：分析测试执行趋势
- **覆盖率建议**：测试覆盖范围建议
- **执行优化**：并行执行建议

#### 报告内容

- **建议概览**：不同优先级的建议数量
- **具体建议**：详细的优化建议和操作指导
- **优先级标识**：高/中/低优先级建议区分

