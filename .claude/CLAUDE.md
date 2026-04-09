# AI 测试开发指南

> **最后更新**：2026-04-09
> **适用对象**：AI 助手
> **目标**：根据 PRD 生成测试用例和自动化代码

## 快速导航

| 场景 | 参考文档 |
|------|---------|
| 测试计划 | [testing_plan.md](testing_plan.md) |
| 测试指南 | [testing_guidelines.md](testing_guidelines.md) |
| 模块模板 | [templates/module_list.md](templates/module_list.md) |
| 问题追踪模板 | [templates/problem_tracking.md](templates/problem_tracking.md) |

## AI 执行流程

1. **读取 PRD 文档**
2. **阶段 0**: 分析功能模块 → 输出 module_list.md
3. **循环每个模块**:
   - 任务 X.1: 页面分析 → 用例设计 → 输出 [模块名]_用例.md
   - 任务 X.2: Page Object 编写 → 输出 [模块名]_page.py
   - 任务 X.3: 测试数据编写 → 输出 [模块名]_data.yaml
   - 任务 X.4: 测试用例编写 → 输出 test_[模块名].py
   - 任务 X.5: 执行验证 → 输出 Allure 报告

## 核心原则

- ✅ 质量优先：需求覆盖率、数据幂等性、定位器稳定性
- ✅ 模块化测试：每个模块独立执行，形成完整闭环
- ✅ 问题追踪：所有问题统一记录到 [模块名]_问题追踪.md
- ✅ 修复上限：同一用例修复 3 次未通过时暂停并上报
- ✅ 效率优先：在保证质量的前提下，最大化执行效率

## 代码编写约束

### 禁止修改的文件

以下文件只能使用，**禁止修改**：
- ❌ `tests/conftest.py` - 测试框架核心配置
- ❌ `config/settings.py` - 配置管理类
- ❌ `tests/utils/` 下的所有工具类
- ❌ `core/pages/base/` 下的基础页面类
- ❌ `utils/` 下的通用工具模块

### 允许创建/修改的文件

以下文件可以**创建或修改**：
- ✅ `tests/e2e/test_*.py` - 测试用例文件
- ✅ `core/pages/specific/*.py` - 特定页面类
- ✅ `resources/data/*.yaml` - 测试数据文件
- ✅ `resources/locators/*.yaml` - 定位器文件
- ✅ `output/testcases_docs/*.md` - 测试文档

### 代码编写原则

1. **只读使用**：使用现有 fixture 和工具类，不修改实现
2. **扩展而非修改**：通过继承或组合扩展现有功能
3. **遵循接口**：使用现有类和方法的公开接口
4. **数据隔离**：测试数据使用 `at_` 前缀，避免污染生产数据
5. **问题上报**：如需修改现有代码，记录到问题追踪文件并上报，不要自行修改

## 技术栈

- **测试框架**：pytest 9.0.2 + pytest-playwright 1.49.0+
- **浏览器**：Playwright 1.49.0+ (Chromium/Firefox)
- **报告**：Allure 2.15.3
- **代码质量**：pylint + flake8 + black + isort + mypy

## 核心配置

### conftest.py 功能

`tests/conftest.py` 是项目 UI 测试的核心，提供：

- **环境配置**：加载环境变量、配置 Allure 报告
- **浏览器管理**：配置浏览器启动参数、上下文、页面
- **测试增强**：自动录制视频、截图、集成 Allure 报告
- **数据管理**：测试数据清理、数据库连接、Mock 服务器
- **工具类集成**：集成 VideoManager、AttachmentManager、ReportManager

### 主要 Fixture

- `settings`：配置管理
- `page`：浏览器页面
- `test_data_cleanup`：测试数据清理
- `setup_teardown`：测试前后置操作
- `db_session`：数据库会话
- `mock_server`：Mock 服务器

## 执行命令

```bash
# 安装依赖
pip install -r requirements.txt
playwright install

# 执行测试
pytest tests/e2e/test_login.py --alluredir=reports/allure-results

# 多浏览器测试
pytest tests/e2e/test_login.py --alluredir=reports/allure-results --browser chromium --browser firefox

# 生成 Allure 报告
allure generate reports/allure-results -o reports/login_allure_report --clean

# 代码质量检查
black core/ tests/
isort core/ tests/
flake8 core/ tests/
pylint core/ tests/
mypy core/
```

## 基础框架状态

**⚠️ 基础框架已搭建完成**：
- ✅ 项目目录结构已创建
- ✅ 依赖包已安装
- ✅ 配置文件已配置
- ✅ 测试工具类已实现
- ✅ 基础功能已验证

## AI 执行提醒

- **灵活决策**：根据实际情况调整执行策略
- **上下文管理**：文件顶部添加简短元信息，避免冗长模板
- **命名规范**：使用小写字母 + 下划线格式
- **多浏览器支持**：考虑 Chromium 和 Firefox 兼容性
- **工具类使用**：充分利用 tests/utils/ 下的工具类
- **代码约束**：严格遵守代码编写约束，禁止修改核心文件

## 参考文件

- **PRD 文档**：`<项目根目录>/PRD/`
- **测试计划**：`<项目根目录>/.claude/testing_plan.md`
- **测试指南**：`<项目根目录>/.claude/testing_guidelines.md`
- **项目架构**：`<项目根目录>/docs/architecture/SYSTEM_ARCHITECTURE.md`
- **开发规范**：`<项目根目录>/docs/development/DEVELOPMENT_GUIDELINES.md`
