# Allure 报告配置指南

## 目录

- [Categories（缺陷分类）](#categories 缺陷分类)
- [配置方法](#配置方法)
- [示例配置](#示例配置)

---

## Categories（缺陷分类）

### 问题现象

如果你在 Allure 报告中看到"类别"是空的，这是因为需要手动创建 `categories.json` 配置文件。

### 什么是 Categories

Allure 的 Categories 功能用于：
- **自动分类缺陷**：根据错误信息自动将失败归类到不同的缺陷类别
- **缺陷分析**：帮助团队快速识别问题类型（自动化缺陷、元素未找到、网络问题等）
- **质量改进**：通过缺陷分布了解测试失败的主要原因

### 配置文件位置

**推荐位置**：`config/categories.json`

```
项目根目录/
├── config/
│   └── categories.json          # ← 缺陷分类配置（永久保存）
├── reports/
│   ├── allure-results/          # ← 测试执行时自动生成
│   │   └── categories.json      # ← 从 config/ 自动复制
│   └── allure-report/
```

**说明**：
- ✅ `config/categories.json` - 主配置文件，永久保存，不会被清空
- ✅ `reports/allure-results/categories.json` - 运行时自动复制，用于生成报告

---

## 配置方法

### 1. 创建 categories.json（一次性配置）

在 `config/` 目录下创建 `categories.json` 文件：

```bash
# 项目已提供默认配置，位于 config/categories.json
# 如需自定义，编辑此文件即可
```

**注意**：配置文件只需放在 `config/categories.json`，框架会自动处理复制工作。

### 2. 自动生成报告

测试执行时，框架会自动：
1. ✅ 从 `config/categories.json` 复制到 `reports/allure-results/`
2. ✅ 运行测试并收集结果
3. ✅ 生成包含分类的 Allure 报告

**使用命令**：
```bash
# 方式 1：直接运行测试（自动复制 categories.json）
pytest -v --alluredir=reports/allure-results

# 方式 2：使用 Makefile 命令
make allure

# 方式 3：手动复制后生成报告
python scripts/prepare_allure.py
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `name` | 类别名称 | ✅ | "自动化缺陷" |
| `messageRegex` | 匹配错误信息的正则表达式 | ✅ | `.*AssertionError.*` |
| `matchedStatuses` | 匹配的测试状态 | ✅ | `["failed", "broken"]` |

### 3. 重新生成报告

```bash
# 生成包含分类的报告
allure generate reports/allure-results -o reports/allure-report --clean

# 查看报告
allure open reports/allure-report
```

**注意**：每次运行测试后，`reports/allure-results/categories.json` 会自动从 `config/categories.json` 复制，无需手动操作。

---

## 查看 Categories 组件

### 在报告中找到 Categories

生成报告后，在 Allure 报告中查看：

1. **打开报告**
   ```bash
   allure open reports/allure-report
   ```

2. **左侧导航栏** → 点击 **"Categories"**（类别）

3. **查看内容**：
   - 缺陷分类列表（按匹配数量排序）
   - 每个分类下的失败测试用例
   - 每个测试的详细错误信息

### 常见问题排查

#### Q: 找不到 Categories 菜单？

**解决方法**：
1. ✅ 强制刷新浏览器：`Ctrl + Shift + R`
2. ✅ 确认报告已重新生成：`allure generate ... --clean`
3. ✅ 检查 `reports/allure-report/widgets/categories.json` 是否存在

#### Q: Categories 显示为空？

**检查清单**：
1. ✅ `config/categories.json` 是否存在
2. ✅ JSON 格式是否正确
3. ✅ 日志中是否有 "已复制 Allure categories.json" 信息
4. ✅ 测试失败信息是否匹配正则表达式

**查看日志**：
```bash
pytest -v | Select-String "categories.json"
```

#### Q: 如何优化类别匹配？

**A:** 
1. 查看实际的错误信息（在测试详情中）
2. 调整正则表达式使其更精确
3. 使用在线工具测试正则：[regex101.com](https://regex101.com/)
4. 添加更多相关类别

---

## 示例配置

### 项目默认配置

项目已提供默认的 `categories.json` 配置：

```json
[
  {
    "name": "自动化缺陷",
    "messageRegex": ".*AssertionError.*|.*assert.*|.*应该.*",
    "matchedStatuses": ["failed"]
  },
  {
    "name": "元素未找到",
    "messageRegex": ".*TimeoutError.*|.*ElementHandle.*|.*locator.*not found.*",
    "matchedStatuses": ["failed"]
  },
  {
    "name": "网络错误",
    "messageRegex": ".*NetworkError.*|.*ERR_.*|.*connection.*|.*timeout.*",
    "matchedStatuses": ["failed", "broken"]
  },
  {
    "name": "浏览器问题",
    "messageRegex": ".*browser.*|.*playwright.*|.*chromium.*|.*firefox.*|.*webkit.*",
    "matchedStatuses": ["failed", "broken"]
  },
  {
    "name": "测试数据问题",
    "messageRegex": ".*data.*|.*fixture.*|.*test data.*",
    "matchedStatuses": ["failed", "broken"]
  },
  {
    "name": "环境问题",
    "messageRegex": ".*environment.*|.*config.*|.*setup.*|.*teardown.*",
    "matchedStatuses": ["broken"]
  },
  {
    "name": "已知问题",
    "messageRegex": ".*TODO.*|.*FIXME.*|.*XXX.*",
    "matchedStatuses": ["failed", "broken", "skipped"]
  }
]
```

### 自定义配置示例

根据你的项目需求，可以添加更多类别：

```json
[
  {
    "name": "数据库连接失败",
    "messageRegex": ".*DatabaseError.*|.*MySQL.*|.*connection refused.*",
    "matchedStatuses": ["broken"]
  },
  {
    "name": "API 超时",
    "messageRegex": ".*504 Gateway Timeout.*|.*request timeout.*",
    "matchedStatuses": ["failed"]
  },
  {
    "name": "权限问题",
    "messageRegex": ".*403 Forbidden.*|.*permission denied.*|.*unauthorized.*",
    "matchedStatuses": ["failed"]
  }
]
```

---

## 正则表达式技巧

### 常用正则模式

| 模式 | 说明 | 示例 |
|------|------|------|
| `.*关键词.*` | 包含关键词 | `.*timeout.*` |
| `.*ERROR.*\|.*FAILED.*` | 匹配多个关键词 | `.*ERROR.*\|.*FAILED.*` |
| `^开始.*结束$` | 精确匹配整行 | `^AssertionError.*` |
| `.*\d+.*` | 包含数字 | `.*line \d+.*` |

### 正则表达式测试

建议使用在线工具测试正则表达式：
- [regex101.com](https://regex101.com/)
- [regexpal.com](https://www.regexpal.com/)

---

## 验证配置

### 1. 检查文件是否存在

```bash
# Windows PowerShell
Get-ChildItem reports\allure-results\categories.json

# Linux/Mac
ls reports/allure-results/categories.json
```

### 2. 验证 JSON 格式

```bash
# 使用 Python 验证
python -c "import json; json.load(open('reports/allure-results/categories.json'))"
```

### 3. 查看报告中的类别

生成报告后，在 Allure 报告中查看：
1. 打开 Allure 报告
2. 点击左侧菜单的 **"Categories"**（类别）
3. 应该能看到配置的缺陷分类

---

## 常见问题

### Q: 类别仍然是空的？

**A:** 检查以下几点：
1. ✅ `config/categories.json` 文件是否存在
2. ✅ JSON 格式是否正确
3. ✅ 测试运行时是否成功复制到 `reports/allure-results/`
4. ✅ 是否重新生成了报告（使用 `--clean` 参数）
5. ✅ 测试失败信息是否匹配正则表达式

**查看日志确认复制成功**：
```bash
pytest -v
# 查找日志中的 "已复制 Allure categories.json" 信息
```

---

## 最佳实践

### 配置管理

1. **保持简洁**：不要创建太多类别，5-7 个为宜
2. **定期更新**：根据实际失败原因调整类别
3. **团队共识**：确保团队成员理解每个类别的含义
4. **版本控制**：将 `config/categories.json` 纳入 Git 管理

### 使用技巧

| 场景 | 推荐操作 |
|------|----------|
| 日常开发 | `pytest -v` (自动处理) |
| 生成报告 | `make allure` (一键完成) |
| 调试问题 | 查看日志中的复制信息 |
| 自定义配置 | 编辑 `config/categories.json` |

---

## 参考资源

### 相关文档
- [Allure Categories 查看指南](ALLURE_CATEGORIES_VIEW_GUIDE.md) - 详细的报告查看和排查指南
- [Allure 官方文档 - Categories](https://docs.qameta.io/allure/#_categories)
- [Allure GitHub 示例](https://github.com/allure-examples)

### 项目文件
- [conftest.py](../../conftest.py) - 自动复制逻辑实现
- [Makefile](../../Makefile) - 便捷命令定义
- [config/categories.json](../../config/categories.json) - 默认配置示例
