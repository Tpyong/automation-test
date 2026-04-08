# 自动化测试计划

> **最后更新**：2026-04-08
> **状态**：基础框架已搭建完成，直接从 PRD 分析开始

---

## 技术栈
Python 3.12.10 / Pytest 9.0.2 / Playwright 1.49.0+ / Allure 2.15.3 / Loguru 0.7.2+

---

## 测试阶段划分

### 阶段 0：PRD 整体分析与模块识别

**目标**：全面分析 PRD需求文档，识别所有功能模块，评估自动化可行性，形成完整的模块清单和优先级排序

**任务内容**：
1. 读取所有 PRD文档，提取功能模块清单
2. 对每个模块进行初步评估：
   - 功能复杂度（高/中/低）
   - 页面交互复杂度（高/中/低）
   - 数据依赖关系（是否需要前置数据）
   - 自动化可行性（适合自动化/部分自动化/不建议自动化）
   - 预估工作量（人天或 AI 执行轮次）
3. 确定模块执行顺序（考虑依赖关系）
4. 输出完整的模块清单和执行计划

**输出内容**：
- `output/testcases_docs/module_list.md`（功能模块清单，含优先级、复杂度、预估工作量）
- `output/testcases_docs/automation_feasibility.md`（自动化可行性分析报告）

**⚠️ 完成本任务后停止执行，等待 /compact**

---

### 阶段 2 起：UI 功能模块测试

**目标**：完成 [具体功能描述] 模块的 UI自动化测试全流程实现，确保测试用例覆盖全面、执行稳定、结果可追溯，形成"设计 - 开发 - 执行 - 验收 - 沉淀"的完整闭环。

**说明**：本阶段为标准化模板，后续每个功能模块（阶段 3、4、5...）都复制本阶段的任务结构，仅替换 [模块名] 和具体功能内容。

#### 任务 X.1：页面分析与用例设计

**参考文件**：
- PRD/[相关需求文档].md
- testing_guidelines.md（测试用例编写规范）

**任务内容**：
1. 打开实际页面，设置视口为 1920x1080，获取**关键页面截图**（仅核心流程页面），保存到 `output/snapshots/[模块名]/` 
2. 识别所有交互元素（包括动态元素），触发显示后获取快照，过程截图保存同步骤 1 
3. 主动触发关键交互（提交、校验、删除等），采集实际提示语和反馈信息，过程截图保存同步骤 1 
4. 基于步骤 1-3 的截图和快照，整理**困难元素定位清单**（只记录无法使用 getByRole/Label/Placeholder/Text 定位的元素），保存到 `output/testcases_docs/[模块名]_元素定位临时清单.md` 
5. 六维场景分析（**分级策略**：核心功能全覆盖，一般功能正向 + 负向 + 边界，简单功能正向为主）
6. 编写用例表格文档，保存到 `output/testcases_docs/[模块名]_用例.md`（需与 testing_guidelines.md 中用例表格规范一致）
7. 基于步骤 1-4 的发现，对比 PRD 与实际实现，记录差异到 `output/testcases_docs/[模块名]_问题追踪.md` 的"与 PRD 差异记录"章节
8. 创建需求追溯矩阵条目，作为附录添加到 `output/testcases_docs/[模块名]_用例.md` 文档末尾（不再生成独立文件）

**输出内容**：
- `output/testcases_docs/[模块名]_用例.md`（含 RTM 附录）
- `output/snapshots/[模块名]/`（**关键页面截图**，非全部页面）
- `output/testcases_docs/[模块名]_元素定位临时清单.md`（**只记录困难元素**）
- `output/testcases_docs/[模块名]_问题追踪.md`（问题统一追踪文件，初始包含与 PRD 差异记录）

**⚠️ 完成本任务后必须检查**：
- [ ] 用例文档包含：模块信息头、场景矩阵、用例统计、用例列表表格、备注章节、RTM 附录
- [ ] 问题追踪文件已创建，并包含"与 PRD 差异记录"章节
- [ ] 页面截图保存在正确位置：`output/snapshots/[模块名]/`
- [ ] 困难元素清单只记录真正困难的元素（无法用语义化定位的）

**⚠️ 完成本任务后停止执行，等待 /compact**

---

#### 任务 X.2：Page Object 编写

**参考文件**：
- 任务 X.1 输出的用例文档、元素定位临时清单、页面截图
- testing_guidelines.md（Page Object 编写规范）

**任务内容**：
1. 创建 `pages/[模块名]_page.py` 页面类，继承 BasePage
2. 定义定位器（严格遵循 testing_guidelines.md 中的元素定位优先级），封装页面操作方法
3. 如涉及公共组件（弹窗、表格、下拉框等），按 testing_guidelines.md 规范编写 components/ 下的组件类
4. 如发现定位困难、页面结构与 PRD 不符等问题，追加到 `output/testcases_docs/[模块名]_问题追踪.md` 的"与 PRD 差异记录"章节

