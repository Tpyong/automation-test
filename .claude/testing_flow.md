# 自动化测试流程

> **最后更新**：2026-04-09
> **目的**：提供从 PRD 到测试代码的完整转化流程
> **适用对象**：AI 助手、测试工程师

## 一、整体流程架构

```mermaid
flowchart TD
    A[PRD 文档] --> B[/plan 命令生成测试计划]
    B --> C[阶段 1: PRD 分析与模块识别]
    C --> D[生成 module_list.md]
    D --> E[阶段 2: 模块 1 测试]
    E --> F[任务 2.1: 页面分析与用例设计]
    F --> G[任务 2.2: Page Object 编写]
    G --> H[任务 2.3: 测试数据编写]
    H --> I[任务 2.4: 测试用例编写]
    I --> J[任务 2.5: 执行验证与报告生成]
    J --> K[阶段 3: 模块 2 测试]
    K --> L[任务 3.1: 页面分析与用例设计]
    L --> M[任务 3.2: Page Object 编写]
    M --> N[任务 3.3: 测试数据编写]
    N --> O[任务 3.4: 测试用例编写]
    O --> P[任务 3.5: 执行验证与报告生成]
    P --> Q[最终报告与知识沉淀]

    subgraph 质量控制
        QC1[需求覆盖率检查]
        QC2[代码质量检查]
        QC3[测试数据隔离检查]
        QC4[定位器稳定性检查]
    end

    F --> QC1
    I --> QC2
    H --> QC3
    G --> QC4
    J --> QC1
    P --> QC1
```

## 二、详细流程设计

### 1. PRD 分析与模块识别（阶段 1）

**输入**：
- PRD 文档（`/PRD/` 目录下的所有文件）

**流程**：
1. **读取 PRD**：分析所有 PRD 文档，提取功能模块
2. **模块识别**：
   - 按页面/业务域划分模块
   - 评估每个模块的复杂度和自动化可行性
   - 确定模块执行顺序（考虑依赖关系）
3. **输出模块清单**：
   - 生成 `output/testcases_docs/module_list.md`
   - 包含模块 ID、名称、优先级、复杂度、预估工作量等

**约束**：
- 只创建新的文档文件，不修改现有代码
- 遵循代码编写约束

**质量检查点**：
- [ ] 模块识别完整性：是否覆盖所有 PRD 需求
- [ ] 优先级合理性：是否正确评估模块优先级
- [ ] 依赖关系明确：是否明确模块间的依赖关系
- [ ] 复杂度评估准确性：是否合理评估模块复杂度

**依赖关系**：
- 前置条件：PRD 文档已准备就绪
- 后置输出：`output/testcases_docs/module_list.md`（作为后续模块测试的输入）

**⚠️ 完成本任务后停止执行，等待 /compact**

### 2. 模块级页面分析（任务 X.1）

**输入**：
- 模块清单（`output/testcases_docs/module_list.md`）
- PRD 文档

**流程**：
1. **页面分析**：
   - 打开页面，获取关键截图
   - 识别页面元素，整理困难元素清单
   - 分析页面交互逻辑
2. **六维场景分析**：
   - 正向场景：正常操作流程
   - 负向场景：错误输入、异常操作
   - 边界场景：极限值、空值、超长值
   - 异常场景：网络异常、系统异常
   - 安全场景：SQL 注入、XSS、越权访问
   - 性能场景：大数据量、高并发
3. **输出分析结果**：
   - 生成 `output/testcases_docs/[模块名]_用例.md`
   - 生成 `output/testcases_docs/[模块名]_问题追踪.md`
   - 保存页面截图到 `output/snapshots/[模块名]/`

**约束**：
- 只创建新的文档和截图文件
- 不修改现有代码

**质量检查点**：
- [ ] 需求覆盖率：是否覆盖所有 PRD 需求
- [ ] 场景完整性：是否包含六维场景
- [ ] 元素识别准确性：是否准确识别页面元素
- [ ] 困难元素记录：是否记录困难元素并提出解决方案

**依赖关系**：
- 前置条件：`output/testcases_docs/module_list.md` 已生成
- 后置输出：`output/testcases_docs/[模块名]_用例.md`、`output/testcases_docs/[模块名]_问题追踪.md`

**⚠️ 完成本任务后停止执行，等待 /compact**

### 3. 用例设计与文档生成（任务 X.1 续）

**流程**：
1. **用例表格编写**：
   - 使用 Markdown 表格形式
   - 包含字段：ID、标题、优先级、用例类型、前置条件、测试步骤、测试数据、预期结果、自动化、关联需求、备注
