# 企业级自动化测试框架

基于 Python + Pytest + Playwright + Allure 的企业级自动化测试可复用标准框架。

## 技术栈

- **Python**: 3.10+
- **Pytest**: 测试框架
- **Playwright**: 浏览器自动化
- **Allure**: 测试报告
- **pytest-xdist**: 并行测试
- **pytest-rerunfailures**: 失败重试
- **pytest-cov**: 测试覆盖率
- **Faker**: 测试数据生成
- **cryptography**: 敏感信息加密

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install
```

### 2. 配置环境

```bash
cp .env.minimal .env
# 编辑 .env 文件，设置 BASE_URL 等配置
```

### 3. 运行测试

```bash
pytest -v
```

### 4. 查看报告

```bash
allure serve reports/allure-results
```

## 文档

- [快速开始指南](docs/README.md) - 5分钟上手指南
- [完整使用指南](docs/GUIDE.md) - 详细功能说明
- [功能特性](docs/FEATURES.md) - 框架能力一览
- [CI/CD 配置](docs/CI_CD.md) - 持续集成配置

## 核心特性

- ✅ **页面对象模式** - 清晰的 POM 架构
- ✅ **多环境配置** - development/testing/staging/production
- ✅ **数据驱动测试** - 支持 JSON/YAML/CSV
- ✅ **API 测试支持** - 内置 API 客户端
- ✅ **Mock 服务** - 轻量级 Mock 服务器
- ✅ **敏感信息加密** - 配置文件加密保护
- ✅ **Allure 报告** - 美观的测试报告
- ✅ **测试覆盖率** - 代码覆盖率统计
- ✅ **CI/CD 模板** - GitHub/GitLab/Jenkins
- ✅ **录屏功能** - 测试过程录屏

## 项目结构

```
.
├── config/          # 配置管理
├── core/            # 核心模块
│   ├── pages/       # 页面对象
│   └── utils/       # 工具类
├── tests/           # 测试用例
├── docs/            # 文档
└── reports/         # 测试报告
```

## 常用命令

```bash
# 运行所有测试
pytest

# 运行冒烟测试
pytest -m smoke

# 并行运行
pytest -n auto

# 生成覆盖率报告
pytest --cov=core --cov-report=html:reports/coverage-html
```

## 示例

```python
import allure
import pytest
from core.pages.base_page import BasePage

@allure.epic("测试套件")
@allure.feature("功能模块")
class TestExample:
    
    @pytest.mark.smoke
    def test_example(self, page, settings):
        base_page = BasePage(page)
        base_page.navigate(settings.base_url)
        assert "期望标题" in base_page.get_title()
```

## License

MIT