**输出内容**：
- `pages/[模块名]_page.py`
- `components/[组件名].py`（如需要）

**⚠️ 完成本任务后必须检查**：
- [ ] 所有定位器优先使用语义化定位（getByRole > getByLabel > getByPlaceholder > getByText）
- [ ] CSS/XPath 定位器都添加了注释说明原因
- [ ] 页面类行数不超过 300 行（如超过需拆分）
- [ ] 问题追踪文件已更新（如有新发现的问题）

**⚠️ 完成本任务后停止执行，等待 /compact**

---

#### 任务 X.3：测试数据编写

**参考文件**：
- 任务 X.1 输出的用例文档
- testing_guidelines.md（测试数据设计规范）

**任务内容**：
1. 根据用例表格编写 YAML 测试数据文件，保存到 `data/[模块名]_data.yaml`
2. 添加 metadata 信息（generated_by、module、version、last_updated、author）
3. 为每条测试数据添加 tags 字段（如 ["smoke", "regression"]）和 estimated_duration（预估执行时长，单位秒）
4. 遵循数据隔离规则（名称类字段使用 at_ 前缀）
5. 确保数据覆盖所有六维测试场景
6. 确保数据幂等性（详见 testing_guidelines.md 数据幂等性章节）
   - 创建类数据必须使用动态数据：`{{random_alpha_8}}`、`{{timestamp}}` 等
   - 或使用前置清理逻辑
7. 备注字段说明数据用途或特殊约束

**输出内容**：
- `data/[模块名]_data.yaml`（含 metadata、tags、estimated_duration）

**⚠️ 完成本任务后必须检查**：
- [ ] metadata 字段完整（generated_by、module、version、last_updated、author）
- [ ] 每条数据都有 tags 和 estimated_duration
- [ ] 创建类数据使用了动态数据生成（at_user_{{random_alpha_8}} 等）
- [ ] 数据覆盖了所有六维场景（正向、负向、边界、异常、安全、性能）
- [ ] P0 用例添加了 ["smoke", "regression"] 标签
- [ ] P1 用例添加了 ["regression"] 标签

**⚠️ 完成本任务后停止执行，等待 /compact**

---

#### 任务 X.4：测试用例编写

**参考文件**：
- 任务 X.2 输出的 Page Object
- 任务 X.3 输出的测试数据
- testing_guidelines.md（测试用例编写规范）

**任务内容**：
1. 创建 `tests/unit/test_[模块名].py` 或 `tests/e2e/test_[模块名].py` 测试文件，根据测试类型选择合适的目录
2. 编写测试类，添加 Allure 标记（@allure.feature、@allure.story、@allure.severity）
3. 编写独立用例和参数化用例，给涉及数据修改的用例（创建、编辑、删除）添加 `@pytest.mark.serial` 标记
4. 确保用例覆盖六维场景，每个场景至少对应 1 个用例
5. 实现动态数据生成或前置清理逻辑，确保测试可重复执行
6. 断言需覆盖完整维度（页面元素、数据、交互反馈、性能）
7. 核心用例（P0/P1）添加性能断言（页面加载时间 < 3s）
8. 充分利用 `tests/utils/` 下的工具类（VideoManager、AttachmentManager、ReportManager）来简化测试代码

**输出内容**：
- `tests/unit/test_[模块名].py` 或 `tests/e2e/test_[模块名].py`

**⚠️ 完成本任务后必须检查**：
- [ ] 所有用例都有 @allure.feature 和 @allure.story 注解
- [ ] P0/P1/P2 用例正确映射到 allure 严重级别（P0→BLOCKER, P1→CRITICAL, P2→NORMAL）
- [ ] 数据修改类用例添加了 @pytest.mark.serial 标记
- [ ] 每个六维场景都有对应的用例
- [ ] P0/P1 用例包含性能断言（页面加载时间验证）
- [ ] 测试文件行数不超过 500 行（如超过需拆分）
- [ ] 充分利用了测试工具类来简化代码

**⚠️ 完成本任务后停止执行，等待 /compact**

---

#### 任务 X.5：执行验证与报告检查

**参考文件**：
- 任务 X.4 输出的测试用例
- testing_guidelines.md（执行验证规范）
- 任务 X.1 输出的用例文档

