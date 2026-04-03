# 功能特性

本文档详细介绍框架的各项功能特性。

## 目录

- [核心功能](#核心功能)
- [测试功能](#测试功能)
- [报告功能](#报告功能)
- [高级功能](#高级功能)
- [新增功能](#新增功能)

## 核心功能

### 1. 页面对象模式 (POM)

- 基础页面对象 `BasePage` 封装常用操作
- 支持所有 Playwright 操作
- 自动记录操作日志和 Allure 步骤

### 2. 多环境配置管理

支持 development、testing、staging、production 多环境：

```bash
TEST_ENV=testing pytest
```

**环境配置文件管理：**
所有环境配置文件统一存放在 `config/envs/` 目录下，保持项目根目录整洁。

**配置文件说明：**
- `config/envs/.env.minimal` - 最小配置（推荐新手使用）
- `config/envs/.env.standard` - 标准配置
- `config/envs/.env.full` - 完整配置（包含所有选项）
- `config/envs/.env.example` - 示例配置
- `config/envs/.env.development` - 开发环境配置
- `config/envs/.env.testing` - 测试环境配置
- `config/envs/.env.staging` - 预发布环境配置

**使用方法：**
```bash
# 从模板复制配置文件到项目根目录
cp config/envs/.env.minimal .env

# 编辑配置文件
# 然后运行测试
pytest
```

配置加载优先级：项目根目录 `.env` > `config/envs/.env.{env}`

### 3. 元素定位器管理

支持 YAML/JSON 格式的定位器文件，完全支持 Playwright 官方推荐的语义化定位方式：

- **role 定位**（最推荐）
- **label 定位**
- **placeholder 定位**
- **text 定位**
- **title 定位**
- **alt 定位**
- **test_id 定位**（最稳定）

## 测试功能

### 4. 数据驱动测试

支持 JSON、YAML、CSV 格式的测试数据。

### 5. API 测试支持

内置 API 测试客户端 `APIClient` 和断言工具 `APIAssertions`。

**RESTful API 测试**：
- 支持 GET/POST/PUT/DELETE 等 HTTP 方法
- 自动处理请求头、认证、重试逻辑
- 内置断言工具（状态码、响应字段、响应时间）
- Allure 报告集成

**Mock 服务器**：
- 轻量级 Mock 服务器，无需真实后端
- 自定义端点、响应状态码、响应体、响应头
- 模拟延迟响应、错误场景
- 调用次数统计

**API 契约测试**（`core/utils/api_contract_tester.py`）：
- 支持从 OpenAPI/Swagger 规范加载 API 契约
- 自动验证 API 响应是否符合契约定义
- 支持状态码、响应结构、必填字段验证
- 批量运行所有契约测试

**API 性能测试**：
- **负载测试**：模拟多并发用户，测试系统吞吐量
- **压力测试**：持续高负载测试，验证系统稳定性
- **性能指标**：响应时间（P50/P95/P99）、成功率、RPS 等

**使用示例：**
```python
# RESTful API 测试
from core.utils.api_client import APIClient, APIAssertions

@allure.epic("API 测试")
@allure.feature("用户管理")
def test_get_users(api_client):
    response = api_client.get("/api/users", params={"page": 1})
    APIAssertions.assert_status_code(response, 200)
    APIAssertions.assert_response_has_field(response, "users")
    APIAssertions.assert_response_time(response, max_time=2000)

# Mock API 测试（无需真实后端）
def test_mock_api(mock_server):
    mock_server.add_endpoint(
        method="GET",
        path="/api/users",
        status_code=200,
        body={"users": [{"id": 1, "name": "张三"}]}
    )
    base_url = mock_server.get_base_url()
    response = requests.get(f"{base_url}/api/users")
    assert response.status_code == 200

# API 契约测试
from core.utils.api_contract_tester import APIContractTester

def test_api_contract():
    tester = APIContractTester("https://api.example.com")
    tester.load_openapi_spec("api/openapi.json")
    results = tester.run_all_contract_tests()
    assert len(results['failed']) == 0

# API 性能测试 - 负载测试
from core.utils.api_contract_tester import APIPerformanceTester

def test_api_performance():
    tester = APIPerformanceTester("https://api.example.com")
    results = tester.load_test(
        path="/api/users",
        method="GET",
        iterations=100,
        concurrency=10
    )
    assert results['avg_response_time'] < 1.0  # 平均响应时间 < 1 秒
```

def test_api_performance():
    tester = APIPerformanceTester("https://api.example.com")
    # 负载测试：100 次请求，10 并发
    results = tester.load_test(
        path="/api/users",
        method="GET",
        iterations=100,
        concurrency=10
    )
    assert results['avg_response_time'] < 1.0  # 平均响应时间小于 1 秒
    assert results['error_rate'] < 1.0  # 错误率小于 1%

# API 性能测试 - 压力测试
def test_api_stress():
    tester = APIPerformanceTester("https://api.example.com")
    # 压力测试：持续 60 秒，目标 100 RPS
    results = tester.stress_test(
        path="/api/users",
        method="GET",
        duration=60,
        target_rps=100
    )
    assert results['success_rate'] > 99.0  # 成功率大于 99%
```

### 6. 测试数据清理

支持测试前后的数据清理，提供 `test_data_cleanup` 和 `setup_teardown` fixtures。

### 7. 测试数据工厂

使用 Faker 生成真实的测试数据：

- 用户数据
- 商品数据
- 订单数据
- 支付数据
- 地址数据

### 8. 测试分层架构

支持企业级测试分层，按测试类型组织测试用例：

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── api/            # API 测试
└── e2e/            # 端到端测试
```

**测试分层说明：**
- **单元测试**：测试单个函数/方法，不依赖外部服务
- **集成测试**：测试多个模块协作，包括数据库、缓存等
- **API 测试**：测试 RESTful API 接口
- **E2E 测试**：测试完整业务流程

**运行指定层级的测试：**
```bash
# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行 API 测试
pytest tests/api/

# 运行 E2E 测试
pytest tests/e2e/
```

### 9. 自定义 pytest markers

预定义 15 个 markers：

- 基础：smoke、regression、ui、api、slow
- 业务：login、logout、payment、checkout、search、admin
- 类型：critical、positive、negative

## 报告功能

### 9. Allure 报告

- 自动记录测试步骤
- 所有测试自动截图（无论成功还是失败），截图文件格式：`{测试名称}_{时间}.png`
- 截图文件保存在 `reports/screenshots/YYYYMMDD/` 目录（按日期分类）
- 测试过程自动录屏，视频文件格式：`{测试名称}_{时间戳}.webm`
- 视频文件保存在 `reports/videos/YYYYMMDD/` 目录（按日期分类）
- **企业级附件管理**：采用Allure官方推荐的最佳实践，在测试teardown阶段统一附加截图和视频
- **时序优化**：在浏览器上下文关闭后附加视频，确保视频文件完全生成
- **智能录屏控制**：仅为使用浏览器 fixture 的测试启用录屏
- **附件一致性**：所有附件（截图和视频）都在同一阶段附加，确保在报告中位置一致
- 丰富的报告展示

### 10. 测试覆盖率报告

集成 pytest-cov，支持：

- 终端覆盖率报告
- HTML 覆盖率报告
- XML 覆盖率报告（用于 CI/CD）

### 11. 测试结果汇总

自动生成 HTML 和 JSON 格式的测试汇总报告，包含：

- 统计卡片（总计/通过/失败/跳过）
- 通过率
- 按模块统计
- 失败用例列表

### 12. 报告生成器重构

对报告生成器进行了全面重构，提升了可维护性和功能：

- **模块化设计**：将报告生成逻辑拆分为多个模块（models、history_manager、worker_merger、generator）
- **模板引擎**：使用 Jinja2 模板引擎，分离 HTML 结构和数据
- **静态资源分离**：将 CSS 和 JavaScript 分离到单独文件
- **响应式设计**：优化报告在不同设备上的显示效果
- **图表可视化**：集成 Chart.js，提供丰富的测试趋势图表
- **并行测试支持**：优化多 worker 环境下的结果合并
- **统一报告目录**：所有报告统一存放在 `reports` 目录

**报告文件说明**：
- `reports/test-summary.html` - 测试汇总报告
- `reports/test-summary.json` - 测试汇总数据（JSON格式）
- `reports/test-trend.html` - 测试趋势报告（包含图表）
- `reports/history/` - 测试历史数据目录

### 13. 日志系统

- 控制台和文件双输出
- 日志文件自动轮转
- 统一的日志格式

## 高级功能

### 14. 数据库测试支持

企业级数据库测试解决方案：

**数据库连接管理**（`core/utils/db_manager.py`）：
- 数据库连接池管理（基于 SQLAlchemy）
- 支持 MySQL、PostgreSQL 等主流数据库
- 连接池配置：大小、超时、回收等
- 自动连接管理和资源释放

**测试数据管理**（`core/utils/test_data_manager.py`）：
- 测试数据初始化和清理
- 数据快照和恢复功能
- 测试数据构建器（链式 API）
- 自动跟踪和清理测试数据

**事务回滚支持**：
- 测试级事务隔离
- 自动回滚保证测试独立性
- 支持嵌套事务

**使用示例：**
```python
# 使用数据库会话（自动事务回滚）
def test_with_db(db_session):
    # 插入数据
    db_session.execute("INSERT INTO users (name) VALUES (:name)", {"name": "test"})
    # 查询数据
    result = db_session.execute("SELECT * FROM users WHERE name = :name", {"name": "test"})
    # 测试结束后自动回滚

# 使用测试数据管理器
def test_with_data(test_data_manager):
    # 创建测试数据
    user_id = (test_data_manager.get_builder()
               .with_defaults("users")
               .with_field("email", "test@example.com")
               .insert("users"))
    
    # 跟踪记录用于清理
    test_data_manager.track_record("users", user_id)
    # 测试代码...
    # 测试结束后自动清理
```

### 15. Mock 服务支持

内置轻量级 Mock 服务器：

- 支持所有 HTTP 方法
- 可自定义状态码、响应体、响应头
- 支持响应延迟模拟
- 自动记录请求详情
- 调用计数追踪

### 16. 敏感信息加密

- 使用 Fernet 对称加密（AES-128）
- 自动识别敏感字段
- 配置加载时自动解密
- CLI 工具支持

### 17. CI/CD 配置模板

提供主流 CI/CD 平台的配置模板：

- **GitHub Actions**：矩阵测试、定时任务、自动部署
- **GitLab CI**：三阶段流水线、Pages 部署
- **Jenkins**：参数化构建、邮件通知

### 18. 浏览器视口配置

- 可自定义浏览器视口大小（默认 1920x1080）
- 通过环境变量配置

### 19. 录屏功能

- 支持测试过程自动录屏
- 为每个测试用例生成唯一的视频目录，避免并发时的视频文件冲突
- 视频文件自动重命名为友好格式：`{测试名称}_{时间戳}.webm`
- 视频文件保存在 `reports/videos/YYYYMMDD/` 目录（按日期分类）
- 自动附加到 Allure 报告
- 智能录屏控制：仅为使用浏览器 fixture 的测试启用录屏
- 空视频文件过滤：自动检测并删除 0B 的视频文件
- 视频文件与测试用例关联：确保视频正确附加到对应的测试用例
- 集成测试优化：使用 mock_server 的集成测试不会生成视频文件
- 并发测试支持：通过独立目录隔离，支持大量用例并发执行时的录屏匹配
- 时序优化：在浏览器上下文关闭后附加视频，确保视频文件完全生成

### 20. 测试重试

支持失败自动重试，可配置重试次数和间隔。

### 21. 并行测试

支持 pytest-xdist 并行测试。

### 22. 断言工具

封装常用断言方法，自动记录 Allure 步骤。

## 新增功能

### 23. 测试数据管理

- 使用 YAML 文件管理测试数据
- 支持结构化和分层的数据组织
- 提供 `TestDataLoader` 工具类，方便在测试中加载数据
- 支持数据驱动测试，减少测试代码重复

### 24. 统一异常处理

- 提供 `ExceptionHandler` 类和相关异常类
- 支持异常处理、安全执行和异常重试等功能
- 增强错误日志和定位能力，方便问题排查
- 异常信息自动附加到 Allure 报告

### 25. 增强的 Allure 报告

- 增强了 `AllureHelper` 类，添加了更多实用方法
- 支持添加测试参数、链接、问题和测试用例信息
- 提供更丰富的报告附件类型和格式
- 支持 HTML 格式的测试描述

### 26. 依赖管理优化

- 使用 `pip-tools` 管理依赖版本
- 生成锁定版本的 `requirements.lock` 文件，确保依赖版本的稳定性
- 分离运行依赖和开发依赖，提高环境管理的灵活性
- **Makefile 集成**：提供 `make install`、`make update-deps` 等快捷命令
- 方便依赖的更新和维护

### 27. 代码质量工具集成

- 集成了 `pylint`、`flake8`、`black`、`isort`、`mypy` 等代码检查工具
- **配置统一**：所有工具配置已迁移至 `pyproject.toml`，便于集中管理
- **预提交钩子**：配置 `.pre-commit-config.yaml`，自动检查代码质量
- **Makefile 支持**：提供常用命令快捷方式，简化开发流程
- 配置了代码检查规则，确保代码风格一致性
- 提供了代码格式化和导入排序工具，提升代码可读性
- 支持代码质量的持续监控

### 28. 类型注解与 MyPy 类型检查

- **完整类型注解**：核心模块已添加完整的类型注解，提高代码可读性和可维护性
- **MyPy 集成**：集成 MyPy 类型检查工具，可通过 `make mypy` 或 `mypy .` 运行
- **灵活配置**：MyPy 配置已调整为平衡模式，既保证类型安全，又允许逐步添加类型注解
- **核心模块支持**：以下模块已添加完整的类型注解：
  - `core/utils/locators.py` - 定位器管理
  - `core/utils/browser_pool.py` - 浏览器池管理
  - `core/pages/login_page.py` - 登录页面
  - `core/pages/login_page_semantic.py` - 语义化定位登录页面
  - `core/utils/secrets_manager.py` - 敏感信息管理
  - `core/utils/api_client.py` - API 客户端
  - `core/utils/data_cache.py` - 数据缓存
  - `core/utils/data_factory.py` - 数据工厂
  - `core/utils/allure_helper.py` - Allure 报告辅助
  - `core/utils/report_generator.py` - 报告生成器
  - `core/utils/mock_server.py` - Mock 服务器
  - `config/settings.py` - 配置管理
  - `conftest.py` - pytest 配置
  - `scripts/secrets_tool.py` - 敏感信息管理工具

### 29. 交互式测试运行器

- **命令行交互**：提供友好的命令行界面，支持选择测试类别、模块和用例
- **菜单导航**：通过数字选择进行菜单导航，操作简单直观
- **用例选择**：支持运行所有用例或选择特定用例
- **实时反馈**：显示当前运行的测试信息和结果

**使用方法：**
```bash
python scripts/interactive_runner.py
```

### 30. 测试配置向导

- **交互式配置**：通过问答式界面引导用户配置测试环境
- **智能默认值**：基于示例配置提供合理的默认值
- **配置验证**：自动验证用户输入的有效性
- **配置保存**：自动生成配置文件并保存到正确位置

**使用方法：**
```bash
python scripts/config_wizard.py
```

### 31. 增强的测试结果可视化

- **丰富的图表**：添加了通过率趋势、测试数量趋势、执行时长趋势、测试状态分布等图表
- **模块级分析**：支持按模块查看测试性能和趋势
- **交互式标签**：通过标签切换查看不同模块的分析数据
- **响应式设计**：适配不同屏幕尺寸

**查看报告：**
运行测试后，在 `reports/test-trend.html` 文件中查看详细的趋势分析。

### 32. 智能测试建议

- **性能分析**：基于历史测试结果分析测试性能
- **智能建议**：提供针对性的优化建议，包括：
  - 识别执行时间较长的测试
  - 识别频繁失败的测试
  - 识别表现不佳的模块
  - 分析测试执行趋势
  - 测试覆盖建议
  - 并行执行建议
- **详细报告**：生成HTML格式的建议报告，包含优先级和具体操作建议

**使用方法：**
```bash
python -c "from core.utils.test_advisor import get_test_advisor; advisor = get_test_advisor(); advisor.generate_advisor_report()"
```

## 功能对比

| 功能 | 基础版 | 标准版 | 企业版 |
|------|--------|--------|--------|
| POM | ✅ | ✅ | ✅ |
| 多环境配置 | ✅ | ✅ | ✅ |
| 数据驱动 | ✅ | ✅ | ✅ |
| API 测试 | ✅ | ✅ | ✅ |
| Allure 报告 | ✅ | ✅ | ✅ |
| 覆盖率 | ❌ | ✅ | ✅ |
| Mock 服务 | ❌ | ✅ | ✅ |
| 加密功能 | ❌ | ❌ | ✅ |
| CI/CD 模板 | ❌ | ✅ | ✅ |
| 测试数据管理 | ❌ | ✅ | ✅ |
| 统一异常处理 | ❌ | ✅ | ✅ |
| 代码质量工具 | ❌ | ✅ | ✅ |
| 配置统一管理 | ❌ | ✅ | ✅ |
| 预提交钩子 | ❌ | ✅ | ✅ |
| Makefile 支持 | ❌ | ✅ | ✅ |
| 类型注解 | ❌ | ❌ | ✅ |
| MyPy 类型检查 | ❌ | ❌ | ✅ |
| 测试分层 | ❌ | ❌ | ✅ |
| 数据库测试 | ❌ | ❌ | ✅ |
| API 契约测试 | ❌ | ❌ | ✅ |
| API 性能测试 | ❌ | ❌ | ✅ |
| 交互式测试运行器 | ❌ | ❌ | ✅ |
| 测试配置向导 | ❌ | ❌ | ✅ |
| 增强的测试结果可视化 | ❌ | ❌ | ✅ |
| 智能测试建议 | ❌ | ❌ | ✅ |

> 注：本框架提供所有功能，用户可按需使用。
