# 自动化测试指南

> **最后更新**：2026-04-08
> **目的**：提供统一的测试用例编写和代码规范指南

***

## 目录

1. [测试用例编写规范](#一测试用例编写规范)
2. [Page Object 编写规范](#二page-object-编写规范)
3. [测试用例编写规范](#三测试用例编写规范)
4. [执行验证规范](#四执行验证规范)
5. [最佳实践](#五最佳实践)

***

## 一、测试用例编写规范

### 1. 从需求到用例的转化流程

```
PRD需求文档
    ↓ ① 需求拆解 → 功能模块清单（按页面/业务域划分）
    ↓ ② 页面结构分析 → 打开页面，获取关键页面截图；识别所有交互元素
    ↓ ③ 交互行为探索 → 模拟用户交互，观察反馈；对比 PRD 与实际实现
    ↓ ④ 场景分析 → 六维场景分析（分级策略：核心功能全覆盖，一般功能正向 + 负向 + 边界）
    ↓ ⑤ 用例设计 → 用例表格（Markdown）+ 测试数据（YAML）+ RTM 附录
    ↓ ⑥ 自动化实现 → Page Object + 测试代码
    ↓ ⑦ 持续维护 → 需求变更时同步更新用例、数据和代码
```

### 2. 场景分析方法（六维定义）

| 维度     | 定义            | 示例（以登录功能为例）            |
| ------ | ------------- | ---------------------- |
| **正向** | 符合业务规则的正常流程   | 正确的用户名 + 密码登录成功，跳转首页   |
| **负向** | 不符合业务规则的输入或操作 | 错误密码、未注册账号、账号被锁定       |
| **边界** | 输入参数的临界值      | 密码长度最小值（6 位）、最大值（20 位） |
| **异常** | 系统异常状态或非预期操作  | 网络中断、服务超时、并发登录         |
| **安全** | 验证安全机制有效性     | SQL 注入、XSS 攻击、暴力破解防护   |
| **性能** | 验证响应时间和资源占用   | 页面加载速度、并发性能            |

### 3. 优先级划分标准（P0-P4）

| 优先级    | 含义         | Allure 严重级别 | 自动化建议          | 标签                     |
| ------ | ---------- | ----------- | -------------- | ---------------------- |
| **P0** | 核心流程，阻塞性功能 | BLOCKER     | 强烈推荐自动化，纳入冒烟测试 | `smoke` + `regression` |
| **P1** | 重要功能，高频使用  | CRITICAL    | 推荐自动化，纳入回归测试   | `regression`           |
| **P2** | 一般功能，常规场景  | NORMAL      | 可选自动化          | -                      |
| **P3** | 边缘场景，低频操作  | MINOR       | 一般不自动化         | -                      |
| **P4** | UI 细节，文案校验 | TRIVIAL     | 通常不自动化         | -                      |

### 4. 用例表格规范

#### 核心字段定义

| 字段名  | 必填 | 说明                |
| ---- | -- | ----------------- |
| 用例ID | ✅  | 全局唯一标识，格式：模块\_序号  |
| 用例标题 | ✅  | 简明描述测试场景          |
| 优先级  | ✅  | P0/P1/P2/P3/P4    |
| 用例类型 | ✅  | 正向/负向/边界/异常/安全/性能 |
| 前置条件 | ❌  | 执行前需满足的条件         |
| 测试步骤 | ✅  | 操作步骤，用 `<br>` 换行  |
| 测试数据 | ✅  | 输入数据，格式：字段=值      |
| 预期结果 | ✅  | 可验证的预期行为          |
| 自动化  | ✅  | ✅是 / ❌否           |
| 关联需求 | ✅  | PRD 需求编号          |
| 备注   | ❌  | 特殊说明              |

### 5. 测试数据设计规范

- **数据隔离**：名称类字段使用 `at_` 前缀区分测试数据（如 `at_user_{{random_alpha_8}}`）
- **数据幂等性**：
  - **动态数据（推荐）**：使用 `{{random_alpha_8}}`、`{{timestamp}}` 等
  - **前置清理**：测试前先删除可能存在的测试数据
- **数据覆盖**：确保测试数据覆盖六维场景

#### 测试数据文件结构

```yaml
# data/[模块名]_data.yaml

metadata:
  generated_by: AI
  module: [模块名称]
  version: "1.0"
  last_updated: "2026-04-08"
  author: "tester_name"

- case_id: LOGIN_001
  title: 正确账号密码登录成功
  priority: P0
  precondition: 用户已注册
  tags: ["smoke", "regression"]
  estimated_duration: 30
  input:
    username: at_testuser_{{random_alpha_8}}
    password: Test123!
  expect:
    success: true
    redirect_url: /dashboard
  remark: 核心冒烟用例
```

***

## 二、Page Object 编写规范

### 1. 页面类结构

```python
"""
基础页面类
提供页面操作的通用方法
"""

from playwright.sync_api import Page


class BasePage:
    """基础页面类"""

    def __init__(self, page: Page):
        """
        初始化页面

        Args:
            page: Playwright 页面对象
        """
        self.page = page

    def navigate(self, url: str) -> None:
        """
        导航到指定 URL

        Args:
            url: 目标 URL
        """
        self.page.goto(url)

    def click(self, locator) -> None:
        """
        点击元素

        Args:
            locator: 元素定位器
        """
        self.page.click(locator)

    def fill(self, locator, value: str) -> None:
        """
        填写输入框

        Args:
            locator: 元素定位器
            value: 填写值
        """
        self.page.fill(locator, value)


"""
登录页面类
"""

from core.pages.base.base_page import BasePage
from playwright.sync_api import Page


class LoginPage(BasePage):
    """登录页面类"""

    def __init__(self, page: Page):
        """
        初始化登录页面

        Args:
            page: Playwright 页面对象
        """
        super().__init__(page)
        self.username_input = page.get_by_label("用户名")
        self.password_input = page.get_by_label("密码")
        self.login_button = page.get_by_role("button", name="登录")
        self.error_message = page.get_by_text("错误信息")

    def login(self, username: str, password: str) -> None:
        """
        执行登录操作

        Args:
            username: 用户名
            password: 密码
        """
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def get_error_message(self) -> str:
        """
        获取错误信息

        Returns:
            错误信息文本
        """
        return self.page.text_content(self.error_message)
```

### 2. 元素定位优先级

1. **getByRole()**：语义化定位，最稳定
2. **getByLabel()**：标签定位，适合表单元素
3. **getByPlaceholder()**：占位符定位，适合输入框
4. **getByText()**：文本定位，适合按钮和链接
5. **getByTestId()**：测试 ID 定位
6. **CSS 选择器**：仅当以上方法都无法定位时使用
7. **XPath**：仅当以上方法都无法定位时使用

### 3. 编码规范

- **行数限制**：Page Object ≤300 行、测试文件 ≤500 行、方法 ≤50 行
- **命名规范**：
  - 类名：使用驼峰命名法（如 `LoginPage`）
  - 方法名：使用小写字母 + 下划线（如 `login`）
  - 变量名：使用小写字母 + 下划线（如 `username_input`）
- **注释规范**：为所有公共函数和类添加文档字符串

***

## 三、测试用例编写规范

### 1. 测试文件结构

```python
"""
登录模块测试
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.login_page import LoginPage
from utils.data.test_data_loader import TestDataLoader


@allure.epic("登录模块")
@allure.feature("登录功能")
class TestLogin:
    """登录模块测试类"""

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.story("登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("正确账号密码登录成功")
    def test_login_success(self, page: Page, settings: Settings) -> None:
        """测试登录成功场景"""
        login_page = LoginPage(page)

        with allure.step("导航到登录页"):
            login_page.navigate(settings.base_url)

        with allure.step("执行登录操作"):
            login_page.login("admin", "password")

        with allure.step("验证登录结果"):
            page.wait_for_url(f"{settings.base_url}/dashboard")
            assert page.url == f"{settings.base_url}/dashboard"
```

### 2. 使用测试数据

```python
"""
登录模块测试
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.login_page import LoginPage
from utils.data.test_data_loader import TestDataLoader


@allure.epic("登录模块")
@allure.feature("登录功能")
class TestLogin:
    """登录模块测试类"""

    login_data = TestDataLoader.get_login_data('login_success')

    @pytest.mark.parametrize("data", login_data)
    @allure.story("登录测试")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login(self, page: Page, settings: Settings, data: dict) -> None:
        """测试登录功能"""
        login_page = LoginPage(page)
        
        with allure.step("导航到登录页"):
            login_page.navigate(settings.base_url)
        
        with allure.step("执行登录操作"):
            login_page.login(data['username'], data['password'])
        
        with allure.step("验证登录结果"):
            if data['expect']['success']:
                page.wait_for_url(f"{settings.base_url}/dashboard")
                assert page.url == f"{settings.base_url}/dashboard"
            else:
                error_message = login_page.get_error_message()
                assert data['expect']['error_message'] in error_message
```

### 3. 测试标记

```python
@pytest.mark.smoke      # 冒烟测试
@pytest.mark.regression # 回归测试
@pytest.mark.serial     # 串行执行（数据修改类用例）
@pytest.mark.flaky(reruns=3, reruns_delay=2)  # 不稳定用例
```

### 4. conftest.py 使用指南

`tests/conftest.py` 是项目 UI 测试的核心配置文件，提供了丰富的 fixture 和测试增强功能。

**主要 Fixture**：

1. **settings** - 配置管理
   ```python
   def test_example(settings):
       print(f"Base URL: {settings.base_url}")
       print(f"Browser: {settings.browser}")
   ```

2. **page** - 浏览器页面
   ```python
   def test_login(page, settings):
       page.goto(settings.base_url)
       # 页面操作...
   ```

3. **test_data_cleanup** - 测试数据清理
   ```python
   def test_create_user(page, test_data_cleanup):
       # 创建用户
       user_id = create_user()
       
       # 注册清理函数
       def cleanup():
           delete_user(user_id)
       
       test_data_cleanup["cleanup_funcs"].append(cleanup)
       
       # 测试断言...
   ```

4. **setup_teardown** - 测试前后置操作
   ```python
   def test_with_setup_teardown(page, setup_teardown):
       # 注册 setup 和 teardown 函数
       def setup():
           print("Setup: 准备测试环境")
       
       def teardown():
           print("Teardown: 清理测试环境")
       
       setup_teardown(setup_func=setup, teardown_func=teardown)
       
       # 测试操作...
   ```

5. **db_session** - 数据库会话
   ```python
   def test_database_operation(db_session):
       # 使用数据库会话进行操作
       result = db_session.query(User).filter_by(id=1).first()
       assert result is not None
   ```

6. **mock_server** - Mock 服务器
   ```python
   def test_api_with_mock(mock_server, page):
       # 配置 Mock 响应
       mock_server.add_response("/api/users", "GET", 200, {"users": []})
       
       # 访问页面，触发 API 请求
       page.goto("/users")
       # 测试断言...
   ```

### 5. 测试工具类使用

```python
"""
示例测试文件
"""

import allure
import pytest
from playwright.sync_api import Page

from tests.utils.attachment_manager import AttachmentManager
from tests.utils.report_manager import ReportManager
from tests.utils.video_manager import VideoManager


@allure.epic("示例模块")
@allure.feature("示例功能")
class TestExample:
    """示例测试类"""

    @allure.story("示例测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试工具类使用")
    def test_example(self, page: Page) -> None:
        """测试工具类使用场景"""
        test_name = "test_example"
        video_dir = "reports/videos"
        test_id = "EXAMPLE_001"
        duration = 10.5

        # 使用 VideoManager
        video_manager = VideoManager()
        video_path = video_manager.find_video_file(video_dir, test_name)
        
        # 清理空视频文件
        video_manager.clean_empty_videos()
        video_manager.clean_empty_directories()

        # 使用 AttachmentManager
        attachment_manager = AttachmentManager()
        attachment_manager.attach_screenshot(page, test_name, "测试截图")
        
        # 如果有视频文件，也可以添加视频附件
        if video_path:
            attachment_manager.attach_video(video_path, test_name, "测试视频")

        # 使用 ReportManager
        report_manager = ReportManager()
        report_manager.add_result(test_id, "passed", duration, None)
        
        # 生成测试报告摘要
        report_summary = report_manager.get_summary()
        allure.attach(str(report_summary), "测试报告摘要", allure.attachment_type.TEXT)
```

***

## 四、执行验证规范

### 1. 测试执行命令

- **执行单个模块测试**：
  ```bash
  pytest tests/e2e/test_login.py --alluredir=reports/allure-results
  ```
- **执行多浏览器测试**：
  ```bash
  pytest tests/e2e/test_login.py --alluredir=reports/allure-results --browser chromium --browser firefox
  ```
- **生成 Allure 报告**：
  ```bash
  allure generate reports/allure-results -o reports/login_allure_report --clean
  allure serve reports/allure-results
  ```

### 2. 质量评估

- **需求覆盖率**：确保所有 PRD 需求都有对应的测试用例
- **测试通过率**：目标通过率 ≥95%
- **自动化率**：P0/P1 用例自动化率 100%
- **多浏览器兼容性**：确保测试在 Chromium 和 Firefox 中都能正常运行
- **性能指标**：核心页面加载时间 P0≤3s, P1≤5s, P2≤10s

***

## 五、最佳实践

### 1. 测试分层

```
tests/
├── unit/           # 单元测试（测试独立逻辑）
├── integration/    # 集成测试（测试组件交互）
├── api/            # API 测试（测试 RESTful 接口）
└── e2e/            # E2E 测试（测试完整用户流程）
```

### 2. 代码质量检查

#### 2.1 工具介绍

| 工具         | 用途               | 命令                    |
| ---------- | ---------------- | --------------------- |
| **pylint** | 代码质量检查（风格、错误、警告） | `pylint core/ tests/` |
| **flake8** | 代码风格检查（PEP8 规范）  | `flake8 core/ tests/` |
| **black**  | 代码格式化（自动修复）      | `black core/ tests/`  |
| **isort**  | 导入排序（自动修复）       | `isort core/ tests/`  |
| **mypy**   | 类型检查             | `mypy core/`          |

#### 2.2 使用方法

**检查代码质量**：

```bash
# 运行所有代码质量检查
pylint core/ tests/
flake8 core/ tests/
mypy core/

# 自动修复代码风格
black core/ tests/
isort core/ tests/

# 一键执行所有检查和修复
black core/ tests/ && isort core/ tests/ && flake8 core/ tests/ && mypy core/
```

#### 2.3 配置文件

所有代码质量工具的配置已统一到 `pyproject.toml` 文件中：

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

#### 2.4 预提交钩子

项目已配置 pre-commit 钩子，自动在提交代码前检查代码质量：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

### 3. 页面对象模式

使用 Page Object 模式封装页面操作，提高代码的可维护性和可重用性

### 3. 数据驱动

使用 YAML 文件管理测试数据，提高测试数据的可维护性

### 4. 语义化定位

优先使用 `getByRole()`、`getByLabel()` 等语义化定位器，提高测试稳定性

### 5. 智能等待

使用 `page.wait_for_selector()` 等显式等待方法，避免使用硬编码的等待时间

### 6. 多浏览器测试

确保测试在不同浏览器中都能正常运行，提高测试的覆盖率

### 7. 问题追踪

及时记录和追踪测试过程中发现的问题，确保问题得到及时解决

### 8. 知识沉淀

将测试过程中的经验和解决方案沉淀到知识库中，供后续参考

***

## 六、常见问题及解决方案

### 1. 元素定位失败

- **解决方案**：按优先级尝试不同的定位方法，使用语义化定位器
- **最佳实践**：优先使用 `getByRole()` 等语义化定位器

### 2. 测试数据冲突

- **解决方案**：使用动态数据生成，确保测试数据的唯一性
- **最佳实践**：使用 `at_` 前缀和动态数据生成方法

### 3. 测试执行不稳定

- **解决方案**：添加适当的等待时间，使用显式等待
- **最佳实践**：使用 `page.wait_for_selector()` 等显式等待方法

### 4. 多浏览器兼容性问题

- **解决方案**：针对不同浏览器使用不同的定位器或操作方法
- **最佳实践**：在测试中添加浏览器特定的处理逻辑

### 5. 性能问题

- **解决方案**：优化测试代码，减少不必要的操作
- **最佳实践**：使用性能断言，监控页面加载时间

***

## 七、参考文档

- [系统架构文档](../docs/architecture/SYSTEM_ARCHITECTURE.md)
- [开发规范文档](../docs/development/DEVELOPMENT_GUIDELINES.md)
- [定位器使用指南](../docs/best-practices/LOCATORS_GUIDE.md)
- [Playwright 使用指南](../docs/best-practices/PLAYWRIGHT_GUIDE.md)

