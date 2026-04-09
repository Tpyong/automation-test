# 自动化测试计划

> **最后更新**：2026-04-08
> **状态**：基础框架已搭建完成，直接从 PRD 分析开始

***

## 技术栈

- **测试框架**：pytest 9.0.2 + pytest-playwright 1.49.0+
- **浏览器自动化**：Playwright (Chromium/Firefox)
- **报告工具**：Allure 2.15.3
- **代码质量**：pylint + flake8 + black + isort + mypy
- **数据格式**：YAML/JSON

***

## 测试环境配置

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

`tests/conftest.py` 是项目 UI 测试的核心配置文件，提供了以下功能：

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

***

## 测试阶段划分

### 阶段 0：PRD 整体分析与模块识别

**目标**：全面分析 PRD 需求文档，识别所有功能模块，评估自动化可行性，形成完整的模块清单和优先级排序

**任务内容**：

1. 读取所有 PRD 文档，提取功能模块清单
2. 对每个模块进行初步评估：
   - 功能复杂度（高/中/低）
   - 页面交互复杂度（高/中/低）
   - 数据依赖关系（是否需要前置数据）
   - 自动化可行性（适合自动化/部分自动化/不建议自动化）
   - 预估工作量（AI 执行轮次）
3. 确定模块执行顺序（考虑依赖关系）
4. 输出完整的模块清单和执行计划

**输出内容**：

- `output/testcases_docs/module_list.md`（功能模块清单，含优先级、复杂度、预估工作量）

**⚠️ 完成本任务后停止执行，等待 /compact**

***

### 阶段 2 起：UI 功能模块测试

**目标**：完成 \[具体功能描述] 模块的 UI 自动化测试全流程实现，确保测试用例覆盖全面、执行稳定、结果可追溯

**说明**：本阶段为标准化模板，后续每个功能模块（阶段 3、4、5...）都复制本阶段的任务结构，仅替换 \[模块名] 和具体功能内容

***

#### 任务 X.1：页面分析与用例设计

**参考文件**：

- PRD/\[相关需求文档].md
- testing\_guidelines.md（测试用例编写规范）
- templates/module\_list.md（模块清单模板）

**任务内容**：

1. 打开实际页面，设置视口为 1920x1080，获取**关键页面截图**（仅核心流程页面），保存到 `output/snapshots/[模块名]/`
2. 识别所有交互元素（包括动态元素），触发显示后获取快照
3. 主动触发关键交互（提交、校验、删除等），采集实际提示语和反馈信息
4. 基于截图和快照，整理**困难元素定位清单**（只记录无法使用 getByRole/Label/Placeholder/Text 定位的元素），保存到 `output/testcases_docs/[模块名]_元素定位临时清单.md`
5. 六维场景分析（**分级策略**：核心功能全覆盖，一般功能正向 + 负向 + 边界，简单功能正向为主）
6. 编写用例表格文档，保存到 `output/testcases_docs/[模块名]_用例.md`
7. 对比 PRD 与实际实现，记录差异到 `output/testcases_docs/[模块名]_问题追踪.md` 的"与 PRD 差异记录"章节
8. 创建需求追溯矩阵条目，作为附录添加到 `output/testcases_docs/[模块名]_用例.md` 文档末尾

**输出内容**：

- `output/testcases_docs/[模块名]_用例.md`（含 RTM 附录）
- `output/snapshots/[模块名]/`（关键页面截图）
- `output/testcases_docs/[模块名]_元素定位临时清单.md`（只记录困难元素）
- `output/testcases_docs/[模块名]_问题追踪.md`（问题统一追踪文件）

**⚠️ 完成本任务后停止执行，等待 /compact**

***

#### 任务 X.2：Page Object 编写

**参考文件**：

- 任务 X.1 输出的用例文档、元素定位临时清单、页面截图
- testing\_guidelines.md（Page Object 编写规范）
- docs/development/DEVELOPMENT\_GUIDELINES.md（开发规范）

**任务内容**：

1. 创建 `pages/[模块名]_page.py` 页面类，继承 BasePage
2. 定义定位器（严格遵循 testing\_guidelines.md 中的元素定位优先级），封装页面操作方法
3. 如涉及公共组件（弹窗、表格、下拉框等），按规范编写 `components/` 下的组件类
4. 如发现定位困难、页面结构与 PRD 不符等问题，追加到问题追踪文件

**输出内容**：

- `pages/[模块名]_page.py`
- `components/[组件名].py`（如需要）