2. **RTM 矩阵**：
   - 生成需求与测试用例的映射矩阵
   - 确保需求覆盖率 100%
3. **问题记录**：
   - 记录 PRD 与页面实际不符的问题
   - 记录困难元素和潜在风险

**输出**：
- `output/testcases_docs/[模块名]_用例.md`（完整用例文档）

**质量检查点**：
- [ ] 需求覆盖率：是否达到 100%
- [ ] 用例完整性：是否包含所有必要字段
- [ ] RTM 矩阵完整性：是否完整映射需求与用例
- [ ] 问题记录完整性：是否记录所有发现的问题

**依赖关系**：
- 前置条件：`output/testcases_docs/[模块名]_用例.md`（初稿）已生成
- 后置输出：`output/testcases_docs/[模块名]_用例.md`（完整版）

### 4. Page Object 编写（任务 X.2）

**输入**：
- 用例文档（`output/testcases_docs/[模块名]_用例.md`）
- 页面截图（`output/snapshots/[模块名]/`）
- 元素定位临时清单

**流程**：
1. **创建页面类**：
   - 创建 `core/pages/specific/[模块名]_page.py`
   - 继承 `BasePage` 类
   - 定义页面元素定位器（优先使用语义化定位器）
2. **实现页面方法**：
   - 实现页面操作方法（如 `login()`、`submit_form()` 等）
   - 添加页面验证方法（如 `is_logged_in()` 等）
   - 添加页面等待方法（如 `wait_for_page_load()` 等）
3. **定位器文件**：
   - 创建 `resources/locators/[模块名]_page.yaml`
   - 存储页面元素定位器

**约束**：
- 只创建新的页面类和定位器文件
- 不修改 `core/pages/base/` 下的基础页面类

**质量检查点**：
- [ ] 代码质量：是否符合 PEP8 规范
- [ ] 定位器稳定性：是否使用语义化定位器
- [ ] 方法完整性：是否实现所有必要的页面方法
- [ ] 继承关系：是否正确继承 BasePage 类

**依赖关系**：
- 前置条件：`output/testcases_docs/[模块名]_用例.md`（完整版）已生成
- 后置输出：`core/pages/specific/[模块名]_page.py`、`resources/locators/[模块名]_page.yaml`

**⚠️ 完成本任务后停止执行，等待 /compact**

### 5. 测试数据编写（任务 X.3）

**输入**：
- 用例文档（`output/testcases_docs/[模块名]_用例.md`）

**流程**：
1. **数据文件结构**：
   - 创建 `resources/data/[模块名]_data.yaml`
   - 添加完整的 metadata 信息
2. **数据字段**：
   - `case_id`：用例 ID
   - `title`：用例标题
   - `priority`：优先级（P0/P1/P2）
   - `precondition`：前置条件
   - `tags`：标签（如 ["smoke", "regression"]）
   - `estimated_duration`：预估执行时长
   - `input`：输入数据
   - `expect`：预期结果
   - `remark`：备注
3. **数据隔离**：
   - 名称类字段使用 `at_` 前缀（如 `at_user_{{random_alpha_8}}`）
   - 使用动态数据生成，确保数据幂等性

**输出**：
- `resources/data/[模块名]_data.yaml`

**质量检查点**：
- [ ] 数据隔离：是否使用 `at_` 前缀
- [ ] 数据完整性：是否包含所有必要字段
- [ ] 数据幂等性：是否使用动态数据生成
- [ ] 数据格式：是否符合 YAML 格式规范

**依赖关系**：
- 前置条件：`output/testcases_docs/[模块名]_用例.md`（完整版）已生成
- 后置输出：`resources/data/[模块名]_data.yaml`

**⚠️ 完成本任务后停止执行，等待 /compact**

### 6. 测试用例编写（任务 X.4）

**输入**：
- Page Object（`core/pages/specific/[模块名]_page.py`）
- 测试数据（`resources/data/[模块名]_data.yaml`）

**流程**：
1. **创建测试文件**：
   - 创建 `tests/e2e/test_[模块名].py`
   - 编写测试类，添加 Allure 标记
2. **编写测试方法**：
   - 编写独立用例和参数化用例
   - 给涉及数据修改的用例添加 `@pytest.mark.serial` 标记
   - 确保用例覆盖六维场景
3. **使用 fixture 和工具类**：
   - 使用 `tests/conftest.py` 提供的 fixture（`settings`、`page`、`test_data_cleanup` 等）
   - 使用 `tests/utils/` 下的工具类（`VideoManager`、`AttachmentManager`、`ReportManager`）
