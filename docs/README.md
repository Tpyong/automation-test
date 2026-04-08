# 测试框架文档

本文档是测试框架的导航中心，包含框架的所有文档资源。

## 文档结构

### 入门指南
- [快速开始](getting-started/README.md) - 框架的快速入门指南
- [完整使用指南](getting-started/GUIDE.md) - 框架的详细使用指南

### 系统架构
- [系统架构文档](architecture/SYSTEM_ARCHITECTURE.md) - 框架的系统架构和模块关系

### API 文档
- [API 接口文档](api/API_DOCUMENTATION.md) - 框架的 API 接口文档

### 核心功能
- [功能特性](core-features/FEATURES.md) - 框架的各项功能特性
- [Allure 分类配置](core-features/ALLURE_CATEGORIES.md) - Allure 报告的分类配置

### 部署与运维
- [部署与运维文档](deployment/DEPLOYMENT_AND_OPERATION.md) - 框架的部署和运维指南

### 开发规范
- [开发规范与代码审查指南](development/DEVELOPMENT_GUIDELINES.md) - 框架的开发规范和代码审查流程

### CI/CD 配置
- [CI/CD 配置指南](ci-cd/CI_CD.md) - 各平台 CI/CD 配置指南
- [GitHub Actions 配置](ci-cd/GITHUB_SETUP.md) - GitHub Actions 详细配置指南
- [GitHub Pages 配置](ci-cd/GITHUB_PAGES_SETUP.md) - GitHub Pages 部署配置
- [CI/CD 故障排查](ci-cd/TROUBLESHOOTING.md) - CI/CD 故障排查指南

### 最佳实践
- [目录结构指南](best-practices/DIRECTORY_STRUCTURE.md) - 项目目录结构的最佳实践
- [定位器使用指南](best-practices/LOCATORS_GUIDE.md) - 元素定位器的最佳使用实践
- [pytest-playwright 使用指南](best-practices/PLAYWRIGHT_GUIDE.md) - pytest-playwright 插件使用指南

### 故障排查
- [故障排查手册](troubleshooting/TROUBLESHOOTING.md) - 框架的常见问题和解决方案

## 框架概述

本测试框架基于以下技术栈：

- **测试框架**：Pytest + pytest-playwright 插件
- **报告工具**：Allure + 自定义报告
- **代码质量**：pylint + flake8 + black + isort + mypy
- **依赖管理**：pip-tools
- **CI/CD**：GitHub Actions + GitLab CI + Jenkins

## 核心特性

- ✅ 页面对象模式 (POM) 与智能定位器
- ✅ 多环境配置管理（development/testing/production）
- ✅ 配置模式支持（strict/relaxed）
- ✅ 数据驱动测试框架
- ✅ API 测试与 Mock 服务支持
- ✅ Allure 报告集成与自定义报告
- ✅ 测试覆盖率报告
- ✅ 敏感信息加密与管理
- ✅ 并行测试执行
- ✅ 测试数据管理与清理
- ✅ 统一异常处理与日志记录
- ✅ 代码质量工具集成
- ✅ 浏览器池与智能等待策略

## 快速开始

1. **安装依赖**：`pip install -e .`
2. **安装浏览器**：`playwright install`
3. **运行测试**：`pytest tests/e2e/test_todomvc.py -v`
4. **查看报告**：`allure serve reports/allure-results`

## 联系与支持

- **问题反馈**：在 GitHub 仓库创建 Issue
- **贡献代码**：提交 Pull Request
- **文档更新**：修改相应的 Markdown 文件
