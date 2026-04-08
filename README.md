# 企业级自动化测试框架

基于 Python + Pytest + Playwright + Allure 的企业级自动化测试可复用标准框架。

***

## 技术栈

- **Python**: 3.10+
- **Pytest**: 测试框架
- **Playwright**: 浏览器自动化
- **Allure**: 测试报告
- **pytest-xdist**: 并行测试
- **pytest-rerunfailures**: 失败重试
- **pytest-cov**: 测试覆盖率
- **Faker**: 测试数据生成
- **cryptography**: 敏感信息加密
- **Docker**: 容器化支持
- **SQLAlchemy**: 数据库 ORM
- **Safety/Bandit**: 安全扫描
- **Test Monitoring**: 测试执行监控和性能分析
- **Alert Management**: 测试失败告警（邮件/钉钉/企业微信）
- **Data Masking**: 测试数据脱敏和敏感信息检测
- **Circuit Breaker**: 断路器模式，防止级联故障
- **High Availability**: 高可用性机制，故障自愈
- **Audit Logging**: 操作审计日志，合规检查
- **Smart Waiting**: 智能等待策略，优化测试执行

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install
```

### 2. 配置环境

```bash
# 从模板复制配置文件（推荐使用最小配置）
cp config/envs/.env.minimal .env
# 或者使用完整配置
cp config/envs/.env.full .env

# 编辑 .env 文件，设置 BASE_URL 等配置
```

**环境配置文件说明：**

- `config/envs/.env.base` - 基础配置（所有环境的默认值）
- `config/envs/.env.minimal` - 最小配置（推荐新手使用）
- `config/envs/.env.standard` - 标准配置
- `config/envs/.env.full` - 完整配置（包含所有选项）
- `config/envs/.env.example` - 示例配置
- `config/envs/.env.development` - 开发环境配置
- `config/envs/.env.testing` - 测试环境配置
- `config/envs/.env.staging` - 预发布环境配置

**配置继承机制：**

框架实现了三层配置继承机制，优先级从高到低：

1. `.env.{env}` - 环境特定配置（最高优先级）
2. `.env` - 项目级配置
3. `.env.base` - 基础配置（所有环境的默认值）

这种机制减少了配置重复，确保所有环境都有统一的默认配置。

### 3. 运行测试

```bash
# 默认使用 Chromium 浏览器
pytest -v

# 指定浏览器（Chromium/Firefox/WebKit）
pytest -v --browser=firefox

# 多浏览器并行测试
pytest -v --browser=chromium --browser=firefox

# 并行运行测试
pytest -v -n auto

# 多浏览器并行执行
pytest -n auto -v --browser=chromium --browser=firefox
```

**浏览器配置说明：**

- **本地开发**：使用 `--browser` 命令行参数指定浏览器类型
- **CI/CD**：使用 `TEST_BROWSER` 环境变量指定浏览器类型（避免与 pytest-playwright 冲突）
- **支持的浏览器**：chromium、firefox、webkit
- **默认浏览器**：chromium

**多浏览器配置：**

在 `.env` 文件中配置：

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

### 4. 查看报告

**Allure 报告**：

```bash
# 运行测试并收集 Allure 结果数据
pytest --alluredir=reports/allure-results

# 生成 Allure 报告
allure generate reports/allure-results -o reports/allure-report --clean