4. **代码质量检查**：
   - 运行 `black`、`isort`、`flake8` 检查

**约束**：
- 只创建新的测试文件
- 不修改 `tests/conftest.py` 和 `tests/utils/` 下的文件
- 严格遵守代码编写约束

**质量检查点**：
- [ ] 代码质量：是否通过 flake8、black、isort 检查
- [ ] 测试逻辑：是否覆盖六维场景
- [ ] Allure 注解：是否添加了必要的 Allure 注解
- [ ] Fixture 使用：是否正确使用 tests/conftest.py 提供的 fixture

**依赖关系**：
- 前置条件：`core/pages/specific/[模块名]_page.py` 和 `resources/data/[模块名]_data.yaml` 已生成
- 后置输出：`tests/e2e/test_[模块名].py`

**⚠️ 完成本任务后停止执行，等待 /compact**

### 7. 执行验证与报告生成（任务 X.5）

**输入**：
- 测试用例（`tests/e2e/test_[模块名].py`）

**流程**：
1. **执行测试**：
   - `pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results`
2. **结果验证**：
   - 分析测试结果
   - 修复失败用例（上限 3 次）
   - 记录问题到 `[模块名]_问题追踪.md`
3. **生成报告**：
   - 生成 Allure 报告：`allure generate reports/allure-results -o reports/[模块名]_allure_report --clean`
   - 提取失败用例的根本原因分类
4. **知识沉淀**：
   - 创建 `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`

**输出**：
- `reports/[模块名]_allure_report/`
- `output/testcases_docs/[模块名]_问题追踪.md`（更新）
- `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`

**质量检查点**：
- [ ] 测试通过率：是否达到 ≥95%
- [ ] 报告完整性：是否生成完整的 Allure 报告
- [ ] 问题记录：是否记录所有发现的问题
- [ ] 知识沉淀：是否创建最佳实践文档

**依赖关系**：
- 前置条件：`tests/e2e/test_[模块名].py` 已生成
- 后置输出：`reports/[模块名]_allure_report/`、`output/testcases_docs/[模块名]_问题追踪.md`（更新）、`output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`

**⚠️ 完成本任务后停止执行，等待 /compact**

## 三、测试环境配置

### 核心配置文件

**配置管理**：
- `config/settings.py`：配置管理类，处理环境变量和配置项
- `config/envs/.env.base`：基础环境配置
- `config/envs/.env`：本地环境配置（可选，覆盖基础配置）

**测试框架配置**：
- `tests/conftest.py`：测试框架核心配置，包含浏览器管理、fixture 定义、测试增强等功能

### 环境变量配置

**核心环境变量**：
- `BASE_URL`：测试目标 URL
- `TEST_BROWSER`：测试浏览器（chromium、firefox、webkit）
- `HEADLESS`：是否使用无头模式（true/false）
- `ALLURE_REPORT_DIR`：Allure 报告目录
- `VIDEO_ENABLED`：是否启用视频录制（true/false）
- `PLAYWRIGHT_BROWSERS`：多浏览器配置（逗号分隔，如 "chromium,firefox"）

### conftest.py 配置说明

`tests/conftest.py` 是项目 UI 测试的核心配置文件，提供：
- **环境配置**：加载环境变量、配置 Allure 报告
- **浏览器管理**：配置浏览器启动参数、上下文、页面
- **测试增强**：自动录制视频、截图、集成 Allure 报告
- **数据管理**：测试数据清理、数据库连接、Mock 服务器
- **工具类集成**：集成 VideoManager、AttachmentManager、ReportManager

## 四、代码编写约束

**详细约束请参考**：`.trae/rules/project-rule.md`

## 五、测试执行决策规则

- **元素定位失败时**：按优先级尝试 → getByRole() → getByLabel() → getByPlaceholder() → getByText() → data-testid → CSS → XPath
- **用例执行失败时**：分析根本原因 → 优先修复简单问题（定位器、数据）→ 复杂问题（业务逻辑、环境）评估 ROI 后决策
- **修复上限参考**：同一用例修复 3 次仍未通过时，建议暂停并记录问题
- **不确定场景**：PRD 描述模糊、页面行为异常、前后端不一致时，优先基于常识和最佳实践处理
- **代码约束冲突**：如需修改核心文件，记录到问题追踪文件并上报，不要自行修改

## 六、统一检查清单

### 任务 X.1 检查项
- [ ] 用例文档包含：模块信息头、场景矩阵、用例统计、用例列表表格、备注章节、RTM 附录
- [ ] 问题追踪文件已创建，并包含"与 PRD 差异记录"章节
- [ ] 页面截图保存在正确位置：`output/snapshots/[模块名]/`
- [ ] 困难元素清单只记录真正困难的元素（无法用语义化定位的）

