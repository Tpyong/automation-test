# 快速开始指南

本文档提供框架的快速入门指南。详细文档请查看其他文件。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [常用命令](#常用命令)
- [新功能](#新功能)
- [下一步](#下一步)

## 安装

### 1. 环境要求

- Python 3.10+
- Allure 命令行工具（可选，用于生成报告）

### 2. 安装依赖

```bash
# 安装运行依赖
pip install -r requirements.lock

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 3. 安装浏览器

```bash
playwright install
```

## 快速开始

### 1. 配置环境

从 `config/envs/` 目录下提供了多个配置模板，选择合适的复制到项目根目录：

```bash
# 推荐：最小配置（适合新手）
cp config/envs/.env.minimal .env

# 或者使用标准配置
cp config/envs/.env.standard .env

# 或者使用完整配置
cp config/envs/.env.full .env
```

**环境配置文件说明：
- `config/envs/.env.minimal` - 最小配置（推荐新手使用）
- `config/envs/.env.standard` - 标准配置
- `config/envs/.env.full` - 完整配置（包含所有选项）
- `config/envs/.env.example` - 示例配置
- `config/envs/.env.development` - 开发环境配置
- `config/envs/.env.testing` - 测试环境配置
- `config/envs/.env.staging` - 预发布环境配置

最小配置示例：

```bash
BASE_URL=https://demo.playwright.dev/todomvc
BROWSER=chromium
HEADLESS=false
```

### 2. 运行第一个测试

```bash
# 运行单元测试示例
pytest tests/unit/test_sample.py -v

# 运行 Mock API 测试（推荐，无需真实 API）
pytest tests/api/test_mock_api.py -v

# 运行 UI 测试示例
pytest tests/e2e/test_todomvc.py -v
```

**测试分层说明：**
- `tests/unit/` - 单元测试（测试独立逻辑）
- `tests/integration/` - 集成测试（测试组件交互）
- `tests/api/` - API 测试（测试 RESTful 接口）
- `tests/e2e/` - E2E 测试（测试完整用户流程）

### 3. 查看报告

**Allure报告**：
```bash
# 运行测试并收集Allure结果数据
pytest --alluredir=reports/allure-results

# 生成Allure报告
allure generate reports/allure-results -o reports/allure-report --clean

# 在浏览器中查看报告
allure open reports/allure-report
```

**自定义HTML报告**：
直接在浏览器中打开 `reports/test-summary.html` 文件

## 常用命令

### 使用 Makefile（推荐）

```bash
# 安装依赖和浏览器
make install

# 运行所有测试
make test

# 代码检查
make lint

# 代码格式化
make format

# 类型检查
make mypy

# 生成覆盖率报告
make coverage

# 清理测试结果
make clean
```

### 传统命令

```bash
# 运行所有测试
pytest

# 运行冒烟测试
pytest -m smoke

# 并行运行（注意：并行测试时报告生成器可能无法正确收集测试结果）
pytest -n auto

# 生成覆盖率报告
pytest --cov=core --cov-report=html:reports/coverage-html

# 代码检查
pylint core/ tests/
flake8 core/ tests/

# 代码格式化
black core/ tests/
isort core/ tests/

# 类型检查（MyPy）
mypy . --exclude=venv --exclude=allure-results --exclude=allure-report
```

### 并行测试说明

默认情况下，测试以串行方式执行，以确保测试报告生成器能够正确收集所有测试结果。

如果需要启用并行测试以提高执行速度，可以使用以下命令：

```bash
# 使用所有可用的CPU核心并行运行
pytest -n auto

# 指定并行worker数量
pytest -n 4

# 按文件分发测试（确保同一文件的测试在同一个worker中执行）
pytest -n auto --dist=loadfile
```

**注意**：启用并行测试后，自定义的HTML/JSON测试报告可能无法正确收集所有测试结果。Allure报告不受影响。

## 新功能

### 1. 测试数据管理

使用 YAML 文件管理测试数据：

```bash
# 查看测试数据文件
data/test_data/login_data.yaml

# 在测试中使用```python
from utils.data.test_data_loader import TestDataLoader

data = TestDataLoader.get_login_data('login_success')
```

### 2. 统一异常处理

使用 ExceptionHandler 处理异常：

```python
from utils.common.exception_handler import ExceptionHandler, retry_on_exception

# 安全执行
result = ExceptionHandler.safe_execute(some_function, arg1, arg2)

# 异常重试
@retry_on_exception(max_retries=3, delay=1)
def flaky_function():
    # 可能失败的操作
    pass
```

### 3. 增强的 Allure 报告

使用 AllureHelper 增强测试报告：

```python
from utils.reporting.allure_helper import AllureHelper

# 添加测试参数
AllureHelper.add_parameters({
    "browser": "chromium",
    "environment": "test"
})

# 添加链接
AllureHelper.add_issue("https://example.com/issue/123", "Bug #123")

# 附加文件
AllureHelper.attach_json({"key": "value"}, "测试数据")
```

### 4. 依赖管理优化

使用锁定版本的依赖：

```bash
# 安装锁定版本依赖
pip install -r requirements.lock

# 更新依赖
pip-compile requirements.in -o requirements.lock

# 安装开发依赖
make install-dev
```

### 5. 代码质量工具

所有代码质量工具配置已统一至 `pyproject.toml`：

- **Black**：代码格式化
- **isort**：导入排序
- **Flake8**：代码风格检查
- **Pylint**：代码质量检查
- **MyPy**：类型检查

### 6. 预提交钩子

配置预提交钩子，自动检查代码质量：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

### 7. 测试结果历史存储

框架会自动存储测试结果到历史记录，方便后续分析：

- 历史记录存储在 `reports/history/` 目录
- 每个测试会话生成一个历史文件
- 支持查看历史测试结果

### 8. 测试趋势分析

框架会自动生成测试趋势报告：

- 趋势报告存储在 `reports/test-trend.html`
- 包含通过率、测试数量、执行时长等趋势图表
- 支持查看最近7天的测试趋势
- 提供统计概览数据

### 9. 类型注解与 MyPy 类型检查

框架核心模块已添加完整的类型注解，提高代码可读性和可维护性：

```bash
# 运行 MyPy 类型检查
make mypy

# 或者使用传统命令
mypy . --exclude=venv --exclude=allure-results --exclude=allure-report
```

**MyPy 配置特点**：
- 灵活配置，允许逐步添加类型注解
- 核心模块已添加完整的类型注解
- 支持类型安全检查，提高代码质量

**已添加类型注解的模块**：
- 基础页面（`core/pages/base/base_page.py`）
- 登录页面（`core/pages/specific/login_page.py`）
- 语义化登录页面（`core/pages/specific/login_page_semantic.py`）
- 定位器管理（`core/pages/locators.py`）
- 浏览器池管理（`utils/browser/browser_pool.py`）
- 智能等待（`utils/browser/smart_waiter.py`）
- API 客户端（`utils/api/api_client.py`）
- 数据缓存（`utils/data/data_cache.py`）
- 数据工厂（`utils/data/data_factory.py`）
- 测试数据加载器（`utils/data/test_data_loader.py`）
- 测试数据管理器（`utils/data/test_data_manager.py`）
- Allure 报告辅助（`utils/reporting/allure_helper.py`）
- 报告生成器（`utils/reporting/report_generator.py`）
- Mock 服务器（`core/services/api/mock_server.py`）
- 配置管理（`config/settings.py`）
- 异常管理（`core/exceptions/__init__.py`）
- 模型管理（`core/models/__init__.py`）
- pytest 配置（`conftest.py`）

## 下一步

- 查看 [完整指南](GUIDE.md) 了解详细用法
- 查看 [功能特性](FEATURES.md) 了解框架能力
- 查看 [CI/CD 配置](CI_CD.md) 了解持续集成
- 查看 [API 文档](API.md) 了解 API 参考

## 项目结构

```
.
├── config/                    # 配置管理
│   ├── envs/                  # 环境配置文件目录
│   │   ├── .env.base          # 基础配置
│   │   ├── .env.example       # 示例配置
│   │   ├── .env.minimal       # 最小配置
│   │   ├── .env.standard      # 标准配置
│   │   ├── .env.full          # 完整配置
│   │   ├── .env.development   # 开发环境
│   │   ├── .env.testing       # 测试环境
│   │   └── .env.staging       # 预发布环境
│   ├── settings_dir/          # 配置设置目录
│   │   ├── base/              # 基础设置
│   │   ├── development/       # 开发环境设置
│   │   ├── production/        # 生产环境设置
│   │   └── testing/           # 测试环境设置
│   ├── settings.py            # 配置管理类
│   ├── validators.py          # 配置验证器
│   └── __init__.py
├── core/                      # 核心模块
│   ├── pages/                 # 页面对象
│   │   ├── base/              # 基础页面类
│   │   ├── components/        # 页面组件
│   │   ├── specific/          # 特定页面
│   │   └── locators.py        # 定位器管理
│   ├── services/              # 服务模块
│   │   ├── api/               # API 服务
│   │   ├── auth/              # 认证服务
│   │   └── database/          # 数据库服务
│   ├── exceptions/            # 异常管理
│   ├── models/                # 数据模型
│   └── __init__.py
├── resources/                 # 资源文件
│   ├── data/                  # 测试数据
│   │   ├── datasets/          # 数据集
│   │   └── fixtures/          # 测试固件
│   ├── locators/              # 定位器文件
│   │   ├── mobile/            # 移动设备定位器
│   │   └── web/               # Web 定位器
│   └── templates/             # 模板文件
├── tests/                     # 测试用例
│   ├── api/                   # API 测试
│   │   ├── contracts/         # 契约测试
│   │   └── endpoints/         # 端点测试
│   ├── e2e/                   # 端到端测试
│   │   ├── flows/             # 测试流程
│   │   └── scenarios/         # 测试场景
│   ├── integration/           # 集成测试
│   │   ├── components/        # 组件测试
│   │   └── services/          # 服务测试
│   ├── unit/                  # 单元测试
│   │   ├── core/              # 核心模块测试
│   │   └── utils/             # 工具模块测试
│   └── conftest.py            # 测试配置
├── utils/                     # 工具模块
│   ├── api/                   # API 工具
│   ├── browser/               # 浏览器工具
│   ├── common/                # 通用工具
│   ├── data/                  # 数据工具
│   ├── reporting/             # 报告工具
│   └── security/              # 安全工具
├── scripts/                   # 脚本文件
│   ├── automation/            # 自动化脚本
│   ├── cli/                   # 命令行工具
│   ├── security/              # 安全脚本
│   └── utils/                 # 脚本工具
├── docs/                      # 文档
├── reports/                   # 测试报告
├── .env                       # 当前使用的环境配置（不提交到版本控制）
├── pyproject.toml             # 统一配置文件（Black、isort、Flake8、Pylint、MyPy、Pytest）
├── Makefile                   # 常用命令快捷方式
├── .pre-commit-config.yaml    # 预提交钩子配置
├── requirements.in            # 依赖定义文件
└── requirements.lock          # 锁定版本依赖
```
