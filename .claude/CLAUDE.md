# AI 测试开发指南

> **最后更新**：2026-04-09
> **适用对象**：AI 助手
> **目标**：根据 PRD 生成测试用例和自动化代码

## 快速导航

| 场景     | 参考文档                                                            |
| ------ | --------------------------------------------------------------- |
| 测试流程   | [testing\_flow.md](testing_flow.md)                             |
| 测试指南   | [testing\_guidelines.md](testing_guidelines.md)                 |
| 模块模板   | [templates/module\_list.md](templates/module_list.md)           |
| 问题追踪模板 | [templates/problem\_tracking.md](templates/problem_tracking.md) |

## AI 执行流程

**详细流程请参考**：[testing\_flow.md](testing_flow.md)

**简要流程**：

1. **读取 PRD 文档**
2. **阶段 1**: 分析功能模块 → 输出 module\_list.md
3. **循环每个模块**:
   - 任务 X.1: 页面分析 → 用例设计 → 输出 \[模块名]\_用例.md
   - 任务 X.2: Page Object 编写 → 输出 \[模块名]\_page.py
   - 任务 X.3: 测试数据编写 → 输出 \[模块名]\_data.yaml
   - 任务 X.4: 测试用例编写 → 输出 test\_\[模块名].py
   - 任务 X.5: 执行验证 → 输出 Allure 报告

## 核心原则

- ✅ 质量优先：需求覆盖率、数据幂等性、定位器稳定性
- ✅ 模块化测试：每个模块独立执行，形成完整闭环
- ✅ 问题追踪：所有问题统一记录到 \[模块名]\_问题追踪.md
- ✅ 修复上限：同一用例修复 3 次未通过时暂停并上报
- ✅ 效率优先：在保证质量的前提下，最大化执行效率

## 代码编写约束

**详细约束请参考**：`.trae/rules/project-rule.md`

**核心约束**：

- ✅ 只创建新的测试文件，不修改现有项目代码
- ✅ 建议使用 `tests/conftest.py` 提供的 fixture
- ✅ 建议使用 `tests/utils/` 下的工具类
- ✅ 禁止修改 `config/settings.py` 和 `tests/conftest.py`
- ✅ 禁止修改 `tests/utils/` 下的任何文件
- ✅ 测试数据必须使用 `at_` 前缀，确保数据隔离

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

**详细命令请参考**：[testing\_flow.md](testing_flow.md)

**常用命令**：

```bash
# 执行测试
pytest tests/e2e/test_login.py --alluredir=reports/allure-results

# 生成 Allure 报告
allure generate reports/allure-results -o reports/login_allure_report --clean
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
- **工具类使用**：充分利用 tests/utils/ 下的工具类
- **代码约束**：严格遵守代码编写约束，禁止修改核心文件

## /plan 命令使用说明

**功能**：生成测试执行计划，为后续测试任务提供清晰的执行路线图

**使用方法**：
```
/plan
```

**计划生成逻辑**：
1. **PRD 分析**：自动分析 `/PRD` 目录下的所有需求文档
2. **模块识别**：识别功能模块，评估优先级和复杂度
3. **任务分解**：为每个模块分解测试任务
4. **执行顺序**：根据依赖关系和优先级确定执行顺序
5. **质量目标**：设置明确的质量目标和检查点

**计划内容**：
1. **项目信息**：项目名称、PRD 文档路径、生成时间
2. **执行计划**：
   - 阶段 1：PRD 分析与模块识别
   - 阶段 2+：每个模块的测试任务（页面分析、Page Object 编写、测试数据编写、测试用例编写、执行验证）
3. **执行顺序**：按依赖关系和优先级排序
4. **质量目标**：需求覆盖率、自动化率、通过率等
5. **风险评估**：可能的风险和应对措施

**计划模板**：请参考 [templates/testing\_plan\_template.md](templates/testing_plan_template.md)

**计划执行指导**：
1. **阶段 1 执行**：
   - 读取 PRD 文档
   - 生成 `output/testcases_docs/module_list.md`
   - 确认模块清单和优先级

2. **阶段 2+ 执行**：
   - 按照计划顺序执行每个模块的测试任务
   - 完成一个模块后，更新问题追踪文件
   - 生成 Allure 报告并分析结果

3. **质量控制**：
   - 每个任务完成后进行质量检查
   - 确保需求覆盖率达到 100%
   - 确保测试数据隔离和幂等性

**计划示例**：
```markdown
# 测试执行计划

## 项目信息
- **项目名称**：[项目名称]
- **PRD 文档**：[PRD 路径]
- **生成时间**：[当前时间]

## 执行计划

### 阶段 1：PRD 分析与模块识别
- **任务**：分析 PRD 文档，识别功能模块
- **输出**：`output/testcases_docs/module_list.md`
- **预期结果**：完整的模块清单，包含优先级和复杂度评估
- **质量检查点**：模块识别完整性、优先级合理性

