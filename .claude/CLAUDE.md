# AI 测试开发指南

> **最后更新**：2026-04-08
> **适用对象**：AI 助手
> **目标**：根据 PRD 生成测试用例和自动化代码

---

## 快速导航

| 场景 | 参考文档 |
|------|---------|
| 制定测试计划 | [testing_plan.md](testing_plan.md) |
| 编写测试用例和代码 | [testing_guidelines.md](testing_guidelines.md) |
| 功能模块清单模板 | [templates/module_list.md](templates/module_list.md) |
| 问题追踪模板 | [templates/problem_tracking.md](templates/problem_tracking.md) |
| 项目架构和细节 | [docs/architecture/SYSTEM_ARCHITECTURE.md](../docs/architecture/SYSTEM_ARCHITECTURE.md) |
| 开发规范 | [docs/development/DEVELOPMENT_GUIDELINES.md](../docs/development/DEVELOPMENT_GUIDELINES.md) |

---

## AI 执行流程

```
开始
  ↓
读取 PRD 文档
  ↓
阶段 0: 分析功能模块 → 输出 module_list.md
  ↓
循环每个模块：
  ├─ 任务 X.1: 页面分析 → 用例设计 → 输出 [模块名]_用例.md
  ├─ 任务 X.2: Page Object 编写 → 输出 [模块名]_page.py
  ├─ 任务 X.3: 测试数据编写 → 输出 [模块名]_data.yaml
  ├─ 任务 X.4: 测试用例编写 → 输出 test_[模块名].py
  └─ 任务 X.5: 执行验证 → 输出 Allure 报告
  ↓
完成
```

---

## 核心原则

1. **质量优先**：核心关注需求覆盖率、数据幂等性、定位器稳定性
2. **模块化测试**：每个功能模块独立执行，形成完整闭环
3. **问题追踪**：所有问题统一记录到 `[模块名]_问题追踪.md`
4. **修复上限**：同一用例修复 3 次未通过时暂停并上报
5. **效率优先**：在保证质量的前提下，最大化执行效率

---

## 技术栈

- **测试框架**：pytest 9.0.2 + pytest-playwright 1.49.0+
- **浏览器自动化**：Playwright 1.49.0+ (Chromium/Firefox)
- **报告工具**：Allure 2.15.3
- **代码质量**：pylint + flake8 + black + isort + mypy
- **数据格式**：YAML/JSON
- **代码质量工具**：
  - **pylint**：代码质量检查（风格、错误、警告）
  - **flake8**：代码风格检查（PEP8 规范）
  - **black**：代码格式化（自动修复）
  - **isort**：导入排序（自动修复）
  - **mypy**：类型检查

### 依赖版本

```
pytest==9.0.2
pytest-playwright==0.3.3
playwright==1.49.0
allure-pytest==2.13.2
pylint==2.17.7
flake8==6.1.0
black==23.3.0
isort==5.12.0
mypy==1.3.0
pyyaml==6.0
```

---

## 项目结构

```
项目根目录/
├── config/                    # 配置管理
│   ├── envs/                  # 环境配置文件
│   └── settings.py            # 配置管理类
├── core/                      # 核心模块
│   ├── pages/                 # 页面对象
│   │   ├── base/              # 基础页面类
│   │   ├── components/        # 页面组件
│   │   └── specific/          # 特定页面
│   └── services/              # 服务模块
├── tests/                     # 测试用例
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   ├── api/                   # API 测试
│   ├── e2e/                   # 端到端测试
│   └── utils/                 # 测试工具类
├── utils/                     # 工具模块
│   ├── browser/               # 浏览器工具
│   ├── data/                  # 数据工具
│   ├── reporting/             # 报告工具
│   └── api/                   # API 工具
├── data/                      # 测试数据 (YAML)
├── pages/                     # Page Object 页面类
├── components/                # 公共组件
├── reports/                   # 测试报告
├── output/                    # 输出文件
│   ├── testcases_docs/        # 测试文档
│   └── snapshots/             # 页面截图
└── docs/                      # 项目文档
```

---

## 项目配置

### 核心配置文件

**配置管理**：
- `config/settings.py`：配置管理类，处理环境变量和配置项
- `config/envs/.env.base`：基础环境配置
- `config/envs/.env`：本地环境配置（可选，覆盖基础配置）

**测试配置**：
- `tests/conftest.py`：测试框架配置，包含浏览器管理、fixture 定义、测试增强等核心逻辑

