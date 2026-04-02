# CI/CD Pipeline 故障排查指南

本文档记录了 CI/CD Pipeline 常见问题及解决方案。

## 目录

- [pytest 插件参数无法识别](#pytest-插件参数无法识别)
- [CI 环境浏览器启动失败](#ci-环境浏览器启动失败)
- [PyPI 镜像源 403 错误](#pypi-镜像源 403 错误)
- [Docker Build 失败](#docker-build-失败)
- [Allure Report 部署失败](#allure-report-部署失败)
- [GitHub Pages 启用检查失败](#github-pages-启用检查失败)

---

## pytest 插件参数无法识别

### 症状

```
pytest: error: unrecognized arguments: --html=reports/report.html --self-contained-html --cov=core
```

### 原因

使用了 `-p no:warnings` 参数导致 pytest 插件被禁用，包括：
- `pytest-html`（生成 HTML 报告）
- `pytest-cov`（代码覆盖率）
- 其他第三方插件

### 解决方案

**修改前**（错误）：
```yaml
- name: Run tests
  run: |
    pytest tests/ -v --alluredir=allure-results -p no:warnings
```

**修改后**（正确）：
```yaml
- name: Run tests
  run: |
    pytest tests/ -v --alluredir=allure-results
```

### 验证

运行 pytest 时应该能看到插件正常加载：
```bash
pytest --version
pytest --help | grep -E "(html|cov|allure)"
```

---

## CI 环境浏览器启动失败

### 症状

```
Looks like you launched a headed browser without having a XServer running.
Set either 'headless: true' or use 'xvfb-run <your-playwright-app>' before running Playwright.
[pwd=3221][err] Missing X server or $DISPLAY
```

### 原因

CI 环境（GitHub Actions、GitLab CI 等）没有 XServer 图形界面，但浏览器以 headed（有界面）模式启动。

### 解决方案

#### 方案 1：环境变量配置

确保在 CI 配置中设置：
```yaml
env:
  HEADLESS: true
```

#### 方案 2：conftest.py 自动检测（推荐）

conftest.py 已添加智能检测和强制修正：

```python
# 强制确保在 CI 环境中使用 headless 模式
if os.getenv("CI", "false").lower() == "true" and not headless:
    logger.warning("CI 环境中检测到 HEADLESS=false，强制设置为 true")
    headless = True
```

#### 方案 3：使用 xvfb-run（不推荐）

```yaml
- name: Run tests
  run: |
    xvfb-run pytest tests/ -v
```

### 验证

查看日志确认 headless 模式：
```
HEADLESS 环境变量：true
解析后的 headless 值：True
最终选择的浏览器类型：chromium, headless: True
```

---

## PyPI 镜像源 403 错误

### 症状

```
ERROR: HTTP error 403 while getting https://pypi.tuna.tsinghua.edu.cn/packages/...
ERROR: Could not install requirement allure-pytest==2.15.3
```

### 原因

清华源（pypi.tuna.tsinghua.edu.cn）禁止了某些版本的下载，或镜像策略调整。

### 解决方案

#### 方案 1：移除 lock 文件中的镜像源配置

**修改前**（requirements.lock）：
```
--index-url https://pypi.tuna.tsinghua.edu.cn/simple
--trusted-host pypi.tuna.tsinghua.edu.cn

allure-pytest==2.15.3
```

**修改后**（requirements.lock）：
```
allure-pytest==2.15.3
```

#### 方案 2：CI 中使用官方源

```yaml
- name: Install dependencies
  run: |
    pip install --index-url https://pypi.org/simple -r requirements.lock
```

### 验证

依赖安装应该成功：
```
Collecting allure-pytest==2.15.3
  Downloading allure_pytest-2.15.3-py3-none-any.whl
Successfully installed allure-pytest-2.15.3
```

---

## Docker Build 失败

### 症状

```
ERROR: failed to calculate checksum of ref ...: "/requirements.txt": not found
```

### 原因

Dockerfile 中尝试复制不存在的文件。

### 解决方案

**修改前**（Dockerfile）：
```dockerfile
COPY requirements.txt requirements.lock ./
RUN pip install -r requirements.lock
```

**修改后**（Dockerfile）：
```dockerfile
COPY requirements.in requirements.lock ./
RUN pip install -r requirements.in
```

### 验证

Docker 构建应该成功：
```bash
docker build -t automation-test:latest .
```

---

## Allure Report 部署失败

### 症状 1：路径重复

```
cp: cannot stat 'artifacts/artifacts/allure-report-firefox-3.11/*': No such file or directory
```

### 原因

artifacts 下载后目录结构为 `artifacts/allure-report-{browser}-{version}/`，脚本中路径重复。

### 解决方案

**修改前**：
```yaml
- name: Find latest Allure report
  run: |
    cp -r "artifacts/$LATEST_REPORT"/* .
```

**修改后**：
```yaml
- name: Find latest Allure report
  run: |
    cd artifacts
    REPORT_DIRS=$(find . -name "allure-report-*" -type d | sed 's|^\./||')
    LATEST_REPORT=$(echo "$REPORT_DIRS" | sort | tail -1)
    cp -r "$LATEST_REPORT"/* ..
    cd ..
```

### 症状 2：GitHub Pages 未启用

```
Error: Get Pages site failed. Please verify that the repository has Pages enabled
```

### 解决方案

**方案 1：改用 artifact 上传（推荐）**

```yaml
- name: Upload Allure report as artifact
  uses: actions/upload-artifact@v4
  with:
    name: allure-report-html
    path: .
    retention-days: 30
```

**方案 2：启用 GitHub Pages**

1. Settings > Pages
2. Source: Deploy from a branch
3. Branch: gh-pages / (root)

### 验证

- artifact 应该成功上传
- 可在 GitHub Actions 页面下载 `allure-report-html.zip`

---

## GitHub Pages 启用检查失败

### 症状

```
Error: Get Pages site failed. Please verify that the repository has Pages enabled and configured to build using GitHub Actions
```

### 原因

GitHub Pages 功能需要在仓库设置中手动启用，且需要相应权限。

### 解决方案

#### 方案 1：跳过 Pages 启用检查（不推荐）

```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4
  with:
    enablement: false
```

#### 方案 2：改用 artifact 上传（推荐）

完全移除 Pages 部署，改用普通 artifact：

```yaml
- name: Upload Allure report as artifact
  uses: actions/upload-artifact@v4
  with:
    name: allure-report-html
    path: .
    retention-days: 30
```

### 优缺点对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| GitHub Pages | 永久在线，可直接访问 URL | 需要手动启用，配置复杂 |
| Artifact 上传 | 无需 Pages 权限，配置简单 | 需要手动下载，保留 30 天 |

### 推荐方案

**推荐使用 Artifact 上传**，原因：
1. 无需额外配置
2. 降低权限要求
3. 减少 CI/CD 复杂度
4. 报告仍可方便查看

---

## 完整修复历史

| 日期 | 问题 | 修复内容 |
|------|------|---------|
| 2026-04-02 | pytest 插件参数无法识别 | 移除 `-p no:warnings` |
| 2026-04-02 | CI 环境浏览器启动失败 | 强制 headless=true + 自动检测 |
| 2026-04-02 | PyPI 镜像源 403 错误 | 移除清华源，使用官方源 |
| 2026-04-02 | Docker Build 失败 | 使用 requirements.in |
| 2026-04-02 | Allure Report 部署失败 | 改用 artifact 上传 |
| 2026-04-02 | GitHub Pages 启用检查 | 移除 Pages 部署 |

---

## 调试技巧

### 1. 启用详细日志

```yaml
- name: Run tests
  run: pytest tests/ -v --log-cli-level=DEBUG
```

### 2. 添加调试信息

```yaml
- name: Debug info
  run: |
    echo "TEST_BROWSER: $TEST_BROWSER"
    echo "HEADLESS: $HEADLESS"
    echo "CI: $CI"
```

### 3. 查看 artifact 内容

```yaml
- name: List artifacts
  run: |
    ls -la artifacts/
    find artifacts/ -type f
```

### 4. 使用 SSH 调试（高级）

```yaml
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
```

---

## 参考资源

- [GitHub Actions 文档](https://docs.github.com/cn/actions)
- [Playwright CI 配置](https://playwright.dev/python/docs/ci)
- [pytest 插件系统](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)
- [Allure Report 配置](https://docs.qameta.io/allure/)
