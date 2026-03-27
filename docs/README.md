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

复制示例配置文件：

```bash
cp .env.minimal .env
```

最小配置示例：

```bash
BASE_URL=https://demo.playwright.dev/todomvc
BROWSER=chromium
HEADLESS=false
```

### 2. 运行第一个测试

```bash
pytest tests/sample_tests/test_sample.py -v
```

### 3. 查看报告

**Allure报告**：
```bash
# 运行测试并收集Allure结果数据
pytest --alluredir=allure-results

# 生成Allure报告
allure generate allure-results -o allure-report

# 在浏览器中查看报告
allure serve allure-report
```

**自定义HTML报告**：
直接在浏览器中打开 `reports/test-summary.html` 文件

## 常用命令

```bash
# 运行所有测试
pytest

# 运行冒烟测试
pytest -m smoke

# 并行运行
pytest -n auto

# 生成覆盖率报告
pytest --cov=core --cov-report=html:reports/coverage-html

# 代码检查
pylint core/
flake8 core/

# 代码格式化
black core/
tests/
isort core/
tests/
```

## 新功能

### 1. 测试数据管理

使用 YAML 文件管理测试数据：

```bash
# 查看测试数据文件
data/test_data/login_data.yaml

# 在测试中使用
from core.utils.test_data_loader import TestDataLoader

data = TestDataLoader.get_login_data('login_success')
```

### 2. 统一异常处理

使用 ExceptionHandler 处理异常：

```python
from core.utils.exception_handler import ExceptionHandler, retry_on_exception

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
from core.utils.allure_helper import AllureHelper

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
```

## 下一步

- 查看 [完整指南](GUIDE.md) 了解详细用法
- 查看 [功能特性](FEATURES.md) 了解框架能力
- 查看 [CI/CD 配置](CI_CD.md) 了解持续集成
- 查看 [API 文档](API.md) 了解 API 参考

## 项目结构

```
.
├── config/          # 配置管理
├── core/            # 核心模块
│   ├── pages/       # 页面对象
│   └── utils/       # 工具类
├── data/            # 测试数据
│   └── test_data/   # 测试数据文件
├── tests/           # 测试用例
├── docs/            # 文档
└── reports/         # 测试报告
```