**任务内容**：
1. 读取任务 X.1 输出的用例文档，核对测试用例与用例文档的一致性
2. 执行全部用例：`pytest tests/unit/test_[模块名].py --alluredir=reports/allure-results` 或 `pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results`
3. 执行多浏览器测试：`pytest tests/unit/test_[模块名].py --alluredir=reports/allure-results --browser chromium,firefox`
4. 如有失败：分析原因，补充分析阶段未获取的预期结果到 `data/[模块名]_data.yaml`（**禁止修改测试数据文件中已确认的数据**），记录到 `output/testcases_docs/[模块名]_问题追踪.md` 的"执行失败与修复记录"章节，提出修复方案
5. 自主修复上限 3 次，每次修复必须记录到 `output/testcases_docs/[模块名]_问题追踪.md` 的"执行失败与修复记录"章节（修复原因分类、修改内容、修复结果、是否复发）
6. 修复并重新执行，直到全部通过或达到 3 次上限，超过上限的记录到 `output/testcases_docs/[模块名]_问题追踪.md` 的"遗留问题"章节并上报
7. 不稳定用例标记 `@pytest.mark.flaky(reruns=3, reruns_delay=2)`，无法修复的记录到 `output/testcases_docs/[模块名]_问题追踪.md` 的"遗留问题"章节并上报
8. 全部通过后：生成问题追踪摘要，检查 Allure 报告（覆盖率、时长、附件），生成静态报告：`allure generate reports/allure-results -o reports/[模块名]_allure_report --clean`
9. 提取失败用例的根本原因分类，更新到 `output/testcases_docs/[模块名]_问题追踪.md` 的"修复历史统计"章节
10. 将典型失败案例和解决方案沉淀到 `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`
   - **有失败用例时必须创建**
   - **无失败但遇到技术难题时建议创建**
11. **填写简版自检报告**（可选），保存到 `output/testcases_docs/[模块名]_自检报告.md`（使用简化模板）

**输出内容**：
- `data/[模块名]_data.yaml`（如有补充）
- `output/testcases_docs/[模块名]_问题追踪.md`（统一问题追踪文件，含差异记录、失败修复、遗留问题、修复统计）
- `reports/[模块名]_allure_report/`（Allure 静态报告）
- `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`（知识沉淀，**有失败用例时必须创建**）
- `output/testcases_docs/[模块名]_自检报告.md`（可选，时间充裕时填写）

**⚠️ 完成本任务后必须检查**：
- [ ] 测试代码与用例文档一致（用例 ID、标题、预期结果）
- [ ] Allure 报告生成成功并能正常打开
- [ ] 失败用例均已记录到问题追踪文件
- [ ] 修复历史统计已更新（修复轮次、成功率、根因分布）
- [ ] knowledge_base 目录已创建（如不存在）
- [ ] 有失败用例时，知识沉淀文档已创建
- [ ] 核心质量指标达标：需求覆盖率 100%、P0/P1 自动化率 100%、数据幂等性
- [ ] 多浏览器测试通过（Chromium 和 Firefox）

**⚠️ 完成本任务后停止执行，等待 /compact**

---

**✅ 阶段 X 完成标志**：
- [功能模块名称] UI自动化用例全部通过
- Allure 报告完整可查
- **核心质量指标**（AI 快速确认）：
  - ✅ 需求覆盖率：100%（RTM 检查无遗漏）
  - ✅ P0/P1 用例自动化率：100%
  - ✅ 测试数据幂等性：可重复执行
  - ✅ 多浏览器兼容性：在 Chromium 和 Firefox 中都能正常运行
  - ⚠️ 其他指标供参考（通过率、时长等）

---

## 测试计划制定原则

1. **PRD 分析**：仔细分析所有 PRD 文档，识别所有功能模块，确保无遗漏
2. **模块化测试**：每个功能模块独立执行，形成完整的测试闭环
3. **质量优先**：核心关注需求覆盖率、数据幂等性、定位器稳定性
4. **问题追踪**：所有问题统一记录到 [模块名]_问题追踪.md，避免多文件维护
5. **修复上限**：3 次修复未通过时建议暂停，如 AI 判断有把握可继续但需说明理由
6. **上下文管理**：文件顶部添加简短元信息，避免冗长模板
7. **命名规范**：统一格式便于维护，模块名称使用小写字母 + 下划线
8. **效率优先**：在保证核心质量的前提下，最大化执行效率
9. **多浏览器支持**：考虑不同浏览器的兼容性，确保测试在 Chromium 和 Firefox 中都能正常运行
10. **测试工具类使用**：充分利用 tests/utils/ 下的工具类来简化测试代码

## 测试执行决策规则

- **元素定位失败时**：按优先级尝试 → getByRole() → getByLabel() → getByPlaceholder() → getByText() → data-testid → CSS → XPath
- **用例执行失败时**：分析根本原因 → 优先修复简单问题（定位器、数据）→ 复杂问题（业务逻辑、环境）评估 ROI 后决策
- **修复上限参考**：同一用例修复 3 次仍未通过时，建议暂停并记录问题
- **不确定场景**：PRD 描述模糊、页面行为异常、前后端不一致时，优先基于常识和最佳实践处理

## 质量自检清单

- [ ] 核心功能是否覆盖？（对照 PRD 检查关键场景）
- [ ] 测试数据是否幂等？（可重复执行不冲突）
- [ ] 定位器是否稳定？（优先语义化定位）
- [ ] 断言是否合理？（能验证功能正确性）
- [ ] 文档是否一致？（代码、数据、用例预期一致）
- [ ] 多浏览器兼容性？（在 Chromium 和 Firefox 中都能正常运行）