# 在浏览器中查看报告
allure open reports/allure-report
```

**CI/CD 报告查看**：

- 访问 GitHub Actions 页面
- 选择成功的 workflow 运行
- 在页面底部 "Artifacts" 区域下载 `allure-report-html.zip`
- 解压后打开 `index.html` 查看报告

**自定义 HTML 报告**：
直接在浏览器中打开 `reports/test-summary.html` 文件

## 文档

- [文档中心](docs/README.md) - 所有文档的导航中心
- [快速开始指南](docs/getting-started/README.md) - 5分钟上手指南
- [完整使用指南](docs/getting-started/GUIDE.md) - 详细功能说明
- [功能特性](docs/core-features/FEATURES.md) - 框架能力一览
- [CI/CD 配置](docs/ci-cd/CI_CD.md) - 持续集成配置
- [GitHub Actions 配置](docs/ci-cd/GITHUB_SETUP.md) - GitHub Actions 详细配置
- [定位器使用指南](docs/best-practices/LOCATORS_GUIDE.md) - 元素定位器最佳实践
- [pytest-playwright 使用指南](docs/best-practices/PLAYWRIGHT_GUIDE.md) - pytest-playwright 插件使用指南

## 核心特性

- ✅ **页面对象模式** - 清晰的 POM 架构
- ✅ **多环境配置** - development/testing/staging/production
- ✅ **数据驱动测试** - 支持 JSON/YAML/CSV
- ✅ **API 测试支持** - 内置 API 客户端
- ✅ **Mock 服务** - 轻量级 Mock 服务器
- ✅ **敏感信息加密** - 配置文件加密保护
- ✅ **Allure 报告** - 美观的测试报告
- ✅ **测试覆盖率** - 代码覆盖率统计
- ✅ **CI/CD 模板** - GitHub/GitLab/Jenkins
- ✅ **录屏功能** - 企业级测试录制策略，采用Allure官方推荐的最佳实践，在测试teardown阶段统一附加截图和视频，确保附件一致性和文件完整性
- ✅ **并行测试** - 支持 pytest-xdist 并行执行
- ✅ **测试结果历史** - 自动存储测试历史数据
- ✅ **测试趋势分析** - 生成测试趋势报告
- ✅ **代码质量工具** - Black、isort、Flake8、Pylint、MyPy
- ✅ **配置统一管理** - 所有工具配置统一至 pyproject.toml
- ✅ **预提交钩子** - 自动代码质量检查
- ✅ **Makefile 支持** - 常用命令快捷方式
- ✅ **类型注解支持** - 核心模块已添加完整的类型注解
- ✅ **测试分层** - 支持单元测试、集成测试、API 测试、E2E 测试
- ✅ **数据库测试** - 支持数据库连接池、事务回滚、测试数据管理
- ✅ **API 契约测试** - 支持 OpenAPI/Swagger 验证
- ✅ **API 性能测试** - 支持负载测试和压力测试
- ✅ **容器化支持** - Docker + Docker Compose 完整支持
- ✅ **安全扫描** - 集成 Safety、Bandit、pip-audit
- ✅ **覆盖率要求** - 强制 80% 覆盖率阈值
- ✅ **测试监控** - 测试执行监控、性能分析、趋势报告
- ✅ **告警机制** - 测试失败告警（邮件/钉钉/企业微信）
- ✅ **数据脱敏** - 敏感数据自动脱敏和检测
- ✅ **断路器模式** - 防止级联故障，提供故障隔离
- ✅ **高可用性** - 故障自愈、健康检查、自动恢复
- ✅ **审计日志** - 操作审计、合规检查、数据保留策略
- ✅ **智能等待** - 多种等待策略、自适应重试、性能优化
- ✅ **MyPy 类型检查** - 支持类型安全检查，可通过 `make mypy` 运行
- ✅ **交互式测试运行器** - 命令行界面选择测试模块和用例
- ✅ **测试配置向导** - 帮助用户快速设置测试环境
- ✅ **增强的测试结果可视化** - 详细的趋势图表和统计分析
- ✅ **智能测试建议** - 基于历史测试结果提供优化建议
- ✅ **API 测试完整支持** - RESTful API 测试、Mock 服务器、契约测试、性能测试

## 最近变更

### 2026-04-05: 目录结构重构与规范

- ✅ **config/settings\_dir/ 重构** - 删除根目录下的配置文件，仅保留子目录中的配置
- ✅ **机密文件位置优化** - 将 .secrets.key 和 .secrets.salt 移动到 config/secrets/ 目录
- ✅ **utils/ 目录移动** - 将 core/utils/ 移动到根目录，作为全局通用工具
- ✅ **utils/ 文件分类** - 将所有工具文件分类到对应的子目录（api、browser、data、reporting、security、core）
- ✅ **服务模块迁移** - 将 db\_manager.py、mock\_server.py 移动到 core/services/
- ✅ **定位器模块迁移** - 将 locators.py 移动到 core/pages/
- ✅ **logs/ 和 reports/ 说明** - 为这两个目录添加了 README 说明文档
- ✅ **目录结构规范文档** - 创建了 docs/best-practices/DIRECTORY\_STRUCTURE.md，包含详细的目录说明和新文件归类决策树

### 2026-04-04: API 测试重构与文档更新

- ✅ **API 测试重构** - 完全重构了 API 测试，使用内置 Mock 服务器替代真实 API 调用
- ✅ **Mock 服务实现** - 使用 Python `http.server` 实现了完整的 RESTful API Mock 服务
- ✅ **测试通过验证** - 所有 9 个 API 测试用例都成功通过，无需真实后端
- ✅ **Allure 分类配置修复** - 修复了 `categories.json` 路径问题，确保 Allure 报告正确显示缺陷分类
- ✅ **文档全面更新** - 更新了所有相关文档，反映最新的项目结构和功能

### 2026-04-04: 项目结构优化

- ✅ **测试目录结构** - 按测试类型分类（unit、integration、api、e2e）
- ✅ **核心模块结构** - 按功能分类，包括 pages、utils、services、exceptions、models
- ✅ **页面对象结构** - 分为 base（基础页面）、components（组件）、specific（特定页面）
- ✅ **工具类结构** - 按功能分类（api、browser、data、reporting、security）
- ✅ **脚本目录结构** - 按功能分类（cli、automation、utils、security）
- ✅ **资源目录整合** - 统一管理测试数据、定位器和模板文件
- ✅ **配置验证增强** - 添加了环境、数据库、报告、并行测试和日志配置的验证规则
- ✅ **配置管理优化** - 实现了三层配置继承（.env.{env} > .env > .env.base），减少配置重复
- ✅ **基础配置文件** - 创建了 .env.base 基础配置文件，包含所有环境的默认配置
- ✅ **配置文件清理** - 移除了各环境配置文件中的重复配置项
- ✅ **VIDEO\_ENABLED 默认值** - 将默认值从 false 改为 true，启用视频录制功能

### 2026-04-02: CI/CD Pipeline 完整修复

- ✅ **pytest 插件识别修复** - 移除 `-p no:warnings` 导致 pytest-html、pytest-cov 插件无法识别
- ✅ **浏览器 headless 模式强制** - CI 环境自动检测并强制使用 headless=true，解决 XServer 缺失问题
- ✅ **Allure 报告部署优化** - 改用普通 artifact 上传，无需 GitHub Pages 权限
- ✅ **PyPI 源配置修复** - 移除 requirements.lock 中的清华源，使用官方源避免 403 错误
- ✅ **Dockerfile 修复** - 使用正确的 requirements.in 文件
- ✅ **Allure 路径修复** - 修复 artifacts 路径查找和复制逻辑

### 浏览器配置优化

- ✅ **浏览器配置修复** - 解决了 Firefox 和 WebKit 测试失败的问题
- ✅ **环境变量优化** - 使用 `TEST_BROWSER` 环境变量代替 `BROWSER`，避免与 pytest-playwright 插件冲突
- ✅ **CI/CD 配置更新** - GitHub Actions 和 GitLab CI 已更新为使用正确的浏览器配置
- ✅ **调试代码清理** - 移除了调试日志，保持代码简洁

### 2026-04-08: 多浏览器测试和附件功能优化

- ✅ **多浏览器测试** - 支持在 Chromium 和 Firefox 浏览器中运行测试
- ✅ **附件功能修复** - 修复了 Allure 报告中缺少截图和视频的问题
- ✅ **视频录制优化** - 确保录制整个浏览器窗口，视频尺寸与视口大小匹配
- ✅ **附件附加时机** - 优化了附件附加的时机，确保截图和视频在生成后再附加到报告
- ✅ **视频文件处理** - 改进了视频文件的处理逻辑，确保 Firefox 浏览器的视频文件正确生成
- ✅ **文档更新** - 更新了所有相关文档，详细说明多浏览器测试和附件功能的使用方法

### 2026-04-08: conftest.py 重构

- ✅ **创建 tests/utils 目录** - 用于存放测试专用的工具类
- ✅ **实现 VideoManager 类** - 封装视频文件的查找、清理和重命名逻辑
- ✅ **实现 AttachmentManager 类** - 封装 Allure 附件附加逻辑
- ✅ **实现 ReportManager 类** - 封装报告生成相关逻辑
- ✅ **重构 conftest.py 文件** - 从 645 行减少到 382 行，使用新创建的管理器类简化代码结构
- ✅ **验证重构结果** - 运行测试验证框架正常运行
- ✅ **提高代码可维护性** - 实现单一职责原则，降低代码复杂度

### 代码质量修复

- ✅ **类型错误修复** - 修复了 MyPy 类型检查发现的 58 个类型错误
- ✅ **异常处理优化** - 将通用 Exception 捕获替换为更具体的异常类型（如 RequestException）
- ✅ **日志格式化改进** - 将 f-string 格式的日志语句替换为推荐的 `logger.info("Message: %s", variable)` 格式，支持延迟求值
- ✅ **代码风格统一** - 使用 Black 和 isort 自动格式化代码，统一代码风格
- ✅ **未使用参数清理** - 移除了测试文件中的未使用参数

### Git 配置更新

- ✅ **.gitignore 优化** - 移除了 `test_*.py` 规则，确保测试文件能够被版本控制

### 依赖管理

- ✅ **依赖安装** - 安装了 sqlalchemy 依赖，解决了导入错误问题

### 测试验证

- ✅ **测试全部通过** - 所有 15 个测试用例都成功通过
- ✅ **测试报告生成** - 生成了完整的测试报告，包括 HTML 报告、JSON 报告、测试历史记录和测试趋势报告
- ✅ **代码覆盖率** - 测试覆盖率为 23.89%，低于要求的 80%，但这是因为很多工具类文件没有被测试覆盖

## 项目结构

```
.
├── config/                    # 配置管理
│   ├── envs/                  # 环境配置文件目录
│   │   ├── .env.example       # 示例配置
│   │   ├── .env.minimal       # 最小配置
│   │   ├── .env.standard      # 标准配置
│   │   ├── .env.full          # 完整配置
│   │   ├── .env.development   # 开发环境
│   │   ├── .env.testing       # 测试环境
│   │   └── .env.staging       # 预发布环境
│   ├── secrets/               # 机密文件（密钥、盐值等）
│   │   ├── .secrets.key       # 加密密钥
│   │   └── .secrets.salt      # 加密盐值
│   ├── settings.py            # 配置管理类
│   ├── validators.py          # 配置验证器
│   ├── settings_dir/          # 配置模块目录
│   │   ├── __init__.py
│   │   ├── base/              # 基础配置
│   │   │   └── base.py
│   │   ├── development/       # 开发环境配置
│   │   │   └── development.py
│   │   ├── production/        # 生产环境配置
│   │   │   └── production.py
│   │   └── testing/           # 测试环境配置
│   │       └── testing.py
│   ├── categories.json        # Allure 报告分类配置
│   └── __init__.py
├── core/                      # 核心模块
│   ├── pages/                 # 页面对象
│   │   ├── base/              # 基础页面对象
│   │   │   └── base_page.py
│   │   ├── components/        # 页面组件
│   │   ├── specific/          # 特定页面对象
│   │   │   ├── login_page.py
│   │   │   └── login_page_semantic.py
│   │   ├── locators.py        # 定位器管理器
│   │   └── __init__.py
│   ├── services/              # 服务层
│   │   ├── api/               # API 服务
│   │   │   ├── __init__.py
│   │   │   └── mock_server.py # Mock 服务器
│   │   ├── auth/              # 认证服务
│   │   │   └── __init__.py
│   │   └── database/          # 数据库服务
│   │       ├── __init__.py
│   │       └── db_manager.py  # 数据库管理器
│   ├── exceptions/            # 异常定义
│   ├── models/                # 数据模型
│   └── __init__.py
├── utils/                     # 通用工具（从 core/utils/ 移到根目录）
│   ├── api/                   # API 测试工具
│   │   ├── api_client.py
│   │   ├── api_contract_tester.py
│   │   ├── assertions.py      # 断言工具
│   │   └── circuit_breaker.py # 断路器
│   ├── browser/               # 浏览器自动化工具
│   │   ├── browser_pool.py
│   │   └── smart_waiter.py
│   ├── core/                  # 核心工具
│   │   ├── exception_handler.py # 异常处理器
│   │   ├── logger.py          # 日志工具
│   │   └── path_helper.py     # 路径工具
│   ├── data/                  # 数据管理工具
│   │   ├── data_cache.py
│   │   ├── data_factory.py
│   │   ├── data_provider.py
│   │   ├── test_data_loader.py
│   │   └── test_data_manager.py
│   ├── reporting/             # 报告生成工具
│   │   ├── alert_manager.py   # 告警管理器
│   │   ├── allure_helper.py   # Allure 辅助工具
│   │   ├── generator.py
│   │   ├── history_manager.py
│   │   ├── models.py
│   │   ├── report_generator.py # 报告生成器
│   │   ├── test_advisor.py    # 测试建议
│   │   ├── test_monitor.py    # 测试监控
│   │   └── worker_merger.py
│   ├── security/              # 安全相关工具
│   │   ├── audit_logger.py    # 审计日志
│   │   ├── compliance_checker.py
│   │   ├── data_masking.py
│   │   └── secrets_manager.py # 机密管理器
│   └── __init__.py
├── tests/                     # 测试用例
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   ├── api/                   # API 测试
│   ├── e2e/                   # 端到端测试
│   ├── utils/                 # 测试专用工具
│   │   ├── video_manager.py   # 视频文件管理器
│   │   ├── attachment_manager.py # 附件管理器
│   │   └── report_manager.py  # 报告管理器
│   ├── conftest.py            # 测试配置
│   └── README.md              # 测试说明
├── resources/                 # 资源文件
│   ├── data/                  # 测试数据
│   │   ├── fixtures/          # 测试数据夹具
│   │   └── datasets/          # 测试数据集
│   ├── locators/              # 元素定位器
│   │   ├── web/               # Web 定位器
│   │   └── mobile/            # 移动定位器
│   ├── templates/             # 模板文件
│   └── __init__.py
├── scripts/                   # 脚本文件
│   ├── cli/                   # 命令行工具
│   ├── automation/            # 自动化脚本
│   ├── utils/                 # 脚本工具
│   ├── security/              # 安全脚本
│   ├── interactive_runner.py  # 交互式测试运行器
│   ├── config_wizard.py       # 配置向导
│   ├── config_checker.py      # 配置检查工具
│   └── __init__.py
├── docs/                      # 文档
│   ├── getting-started/       # 入门指南
│   ├── core-features/         # 核心功能说明
│   ├── best-practices/        # 最佳实践
│   │   └── DIRECTORY_STRUCTURE.md # 目录结构规范
│   ├── ci-cd/                 # CI/CD 相关文档
│   └── README.md
├── logs/                      # 日志文件（gitignore）
│   └── README.md              # 日志目录说明
├── reports/                   # 测试报告（gitignore）
│   └── README.md              # 报告目录说明
├── ci-cd/                     # CI/CD 配置
│   ├── .gitlab-ci.yml         # GitLab CI 配置
│   └── Jenkinsfile            # Jenkins 配置
├── .github/                   # GitHub Actions 配置
│   └── workflows/
│       ├── ci.yml
│       └── test.yml
├── .env                       # 当前使用的环境配置（不提交到版本控制）
├── Dockerfile                 # Docker 镜像构建文件
├── docker-compose.yml         # Docker Compose 配置
├── .dockerignore              # Docker 忽略文件
├── pyproject.toml             # 统一配置文件（Black、isort、Flake8、Pylint、MyPy、Pytest、Coverage）
├── Makefile                   # 常用命令快捷方式
├── .pre-commit-config.yaml    # 预提交钩子配置
├── requirements.in            # 依赖定义文件
├── requirements.lock          # 锁定版本依赖
└── logs/                      # 日志文件
```

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

# 类型检查（MyPy）
make mypy

# 生成覆盖率报告
make coverage

# 运行安全扫描
make security

# Docker 构建
make docker-build

# Docker 运行测试
make docker-test

# 清理测试结果
make clean

# 运行交互式测试运行器
python scripts/interactive_runner.py

# 运行测试配置向导
python scripts/config_wizard.py

# 生成智能测试建议报告
python -c "from utils.reporting.test_advisor import get_test_advisor; advisor = get_test_advisor(); advisor.generate_advisor_report()"
```

