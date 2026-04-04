# 项目目录结构规范

本文档定义了自动化测试项目的目录结构规范，帮助团队成员理解如何正确组织和归类新文件。

## 目录概览

```
automation-test/
├── .github/              # GitHub 相关配置
├── ci-cd/                # CI/CD 相关配置
├── config/               # 配置文件
├── core/                 # 核心业务逻辑
├── docs/                 # 文档
├── logs/                 # 日志文件（gitignore）
├── reports/              # 测试报告（gitignore）
├── resources/            # 测试资源
├── scripts/              # 脚本工具
├── tests/                # 测试用例
└── utils/                # 通用工具
```

## 各目录用途详解

### config/ - 配置目录

存放所有配置相关的文件。

| 子目录/文件 | 用途 | 示例 |
|------------|------|------|
| `envs/` | 环境变量文件 | `.env.development`, `.env.testing` |
| `secrets/` | 机密文件（密钥、盐值等） | `.secrets.key`, `.secrets.salt` |
| `settings_dir/` | Python 配置模块 | `base/`, `development/`, `production/` |
| `settings.py` | 主配置入口 | `Settings` 类 |
| `validators.py` | 配置验证器 | 配置验证逻辑 |
| `categories.json` | Allure 报告分类 | 测试结果分类配置 |

### core/ - 核心业务逻辑

存放测试框架的核心业务逻辑。

| 子目录/文件 | 用途 | 示例 |
|------------|------|------|
| `pages/` | 页面对象（POM） | `base/`, `components/`, `specific/` |
| `services/` | 外部服务集成 | `api/`, `database/`, `auth/` |
| `exceptions/` | 自定义异常 | 项目特定异常类 |
| `models/` | 数据模型 | 测试数据模型 |

### utils/ - 通用工具

存放可复用的通用工具函数和类。

| 子目录/文件 | 用途 | 示例 |
|------------|------|------|
| `api/` | API 测试工具 | `api_client.py`, `assertions.py`, `circuit_breaker.py` |
| `browser/` | 浏览器自动化工具 | `browser_pool.py`, `smart_waiter.py` |
| `common/` | 通用工具 | `logger.py`, `path_helper.py`, `exception_handler.py` |
| `data/` | 数据管理工具 | `data_factory.py`, `test_data_manager.py` |
| `reporting/` | 报告生成工具 | `allure_helper.py`, `report_generator.py` |
| `security/` | 安全相关工具 | `secrets_manager.py`, `data_masking.py` |

### tests/ - 测试用例

存放所有测试用例。

| 子目录/文件 | 用途 | 示例 |
|------------|------|------|
| `unit/` | 单元测试 | 测试单个函数/类 |
| `integration/` | 集成测试 | 测试模块间交互 |
| `api/` | API 测试 | 接口测试用例 |
| `e2e/` | 端到端测试 | 完整流程测试 |
| `conftest.py` | Pytest 配置 | Fixtures 和钩子函数 |

### resources/ - 测试资源

存放测试所需的资源文件。

| 子目录/文件 | 用途 | 示例 |
|------------|------|------|
| `data/` | 测试数据 | `fixtures/`, `datasets/` |
| `locators/` | 元素定位器 | `web/`, `mobile/` |
| `templates/` | 模板文件 | 报告模板等 |

### scripts/ - 脚本工具

存放自动化脚本和命令行工具。

| 子目录/文件 | 用途 | 示例 |
|------------|------|------|
| `cli/` | 命令行工具 | `config_wizard.py`, `interactive_runner.py` |
| `automation/` | 自动化脚本 | `prepare_allure.py` |
| `security/` | 安全相关脚本 | `secrets_tool.py`, `security_scan.py` |
| `utils/` | 脚本辅助工具 | `config_checker.py` |

### docs/ - 文档

存放项目文档。

| 子目录/文件 | 用途 |
|------------|------|
| `getting-started/` | 入门指南 |
| `core-features/` | 核心功能说明 |
| `best-practices/` | 最佳实践（包括本文档） |
| `ci-cd/` | CI/CD 相关文档 |

## 新文件归类决策树

当你需要添加新文件时，请按以下步骤决定文件应该放在哪里：

