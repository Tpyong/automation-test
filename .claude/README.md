# .claude 文档导航

> **用途**：AI 测试开发文档导航  
> **适用对象**：AI 助手、测试工程师  
> **最后更新**：2026-04-08

---

## 🎯 按场景查找

| 场景 | 参考文档 |
|------|---------|
| **AI 开发指南** | [CLAUDE.md](CLAUDE.md) |
| **制定测试计划** | [testing_plan.md](testing_plan.md) |
| **编写用例和代码** | [testing_guidelines.md](testing_guidelines.md) |
| **快速上手** | [quick_start.md](quick_start.md) |
| **功能模块清单模板** | [templates/module_list.md](templates/module_list.md) |
| **问题追踪模板** | [templates/problem_tracking.md](templates/problem_tracking.md) |

---

## 📁 核心文档（AI 必读）⭐

| 文档 | 用途 | 优先级 |
|------|------|--------|
| [CLAUDE.md](CLAUDE.md) | AI 执行指南、项目结构、技术栈 | ⭐⭐⭐ |
| [testing_plan.md](testing_plan.md) | 测试阶段划分、任务流程、检查清单 | ⭐⭐⭐ |
| [testing_guidelines.md](testing_guidelines.md) | 用例编写规范、代码规范、最佳实践 | ⭐⭐⭐ |

---

## 📋 模板文件

| 模板 | 用途 |
|------|------|
| [templates/module_list.md](templates/module_list.md) | 功能模块清单模板（阶段 0 使用） |
| [templates/problem_tracking.md](templates/problem_tracking.md) | 问题追踪模板 |

---

## 📖 项目文档（参考）

| 文档 | 用途 |
|------|------|
| [docs/README.md](../docs/README.md) | 项目文档导航 |
| [docs/getting-started/README.md](../docs/getting-started/README.md) | 快速开始指南 |
| [docs/getting-started/GUIDE.md](../docs/getting-started/GUIDE.md) | 完整使用指南 |
| [docs/architecture/SYSTEM_ARCHITECTURE.md](../docs/architecture/SYSTEM_ARCHITECTURE.md) | 系统架构文档 |
| [docs/development/DEVELOPMENT_GUIDELINES.md](../docs/development/DEVELOPMENT_GUIDELINES.md) | 开发规范 |
| [docs/best-practices/LOCATORS_GUIDE.md](../docs/best-practices/LOCATORS_GUIDE.md) | 定位器使用指南 |
| [docs/best-practices/PLAYWRIGHT_GUIDE.md](../docs/best-practices/PLAYWRIGHT_GUIDE.md) | Playwright 使用指南 |

---

## 🗂️ 目录结构

```
.claude/ (5 个核心文件 + 1 个子目录)
│
├── CLAUDE.md                     # AI 必读：顶层指导 ⭐⭐⭐
├── README.md                     # 文档导航
├── quick_start.md                # 快速上手
├── testing_plan.md               # AI 必读：自动化测试计划 ⭐⭐⭐
├── testing_guidelines.md         # AI 必读：测试用例编写和代码规范指南 ⭐⭐⭐
│
└── templates/ (2 个）
    ├── module_list.md            # 功能模块清单模板
    └── problem_tracking.md       # 问题追踪模板
```

---

## 🚀 快速开始

### 1. 环境准备

**安装依赖**：
```bash
pip install -r requirements.txt
playwright install
```

**配置环境**：
```bash
# 复制基础环境配置文件
cp config/envs/.env.base config/envs/.env

# 编辑环境变量（根据实际情况修改）
# BASE_URL=http://localhost:3000
# TEST_BROWSER=chromium
```

### 2. 执行流程

1. **AI 开始工作**：先阅读 [CLAUDE.md](CLAUDE.md) 了解项目结构和执行流程
2. **制定计划**：参考 [testing_plan.md](testing_plan.md) 制定测试计划
3. **编写用例**：参考 [testing_guidelines.md](testing_guidelines.md) 编写测试用例和代码
4. **执行测试**：运行测试并生成报告
   ```bash
   # 执行测试
   pytest tests/e2e/test_login.py --alluredir=reports/allure-results
   
   # 生成报告
   allure generate reports/allure-results -o reports/login_allure_report --clean
   ```
5. **查看示例**：参考 [quick_start.md](quick_start.md) 了解具体执行步骤

---

## 💡 重要提示

- **基础框架已搭建完成**：项目结构、依赖包、配置文件、测试工具类都已准备就绪
- **当前执行流程**：阶段 0（PRD 分析）→ 阶段 2 起（UI 功能模块循环）
- **核心原则**：质量优先、模块化测试、问题追踪、效率优先
- **技术栈**：pytest 9.0.2 + pytest-playwright 1.49.0+ + Allure 2.15.3
- **代码质量**：集成了 pylint、flake8、black、isort、mypy 等代码质量工具
- **多浏览器支持**：支持 Chromium 和 Firefox 浏览器测试
- **配置管理**：使用 config/settings.py 统一管理配置
- **测试工具类**：tests/utils/ 下提供了 VideoManager、AttachmentManager、ReportManager 等工具类
- **数据管理**：使用 YAML 文件管理测试数据，支持动态数据生成

---

**最后更新**：2026-04-09  
**文档版本**：v1.4
