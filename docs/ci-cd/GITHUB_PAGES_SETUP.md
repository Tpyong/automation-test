# GitHub Pages 配置指南

## 📋 功能说明

Allure 测试报告将自动部署到 GitHub Pages，可以通过浏览器访问：

```
https://<用户名>.github.io/<仓库名>/allure-report/
```

---

## 🚀 启用步骤

### 步骤 1：配置 GitHub Pages

1. **进入仓库设置**
   - 打开您的 GitHub 仓库
   - 点击 **Settings**（设置）

2. **配置 Pages**
   - 在左侧菜单点击 **Pages**
   - **Source** 选择：`Deploy from a branch`
   - **Branch** 选择：`gh-pages`
   - **Folder** 选择：`/ (root)`
   - 点击 **Save**

3. **等待配置生效**
   - GitHub 会创建一个 `gh-pages` 分支
   - 等待 1-2 分钟
   - 页面顶部会显示访问地址

---

### 步骤 2：验证配置

1. **查看 CI 运行**
   - 进入 **Actions** 标签
   - 查看最新的 CI 运行
   - 确认 `Deploy Allure Report` 任务成功

2. **访问报告**
   - 访问：`https://<用户名>.github.io/<仓库名>/allure-report/`
   - 例如：`https://tangp.github.io/automation-test/allure-report/`

---

## 📝 配置说明

### CI 配置（ci.yml）

```yaml
# 部署到 GitHub Pages
- name: Deploy to GitHub Pages
  if: github.ref == 'refs/heads/main' && success()
  uses: peaceiris/actions-gh-pages@v4
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: .
    destination_dir: allure-report
    keep_files: false
```

### 配置参数

| 参数 | 说明 | 当前值 |
|------|------|--------|
| **github_token** | GitHub 访问令牌 | 自动提供 |
| **publish_dir** | 要部署的目录 | `.` (当前目录) |
| **destination_dir** | 目标目录 | `allure-report` |
| **keep_files** | 保留旧文件 | `false` (每次覆盖) |

---

## 🎯 触发条件

### 自动部署

- ✅ **分支**: `main`
- ✅ **状态**: CI 测试成功 (`success()`)
- ✅ **时机**: 每次推送到 main 分支

### 手动部署（可选）

如果需要手动触发部署，可以在 GitHub Actions 页面：
1. 选择工作流
2. 点击 **Run workflow**
3. 选择分支
4. 点击 **Run workflow**

---

## 📊 访问地址

### 报告位置

部署成功后，可以通过以下地址访问：

1. **Allure 报告**
   ```
   https://<用户名>.github.io/<仓库名>/allure-report/
   ```

2. **示例地址**
   ```
   https://tangp.github.io/automation-test/allure-report/
   ```

---

## ⚠️ 注意事项

### 1. 首次部署

- 第一次部署可能需要 5-10 分钟
- GitHub 需要创建 `gh-pages` 分支
- 耐心等待 Pages 设置页面显示访问地址

### 2. 报告更新

- 每次 CI 运行成功后都会更新报告
- 旧报告会被覆盖 (`keep_files: false`)
- 可以通过 `gh-pages` 分支查看历史

### 3. 自定义域名（可选）

如果想使用自定义域名：
1. 在 **Settings → Pages → Custom domain** 输入域名
2. 在 DNS 提供商处配置 CNAME 记录

---

## 🔧 禁用部署

如果暂时不需要部署到 Pages，可以：

### 方法 1：注释掉部署步骤

```yaml
# 部署到 GitHub Pages
# - name: Deploy to GitHub Pages
#   if: github.ref == 'refs/heads/main' && success()
#   uses: peaceiris/actions-gh-pages@v4
#   ...
```

### 方法 2：修改触发条件

```yaml
if: false  # 永远不执行
```

### 方法 3：仅在特定分支部署

```yaml
if: github.ref == 'refs/heads/release' && success()
```

---

##  故障排查

### 问题 1：Pages 设置页面显示错误

**解决方案**：
1. 检查 `gh-pages` 分支是否存在
2. 查看 Actions 中的部署日志
3. 确认 `deploy-report` 任务成功

### 问题 2：访问地址 404

**解决方案**：
1. 等待 2-3 分钟（GitHub CDN 缓存）
2. 检查 URL 是否正确
3. 确认 `destination_dir: allure-report` 配置

### 问题 3：报告未更新

**解决方案**：
1. 检查 CI 是否成功运行
2. 查看 `deploy-report` 任务日志
3. 确认触发条件 `if: github.ref == 'refs/heads/main'`

---

## 📖 相关文档

- [GitHub Pages 官方文档](https://docs.github.com/en/pages)
- [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)
- [Allure 报告文档](https://docs.qameta.io/allure/)

---

## 🎁 高级用法

### 1. 保留历史报告

修改配置保留多个版本的报告：

```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v4
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: .
    destination_dir: allure-report-${{ github.run_number }}
    keep_files: true  # 保留旧文件
```

### 2. 仅在生产环境部署

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### 3. 添加部署通知

```yaml
- name: Notify deployment success
  if: success()
  run: |
    echo "✅ Allure report deployed to:"
    echo "https://$GITHUB_REPOSITORY_OWNER.github.io/$GITHUB_REPOSITORY/allure-report/"
```

---

## ✅ 检查清单

部署前确认：

- [ ] 已在 Settings → Pages 配置 `gh-pages` 分支
- [ ] 已保存 Pages 设置
- [ ] 等待 Pages 配置生效（1-2 分钟）
- [ ] CI 配置已包含 Deploy to GitHub Pages 步骤
- [ ] 推送到 main 分支触发新的 CI 运行

部署后验证：

- [ ] Actions 中 `deploy-report` 任务成功
- [ ] `gh-pages` 分支包含 `allure-report` 目录
- [ ] 可以通过浏览器访问报告
- [ ] 报告内容正确显示

---

## 🎉 完成！

配置完成后，每次 CI 运行成功都会自动部署 Allure 报告到 GitHub Pages！

访问地址：`https://<用户名>.github.io/<仓库名>/allure-report/`
