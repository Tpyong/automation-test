# 自动化测试指南

> **最后更新**：2026-04-08
> **目的**：提供统一的测试用例编写和代码规范指南

---

## 一、测试用例编写规范

### 1. 从需求到用例的转化流程

```
PRD需求文档
    ↓ ① 需求拆解 → 功能模块清单（按页面/业务域划分）
    ↓ ② 页面结构分析 → 打开页面，设置视口为 1920x1080，获取关键页面截图；识别所有交互元素（包括动态元素），对动态元素触发显示后获取快照，提取元素定位器
    ↓ ③ 交互行为探索 → 模拟用户交互，观察反馈，抓取网络请求；对比 PRD 与实际实现，记录差异
    ↓ ④ 场景分析 → 六维场景分析（分级策略：核心功能全覆盖，一般功能正向 + 负向 + 边界，简单功能正向为主）
    ↓ ⑤ 用例设计 → 用例表格（Markdown）+ 测试数据（YAML）+ 需求追溯矩阵（RTM）+ 备注章节（记录 PRD 与实际差异、自动化限制、环境限制）
    ↓ ⑥ 自动化实现 → Page Object + 测试代码
    ↓ ⑦ 持续维护 → 需求变更时同步更新用例、数据和代码 + 变更影响分析
```

### 2. 场景分析方法（六维定义）

| 维度 | 定义 | 示例（以登录功能为例） |
|------|------|---------------------|
| **正向** | 符合业务规则的正常流程，验证功能按预期工作 | 正确的用户名 + 密码登录成功，跳转首页 |
| **负向** | 不符合业务规则的输入或操作，验证系统拒绝处理并给出提示 | 错误密码、未注册账号、账号被锁定、用户名不存在 |
| **边界** | 输入参数的临界值，验证边界处理正确性 | 密码长度最小值（6 位）、最大值（20 位）、超长（21 位）、用户名特殊字符 |
| **异常** | 系统异常状态或非预期操作，验证容错能力 | 网络中断、服务超时、并发登录、Session 过期 |
| **安全** | 验证安全机制有效性，防止攻击和数据泄露 | SQL 注入、XSS 攻击、密码明文传输、暴力破解防护、越权访问、会话劫持、CSRF token 校验 |
| **性能** | 验证响应时间和资源占用在可接受范围内 | 页面加载速度、并发性能 |

### 3. 优先级划分标准（P0-P4）

| 优先级 | 含义 | 测试用例示例 | Allure 严重级别 | 自动化建议 | 标签自动分配 |
|-------|------|------------|--------------|-----------|----------------|
| **P0** | 核心流程，阻塞性功能 | 登录功能、核心业务流程的正向场景 | BLOCKER | 强烈推荐自动化，纳入冒烟测试 | `smoke` + `regression` |
| **P1** | 重要功能，高频使用 | 主要功能的正向场景、核心功能的负向场景 | CRITICAL | 推荐自动化，纳入回归测试 | `regression` |
| **P2** | 一般功能，常规场景 | 主要功能的异常/边界场景、次要功能的正向场景 | NORMAL | 可选自动化 | - |
| **P3** | 边缘场景，低频操作 | 次要功能的异常场景、UI 交互优化验证 | MINOR | 一般不自动化，手工覆盖 | - |
| **P4** | UI 细节，文案校验 | 兼容性测试、性能优化验证、提示文案优化 | TRIVIAL | 通常不自动化 | - |

### 4. 用例表格规范

#### 核心字段定义

| 字段名   | 必填 | 说明                          | 示例                           |
| -------- | ---- | ----------------------------- | ------------------------------ |
| 用例ID   | ✅    | 全局唯一标识，格式：模块_序号 | LOGIN_001                      |
| 用例标题 | ✅    | 简明描述测试场景              | 正确账号密码登录成功           |
| 优先级   | ✅    | P0/P1/P2/P3/P4                | P0                             |
| 用例类型 | ✅    | 正向/负向/边界/异常/安全/性能 | 正向                           |
| 前置条件 | ❌    | 执行前需满足的条件            | 已注册账号                     |
| 测试步骤 | ✅    | 操作步骤，用 `<br>` 换行      | 1.打开登录页<br>2.输入账号密码 |
| 测试数据 | ✅    | 输入数据，格式：字段=值       | user=admin, pwd=123            |
| 预期结果 | ✅    | 可验证的预期行为              | 跳转到/dashboard               |
| 自动化   | ✅    | ✅是 / ❌否 / 🔄进行中           | ✅                              |
| 关联需求 | ✅    | PRD需求编号                  | PRD-AUTH-001                   |
| 备注     | ❌    | 特殊说明                      | 纳入冒烟测试                   |

