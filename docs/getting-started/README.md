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
# 以开发模式安装依赖
pip install -e .

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 3. 安装浏览器

```bash
playwright install
```

## 快速开始

### 1. 配置环境

框架会自动加载 `config/envs/.env.base` 作为基础配置，然后根据当前环境加载对应的配置文件。

\*\*环境配置文件说明：

- `config/envs/.env.base` - 基础配置（所有环境的默认值）
- `config/envs/.env.development` - 开发环境配置
- `config/envs/.env.testing` - 测试环境配置
- `config/envs/.env.production` - 生产环境配置

**配置模式：**

- `strict` - 严格模式，配置错误会导致测试失败
- `relaxed` - 宽松模式，配置错误会产生警告但不影响测试执行

**配置优先级：**

1. 环境变量
2. 特定环境配置文件（如 `.env.development`）
3. 项目根目录的 `.env` 文件
4. 基础配置文件（`.env.base`）
5. 默认值

### 2. 运行第一个测试

```bash
# 运行 E2E 测试示例（推荐）
pytest tests/e2e/test_todomvc_example.py -v

# 运行 API 测试示例
pytest tests/api/test_mock_api_example.py -v

# 运行集成测试示例
pytest tests/integration/test_mock_server_example.py -v

# 运行单元测试示例
pytest tests/unit/test_sample_example.py -v
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

# 在浏览器中查看报告
allure serve reports/allure-results
```

**自定义HTML报告**：
直接在浏览器中打开 `reports/test-summary.html` 文件

## 常用命令

### 代码质量检查

```bash
# 代码检查
pylint core/ utils/ config/ scripts/ tests/
flake8 core/ utils/ config/ scripts/ tests/

# 代码格式化
black core/ utils/ config/ scripts/ tests/
isort core/ utils/ config/ scripts/ tests/

# 类型检查（MyPy）
mypy core/ utils/ config/ scripts/
```

### 测试执行

```bash
# 运行所有测试
pytest

# 运行冒烟测试
pytest -m smoke

# 并行运行
pytest -n auto

# 生成覆盖率报告
pytest --cov=core --cov-report=html:reports/coverage

# 只运行特定浏览器的测试
pytest --browser chromium tests/e2e/

# 运行多个浏览器的测试
pytest --browser chromium --browser firefox tests/e2e/
```

### 配置管理

```bash
# 运行配置检查
python scripts/utils/config_checker.py

# 运行配置向导
python scripts/cli/config_wizard.py

# 运行交互式测试运行器
python scripts/cli/interactive_runner.py
```

## 新功能

### 1. pytest-playwright 集成

框架已完全集成 pytest-playwright 插件，提供更强大的浏览器自动化能力：

```python
# 在测试中使用 page fixture
def test_example(page):
    page.goto("https://example.com")
    page.fill("#username", "test")
    page.fill("#password", "password")
    page.click("#login")
```

### 2. 配置管理增强

- **配置模式**：支持 strict/relaxed 两种配置模式
- **配置验证**：自动验证配置的有效性
- **配置变更日志**：记录配置变更历史
- **环境变量管理**：优化环境变量加载和处理

### 3. 智能定位器

支持多种定位策略，提高测试稳定性：

- **CSS 选择器**：传统的 CSS 定位
- **XPath**：强大的 XPath 定位
- **语义化定位**：基于角色和文本的定位
- **数据属性定位**：基于自定义数据属性的定位

### 4. 浏览器池与智能等待

- **浏览器池**：优化浏览器启动和管理
- **智能等待**：自动等待元素可见和可交互
- **显式等待**：提供灵活的等待方法
- **超时管理**：统一的超时配置

### 5. Mock 服务

内置 Mock 服务，支持 API 测试：

- **模拟 API 响应**：返回自定义响应数据
- **请求验证**：验证请求参数和 headers
- **延迟响应**：模拟网络延迟
- **错误响应**：模拟各种错误状态码

### 6. 测试数据管理

- **数据驱动测试**：支持 YAML/JSON/Excel 格式的测试数据
- **测试数据工厂**：动态生成测试数据
- **测试数据清理**：自动清理测试数据
- **测试数据隔离**：确保测试之间数据隔离

### 7. 增强的报告系统

- **Allure 报告**：详细的测试报告和趋势分析
- **自定义报告**：HTML 和 JSON 格式的测试摘要
- **测试趋势**：历史测试结果分析
- **智能测试建议**：基于历史数据的测试优化建议

### 8. 安全管理

- **敏感信息加密**：加密环境变量中的敏感信息
- **审计日志**：记录敏感操作
- **数据掩码**：在报告中掩码敏感数据
- **合规检查**：检查代码中的安全问题

### 9. 类型注解与 MyPy 类型检查

框架核心模块已添加完整的类型注解，提高代码可读性和可维护性：

**已添加类型注解的模块**：

- 基础页面（`core/pages/base/base_page.py`）
- 登录页面（`core/pages/specific/login_page_example.py`）
- 语义化登录页面（`core/pages/specific/login_page_semantic_example.py`）
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
- 查看 [系统架构文档](../architecture/SYSTEM_ARCHITECTURE.md) 了解系统架构
- 查看 [API 接口文档](../api/API_DOCUMENTATION.md) 了解 API 参考
- 查看 [部署与运维文档](../deployment/DEPLOYMENT_AND_OPERATION.md) 了解部署和运维
- 查看 [开发规范与代码审查指南](../development/DEVELOPMENT_GUIDELINES.md) 了解开发规范
- 查看 [故障排查手册](../troubleshooting/TROUBLESHOOTING.md) 了解常见问题和解决方案

## 项目结构

```
.
├── config/                    # 配置管理
│   ├── envs/                  # 环境配置文件目录
│   │   ├── .env.base          # 基础配置
│   │   ├── .env.development   # 开发环境配置
│   │   ├── .env.testing       # 测试环境配置
│   │   └── .env.production    # 生产环境配置
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
│   ├── locators/              # 定位器文件
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
├── pyproject.toml             # 统一配置文件
├── requirements.in            # 依赖定义文件
└── requirements.lock          # 锁定版本依赖
```