**⚠️ 完成本任务后停止执行，等待 /compact**

***

#### 任务 X.3：测试数据编写

**参考文件**：

- 任务 X.1 输出的用例文档
- testing\_guidelines.md（测试数据设计规范）
- utils/data/test\_data\_loader.py（测试数据加载器）

**任务内容**：

1. **数据文件结构**：根据用例表格编写 YAML 测试数据文件，保存到 `data/[模块名]_data.yaml`
2. **metadata 信息**：添加完整的 metadata 信息
   ```yaml
   metadata:
     generated_by: AI
     module: [模块名称]
     version: "1.0"
     last_updated: "2026-04-09"
     author: "tester_name"
   ```
3. **数据字段**：为每条测试数据添加以下字段：
   - `case_id`：用例 ID
   - `title`：用例标题
   - `priority`：优先级（P0/P1/P2）
   - `precondition`：前置条件
   - `tags`：标签（如 \["smoke", "regression"]）
   - `estimated_duration`：预估执行时长（单位秒）
   - `input`：输入数据
   - `expect`：预期结果
   - `remark`：备注
4. **数据隔离**：名称类字段使用 `at_` 前缀（如 `at_user_{{random_alpha_8}}`）
5. **数据幂等性**：
   - 使用动态数据：`{{random_alpha_8}}`、`{{timestamp}}` 等
   - 或使用前置清理逻辑
6. **数据覆盖**：确保数据覆盖所有六维测试场景
7. **数据加载**：使用项目提供的测试数据加载器
   ```python
   from utils.data.test_data_loader import TestDataLoader

   # 加载测试数据
   login_data = TestDataLoader.get_login_data('login_success')
   ```

**输出内容**：

- `data/[模块名]_data.yaml`（含 metadata、tags、estimated\_duration）

**⚠️ 完成本任务后停止执行，等待 /compact**

***

#### 任务 X.4：测试用例编写

**参考文件**：

- 任务 X.2 输出的 Page Object
- 任务 X.3 输出的测试数据
- testing\_guidelines.md（测试用例编写规范）
- docs/development/DEVELOPMENT\_GUIDELINES.md（开发规范）

**任务内容**：

1. 创建 `tests/e2e/test_[模块名].py` 测试文件（优先使用 e2e 目录，除非明确是单元测试）
2. 编写测试类，添加 Allure 标记（@allure.feature、@allure.story、@allure.severity）
3. 编写独立用例和参数化用例，给涉及数据修改的用例（创建、编辑、删除）添加 `@pytest.mark.serial` 标记
4. 确保用例覆盖六维场景，每个场景至少对应 1 个用例
5. 实现动态数据生成或前置清理逻辑，确保测试可重复执行
6. 断言需覆盖完整维度（页面元素、数据、交互反馈、性能）
7. 核心用例（P0/P1）添加性能断言（页面加载时间 < 3s）
8. 充分利用 `tests/utils/` 下的工具类来简化测试代码
9. 确保代码符合质量要求，运行代码质量检查：
   - `black tests/e2e/test_[模块名].py`
   - `isort tests/e2e/test_[模块名].py`
   - `flake8 tests/e2e/test_[模块名].py`

**输出内容**：

- `tests/e2e/test_[模块名].py`

**⚠️ 完成本任务后停止执行，等待 /compact**

***

#### 任务 X.5：执行验证与报告检查

**参考文件**：

- 任务 X.4 输出的测试用例
- testing\_guidelines.md（执行验证规范）
- 任务 X.1 输出的用例文档
- config/settings.py（配置管理类）

**任务内容**：

1. 读取任务 X.1 输出的用例文档，核对测试用例与用例文档的一致性
2. **执行全部用例**：
   ```bash
   # 单浏览器测试
   pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results

   # 多浏览器测试
   pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results --browser chromium --browser firefox

   # 带环境变量的测试
   BASE_URL=https://staging.example.com pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results
   ```
3. **多浏览器测试配置**：
   - 环境变量配置：`PLAYWRIGHT_BROWSERS=chromium,firefox`
   - 命令行参数：`--browser chromium --browser firefox`
   - 配置文件：在 `config/settings.py` 中设置默认浏览器
