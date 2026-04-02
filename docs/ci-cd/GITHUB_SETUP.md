# GitHub Actions 配置指南

本文档介绍如何配置 GitHub Actions 实现自动化测试。

## 目录

- [概述](#概述)
- [配置步骤](#配置步骤)
- [工作流说明](#工作流说明)
- [环境变量](#环境变量)
- [报告查看](#报告查看)
- [故障排除](#故障排除)

## 概述

GitHub Actions 工作流配置位于 `.github/workflows/test.yml`，包含以下功能：

- **多版本测试**：支持 Python 3.9、3.10、3.11、3.12
- **多浏览器测试**：支持 Chromium、Firefox、WebKit
- **代码质量检查**：pylint、flake8、black、isort
- **Allure 报告**：自动生成和发布测试报告
- **定时任务**：每天凌晨2点自动运行
- **失败通知**：测试失败时自动通知

## 配置步骤

### 1. 启用 GitHub Actions

1. 在 GitHub 仓库页面，点击 **Settings** 标签
2. 在左侧菜单选择 **Actions** > **General**
3. 确保 **Allow all actions and reusable workflows** 已选中

### 2. 配置 GitHub Pages

用于托管 Allure 测试报告：

1. 在 GitHub 仓库页面，点击 **Settings** 标签
2. 在左侧菜单选择 **Pages**
3. **Source** 选择 **Deploy from a branch**
4. **Branch** 选择 **gh-pages** 分支的 **/(root)** 目录
5. 点击 **Save**

### 3. 设置 Secrets（可选）

如果需要使用加密的敏感信息：

1. 在 GitHub 仓库页面，点击 **Settings** 标签
2. 在左侧菜单选择 **Secrets and variables** > **Actions**
3. 点击 **New repository secret**
4. 添加以下 secrets（根据项目需要）：
   - `TEST_USERNAME`: 测试账号用户名
   - `TEST_PASSWORD`: 测试账号密码
   - `API_KEY`: API 密钥
   - `ENCRYPTION_KEY`: 数据加密密钥

### 4. 推送配置

将工作流文件推送到 GitHub：

```bash
git add .github/workflows/test.yml
git commit -m "Add GitHub Actions workflow"
git push origin main
```

## 工作流说明

### 触发条件

工作流在以下情况触发：

1. **Push 到 main 或 develop 分支**
2. **Pull Request 到 main 或 develop 分支**
3. **定时任务**：每天凌晨2点（UTC）

### 任务说明

#### 1. Test 任务

- **矩阵策略**：Python 版本 × 浏览器类型（12种组合）
- **步骤**：
  1. 检出代码
  2. 设置 Python 环境
  3. 缓存 pip 包
  4. 安装依赖
  5. 安装 Playwright 浏览器
  6. 运行测试
  7. 上传测试结果

#### 2. Code Quality 任务

- **并行运行**：与 Test 任务同时进行
- **检查内容**：
  - pylint（代码质量，要求评分≥9.0）
  - flake8（代码风格）
  - black（代码格式化）
  - isort（导入排序）

#### 3. Allure Report 任务

- **依赖**：Test 任务完成后运行
- **功能**：
  1. 下载所有测试结果
  2. 合并 Allure 结果
  3. 生成 Allure 报告
  4. 部署到 GitHub Pages

#### 4. Notify 任务

- **条件**：测试失败时触发
- **功能**：在 PR 中发表评论通知

## 环境变量

工作流中设置的环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `TEST_ENV` | `testing` | 测试环境标识 |
| `HEADLESS` | `true` | 无头模式运行浏览器 |
| `TEST_BROWSER` | `${{ matrix.browser }}` | 浏览器类型（chromium/firefox/webkit） |

**重要提示**：
- ✅ **使用 `TEST_BROWSER`**：避免与 pytest-playwright 插件的默认值冲突
- ❌ **不要使用 `BROWSER`**：pytest-playwright 会覆盖这个环境变量

## 报告查看

### Allure 报告

测试完成后，Allure 报告作为 artifact 上传，需要手动下载查看：

1. 在工作流运行页面，滚动到 **Artifacts** 部分
2. 下载 `allure-report` 压缩包
3. 解压后在浏览器中打开 `index.html` 文件

### 工作流运行记录

1. 在 GitHub 仓库页面，点击 **Actions** 标签
2. 选择工作流运行记录
3. 查看详细的执行日志和结果

### 下载测试产物

1. 在工作流运行页面，滚动到 **Artifacts** 部分
2. 下载对应的测试结果压缩包

## 故障排除

### 常见问题

#### 1. Playwright 浏览器安装失败

**症状**：`playwright install` 步骤失败

**解决方案**：
```yaml
- name: Install Playwright browsers
  run: |
    playwright install --with-deps chromium
```

#### 2. 测试超时

**症状**：测试运行时间过长，导致超时

**解决方案**：
- 在 pytest.ini 中增加超时设置
- 减少测试矩阵的组合数量
- 优化测试用例执行时间

#### 3. Allure 报告未生成

**症状**：Allure 报告任务失败

**解决方案**：
- 检查 allure-results 目录是否正确生成
- 确保 pytest-allure-adaptor 已安装
- 检查 Allure 结果文件格式

#### 4. 代码质量检查失败

**症状**：Code Quality 任务失败

**解决方案**：
```bash
# 本地运行代码格式化
black core/ tests/
isort core/ tests/

# 本地运行代码检查
pylint core/ tests/
flake8 core/ tests/
```

### 调试技巧

1. **启用调试日志**：
   ```yaml
   - name: Run tests
     run: pytest tests/ -v --log-cli-level=DEBUG
   ```

2. **保留失败截图**：
   ```yaml
   - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots
          path: reports/screenshots/
   ```

3. **SSH 调试**（高级）：
   ```yaml
   - name: Setup tmate session
     if: failure()
     uses: mxschmitt/action-tmate@v3
   ```

## 自定义配置

### 修改测试矩阵

编辑 `.github/workflows/test.yml`：

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']  # 减少 Python 版本
    browser: [chromium]               # 只测试 Chromium
```

### 添加环境变量

```yaml
- name: Run tests
  run: pytest tests/ -v
  env:
    TEST_ENV: testing
    CUSTOM_VAR: custom_value
```

### 添加自定义步骤

```yaml
- name: Custom step
  run: |
    echo "Running custom commands"
    python custom_script.py
```

## 最佳实践

1. **使用缓存**：利用 actions/cache 加速依赖安装
2. **并行执行**：使用矩阵策略提高测试效率
3. **及时通知**：配置失败通知，快速响应问题
4. **定期运行**：使用定时任务确保代码质量
5. **版本锁定**：使用 requirements.lock 确保环境一致性

## 参考链接

- [GitHub Actions 文档](https://docs.github.com/cn/actions)
- [Playwright CI 配置](https://playwright.dev/python/docs/ci)
- [Allure Report Action](https://github.com/simple-elf/allure-report-action)
