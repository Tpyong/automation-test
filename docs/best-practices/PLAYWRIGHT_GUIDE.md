# pytest-playwright 使用指南

## 一、安装与配置

### 1. 安装 pytest-playwright

```bash
# 安装 pytest-playwright 及其依赖
pip install pytest-playwright
# 安装浏览器
playwright install
```

### 2. 配置文件位置

pytest-playwright 的配置主要通过以下方式进行：

#### 1. pytest 配置文件
- **pyproject.toml**（推荐）：在项目根目录创建或修改此文件
- **pytest.ini**：传统的 pytest 配置文件
- **conftest.py**：在测试目录中创建或修改此文件

#### 2. 环境变量
- 可以通过环境变量设置一些运行时选项

## 二、基本使用

### 1. 测试文件编写

使用 pytest-playwright 提供的 fixtures：

```python
import pytest

def test_example(page):
    # page 是 pytest-playwright 提供的 fixture
    page.goto("https://example.com")
    assert page.title() == "Example Domain"
```

### 2. 常用 Fixtures

- **page**：提供 Playwright 的 Page 对象，用于页面操作
- **context**：提供 BrowserContext 对象，用于管理浏览器上下文
- **browser**：提供 Browser 对象，用于创建浏览器上下文
- **playwright**：提供 Playwright 对象，用于启动和管理浏览器

## 三、配置选项

### 1. 在 pyproject.toml 中配置

```toml
[tool.pytest.ini_options]
# 浏览器配置
# 可以设置默认浏览器
# 也可以通过命令行参数覆盖
# 例如：pytest --browser=firefox
```

### 2. 在环境变量中配置

可以通过环境变量来配置多浏览器启动：

```bash
# 设置单个浏览器
PLAYWRIGHT_BROWSER=chromium

# 设置多个浏览器（逗号分隔）
PLAYWRIGHT_BROWSERS=chromium,firefox

# 启用无头模式
PLAYWRIGHT_HEADLESS=1

# 慢速执行（毫秒）
PLAYWRIGHT_SLOWMO=100
```

### 3. 在 .env 文件中配置

在项目的 `.env` 文件中添加配置：

```
# 设置默认浏览器（单个浏览器）
PLAYWRIGHT_BROWSER=chromium
# 或者设置多个浏览器（逗号分隔）
PLAYWRIGHT_BROWSERS=chromium,firefox
# 启用无头模式
# PLAYWRIGHT_HEADLESS=1
# 慢速执行（毫秒）
# PLAYWRIGHT_SLOWMO=100
```

### 4. 在 conftest.py 中配置

可以通过重写 pytest-playwright 的 fixtures 来自定义配置：

```python
@pytest.fixture(scope="function")
def browser_context_args(request):
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
    }
```

### 3. 命令行参数

```bash
# 指定浏览器
pytest --browser=chromium
pytest --browser=firefox
pytest --browser=webkit

# 指定多个浏览器并行测试
pytest --browser=chromium --browser=firefox

# 无头模式
pytest --headless

# 慢速执行（用于调试）
pytest --slowmo=100
```

## 四、多浏览器并行测试

### 1. 基本用法

```bash
# 运行所有测试在多个浏览器中
pytest --browser=chromium --browser=firefox

# 运行特定测试在多个浏览器中
pytest tests/e2e/test_todomvc.py --browser=chromium --browser=firefox
```

### 2. 并行执行

结合 pytest-xdist 插件可以实现真正的并行测试：

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 并行运行测试
pytest -n auto --browser=chromium --browser=firefox
```

## 五、与 Allure 报告集成

### 1. 安装 Allure 插件

```bash
pip install allure-pytest
```

### 2. 生成 Allure 报告

```bash
# 运行测试并收集 Allure 结果
pytest --alluredir=reports/allure-results

# 生成 Allure 报告
allure generate reports/allure-results -o reports/allure-report --clean

# 打开 Allure 报告
allure open reports/allure-report
```

### 3. 报告中的浏览器信息

pytest-playwright 会自动在 Allure 报告中添加浏览器信息，确保清晰展示各浏览器的测试结果。

## 六、常见问题与解决方案

### 1. 浏览器安装问题

```bash
# 安装特定浏览器
playwright install chromium
playwright install firefox
playwright install webkit

# 检查已安装的浏览器
playwright install --list
```

### 2. 环境变量配置

可以通过环境变量设置默认行为：

- `PLAYWRIGHT_HEADLESS`：设置为 `1` 启用无头模式
- `PLAYWRIGHT_SLOWMO`：设置为毫秒值，启用慢速执行
- `PLAYWRIGHT_BROWSERS_PATH`：设置浏览器安装路径

### 3. 自定义浏览器配置

在 conftest.py 中可以通过重写 fixtures 来自定义浏览器配置：

```python
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized"],
    }
```

## 七、示例项目结构

```
project/
├── tests/
│   ├── e2e/
│   │   ├── test_example.py  # 测试文件
│   ├── api/
│   │   ├── test_api.py  # API 测试文件
│   ├── integration/
│   │   ├── test_integration.py  # 集成测试文件
│   ├── unit/
│   │   ├── test_unit.py  # 单元测试文件
│   ├── conftest.py  # 测试配置
├── core/
│   ├── pages/
│   │   ├── base/
│   │   │   ├── base_page.py  # 基础页面类
│   │   ├── specific/
│   │   │   ├── login_page.py  # 登录页面
│   │   ├── locators.py  # 定位器管理
│   ├── services/
│   │   ├── api/
│   │   │   ├── mock_server.py  # Mock 服务器
│   ├── exceptions/  # 异常管理
│   ├── models/  # 数据模型
├── utils/
│   ├── browser/
│   │   ├── browser_pool.py  # 浏览器池管理
│   │   ├── smart_waiter.py  # 智能等待
│   ├── api/  # API 工具
│   ├── data/  # 数据工具
│   ├── reporting/  # 报告工具
├── config/
│   ├── envs/  # 环境配置文件
│   ├── settings.py  # 配置管理
├── pyproject.toml  # 项目配置
├── requirements.in  # 依赖定义
├── requirements.lock  # 锁定版本依赖
```

## 八、总结

pytest-playwright 是一个强大的插件，它简化了 Playwright 与 pytest 的集成，提供了便捷的 fixtures 和配置选项。通过合理配置，可以轻松实现多浏览器并行测试和生成详细的测试报告。