#### 用例文档模板

```markdown
# [模块名称] - 测试用例

| 项目 | 内容 |
|------|------|
| **模块名称** | XXX模块 |
| **PRD需求** | PRD-XXX-001 |
| **负责人** | 测试团队 |
| **创建日期** | YYYY-MM-DD |
| **版本号** | v1.0 |
| **用例总数** | 0 |
| **自动化覆盖** | 0/0 (0%) |

## 场景矩阵

## 用例统计

| 类型 | 数量 | 自动化 | 手工 |
|------|------|--------|------|
| 正向 | 0 | 0 | 0 |

## 用例列表

| 用例ID | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 测试数据 | 预期结果 | 自动化 | 关联需求 | 备注 |
|--------|---------|--------|------|---------|---------|---------|---------|--------|---------|------|
| MOD_001 | | P0 | 正向 | | | | | ✅ | | |

## 备注

### 其它
1. **[功能名称]**：具体场景说明，自动化限制原因，标记为手工测试
2. **[功能名称]**：环境或数据限制说明，当前状态

---

## 附录：需求追溯矩阵（RTM）

| 需求 ID | 需求描述 | 对应用例 ID | 测试状态 | 自动化状态 | 最后更新时间 |
|---------|---------|------------|---------|-----------|-------------|
| PRD-AUTH-001 | 用户登录功能：支持账号密码登录，登录成功后跳转首页 | LOGIN_001~010 | ⏳未执行 | 🔄进行中 | 2026-04-08 |

**图例说明**：
- 测试状态：✅通过 / ❌失败 / ⏳未执行 / ⚠️部分通过
- 自动化状态：✅已覆盖 / 🔄进行中 / ❌不自动化（需备注原因）

### 需求覆盖统计

| 需求 ID | 用例总数 | 已通过 | 已自动化 | 覆盖率 | 状态评估 |
|---------|---------|--------|---------|--------|---------|
| PRD-AUTH-001 | 10 | 0 | 8 | 80% | ⚠️ 部分覆盖（缺少安全场景） |
| **总计** | 10 | 0 | 8 | 80% | - |

### 未覆盖需求说明

| 需求 ID | 未覆盖原因 | 计划解决时间 | 责任人 |
|---------|-----------|-------------|--------|
| PRD-XXX-001 | 功能暂未实现（PRD 中标记为“二期规划”） | 待定 | AI 标记 |
```

### 5. 测试数据设计规范

- **数据隔离**：名称类字段使用 `at_` 前缀区分测试数据（如 `at_客户A`、`at_部门1`）
- **数据幂等性**：确保测试可重复执行，避免数据冲突
  - **动态数据（推荐）**：根据字段约束生成唯一数据，确保符合格式和长度要求
    - 纯字母字段（如用户名只能字母，6-20位）：`at_user_{{random_alpha_8}}`（固定前缀+8位随机字母）
    - 数字字段（如工号，6位）：`{{random_6digits}}` 或 `{{timestamp_6}}`（截取时间戳后6位）
    - 混合字段（字母+数字，无长度限制）：`at_用户_{{timestamp}}` 或 `at_用户_{{random}}`
    - 邮箱字段：`at_test_{{timestamp}}@example.com`
    - 手机号字段（11位）：`138{{random_8digits}}`（固定前缀+8位随机数字）
    - 日期字段：使用当前日期或相对日期（如 `{{today}}`、`{{tomorrow}}`）
  - **前置清理**：测试前先删除可能存在的测试数据（适用于必须使用固定名称的场景）
  - **检查后创建**：先检查数据是否存在，不存在才创建（适用于幂等性要求高的场景）
- **前置数据**：优先通过 UI 创建（验证功能）；禁止依赖其他用例的操作结果作为前置条件
- **数据清理**：暂无需考虑（测试团队拥有测试环境主导权，可随时手动还原数据库）
- **数据覆盖**：确保测试数据覆盖六维场景（正向、负向、边界、异常、安全、性能）