### 任务 X.2 检查项
- [ ] 所有定位器优先使用语义化定位（getByRole > getByLabel > getByPlaceholder > getByText）
- [ ] CSS/XPath 定位器都添加了注释说明原因
- [ ] 页面类行数不超过 300 行（如超过需拆分）
- [ ] 问题追踪文件已更新（如有新发现的问题）

### 任务 X.3 检查项
- [ ] metadata 字段完整（generated_by、module、version、last_updated、author）
- [ ] 每条数据都有 tags 和 estimated_duration
- [ ] 创建类数据使用了动态数据生成（at_user_{{random_alpha_8}} 等）
- [ ] 数据覆盖了所有六维场景（正向、负向、边界、异常、安全、性能）
- [ ] P0 用例添加了 ["smoke", "regression"] 标签
- [ ] P1 用例添加了 ["regression"] 标签

### 任务 X.4 检查项
- [ ] 所有用例都有 @allure.feature 和 @allure.story 注解
- [ ] P0/P1/P2 用例正确映射到 allure 严重级别（P0→BLOCKER, P1→CRITICAL, P2→NORMAL）
- [ ] 数据修改类用例添加了 @pytest.mark.serial 标记
- [ ] 每个六维场景都有对应的用例
- [ ] P0/P1 用例包含性能断言（页面加载时间验证）
- [ ] 测试文件行数不超过 500 行（如超过需拆分）
- [ ] 充分利用了测试工具类来简化代码
- [ ] 代码质量检查通过：
  - [ ] 已运行 `black` 格式化
  - [ ] 已运行 `isort` 排序
  - [ ] 已运行 `flake8` 检查
- [ ] **代码编写约束检查**：
  - [ ] 没有修改 `tests/conftest.py`
  - [ ] 没有修改 `config/settings.py`
  - [ ] 没有修改 `tests/utils/` 下的文件
  - [ ] 没有修改 `core/pages/base/` 下的文件
  - [ ] 只创建了新的测试文件和页面类

### 任务 X.5 检查项
- [ ] 测试代码与用例文档一致（用例 ID、标题、预期结果）
- [ ] Allure 报告生成成功并能正常打开
- [ ] 失败用例均已记录到问题追踪文件
- [ ] 修复历史统计已更新（修复轮次、成功率、根因分布）
- [ ] knowledge_base 目录已创建（如不存在）
- [ ] 有失败用例时，知识沉淀文档已创建
- [ ] 核心质量指标达标：需求覆盖率 100%、P0/P1 自动化率 100%、数据幂等性
- [ ] 多浏览器测试通过（Chromium 和 Firefox）

### 核心质量指标（AI 快速确认）
- [ ] 需求覆盖率：100%（RTM 检查无遗漏）
- [ ] P0/P1 用例自动化率：100%
- [ ] 测试数据幂等性：可重复执行
- [ ] 多浏览器兼容性：在 Chromium 和 Firefox 中都能正常运行
- [ ] 代码编写约束遵守：没有修改核心文件

## 七、工具与脚本使用

### 1. 代码检查脚本
- **使用方法**：`python scripts/ai_code_checker.py`
- **功能**：检查是否修改了禁止的文件，确保新增文件在允许范围内
- **返回码**：0（检查通过），1（检查失败）

### 2. 测试执行命令
- **单浏览器测试**：
  ```bash
  pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results
  ```
- **多浏览器测试**：
  ```bash
  pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results --browser chromium --browser firefox
  ```
- **生成 Allure 报告**：
  ```bash
  allure generate reports/allure-results -o reports/[模块名]_allure_report --clean
  ```

### 3. 代码质量工具
- **格式化代码**：`black core/ tests/ && isort core/ tests/`
- **检查代码**：`flake8 core/ tests/ && mypy core/`

## 八、执行建议

1. **循序渐进**：按照流程顺序执行，确保每个步骤都完成后再进入下一步
2. **质量优先**：在保证质量的前提下，最大化执行效率
3. **问题记录**：及时记录和追踪测试过程中发现的问题
4. **约束遵守**：严格遵守代码编写约束，确保不修改核心文件
5. **工具使用**：充分利用项目提供的工具类和脚本，简化测试代码
6. **多浏览器测试**：确保测试在 Chromium 和 Firefox 中都能正常运行
7. **知识沉淀**：将测试过程中的经验和解决方案沉淀到知识库中