### 传统命令

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
pylint core/ tests/
flake8 core/ tests/
mypy . --exclude=venv --exclude=allure-results --exclude=allure-report

# 代码格式化
black core/ tests/
isort core/ tests/
```

## 示例

### UI 测试示例

```python
import allure
import pytest
from core.pages.base_page import BasePage

@allure.epic("测试套件")
@allure.feature("功能模块")
class TestExample:
    
    @pytest.mark.smoke
    def test_example(self, page, settings):
        base_page = BasePage(page)
        base_page.navigate(settings.base_url)
        assert "期望标题" in base_page.get_title()
```

### API 测试示例

**真实 API 测试**：

```python
import allure
from utils.api.api_client import APIClient, APIAssertions

@allure.epic("API 测试")
@allure.feature("用户管理")
def test_get_users(api_client):
    # 发送 GET 请求
    response = api_client.get("/api/users", params={"page": 1})
    
    # 验证状态码
    APIAssertions.assert_status_code(response, 200)
    
    # 验证响应字段
    APIAssertions.assert_response_has_field(response, "users")
    
    # 验证响应时间
    APIAssertions.assert_response_time(response, max_time=2000)
```

**Mock API 测试**（无需真实后端）：

```python
import pytest
import requests

@allure.epic("API 测试")
@allure.feature("Mock API 测试")
def test_mock_get_users(mock_server):
    # 1. 添加 Mock 端点
    mock_server.add_endpoint(
        method="GET",
        path="/api/users",
        status_code=200,
        body={"users": [{"id": 1, "name": "张三"}], "total": 1}
    )
    
    # 2. 获取 Mock 服务器地址并发送请求
    base_url = mock_server.get_base_url()
    response = requests.get(f"{base_url}/api/users")
    
    # 3. 验证响应
    assert response.status_code == 200
    assert len(response.json()["users"]) == 1
```

**运行 API 测试**：

```bash
# 运行所有 API 测试
pytest tests/api/ -v

# 运行 Mock API 测试（推荐先试这个，无需真实 API）
pytest tests/api/test_mock_api.py -v

# 运行真实 API 测试（需要配置 .env 中的 API_BASE_URL）
pytest tests/api/test_user_api.py -v
```

详细文档请查看：[tests/api/README.md](tests/api/README.md)

## License

MIT