```
开始
  │
  ▼
这是配置相关的文件吗？
  ├─ 是 → config/ 目录
  │       ├─ 环境变量？ → config/envs/
  │       ├─ 机密文件？ → config/secrets/
  │       └─ 其他配置？ → config/settings_dir/ 或 config/
  │
  └─ 否 → 这是核心业务逻辑吗？
           ├─ 是 → core/ 目录
           │       ├─ 页面对象？ → core/pages/
           │       ├─ 外部服务？ → core/services/
           │       ├─ 数据模型？ → core/models/
           │       └─ 自定义异常？ → core/exceptions/
           │
           └─ 否 → 这是测试用例吗？
                    ├─ 是 → tests/ 目录
                    │       ├─ 单元测试？ → tests/unit/
                    │       ├─ 集成测试？ → tests/integration/
                    │       ├─ API 测试？ → tests/api/
                    │       └─ E2E 测试？ → tests/e2e/
                    │
                    └─ 否 → 这是测试资源吗？
                             ├─ 是 → resources/ 目录
                             │       ├─ 测试数据？ → resources/data/
                             │       ├─ 定位器？ → resources/locators/
                             │       └─ 模板？ → resources/templates/
                             │
                             └─ 否 → 这是脚本工具吗？
                                      ├─ 是 → scripts/ 目录
                                      │       ├─ 命令行？ → scripts/cli/
                                      │       ├─ 自动化？ → scripts/automation/
                                      │       └─ 安全？ → scripts/security/
                                      │
                                      └─ 否 → utils/ 目录（通用工具）
                                               ├─ API 相关？ → utils/api/
                                               ├─ 浏览器相关？ → utils/browser/
                                               ├─ 数据相关？ → utils/data/
                                               ├─ 报告相关？ → utils/reporting/
                                               ├─ 安全相关？ → utils/security/
                                               └─ 其他核心工具？ → utils/core/
```

## 常见文件归类示例

| 文件类型 | 建议位置 | 理由 |
|---------|---------|------|
| 页面对象类 | `core/pages/specific/` | 属于核心业务逻辑 |
| API 客户端 | `utils/api/` | 通用 API 工具 |
| 数据库连接管理 | `core/services/database/` | 外部服务集成 |
| 测试数据工厂 | `utils/data/` | 数据管理工具 |
| Allure 报告辅助 | `utils/reporting/` | 报告生成工具 |
| 环境配置 | `config/envs/` | 配置文件 |
| 测试用例 | `tests/e2e/` 或 `tests/api/` | 测试代码 |
| 日志工具 | `utils/core/` | 核心通用工具 |
| 机密管理 | `utils/security/` | 安全相关工具 |
| 元素定位器 | `core/pages/` | 页面对象相关 |
| 测试 Fixtures | `tests/conftest.py` | Pytest 配置 |
| CLI 工具 | `scripts/cli/` | 命令行脚本 |

## 命名约定

### 目录命名
- 使用小写字母
- 使用下划线分隔单词（snake_case）
- 使用复数形式表示集合（如 `pages/`, `tests/`）

### 文件命名
- 使用小写字母
- 使用下划线分隔单词（snake_case）
- 模块文件：`module_name.py`
- 测试文件：`test_*.py`

### 类命名
- 使用大驼峰命名法（PascalCase）
- 例如：`LoginPage`, `APIClient`, `TestDataManager`

### 函数命名
- 使用小写字母
- 使用下划线分隔单词（snake_case）
- 例如：`get_logger()`, `load_config()`, `validate_data()`

## 导入规范

### 导入顺序
1. 标准库导入
2. 第三方库导入
3. 项目内部导入

### 导入路径
- 使用绝对导入而非相对导入
- 从项目根目录开始导入
- 例如：`from utils.common.logger import get_logger`

## 维护建议

1. **定期审查**：定期检查目录结构，确保没有文件放错位置
2. **遵循规范**：添加新文件时，务必参考本文档
3. **及时更新**：如果目录结构发生变化，及时更新本文档
4. **团队培训**：新成员加入时，确保他们理解并遵循此规范

## 常见问题

### Q: 我不确定文件应该放在哪里怎么办？
A: 先问自己几个问题：
- 这个文件是配置吗？→ config/
- 这个文件是测试吗？→ tests/
- 这个文件是核心业务逻辑吗？→ core/
- 这个文件是通用工具吗？→ utils/
- 如果还是不确定，参考决策树或咨询团队

### Q: 可以创建新的子目录吗？
A: 可以，但建议：
1. 先确认现有目录是否合适
2. 新目录应该有明确的用途
3. 更新本文档，记录新目录的用途

### Q: 什么情况下应该重构目录结构？
A: 当以下情况发生时考虑重构：
1. 现有目录无法满足需求
2. 目录职责变得模糊
3. 大量文件放错位置
4. 项目架构发生重大变化

## 联系与反馈

如有疑问或建议，请联系项目维护者或提交 Issue。
