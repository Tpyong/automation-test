# 文档体系导航（简版）

> **用途**：快速找到需要的文档  
> **适用对象**：AI、测试工程师

---

## 🎯 按场景查找

### 我是新手
→ [`quick_start.md`](quick_start.md) - 5 分钟快速上手

### 我要制定计划
→ [`testing_plan.md`](testing_plan.md) - 自动化测试计划

### 我要写用例
→ [`testing_guidelines.md`](testing_guidelines.md) - 测试用例编写和代码规范指南

### 我遇到问题
→ 参考 `testing_plan.md` 中对应阶段的任务描述

### 我要了解优化历史
→ 优化过程文档已精简，如需了解请查阅 Git 提交历史

---

## 📁 核心规范（必读）⭐

| 文件 | 用途 |
|------|------|
| [`CLAUDE.md`](CLAUDE.md) | 顶层指导（AI 必读） |
| [`testing_plan.md`](testing_plan.md) | 自动化测试计划（AI 必读） |
| [`testing_guidelines.md`](testing_guidelines.md) | 测试用例编写和代码规范指南（AI 必读） |

---

## 📋 模板文件（使用时参考）

| 文件 | 用途 |
|------|------|
| [`templates/module_list.md`](templates/module_list.md) | 功能模块清单 |
| [`templates/problem_tracking.md`](templates/problem_tracking.md) | 问题追踪模板 |

---

## 📖 人类专用指南（可选）

| 文件 | 用途 |
|------|------|
| [`quick_start.md`](quick_start.md) | 新手快速入门 |
| [`README.md`](README.md) | 文档导航 |
| [`MODIFICATION_PLAN.md`](MODIFICATION_PLAN.md) | 文档修改计划 |

---

## 🗂️ 目录结构

```
.claude/ (6 个核心文件 + 1 个子目录)
│
├── CLAUDE.md                     # AI 必读：顶层指导 ⭐⭐⭐
├── README.md                     # 人类专用：文档导航
├── quick_start.md                # 人类专用：新手入门
├── testing_plan.md               # AI 必读：自动化测试计划 ⭐⭐⭐
├── testing_guidelines.md         # AI 必读：测试用例编写和代码规范指南 ⭐⭐⭐
├── MODIFICATION_PLAN.md          # 文档修改计划
│
└── templates/ (2 个）
    ├── module_list.md            # 功能模块清单模板
    └── problem_tracking.md       # 问题追踪模板
```

---

**最后更新**：2026-04-08  
**文档版本**：v1.2（简版）
