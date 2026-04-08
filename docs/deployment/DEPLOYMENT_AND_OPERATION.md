# 部署与运维文档

## 1. 概述

本文档描述了系统的部署和运维流程，包括环境准备、安装配置、部署步骤、运行维护和故障排查等内容。

## 2. 环境准备

### 2.1 系统要求

- **操作系统**：Linux, macOS, Windows
- **Python**：3.10 或更高版本
- **浏览器**：Chrome, Firefox, Safari (Playwright 会自动安装)
- **内存**：至少 4GB
- **磁盘空间**：至少 5GB

### 2.2 依赖项

- **核心依赖**：pytest, pytest-playwright, playwright, allure-pytest, requests, PyYAML, Faker, python-dotenv, TOML
- **开发依赖**：pylint, flake8, black, isort, mypy, pre-commit, sphinx, pip-tools
- **系统依赖**：Playwright 浏览器依赖（会自动安装）

## 3. 安装配置

### 3.1 克隆代码库

```bash
git clone <repository-url>
cd <repository-directory>
```

### 3.2 安装依赖

```bash
# 以开发模式安装依赖
pip install -e .

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装 Playwright 浏览器
playwright install
```

### 3.3 配置环境变量

框架会自动加载 `config/envs/.env.base` 作为基础配置，然后根据当前环境加载对应的配置文件。

**环境配置文件说明**：
- `config/envs/.env.base` - 基础配置（所有环境的默认值）
- `config/envs/.env.development` - 开发环境配置
- `config/envs/.env.testing` - 测试环境配置
- `config/envs/.env.production` - 生产环境配置

**配置模式**：
- `strict` - 严格模式，配置错误会导致测试失败
- `relaxed` - 宽松模式，配置错误会产生警告但不影响测试执行

**配置优先级**：
1. 环境变量
2. 特定环境配置文件（如 `.env.development`）
3. 项目根目录的 `.env` 文件
4. 基础配置文件（`.env.base`）
5. 默认值

### 3.4 配置预提交钩子

```bash
pre-commit install
```

## 4. 部署步骤

### 4.1 本地部署

1. **安装依赖**：按照 3.2 步骤安装依赖
2. **配置环境变量**：框架会自动加载配置文件，如需自定义配置，可在项目根目录创建 `.env` 文件
3. **运行测试**：

```bash
# 运行所有测试
pytest

# 运行特定类型的测试
pytest tests/e2e/  # 运行 E2E 测试
pytest tests/api/  # 运行 API 测试
pytest tests/integration/  # 运行集成测试
pytest tests/unit/  # 运行单元测试

# 生成 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 4.2 Docker 部署

1. **构建 Docker 镜像**：

```bash
docker build -t automation-test:latest .
```

2. **运行 Docker 容器**：

```bash
docker run --rm -v $(pwd)/reports:/app/reports -v $(pwd)/screenshots:/app/screenshots automation-test:latest pytest
```

### 4.3 CI/CD 部署

系统已集成 GitHub Actions、GitLab CI 和 Jenkins，支持自动测试和报告部署：

1. **推送代码**：将代码推送到版本控制仓库
2. **CI/CD 自动运行**：
   - 安全扫描：检查依赖和代码安全
   - 测试：在不同 Python 版本和浏览器上运行测试
   - 代码质量检查：运行 pylint、flake8、black、isort、mypy
   - 代码覆盖率：生成代码覆盖率报告
   - 报告部署：将 Allure 报告部署到 GitHub Pages 或其他服务

## 5. 运行维护

### 5.1 日常维护

1. **更新依赖**：

```bash
pip install --upgrade pip
pip-compile --upgrade requirements.in
pip install -r requirements.lock
```

2. **更新 Playwright 浏览器**：

```bash
playwright install
```

3. **清理缓存**：

```bash
# 清理 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 清理 pip 缓存
pip cache purge

