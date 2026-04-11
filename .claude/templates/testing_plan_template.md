# 测试执行计划模板

## 项目信息

- **项目名称**：\[项目名称]
- **PRD 文档**：\[PRD 路径]
- **生成时间**：\[当前时间]
- **执行环境**：\[环境信息]

## 执行计划

### 六维场景分析法说明

**六维场景分析法**是一种全面的测试场景设计方法，用于确保测试覆盖各种可能的使用场景：

| 维度     | 定义            | 示例（以登录功能为例）            |
| ------ | ------------- | ---------------------- |
| **正向** | 符合业务规则的正常流程   | 正确的用户名 + 密码登录成功，跳转首页   |
| **负向** | 不符合业务规则的输入或操作 | 错误密码、未注册账号、账号被锁定       |
| **边界** | 输入参数的临界值      | 密码长度最小值（6 位）、最大值（20 位） |
| **异常** | 系统异常状态或非预期操作  | 网络中断、服务超时、并发登录         |
| **安全** | 验证安全机制有效性     | SQL 注入、XSS 攻击、暴力破解防护   |
| **性能** | 验证响应时间和资源占用   | 页面加载速度、并发性能            |

### 阶段 1：PRD 分析与模块识别

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

**输出**：
- `output/testcases_docs/module_list.md`（作为后续模块测试的输入）

### 阶段 2：\[模块名 1] 测试

#### 任务 2.1：页面分析与用例设计
**输入**：
- 模块清单（`output/testcases_docs/module_list.md`）
- 测试用例设计指南（`.claude/testing_guidelines.md` 章节 一、测试用例设计规范）
- 问题追踪模板（`.claude/templates/problem_tracking.md`）
- PRD 文档（`/PRD/[相关需求文档].md`）

**流程**：
1. 以 1920×1080 视口访问目标页面，自动触发全量交互与关键操作（提交、校验、删除等），同步截取截图并采集界面反馈信息，输出至 `output/snapshots/[模块名]/`。
2. 整理无法通过标准方式定位的困难元素，保存到 `output/testcases_docs/[模块名]_元素定位临时清单.md` 。
3. 对比 PRD 与实际实现，使用 `.claude/templates/problem_tracking.md` 模板创建 `output/testcases_docs/[模块名]_问题追踪.md` 并记录差异。
4. 按照六维场景分析法设计测试用例，生成符合 `.claude/testing_guidelines.md` 章节 一、测试用例设计规范 - 4. 用例表格规范，输出 `output/testcases_docs/[模块名]_用例.md`。
5. 构建需求追溯矩阵，作为附录添加到 `output/testcases_docs/[模块名]_用例.md`。

**约束**：
- 只创建新的文档和截图文件
- 不修改现有代码

**质量检查点**：
- [ ] 需求覆盖率：是否覆盖所有 PRD 需求
- [ ] 场景完整性：是否包含六维场景
- [ ] 元素识别准确性：是否准确识别页面元素
- [ ] 困难元素记录：是否记录困难元素并提出解决方案

**输出**：
- `output/testcases_docs/[模块名]_用例.md`（含 RTM 附录）
- `output/snapshots/[模块名]/`（**关键页面截图**，非全部页面）
- `output/testcases_docs/[模块名]_元素定位临时清单.md`（**只记录困难元素**）
- `output/testcases_docs/[模块名]_问题追踪.md`（问题统一追踪文件，初始包含与 PRD 差异记录）

**⚠️ 完成本任务后停止执行，等待人工确认**

#### 任务 2.2：Page Object 编写
**输入**：
- 用例文档（`output/testcases_docs/[模块名]_用例.md`）
- 页面截图（`output/snapshots/[模块名]/`）
- 元素定位临时清单（`output/testcases_docs/[模块名]_元素定位临时清单.md`）
- 测试用例设计指南（`.claude/testing_guidelines.md` 章节 二、Page Object 编写规范）

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

**输出**：
- `core/pages/specific/[模块名]_page.py`
- `resources/locators/[模块名]_page.yaml`

**⚠️ 完成本任务后停止执行，等待人工确认**

