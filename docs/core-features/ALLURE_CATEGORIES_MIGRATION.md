# Allure Categories 配置迁移指南

## 📋 变更概述

**问题**：原来的 `reports/allure-results/categories.json` 在每次测试执行时会被清空

**解决方案**：将配置文件移至 `config/` 目录，实现永久保存和自动复制

---

## 🎯 新的配置位置

### 主配置文件
```
config/categories.json  ← 永久保存，不会被清空
```

### 运行时文件（自动生成）
```
reports/allure-results/categories.json  ← 从 config/ 自动复制
```

---

## ✨ 新增功能

### 1️⃣ **自动复制机制**

框架现在会在测试启动时自动复制配置文件：

```python
# conftest.py 中的 _prepare_allure_categories() 函数
# 在 pytest_sessionstart 阶段自动执行
```

**日志输出示例**：
```
INFO - 已复制 Allure categories.json: config/categories.json -> reports/allure-results/categories.json
```

### 2️⃣ **便捷命令**

#### Makefile 命令
```bash
# 一键生成并打开 Allure 报告
make allure
```

#### 手动脚本
```bash
# 手动复制配置文件（可选）
python scripts/prepare_allure.py
```

---

## 🚀 使用方法

### 方式 1：直接运行测试（推荐）

```bash
pytest -v --alluredir=reports/allure-results
```

框架会自动：
1. ✅ 复制 `config/categories.json` 到 `reports/allure-results/`
2. ✅ 运行测试并收集结果
3. ✅ 生成包含分类的报告

### 方式 2：使用 Makefile

```bash
make allure
```

这个命令会：
1. ✅ 运行 `python scripts/prepare_allure.py`
2. ✅ 生成 Allure 报告
3. ✅ 自动打开浏览器查看报告

### 方式 3：分步执行

```bash
# 步骤 1：复制配置文件
python scripts/prepare_allure.py

# 步骤 2：运行测试
pytest -v --alluredir=reports/allure-results

# 步骤 3：生成报告
allure generate reports/allure-results -o reports/allure-report --clean

# 步骤 4：查看报告
allure open reports/allure-report
```

---

## 📁 文件结构对比

### ❌ 旧结构（已废弃）
```
reports/
└── allure-results/
    └── categories.json  ← 每次测试被清空，需要手动重新创建
```

### ✅ 新结构（推荐）
```
项目根目录/
├── config/
│   └── categories.json  ← 永久保存，版本控制友好
├── scripts/
│   └── prepare_allure.py  ← 自动复制工具
├── conftest.py  ← 集成自动复制逻辑
├── Makefile  ← 提供便捷命令
└── reports/
    └── allure-results/
        └── categories.json  ← 运行时自动生成
```

---

## 🔧 自定义配置

如需添加或修改缺陷分类，只需编辑：

```bash
# 编辑主配置文件
code config/categories.json
```

**示例：添加数据库相关类别**
```json
{
  "name": "数据库连接失败",
  "messageRegex": ".*DatabaseError.*|.*MySQL.*|.*connection refused.*",
  "matchedStatuses": ["broken"]
}
```

修改后会自动在下一次测试运行时生效。

---

## ✅ 优点总结

| 特性 | 旧方案 | 新方案 |
|------|--------|--------|
| 配置文件位置 | `reports/allure-results/` | `config/` |
| 是否会被清空 | ❌ 是 | ✅ 否 |
| 版本控制 | ❌ 忽略 | ✅ 跟踪 |
| 团队协作 | ❌ 容易丢失 | ✅ 易于共享 |
| 维护成本 | ❌ 需要手动处理 | ✅ 全自动 |
| 符合规范 | ❌ 临时文件目录 | ✅ 配置管理目录 |

---

## 🐛 故障排查

### 问题 1：类别仍然为空

**检查清单**：
1. ✅ `config/categories.json` 是否存在
2. ✅ JSON 格式是否正确
3. ✅ 运行日志中是否有 "已复制 Allure categories.json" 信息
4. ✅ `reports/allure-results/categories.json` 是否存在

**查看日志**：
```bash
pytest -v | grep "categories.json"
```

### 问题 2：复制失败

**可能原因**：
- 文件权限问题
- 目录不存在

**解决方案**：
```bash
# 手动运行复制脚本
python scripts/prepare_allure.py

# 检查错误信息
```

### 问题 3：CI/CD 环境

**GitHub Actions**：无需额外配置，框架会自动处理

**Jenkins/GitLab CI**：确保工作目录可写即可

---

## 📝 迁移步骤（如果从旧版本升级）

如果你之前在其他位置有 `categories.json`：

### 步骤 1：备份现有配置
```bash
cp reports/allure-results/categories.json config/categories.json.backup
```

### 步骤 2：复制到 config 目录
```bash
cp reports/allure-results/categories.json config/categories.json
```

### 步骤 3：验证格式
```bash
python -c "import json; json.load(open('config/categories.json'))"
```

### 步骤 4：运行测试验证
```bash
pytest tests/unit/test_sample.py -v
```

### 步骤 5：查看报告
```bash
allure open reports/allure-report
```

确认类别正常显示后，迁移完成！

---

## 📚 相关文档

- [Allure Categories 完整指南](ALLURE_CATEGORIES.md)
- [conftest.py 配置说明](../../conftest.py)
- [Makefile 使用指南](../../Makefile)

---

## 🎉 总结

新的配置管理方式：
- ✅ **更可靠**：配置文件不会被清空
- ✅ **更易用**：自动化处理，无需手动操作
- ✅ **更规范**：符合项目配置管理最佳实践
- ✅ **更友好**：提供多种使用方式和详细文档

立即体验：
```bash
make allure
```