4. 如有失败：分析原因，补充分析阶段未获取的预期结果到数据文件，记录到问题追踪文件的"执行失败与修复记录"章节，提出修复方案
5. 自主修复上限 3 次，每次修复必须记录到问题追踪文件
6. 修复并重新执行，直到全部通过或达到 3 次上限，超过上限的记录到"遗留问题"章节并上报
7. 不稳定用例标记 `@pytest.mark.flaky(reruns=3, reruns_delay=2)`，无法修复的记录到"遗留问题"章节并上报
8. 全部通过后：生成问题追踪摘要，检查 Allure 报告，生成静态报告：`allure generate reports/allure-results -o reports/[模块名]_allure_report --clean`
9. 提取失败用例的根本原因分类，更新到问题追踪文件的"修复历史统计"章节
10. 将典型失败案例和解决方案沉淀到 `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`

**输出内容**：

- `data/[模块名]_data.yaml`（如有补充）
- `output/testcases_docs/[模块名]_问题追踪.md`（统一问题追踪文件）
- `reports/[模块名]_allure_report/`（Allure 静态报告）
- `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`（知识沉淀，有失败用例时必须创建）

**⚠️ 完成本任务后停止执行，等待 /compact**

***

**✅ 阶段 X 完成标志**：

- \[功能模块名称] UI 自动化用例全部通过
- Allure 报告完整可查
- **核心质量指标**：
  - ✅ 需求覆盖率：100%（RTM 检查无遗漏）
  - ✅ P0/P1 用例自动化率：100%
  - ✅ 测试数据幂等性：可重复执行
  - ✅ 多浏览器兼容性：在 Chromium 和 Firefox 中都能正常运行

***

## 测试计划制定原则

1. **PRD 分析**：仔细分析所有 PRD 文档，识别所有功能模块，确保无遗漏
2. **模块化测试**：每个功能模块独立执行，形成完整的测试闭环
3. **质量优先**：核心关注需求覆盖率、数据幂等性、定位器稳定性
4. **问题追踪**：所有问题统一记录到 \[模块名]\_问题追踪.md，避免多文件维护
5. **修复上限**：3 次修复未通过时建议暂停，如 AI 判断有把握可继续但需说明理由
6. **上下文管理**：文件顶部添加简短元信息，避免冗长模板
7. **命名规范**：统一使用小写字母 + 下划线格式，便于维护
8. **效率优先**：在保证核心质量的前提下，最大化执行效率
9. **多浏览器支持**：考虑不同浏览器的兼容性，确保测试在 Chromium 和 Firefox 中都能正常运行
10. **测试工具类使用**：充分利用 tests/utils/ 下的工具类来简化测试代码

***

## 测试执行决策规则

- **元素定位失败时**：按优先级尝试 → getByRole() → getByLabel() → getByPlaceholder() → getByText() → data-testid → CSS → XPath
- **用例执行失败时**：分析根本原因 → 优先修复简单问题（定位器、数据）→ 复杂问题（业务逻辑、环境）评估 ROI 后决策
- **修复上限参考**：同一用例修复 3 次仍未通过时，建议暂停并记录问题
- **不确定场景**：PRD 描述模糊、页面行为异常、前后端不一致时，优先基于常识和最佳实践处理

***

## 统一检查清单

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

- [ ] metadata 字段完整（generated\_by、module、version、last\_updated、author）
- [ ] 每条数据都有 tags 和 estimated\_duration
- [ ] 创建类数据使用了动态数据生成（at\_user\_{{random\_alpha\_8}} 等）
- [ ] 数据覆盖了所有六维场景（正向、负向、边界、异常、安全、性能）
- [ ] P0 用例添加了 \["smoke", "regression"] 标签
- [ ] P1 用例添加了 \["regression"] 标签

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

### 任务 X.5 检查项

- [ ] 测试代码与用例文档一致（用例 ID、标题、预期结果）
- [ ] Allure 报告生成成功并能正常打开
- [ ] 失败用例均已记录到问题追踪文件
- [ ] 修复历史统计已更新（修复轮次、成功率、根因分布）
- [ ] knowledge\_base 目录已创建（如不存在）
- [ ] 有失败用例时，知识沉淀文档已创建
- [ ] 核心质量指标达标：需求覆盖率 100%、P0/P1 自动化率 100%、数据幂等性
- [ ] 多浏览器测试通过（Chromium 和 Firefox）

### 核心质量指标（AI 快速确认）

- [ ] 需求覆盖率：100%（RTM 检查无遗漏）
- [ ] P0/P1 用例自动化率：100%
- [ ] 测试数据幂等性：可重复执行
- [ ] 多浏览器兼容性：在 Chromium 和 Firefox 中都能正常运行