#### 任务 2.3：测试数据编写
**输入**：
- 用例文档（`output/testcases_docs/[模块名]_用例.md`）
- 测试用例设计指南（`.claude/testing_guidelines.md` 章节 一、测试用例设计规范 - 5. 测试数据设计规范）

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
- **数据隔离**：名称类字段使用 `at_` 前缀区分测试数据（如 `at_客户A`、`at_部门1`），其他字段（如手机号、邮箱）无需前缀
- **数据幂等性**：确保测试可重复执行，避免数据冲突
  - **动态数据（推荐）**：根据字段约束生成唯一数据，确保符合格式和长度要求
    - 纯字母字段（如用户名只能字母，6-20位）：`at_user_{{random_alpha_8}}`（固定前缀+8位随机字母）
    - 数字字段（如工号，6位）：`{{random_6digits}}` 或 `{{timestamp_6}}`（截取时间戳后6位）
    - 混合字段（字母+数字，无长度限制）：`at_用户_{{timestamp}}` 或 `at_用户_{{random}}`
    - 邮箱字段：`at_test_{{timestamp}}@example.com`
    - 手机号字段（11位）：`138{{random_8digits}}`（固定前缀+8位随机数字）
    - 日期字段：使用当前日期或相对日期（如 `{{today}}`、`{{tomorrow}}`）
  - **前置清理**：测试前先删除可能存在的测试数据
- **数据覆盖**：确保测试数据覆盖六维场景

**质量检查点**：
- [ ] 数据隔离：是否使用 `at_` 前缀
- [ ] 数据完整性：是否包含所有必要字段
- [ ] 数据幂等性：是否使用动态数据生成
- [ ] 数据格式：是否符合 YAML 格式规范

**输出**：
- `resources/data/[模块名]_data.yaml`

**⚠️ 完成本任务后停止执行，等待人工确认**

#### 任务 2.4：测试用例编写

**输入**：
- Page Object（`core/pages/specific/[模块名]_page.py`）
- 测试数据（`resources/data/[模块名]_data.yaml`）
- 测试用例设计指南（`.claude/testing_guidelines.md` 章节 三、测试用例实现规范）

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

**输出**：
- `tests/e2e/test_[模块名].py`

**⚠️ 完成本任务后停止执行，等待人工确认**


#### 任务 2.5：执行验证与报告生成

**输入**：
- 测试用例（`tests/e2e/test_[模块名].py`）
- 问题追踪文件（`output/testcases_docs/[模块名]_问题追踪.md`）

**流程**：
1. **执行测试**：
   - `pytest tests/e2e/test_[模块名].py --alluredir=reports/allure-results`
2. **结果验证**：
   - 分析测试结果
   - 修复失败用例（上限 3 次）
   - 记录问题到 `output/testcases_docs/[模块名]_问题追踪.md`
3. **生成报告**：
   - 生成 Allure 报告：`allure generate reports/allure-results -o reports/[模块名]_allure_report --clean`
   - 提取失败用例的根本原因分类
4. **知识沉淀**：
   - 创建 `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`

**质量检查点**：
- [ ] 测试通过率：是否达到 ≥95%
- [ ] 报告完整性：是否生成完整的 Allure 报告
- [ ] 问题记录：是否记录所有发现的问题
- [ ] 知识沉淀：是否创建最佳实践文档

**输出**：
- `reports/[模块名]_allure_report/`
- `output/testcases_docs/[模块名]_问题追踪.md`（更新）
- `output/testcases_docs/knowledge_base/[模块名]_最佳实践.md`

**⚠️ 完成本任务后停止执行，等待人工确认**


## 执行顺序

1. 阶段 1：PRD 分析与模块识别
2. 阶段 2：\[模块名 1] 测试
3. ...

## 质量目标

- **需求覆盖率**：100%
- **P0/P1 用例自动化率**：100%
- **测试通过率**：≥95%
- **性能指标**：核心页面加载时间 P0≤3s, P1≤5s, P2≤10s

## 风险评估

- **技术风险**：\[技术风险评估]
- **时间风险**：\[时间风险评估]
- **资源风险**：\[资源风险评估]

## 依赖项

- **外部依赖**：\[外部依赖项]
- **内部依赖**：\[内部依赖项]

## 备注

\[备注信息]