#### 测试数据文件结构

```yaml
# data/[模块名]_data.yaml

metadata:
  generated_by: AI              # 固定为 AI
  module: [模块名称]             # 所属功能模块
  version: "1.0"                # 版本号（手动维护）
  last_updated: "2026-04-08"    # 最后更新日期
  author: "tester_name"         # 作者/责任人

# 每条数据对应一个参数化用例
- case_id: LOGIN_001
  title: 正确账号密码登录成功
  priority: P0
  precondition: 用户已注册
  tags: ["smoke", "regression"]  # AI 自动分配：P0=smoke+regression, P1=regression
  performance_requirement: ≤3s  # 性能要求：P0≤3s, P1≤5s, P2≤10s
  estimated_duration: 30  # 预估执行时长 (秒)
  input:
    username: at_testuser_{{random_alpha_8}}
    password: Test123!
  expect:
    success: true
    redirect_url: /dashboard
    message: 登录成功
  remark: 核心冒烟用例

- case_id: LOGIN_002
  title: 密码错误登录失败
  priority: P1
  precondition: 用户已注册
  tags: ["regression"]
  estimated_duration: 20
  input:
    username: testuser
    password: wrong_password
  expect:
    success: false
    message: 密码错误
  remark: 负向场景
```

## 二、Page Object 编写规范

### 1. 页面类结构

```python
# pages/base_page.py
class BasePage:
    def __init__(self, page):
        self.page = page

    def navigate(self, url):
        self.page.goto(url)

    def click(self, locator):
        self.page.click(locator)

    def fill(self, locator, value):
        self.page.fill(locator, value)

    def get_text(self, locator):
        return self.page.text_content(locator)

# pages/login_page.py
class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username_input = page.get_by_label("用户名")
        self.password_input = page.get_by_label("密码")
        self.login_button = page.get_by_role("button", name="登录")
        self.error_message = page.get_by_text("错误信息")

    def login(self, username, password):
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def get_error_message(self):
        return self.get_text(self.error_message)
```

### 2. 元素定位优先级

1. **getByRole()**：语义化定位，最稳定
2. **getByLabel()**：标签定位，适合表单元素
3. **getByPlaceholder()**：占位符定位，适合输入框
4. **getByText()**：文本定位，适合按钮和链接
5. **getByTestId()**：测试 ID 定位，适合自定义元素
6. **CSS 选择器**：仅当以上方法都无法定位时使用
7. **XPath**：仅当以上方法都无法定位时使用

### 3. 编码规范

- **行数限制**：Page Object ≤300 行、测试文件 ≤500 行、方法 ≤50 行
- **命名规范**：
  - 类名：使用驼峰命名法（如 `LoginPage`）
  - 方法名：使用小写字母 + 下划线（如 `login`）
  - 变量名：使用小写字母 + 下划线（如 `username_input`）
- **注释规范**：
  - 类和方法添加文档字符串
  - CSS/XPath 定位器添加注释说明原因
  - 关键操作添加注释说明

## 三、测试用例编写规范

### 1. 测试文件结构

```python
# tests/unit/test_login.py
import pytest
import allure
from pages.login_page import LoginPage
from utils.common.data_loader import load_test_data

@allure.feature("登录功能")
class TestLogin:
    @pytest.mark.parametrize("test_data", load_test_data("login_data.yaml"))
    def test_login(self, page, test_data):
        """登录测试"""
        login_page = LoginPage(page)
        
        # 执行登录操作
        login_page.login(test_data["input"]["username"], test_data["input"]["password"])
        
        # 验证结果
        if test_data["expect"]["success"]:
            # 验证登录成功
            page.wait_for_url(test_data["expect"]["redirect_url"])
            assert page.url == test_data["expect"]["redirect_url"]
        else:
            # 验证登录失败
            error_message = login_page.get_error_message()
            assert test_data["expect"]["message"] in error_message

    @allure.story("登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, page):
        """测试登录成功场景"""
        login_page = LoginPage(page)
        login_page.login("admin", "password")
        page.wait_for_url("/dashboard")
        assert page.url == "https://example.com/dashboard"

    @allure.story("登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_failure(self, page):
        """测试登录失败场景"""
        login_page = LoginPage(page)
        login_page.login("admin", "wrong_password")
        error_message = login_page.get_error_message()
        assert "密码错误" in error_message
```

