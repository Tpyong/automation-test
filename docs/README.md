# 测试框架文档

本文档是测试框架的导航中心，包含框架的所有文档资源。

## 文档结构

### 入门指南
- [快速开始](getting-started/README.md) - 框架的快速入门指南
- [完整使用指南](getting-started/GUIDE.md) - 框架的详细使用指南

### 核心功能
- [功能特性](core-features/FEATURES.md) - 框架的各项功能特性

### CI/CD 配置
- [CI/CD 配置指南](ci-cd/CI_CD.md) - 各平台 CI/CD 配置指南
- [GitHub Actions 配置](ci-cd/GITHUB_SETUP.md) - GitHub Actions 详细配置指南

### 最佳实践
- [定位器使用指南](best-practices/LOCATORS_GUIDE.md) - 元素定位器的最佳使用实践

### 参考文档
- [API 参考](reference/API.md) - 框架 API 参考文档（待更新）
- [配置参考](reference/CONFIG.md) - 框架配置参考文档（待更新）

## 框架概述

本测试框架基于以下技术栈：

- **测试框架**：Pytest + Playwright
- **报告工具**：Allure + 自定义报告
- **代码质量**：pylint + flake8 + black + isort
- **依赖管理**：pip-tools
- **CI/CD**：GitHub Actions + GitLab CI + Jenkins

## 核心特性

- ✅ 页面对象模式 (POM)
- ✅ 多环境配置管理
- ✅ 数据驱动测试
- ✅ API 测试支持
- ✅ Allure 报告集成
- ✅ 测试覆盖率报告
- ✅ Mock 服务支持
- ✅ 敏感信息加密
- ✅ 并行测试
- ✅ 测试数据管理
- ✅ 统一异常处理
- ✅ 代码质量工具集成

## 快速开始

1. **安装依赖**：`pip install -r requirements.lock`
2. **安装浏览器**：`playwright install`
3. **运行测试**：`pytest tests/sample_tests/test_sample.py -v`
4. **查看报告**：`allure serve allure-results`

## 联系与支持

- **问题反馈**：在 GitHub 仓库创建 Issue
- **贡献代码**：提交 Pull Request
- **文档更新**：修改相应的 Markdown 文件
