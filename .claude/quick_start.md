# 5 分钟快速上手（简版）

> **适用对象**：第一次使用本自动化测试体系  
> **预计时间**：5 分钟理解，10 分钟完成第一个任务

---

## 🎯 整体流程

```
阶段 0: PRD 分析 → module_list.md
  ↓
阶段 2-N: 循环执行模块 → 用例 + PO + 数据 + 报告
```

**核心原则**：
- ✅ 一个模块一个闭环
- ✅ 阶段 2 是模板，后续直接复制
- ✅ 遇到问题记录到 `[模块名]_问题追踪.md`
- ✅ 充分利用测试工具类简化代码

**基础框架状态**：⚠️ 基础框架已经搭建完成，包含项目结构、依赖安装、配置文件和测试工具类

**当前执行流程**：直接从 PRD 分析开始，然后进入功能模块测试

---

## 🚀 第一步：PRD 分析（3 分钟）

**输入**：`/PRD` 目录下的需求文档

**步骤**：
1. 读取所有 PRD 文档
2. 参考：`reference_rules/quality/module_list_template.md`
3. 生成：`output/testcases_docs/module_list.md`
4. 等待 `/compact` 确认

**输出示例**：
```markdown
| 序号 | 模块名称 | 复杂度 | 自动化建议 | 优先级 |
|------|---------|--------|-----------|--------|
| 1 | 用户登录 | 中 | ✅适合 | P0 |
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
- `pages/login_page.py`

### 任务 X.3：测试数据编写
**输出**：
- `data/login_data.yaml`

### 任务 X.4：测试用例编写
**输出**：
- `tests/unit/test_login.py`（单元测试）
- 或 `tests/e2e/test_login.py`（端到端测试）

### 任务 X.5：执行验证
**输出**：
- `reports/login_allure_report/`

---

## 🔍 核心文档速查

| 场景 | 文档 |
|------|------|
| 制定计划 | `plan/plan_create_principle.md` |
| 写用例 | `reference_rules/quality/common_case.md` |
| 写代码 | `reference_rules/quality/ui_code.md` |
| 模块分析 | `reference_rules/quality/module_list_template.md` |
| 文档修改 | `MODIFICATION_PLAN.md` |

---

## 💡 常见问题

**Q：如何知道当前做什么？**  
A：查看 `plan/plan_content_structure.md` 的对应阶段

**Q：遇到不会的问题？**  
A：记录到 `[模块名]_问题追踪.md` 的"遗留问题"章节并上报

**Q：如何判断质量？**  
A：参考简版自检（5 项核心确认）：
- [ ] 需求覆盖率 100%？
- [ ] 数据幂等性？
- [ ] 定位器稳定？
- [ ] 断言合理？
- [ ] 文档一致？

**Q：如何处理多浏览器测试？**  
A：测试框架支持 Chromium 和 Firefox 浏览器，执行时会自动在多个浏览器中运行测试

**Q：如何使用测试工具类？**  
A：充分利用 `tests/utils/` 下的工具类，如 VideoManager、AttachmentManager、ReportManager 来简化测试代码

---

## 🎉 成功标志

完成第一个模块后应该看到：
- ✅ `login_用例.md`
- ✅ `login_page.py`
- ✅ `login_data.yaml`
- ✅ `test_login.py`（在 tests/unit/ 或 tests/e2e/ 目录下）
- ✅ `login_allure_report/`
- ✅ `login_问题追踪.md`

**恭喜！接下来复制流程做下一个模块！** 🎊

---

**最后更新**：2026-04-08  
**文档版本**：v1.1（简版）