### 2. 测试工具类使用

```python
# 导入测试工具类
from tests.utils.video_manager import VideoManager
from tests.utils.attachment_manager import AttachmentManager
from tests.utils.report_manager import ReportManager

# 使用 VideoManager
video_manager = VideoManager()
video_path = video_manager.find_video_file(video_dir, test_name)

# 使用 AttachmentManager
attachment_manager = AttachmentManager()
attachment_manager.attach_screenshot(page, test_name, "测试截图")
attachment_manager.attach_video(video_path, test_name, "测试视频")

# 使用 ReportManager
report_manager = ReportManager()
report_manager.add_result(test_id, "passed", duration, None)
reports = report_manager.finalize(exitstatus)
```

### 3. 多浏览器测试

```python
# 在测试文件中使用多浏览器测试
@pytest.mark.parametrize("browser", ["chromium", "firefox"])
def test_login(browser, page):
    """多浏览器登录测试"""
    login_page = LoginPage(page)
    login_page.login("admin", "password")
    page.wait_for_url("/dashboard")
    assert page.url == "https://example.com/dashboard"
```

## 四、执行验证规范

### 1. 测试执行命令

- **执行单个模块测试**：
  ```bash
  pytest tests/unit/test_login.py --alluredir=reports/allure-results
  ```

- **执行多浏览器测试**：
  ```bash
  pytest tests/unit/test_login.py --alluredir=reports/allure-results --browser chromium,firefox
  ```

- **生成 Allure 报告**：
  ```bash
  allure generate reports/allure-results -o reports/login_allure_report --clean
  ```

### 2. 测试结果分析

- **查看测试报告**：打开 `reports/login_allure_report/index.html`
- **分析失败原因**：查看 Allure 报告中的失败用例详情
- **记录问题**：将失败原因记录到 `output/testcases_docs/login_问题追踪.md`
- **修复问题**：根据失败原因修复测试代码或测试数据
- **重新执行**：修复后重新执行测试，验证修复效果

### 3. 质量评估

- **需求覆盖率**：确保所有 PRD 需求都有对应的测试用例
- **测试通过率**：目标通过率 ≥95%
- **自动化率**：P0/P1 用例自动化率 100%
- **多浏览器兼容性**：确保测试在 Chromium 和 Firefox 中都能正常运行
- **性能指标**：核心页面加载时间 P0≤3s, P1≤5s, P2≤10s

## 五、最佳实践

1. **模块化设计**：将测试代码分解为小的、可管理的模块
2. **数据驱动**：使用 YAML 文件管理测试数据，提高测试数据的可维护性
3. **Page Object 模式**：使用 Page Object 模式封装页面操作，提高代码的可维护性和可重用性
4. **测试工具类**：充分利用测试工具类来简化测试代码，提高测试代码的可读性和可维护性
5. **多浏览器测试**：确保测试在不同浏览器中都能正常运行，提高测试的覆盖率
6. **性能测试**：为核心功能添加性能断言，确保系统性能符合要求
7. **问题追踪**：及时记录和追踪测试过程中发现的问题，确保问题得到及时解决
8. **知识沉淀**：将测试过程中的经验和解决方案沉淀到知识库中，供后续参考

## 六、常见问题及解决方案

### 1. 元素定位失败
- **解决方案**：按优先级尝试不同的定位方法，使用语义化定位器
- **最佳实践**：优先使用 getByRole()、getByLabel() 等语义化定位器

### 2. 测试数据冲突
- **解决方案**：使用动态数据生成，确保测试数据的唯一性
- **最佳实践**：使用 `at_` 前缀和动态数据生成方法

### 3. 测试执行不稳定
- **解决方案**：添加适当的等待时间，使用显式等待
- **最佳实践**：使用 `page.wait_for_selector()` 等显式等待方法

### 4. 多浏览器兼容性问题
- **解决方案**：针对不同浏览器使用不同的定位器或操作方法
- **最佳实践**：在测试中添加浏览器特定的处理逻辑

### 5. 性能问题
- **解决方案**：优化测试代码，减少不必要的操作
- **最佳实践**：使用性能断言，监控页面加载时间