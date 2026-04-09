# 5 分钟快速上手

> **适用对象**：第一次使用本自动化测试体系的 AI  
> **预计时间**：5 分钟理解，10 分钟完成第一个任务  
> **最后更新**：2026-04-09

---

## 🎯 整体流程

```
环境准备 → 阶段 1: PRD 分析 → module_list.md → 阶段 2-N: 循环执行模块 → 用例 + PO + 数据 + 报告
```

**核心原则**：
- ✅ 一个模块一个闭环
- ✅ 阶段 2 是模板，后续直接复制
- ✅ 遇到问题记录到 `[模块名]_问题追踪.md`
- ✅ 充分利用测试工具类简化代码
- ✅ 代码质量检查通过

**基础框架状态**：⚠️ 基础框架已经搭建完成，包含项目结构、依赖安装、配置文件和测试工具类

**当前执行流程**：先进行环境准备，然后从 PRD 分析开始，进入功能模块测试

---

## 🛠️ 环境准备（2 分钟）

**步骤**：
1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **配置环境**：
   ```bash
   # 复制基础环境配置文件
   cp config/envs/.env.base config/envs/.env
   
   # 编辑环境变量（根据实际情况修改）
   # BASE_URL=http://localhost:3000
   # TEST_BROWSER=chromium
   ```

3. **验证环境**：
   ```bash
   # 验证 pytest 安装
   pytest --version
   
   # 验证 playwright 安装
   playwright --version
   
   # 验证 allure 安装
   allure --version
   ```

4. **了解测试框架核心**：
   - `tests/conftest.py` 是项目 UI 测试的核心配置文件
   - 提供丰富的 fixture 和测试增强功能
   - 自动处理浏览器管理、视频录制、截图、报告生成等

---

## 🚀 第一步：PRD 分析（3 分钟）

**输入**：`/PRD` 目录下的需求文档

**步骤**：
1. 读取所有 PRD 文档
2. 参考：`templates/module_list.md`
3. 生成：`output/testcases_docs/module_list.md`
4. 等待 `/compact` 确认

**输出示例**：
```markdown
| 模块 ID | 模块名称 | 功能描述 | 优先级 | 复杂度 | 自动化建议 | 执行顺序 |
|---------|---------|---------|--------|--------|-----------|----------|
| MOD_001 | 用户登录 | 用户登录认证 | P0 | 低 | ✅适合 | 1 |
```

---

## 📝 第二步：执行第一个模块（7 分钟）

### 任务 X.1：页面分析与用例设计
**AI 自动执行**：
1. 打开页面，获取关键截图
2. 识别元素，整理困难元素清单
3. 六维场景分析（分级策略）
4. 编写用例表格
5. 记录 PRD 差异

**输出**：
- `output/testcases_docs/login_用例.md`
- `output/testcases_docs/login_问题追踪.md`
- `output/snapshots/login/`（截图）

### 任务 X.2：Page Object 编写
**参考**：
- login_用例.md
- login_元素定位临时清单.md
- login/ 截图

**输出**：
- `core/pages/specific/login_page.py`
- `resources/locators/login_page.yaml`

### 任务 X.3：测试数据编写
**输出**：
- `resources/data/login_data.yaml`

### 任务 X.4：测试用例编写
**输出**：
- `tests/e2e/test_login.py`

### 任务 X.5：执行验证
**输出**：
- `reports/login_allure_report/`
- `output/testcases_docs/knowledge_base/login_最佳实践.md`

---

## 🔍 核心文档速查

| 场景 | 文档 |
|------|------|
| AI 开发指南 | `CLAUDE.md` |
| 测试流程 | `testing_flow.md` |
| 写用例和代码 | `testing_guidelines.md` |
| 模块分析 | `templates/module_list.md` |
| 问题追踪 | `templates/problem_tracking.md` |
| 测试计划模板 | `templates/testing_plan_template.md` |
| 项目架构 | `docs/architecture/SYSTEM_ARCHITECTURE.md` |
| 开发规范 | `docs/development/DEVELOPMENT_GUIDELINES.md` |
| 功能特性 | `docs/core-features/FEATURES.md` |
| CI/CD 配置 | `docs/ci-cd/CI_CD.md` |
| 定位器使用指南 | `docs/best-practices/LOCATORS_GUIDE.md` |
| Playwright 使用指南 | `docs/best-practices/PLAYWRIGHT_GUIDE.md` |
| 目录结构 | `docs/best-practices/DIRECTORY_STRUCTURE.md` |

---

## 💡 常见问题与故障排除

**Q：如何知道当前做什么？**  
A：查看 `testing_flow.md` 的对应阶段

**Q：遇到不会的问题？**  
A：记录到 `[模块名]_问题追踪.md` 的"遗留问题"章节并上报

**Q：如何判断质量？**  
A：参考简版自检（5 项核心确认）：
- [ ] 需求覆盖率 100%？
- [ ] 数据幂等性？
- [ ] 定位器稳定？
- [ ] 断言合理？
- [ ] 文档一致？

**Q：如何使用测试工具类？**  
A：充分利用 `tests/utils/` 下的工具类，如 VideoManager、AttachmentManager、ReportManager 来简化测试代码

**Q：环境变量配置无效？**  
A：检查 `config/envs/.env` 文件是否正确配置，确保环境变量名称与 `config/settings.py` 中的一致

**Q：浏览器启动失败？**  
A：检查 Playwright 是否已正确安装，运行 `playwright install` 重新安装浏览器

**Q：Allure 报告生成失败？**  
A：检查 Allure 是否已正确安装，确保 `reports/allure-results` 目录存在且有测试结果

**Q：代码质量检查失败？**  
A：运行 `black core/ tests/ && isort core/ tests/ && flake8 core/ tests/` 自动修复代码风格

**Q：测试数据冲突？**  
A：使用动态数据生成，如 `at_user_{{random_alpha_8}}`，确保测试数据的唯一性

---

## 🎉 成功标志

完成第一个模块后应该看到：
- ✅ `login_用例.md`
- ✅ `login_page.py`（在 core/pages/specific/ 目录下）
- ✅ `login_page.yaml`（在 resources/locators/ 目录下）
- ✅ `login_data.yaml`（在 resources/data/ 目录下）
- ✅ `test_login.py`（在 tests/e2e/ 目录下）
- ✅ `login_allure_report/`
- ✅ `login_问题追踪.md`
- ✅ `login_最佳实践.md`（在 output/testcases_docs/knowledge_base/ 目录下）

**恭喜！接下来复制流程做下一个模块！** 🎊

---

**最后更新**：2026-04-09  
**文档版本**：v1.5（简版）