**配置示例**：
```python
# config/settings.py
class Settings:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "http://localhost:3000")
        self.browser = os.getenv("TEST_BROWSER", "chromium")
        self.headless = os.getenv("HEADLESS", "true").lower() == "true"
```

### conftest.py 核心功能

`tests/conftest.py` 是项目 UI 测试的核心配置文件，包含以下功能：

1. **环境配置**：
   - 加载环境变量（`.env.base` 和 `.env`）
   - 配置 Allure 报告目录
   - 配置浏览器选项（支持多浏览器）

2. **浏览器管理**：
   - 浏览器启动参数配置（无头模式等）
   - 浏览器上下文配置（视口、时区、语言等）
   - 页面管理（超时设置、截图等）

3. **测试增强**：
   - 视频录制功能（自动录制测试过程）
   - 截图功能（测试结束后自动截图）
   - Allure 报告集成
   - 测试结果记录

4. **数据管理**：
   - 测试数据清理
   - 数据库连接管理
   - Mock 服务器设置

5. **工具类集成**：
   - 集成了 `VideoManager`、`AttachmentManager`、`ReportManager` 等工具类

### 执行命令

**安装依赖**：
```bash
pip install -r requirements.txt
playwright install
```

**执行测试**：
```bash
# 执行单个模块测试
pytest tests/e2e/test_login.py --alluredir=reports/allure-results

# 执行多浏览器测试
pytest tests/e2e/test_login.py --alluredir=reports/allure-results --browser chromium --browser firefox

# 生成 Allure 报告
allure generate reports/allure-results -o reports/login_allure_report --clean
allure serve reports/allure-results
```

**代码质量检查**：
```bash
# 运行所有代码质量检查
pylint core/ tests/
flake8 core/ tests/
mypy core/

# 自动修复代码风格
black core/ tests/
isort core/ tests/
```

---

## 基础框架状态

**⚠️ 基础框架已经搭建完成**：
- ✅ 项目目录结构已创建
- ✅ 依赖包已安装 (pytest-playwright, allure-pytest 等)
- ✅ 配置文件已配置 (config/envs/.env.base)
- ✅ 测试工具类已实现 (tests/utils/)
- ✅ 基础功能已验证

**当前执行流程**：
1. 阶段 0：PRD 分析与模块识别
2. 阶段 2 起：UI 功能模块测试（循环执行）

---

## 文件写入要求

1. **分批写入**：一次写入太多内容可能导致命令被截断，出现错误时必须截断文本后分多次写入
2. **唯一标识**：追加/插入/替换内容时，需要提供至少 5 行内容来唯一标识要替换的位置

---

## AI 执行特别提醒

1. **灵活决策**：testing_plan.md 中的决策规则是指导原则，AI 可根据实际情况灵活调整
2. **上下文管理**：文件顶部添加简短元信息即可，避免冗长模板占用 token
3. **命名规范**：统一使用小写字母 + 下划线格式，便于维护
4. **时间标注**：所有日期统一使用当前实际年份（2026 年）
5. **目录检查**：确保所有必要的目录都已存在（reports/, logs/, output/ 等）
6. **多浏览器支持**：测试框架支持 Chromium 和 Firefox，执行时需考虑兼容性
7. **测试工具类**：充分利用 tests/utils/ 下的工具类来简化测试代码

---

## 参考文件路径

- **PRD 文档**：`<项目根目录>/PRD/`
- **测试计划**：`<项目根目录>/.claude/testing_plan.md`
- **测试指南**：`<项目根目录>/.claude/testing_guidelines.md`
- **模块模板**：`<项目根目录>/.claude/templates/module_list.md`
- **问题追踪模板**：`<项目根目录>/.claude/templates/problem_tracking.md`
- **项目架构**：`<项目根目录>/docs/architecture/SYSTEM_ARCHITECTURE.md`
- **开发规范**：`<项目根目录>/docs/development/DEVELOPMENT_GUIDELINES.md`
- **定位器使用指南**：`<项目根目录>/docs/best-practices/LOCATORS_GUIDE.md`
- **Playwright 使用指南**：`<项目根目录>/docs/best-practices/PLAYWRIGHT_GUIDE.md`
- **目录结构指南**：`<项目根目录>/docs/best-practices/DIRECTORY_STRUCTURE.md`
- **CI/CD 配置**：`<项目根目录>/docs/ci-cd/CI_CD.md`
