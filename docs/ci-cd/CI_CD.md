# CI/CD 配置指南

本文档介绍如何在 CI/CD 环境中使用本框架。

## 目录

- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [最佳实践](#最佳实践)

## GitHub Actions

配置文件：`.github/workflows/test.yml`

### 功能特性

- 多 Python 版本（3.11/3.12）矩阵测试
- 多浏览器（Chromium/Firefox/WebKit）矩阵测试
- 定时任务（每天凌晨 2 点）
- 自动上传 Allure 报告、测试摘要、失败截图
- 代码覆盖率统计
- ~~自动部署 Allure 报告到 GitHub Pages~~（已改为 artifact 上传）

### 使用方法

1. 将代码推送到 GitHub
2. 配置完成后，每次推送都会自动触发测试

### 查看结果

- 测试报告：Actions > 工作流运行记录 > Artifacts
- Allure 报告：Actions > 工作流运行记录 > Artifacts > allure-report-html.zip（下载解压查看）

## GitLab CI

配置文件：`.gitlab-ci.yml`

### 功能特性

- 三阶段流水线（test → coverage → report）
- 并行矩阵测试
- 自动缓存依赖
- Pages 部署 Allure 和覆盖率报告

### 使用方法

1. 将代码推送到 GitLab
2. 在 CI/CD > Pipelines 中查看运行状态
3. 报告自动部署到 GitLab Pages

### 查看结果

- 测试报告：CI/CD > Pipelines > 运行记录 > Artifacts
- Allure 报告：https://your-username.gitlab.io/your-repo/

## Jenkins

配置文件：`Jenkinsfile`

### 功能特性

- 参数化构建（选择环境、浏览器、是否仅冒烟）
- 定时和轮询触发
- Allure 报告插件集成
- Cobertura 覆盖率报告
- 失败邮件通知

### 使用方法

1. 在 Jenkins 中创建 Pipeline 项目
2. 配置 Pipeline 脚本路径为 `Jenkinsfile`
3. 运行构建

### 参数说明

| 参数 | 说明 | 选项 |
|------|------|------|
| TEST_ENV | 测试环境 | testing, staging |
| TEST_BROWSER | 浏览器 | chromium, firefox, webkit |
| RUN_SMOKE_ONLY | 仅运行冒烟测试 | true, false |

**注意**：Jenkins 中使用 `TEST_BROWSER` 而不是 `BROWSER`，以避免与 pytest-playwright 冲突。

## 最佳实践

### 1. 环境变量配置

在 CI/CD 中设置必要的环境变量：

```bash
# 基础配置
BASE_URL=https://your-test-site.com
TEST_BROWSER=chromium  # 使用 TEST_BROWSER 而不是 BROWSER，避免与 pytest-playwright 冲突
HEADLESS=true

# 敏感信息（建议使用加密或 Secrets）
DB_PASSWORD=ENC:xxx
API_KEY=ENC:xxx
```

**重要提示**：
- ✅ **使用 `TEST_BROWSER` 环境变量**：避免被 pytest-playwright 的默认值覆盖
- ❌ **不要使用 `BROWSER`**：pytest-playwright 会设置其默认值（chromium），导致配置失效
- 🔧 **本地开发**：可以使用 `--browser` 命令行参数指定浏览器类型

### 2. 密钥管理

对于敏感信息，建议使用：

- **GitHub**: Settings > Secrets and variables > Actions
- **GitLab**: Settings > CI/CD > Variables
- **Jenkins**: Credentials 管理

### 3. 测试策略

```bash
# 快速反馈（PR 检查）
pytest -m smoke

# 完整测试（每日构建）
pytest -v --cov=core --cov-report=xml

# 特定环境测试
TEST_ENV=staging pytest -m regression

# 并行测试（注意：可能影响自定义报告收集）
pytest -n auto
```

**注意**：框架已完全支持并行测试，所有报告（包括自定义HTML/JSON报告）都能正确收集和合并测试结果。CI配置可根据需要启用并行测试以提高执行速度。

### 4. 报告归档

建议归档的报告：

- Allure 报告（HTML）
- 覆盖率报告（HTML/XML）
- 测试汇总（HTML/JSON）
- 失败截图（PNG）
- 录屏文件（WebM，如启用）

### 5. 通知配置

配置失败通知：

```groovy
// Jenkins 示例
emailext(
    subject: "构建失败: ${env.JOB_NAME}",
    body: "查看详情: ${env.BUILD_URL}",
    to: "team@example.com"
)
```

## 故障排除

### 浏览器安装失败

```bash
# 安装系统依赖
playwright install-deps

# 或使用 Docker 镜像
image: mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

### 内存不足

```bash
# 减少并行数
pytest -n 2

# 或禁用录屏
VIDEO_ENABLED=false pytest
```

### 超时问题

```bash
# 增加超时时间
pytest --timeout=300

# 或使用更长的默认超时
TIMEOUT=60000 pytest
```

### pytest 插件参数无法识别

**症状**：`pytest: error: unrecognized arguments: --html --cov`

**原因**：使用了 `-p no:warnings` 导致插件被禁用

**解决方案**：
```yaml
# 移除 -p no:warnings 参数
pytest tests/ -v --alluredir=allure-results
```

### CI 环境浏览器启动失败

**症状**：`Missing X server or $DISPLAY`

**原因**：CI 环境没有 XServer，但浏览器以 headed 模式启动

**解决方案**：
```yaml
# 确保设置 HEADLESS=true
env:
  HEADLESS: true
```

**conftest.py 已添加自动检测**：
```python
# CI 环境中强制使用 headless 模式
if os.getenv("CI", "false").lower() == "true" and not headless:
    headless = True
```

### PyPI 镜像源 403 错误

**症状**：`HTTP error 403 while getting https://pypi.tuna.tsinghua.edu.cn/...`

**原因**：清华源禁止了某些版本的下载

**解决方案**：
```bash
# 移除 requirements.lock 中的镜像源配置
# 使用官方 PyPI 源
--index-url https://pypi.org/simple
```