# 清理测试结果和报告
rm -rf reports/*
rm -rf screenshots/*
```

### 5.2 监控

1. **日志监控**：检查测试日志，及时发现问题
2. **测试结果监控**：监控测试通过率和执行时间
3. **资源监控**：监控系统资源使用情况
4. **测试趋势**：分析历史测试结果，识别测试稳定性问题

### 5.3 备份

1. **代码备份**：使用 Git 进行版本控制
2. **配置备份**：备份环境变量配置文件
3. **报告备份**：定期备份测试报告
4. **测试数据备份**：备份测试数据文件

## 6. 故障排查

### 6.1 常见问题

#### 6.1.1 浏览器启动失败

**症状**：测试执行时浏览器无法启动

**原因**：
- 浏览器依赖缺失
- 端口被占用
- 权限不足

**解决方案**：
- 重新安装 Playwright 浏览器：`playwright install`
- 检查端口占用情况：`lsof -i :9222`（Linux/macOS）或 `netstat -ano | findstr :9222`（Windows）
- 以管理员权限运行测试

#### 6.1.2 测试超时

**症状**：测试执行超时

**原因**：
- 网络连接慢
- 页面加载时间长
- 元素定位失败

**解决方案**：
- 增加超时时间：修改 `TIMEOUT` 环境变量
- 检查网络连接
- 优化元素定位策略，使用语义化定位
- 使用智能等待，避免硬编码等待时间

#### 6.1.3 元素定位失败

**症状**：测试执行时元素定位失败

**原因**：
- 元素选择器错误
- 页面结构变化
- 元素加载延迟

**解决方案**：
- 检查元素选择器
- 使用语义化定位
- 增加等待时间，使用智能等待
- 检查页面是否有动态加载的内容

#### 6.1.4 报告生成失败

**症状**：Allure 报告生成失败

**原因**：
- Allure 命令行工具未安装
- 报告目录权限不足
- 测试结果文件损坏

**解决方案**：
- 安装 Allure 命令行工具
- 检查目录权限
- 清理测试结果目录：`rm -rf reports/allure-results`

#### 6.1.5 配置错误

**症状**：测试执行时出现配置错误

**原因**：
- 环境变量配置错误
- 配置文件格式错误
- 配置模式设置不当

**解决方案**：
- 检查环境变量配置
- 检查配置文件格式
- 根据需要调整配置模式（strict/relaxed）
- 运行配置检查：`python scripts/utils/config_checker.py`

### 6.2 日志分析

1. **测试日志**：查看测试执行日志，了解测试执行过程
2. **浏览器日志**：查看浏览器控制台日志，了解页面错误
3. **系统日志**：查看系统日志，了解系统级错误
4. **配置日志**：查看配置变更日志，了解配置变化

### 6.3 调试技巧

1. **开启调试模式**：

```bash
pytest -v --tb=long
```

2. **启用视频录制**：设置 `VIDEO_ENABLED=true`
3. **启用截图**：设置 `SCREENSHOT_ENABLED=true`
4. **使用交互式调试**：

```bash
pytest -v -s
```

5. **使用配置向导**：

```bash
python scripts/cli/config_wizard.py
```

6. **使用交互式测试运行器**：

```bash
python scripts/cli/interactive_runner.py
```

## 7. 性能优化

### 7.1 测试执行优化

1. **并行测试**：

```bash
pytest -n auto  # 自动检测 CPU 核心数
pytest -n 4     # 使用 4 个进程
```

2. **选择特定测试**：

```bash
pytest -k "test_name"  # 运行特定测试
pytest tests/e2e/test_todomvc.py::test_add_todo  # 运行特定测试方法
```

3. **使用标记**：

```bash
pytest -m smoke  # 运行标记为 smoke 的测试
```

4. **选择特定浏览器**：

```bash
pytest --browser chromium tests/e2e/  # 只在 Chrome 上运行测试
pytest --browser chromium --browser firefox tests/e2e/  # 在 Chrome 和 Firefox 上运行测试
```

### 7.2 资源优化

1. **浏览器池**：使用浏览器池减少浏览器启动时间
2. **智能等待**：使用智能等待减少不必要的等待时间
3. **测试数据管理**：使用测试数据工厂减少数据准备时间
4. **定位器策略**：使用语义化定位提高定位成功率
5. **Mock 服务**：使用 Mock 服务减少对外部 API 的依赖

## 8. 安全管理

### 8.1 敏感信息管理

1. **环境变量**：使用环境变量存储敏感信息
2. **密钥管理**：使用密钥管理工具管理密钥
3. **数据脱敏**：对敏感数据进行脱敏处理
4. **加密存储**：使用 SecretsManager 加密存储敏感信息

### 8.2 安全扫描

1. **依赖扫描**：定期扫描依赖包安全漏洞

```bash
python scripts/security/security_scan.py
```

2. **代码安全扫描**：定期扫描代码安全问题

```bash
bandit -r core/ tests/
```

3. **配置安全检查**：检查配置文件中的安全问题

```bash
python scripts/security/config_security_check.py
```

## 9. 最佳实践

### 9.1 部署最佳实践

1. **环境隔离**：为不同的环境（开发、测试、生产）使用不同的配置
2. **版本控制**：使用 Git 管理代码和配置文件
3. **自动化部署**：使用 CI/CD 工具自动化部署和测试
4. **监控告警**：设置测试失败告警机制

### 9.2 运维最佳实践

1. **定期更新**：定期更新依赖和浏览器
2. **备份策略**：定期备份代码、配置和报告
3. **性能监控**：监控测试执行性能
4. **安全审计**：定期进行安全审计

### 9.3 故障排查最佳实践

1. **日志分析**：详细分析测试日志和浏览器日志
2. **逐步排查**：从简单到复杂，逐步排查问题
3. **记录问题**：记录常见问题和解决方案
4. **持续改进**：根据故障排查结果持续改进系统

## 10. 结论

本文档描述了系统的部署和运维流程，包括环境准备、安装配置、部署步骤、运行维护和故障排查等内容。通过按照本文档的指导进行部署和运维，可以确保系统的稳定运行和高效测试。

系统的部署和运维设计遵循以下原则：
- **自动化**：尽可能自动化部署和测试流程
- **可配置**：通过配置文件和环境变量控制系统行为
- **可监控**：建立完善的监控和告警机制
- **可维护**：提供详细的文档和故障排查指南
- **安全**：保护敏感信息，定期进行安全扫描

这些原则使得系统能够在不同的环境中稳定运行，提供可靠的测试结果，为项目质量保驾护航。