### 阶段 2：[模块名] 测试
- **任务 2.1**：页面分析 → 用例设计
  - **输出**：`output/testcases_docs/[模块名]_用例.md`、`output/testcases_docs/[模块名]_问题追踪.md`
  - **质量检查点**：需求覆盖率、场景完整性

- **任务 2.2**：Page Object 编写
  - **输出**：`core/pages/specific/[模块名]_page.py`、`resources/locators/[模块名]_page.yaml`
  - **质量检查点**：代码质量、定位器稳定性

- **任务 2.3**：测试数据编写
  - **输出**：`resources/data/[模块名]_data.yaml`
  - **质量检查点**：数据隔离、数据完整性

- **任务 2.4**：测试用例编写
  - **输出**：`tests/e2e/test_[模块名].py`
  - **质量检查点**：代码质量、测试逻辑合理性

- **任务 2.5**：执行验证 → 输出 Allure 报告
  - **输出**：`reports/[模块名]_allure_report/`、`output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`
  - **质量检查点**：测试通过率、报告完整性

## 执行顺序
1. 阶段 1：PRD 分析与模块识别
2. 阶段 2：[模块 1] 测试（优先级 P0）
3. 阶段 3：[模块 2] 测试（优先级 P0）
4. 阶段 4：[模块 3] 测试（优先级 P1）
...

## 质量目标
- 需求覆盖率：100%
- P0/P1 用例自动化率：100%
- 测试通过率：≥95%
- 代码质量：通过 flake8、black、isort 检查

## 风险评估
- **技术风险**：[技术风险评估]
- **时间风险**：[时间风险评估]
- **资源风险**：[资源风险评估]
```

## 标准化 PRD 输入模板

为了帮助 AI 更好地理解需求，建议使用以下结构化 PRD 模板：

```markdown
【测试模块】：[模块名称]
【功能点】：[功能描述]
【前置条件】：
1. [条件 1]
2. [条件 2]
【操作步骤】：
1. [步骤 1]
2. [步骤 2]
3. [步骤 3]
【预期结果】：
1. [结果 1]
2. [结果 2]
【异常场景】：
1. [异常场景 1] → 预期提示：[提示信息]
2. [异常场景 2] → 预期提示：[提示信息]
【环境要求】：[环境说明]
```

## AI 提示词模板

为了确保 AI 生成符合项目规范的代码，建议使用以下提示词模板：

```
### 背景
你需要基于以下测试框架规则，根据 PRD 生成可直接运行的自动化测试代码。

### 测试框架规则
1. 技术栈：Python 3.12.10 + pytest 9.0.2 + playwright 1.49.0+ + Allure 2.15.3
2. 目录规范：
   - 测试用例文件：tests/e2e/test_[模块名].py
   - 页面类文件：core/pages/specific/[模块名]_page.py
   - 测试数据文件：resources/data/[模块名]_data.yaml
   - 定位器文件：resources/locators/[模块名]_page.yaml
3. 命名规范：
   - 测试函数命名：test_[功能点]_[场景]
   - 页面类命名：[模块名]Page
   - 文件命名：小写字母 + 下划线格式
4. 编码规范：
   - 必须使用 tests/conftest.py 提供的 fixture（如 settings、page）
   - 必须使用 tests/utils/ 下的工具类
   - 所有元素定位使用 PageObject 模式
   - 断言使用 pytest.assert
   - 必须添加 Allure 注解（@allure.feature/@allure.story/@allure.step）
5. 输出要求：
   - 先输出"测试用例设计思路"（覆盖正常/异常场景）
   - 再输出完整的测试代码（包含依赖导入、测试类、测试函数、注释）
   - 代码末尾补充"运行说明"（如依赖安装、执行命令）

### PRD 测试需求
[在此粘贴标准化的 PRD 内容]

### 参考样例
请参考以下项目样例文件的风格和结构：
- tests/e2e/test_todomvc.py
- core/pages/specific/[现有页面类文件]
- resources/data/[现有测试数据文件]

### 输出要求
1. 代码需符合 PEP8 规范，无语法错误
2. 注释清晰，关键步骤需添加 @allure.step 说明
3. 输出完整的文件内容（可直接保存为对应路径的文件）
```

## 参考文件

- **PRD 文档**：`<项目根目录>/PRD/`
- **测试流程**：`<项目根目录>/.claude/testing_flow.md`
- **测试指南**：`<项目根目录>/.claude/testing_guidelines.md`
- **项目架构**：`<项目根目录>/docs/architecture/SYSTEM_ARCHITECTURE.md`
- **开发规范**：`<项目根目录>/docs/development/DEVELOPMENT_GUIDELINES.md`

