# API 接口文档

## 1. 概述

本文档描述了系统中使用的 API 接口，包括内部 API 和外部 API。内部 API 主要用于系统内部模块之间的通信，外部 API 主要用于与外部系统的交互。

## 2. 内部 API

### 2.1 页面对象 API

#### 2.1.1 BasePage 类

**路径**：`core/pages/base/base_page.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `navigate(url, wait_until, timeout)` | url: str - 目标 URL<br>wait_until: Literal - 等待条件<br>timeout: int - 超时时间 | Optional[Response] - 导航响应对象 | 导航到指定 URL |
| `wait_for_page_load(state, timeout)` | state: Literal - 加载状态<br>timeout: int - 超时时间 | None | 等待页面加载完成 |
| `execute_script(script, *args)` | script: str - JavaScript 代码<br>*args: Any - 传递给 JavaScript 的参数 | Any - JavaScript 执行结果 | 执行 JavaScript |
| `get_title()` | 无 | str - 页面标题 | 获取页面标题 |
| `get_url()` | 无 | str - 页面 URL | 获取页面 URL |
| `wait_for_network_idle(timeout)` | timeout: int - 超时时间 | None | 等待网络空闲 |
| `refresh(wait_until, timeout)` | wait_until: Literal - 等待条件<br>timeout: int - 超时时间 | Optional[Response] - 刷新响应对象 | 刷新页面 |
| `go_back(wait_until, timeout)` | wait_until: Literal - 等待条件<br>timeout: int - 超时时间 | Optional[Response] - 导航响应对象 | 返回上一页 |
| `go_forward(wait_until, timeout)` | wait_until: Literal - 等待条件<br>timeout: int - 超时时间 | Optional[Response] - 导航响应对象 | 前进到下一页 |
| `get_locator(selector)` | selector: Union[str, Dict[str, Any]] - 选择器 | Locator - Playwright 定位器对象 | 获取元素定位器 |
| `click(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | None | 点击元素 |
| `fill(selector, value, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>value: str - 输入值<br>timeout: int - 超时时间 | None | 填充输入框 |
| `get_text(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | str - 元素文本 | 获取元素文本 |
| `is_visible(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | bool - 是否可见 | 检查元素是否可见 |
| `is_enabled(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | bool - 是否启用 | 检查元素是否启用 |
| `wait_for_selector(selector, timeout, state)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间<br>state: Literal - 等待状态 | Locator - Playwright 定位器对象 | 等待元素出现 |
| `screenshot(path, full_page)` | path: str - 截图路径<br>full_page: bool - 是否全屏 | str - 截图路径 | 截取页面截图 |

### 2.2 定位器 API

#### 2.2.1 SmartPage 类

**路径**：`core/pages/locators.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `__init__(page, locator_file)` | page: Page - Playwright 页面对象<br>locator_file: str - 定位器文件路径 | None | 初始化 SmartPage |
| `get_locator(name, **kwargs)` | name: str - 定位器名称<br>**kwargs: Dict[str, Any] - 定位器参数 | Locator - Playwright 定位器对象 | 获取定位器 |
| `click(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | None | 点击元素 |
| `fill(selector, value, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>value: str - 输入值<br>timeout: int - 超时时间 | None | 填充输入框 |
| `get_text(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | str - 元素文本 | 获取元素文本 |
| `is_visible(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | bool - 是否可见 | 检查元素是否可见 |
| `is_enabled(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | bool - 是否启用 | 检查元素是否启用 |
| `wait_for_selector(selector, timeout, state)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间<br>state: Literal - 等待状态 | Locator - Playwright 定位器对象 | 等待元素出现 |

### 2.3 API 服务 API

#### 2.3.1 MockServer 类

**路径**：`core/services/api/mock_server.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `__init__(base_url)` | base_url: str - 基础 URL | None | 初始化 MockServer |
| `add_mock_response(path, method, response, status_code, headers, delay)` | path: str - 请求路径<br>method: str - 请求方法<br>response: Any - 响应数据<br>status_code: int - 状态码<br>headers: Dict[str, str] - 响应头<br>delay: int - 响应延迟（毫秒） | None | 添加模拟响应 |
| `get(path, params, headers)` | path: str - 请求路径<br>params: Dict[str, Any] - 查询参数<br>headers: Dict[str, str] - 请求头 | Dict[str, Any] - 响应数据 | 发送 GET 请求 |
| `post(path, data, headers)` | path: str - 请求路径<br>data: Dict[str, Any] - 请求数据<br>headers: Dict[str, str] - 请求头 | Dict[str, Any] - 响应数据 | 发送 POST 请求 |
| `put(path, data, headers)` | path: str - 请求路径<br>data: Dict[str, Any] - 请求数据<br>headers: Dict[str, str] - 请求头 | Dict[str, Any] - 响应数据 | 发送 PUT 请求 |
| `delete(path, headers)` | path: str - 请求路径<br>headers: Dict[str, str] - 请求头 | Dict[str, Any] - 响应数据 | 发送 DELETE 请求 |
| `get_request_history()` | 无 | List[Dict[str, Any]] - 请求历史 | 获取请求历史 |
| `reset()` | 无 | None | 重置模拟服务器 |

### 2.4 浏览器工具 API

#### 2.4.1 BrowserPool 类

**路径**：`utils/browser/browser_pool.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `__init__(max_browsers)` | max_browsers: int - 最大浏览器数 | None | 初始化浏览器池 |
| `get_browser(browser_type)` | browser_type: str - 浏览器类型 | Browser - Playwright 浏览器对象 | 获取浏览器 |
| `get_context(browser, viewport)` | browser: Browser - Playwright 浏览器对象<br>viewport: Dict[str, int] - 视口大小 | BrowserContext - Playwright 浏览器上下文对象 | 获取浏览器上下文 |
| `get_page(context)` | context: BrowserContext - Playwright 浏览器上下文对象 | Page - Playwright 页面对象 | 获取页面 |
| `release_browser(browser)` | browser: Browser - Playwright 浏览器对象 | None | 释放浏览器 |
| `release_context(context)` | context: BrowserContext - Playwright 浏览器上下文对象 | None | 释放浏览器上下文 |
| `release_page(page)` | page: Page - Playwright 页面对象 | None | 释放页面 |
| `close_all()` | 无 | None | 关闭所有浏览器 |

#### 2.4.2 SmartWaiter 类

**路径**：`utils/browser/smart_waiter.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `__init__(page)` | page: Page - Playwright 页面对象 | None | 初始化 SmartWaiter |
| `wait_for_element(selector, timeout, state)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间<br>state: Literal - 等待状态 | Locator - Playwright 定位器对象 | 等待元素 |
| `wait_for_element_visible(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | Locator - Playwright 定位器对象 | 等待元素可见 |
| `wait_for_element_hidden(selector, timeout)` | selector: Union[str, Dict[str, Any]] - 选择器<br>timeout: int - 超时时间 | Locator - Playwright 定位器对象 | 等待元素隐藏 |
| `wait_for_load_state(state, timeout)` | state: Literal - 加载状态<br>timeout: int - 超时时间 | None | 等待页面加载状态 |
| `wait_for_navigation(url, timeout)` | url: str - 目标 URL<br>timeout: int - 超时时间 | Response - 导航响应对象 | 等待导航完成 |
| `wait_for_network_idle(timeout)` | timeout: int - 超时时间 | None | 等待网络空闲 |
| `wait_for_timeout(timeout)` | timeout: int - 等待时间 | None | 等待指定时间 |

### 2.5 配置 API

#### 2.5.1 Settings 类

**路径**：`config/settings.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `__init__(env, validate, config_mode)` | env: Optional[str] - 环境名称<br>validate: bool - 是否验证配置<br>config_mode: str - 配置模式 | None | 初始化配置 |
| `get(key, default)` | key: str - 配置项键名<br>default: Any - 默认值 | Any - 配置项值或默认值 | 获取配置项 |
| `get_config_summary()` | 无 | Dict[str, Any] - 配置摘要 | 获取配置摘要 |
| `get_config_changes()` | 无 | List[str] - 配置变更列表 | 获取配置变更历史 |
| `is_development` | 无 | bool - 是否为开发环境 | 是否为开发环境 |
| `is_testing` | 无 | bool - 是否为测试环境 | 是否为测试环境 |
| `is_production` | 无 | bool - 是否为生产环境 | 是否为生产环境 |
| `is_strict_mode` | 无 | bool - 是否为严格配置模式 | 是否为严格配置模式 |
| `is_relaxed_mode` | 无 | bool - 是否为宽松配置模式 | 是否为宽松配置模式 |

### 2.6 数据工具 API

#### 2.6.1 TestDataLoader 类

**路径**：`utils/data/test_data_loader.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `get_test_data(file_path, section)` | file_path: str - 测试数据文件路径<br>section: str - 数据节名称 | Dict[str, Any] - 测试数据 | 获取测试数据 |
| `get_login_data(section)` | section: str - 数据节名称 | Dict[str, Any] - 登录测试数据 | 获取登录测试数据 |
| `get_api_data(section)` | section: str - 数据节名称 | Dict[str, Any] - API 测试数据 | 获取 API 测试数据 |

#### 2.6.2 DataFactory 类

**路径**：`utils/data/data_factory.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `create_user()` | 无 | Dict[str, str] - 用户数据 | 创建用户数据 |
| `create_product()` | 无 | Dict[str, Any] - 产品数据 | 创建产品数据 |
| `create_order()` | 无 | Dict[str, Any] - 订单数据 | 创建订单数据 |
| `generate_random_string(length)` | length: int - 字符串长度 | str - 随机字符串 | 生成随机字符串 |
| `generate_random_email()` | 无 | str - 随机邮箱 | 生成随机邮箱 |

### 2.7 报告工具 API

#### 2.7.1 AllureHelper 类

**路径**：`utils/reporting/allure_helper.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `add_parameter(name, value)` | name: str - 参数名称<br>value: Any - 参数值 | None | 添加测试参数 |
| `add_parameters(parameters)` | parameters: Dict[str, Any] - 参数字典 | None | 添加多个测试参数 |
| `add_attachment(name, content, attachment_type)` | name: str - 附件名称<br>content: Any - 附件内容<br>attachment_type: str - 附件类型 | None | 添加附件 |
| `add_screenshot(page, name)` | page: Page - Playwright 页面对象<br>name: str - 截图名称 | None | 添加截图 |
| `add_video(page, name)` | page: Page - Playwright 页面对象<br>name: str - 视频名称 | None | 添加视频 |
| `add_link(url, name, link_type)` | url: str - 链接 URL<br>name: str - 链接名称<br>link_type: str - 链接类型 | None | 添加链接 |
| `add_issue(url, name)` | url: str - 问题 URL<br>name: str - 问题名称 | None | 添加问题链接 |
| `add_test_case(url, name)` | url: str - 测试用例 URL<br>name: str - 测试用例名称 | None | 添加测试用例链接 |
| `attach_json(data, name)` | data: Dict[str, Any] - JSON 数据<br>name: str - 附件名称 | None | 附加 JSON 数据 |
| `attach_text(text, name)` | text: str - 文本数据<br>name: str - 附件名称 | None | 附加文本数据 |

#### 2.7.2 ReportGenerator 类

**路径**：`utils/reporting/report_generator.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `__init__(report_dir)` | report_dir: str - 报告目录 | None | 初始化报告生成器 |
| `add_test_result(test_name, status, duration, error_message)` | test_name: str - 测试名称<br>status: str - 测试状态<br>duration: float - 测试时长<br>error_message: str - 错误信息 | None | 添加测试结果 |
| `generate_html_report()` | 无 | str - 报告文件路径 | 生成 HTML 报告 |
| `generate_json_report()` | 无 | str - 报告文件路径 | 生成 JSON 报告 |
| `generate_summary()` | 无 | Dict[str, Any] - 测试摘要 | 生成测试摘要 |

### 2.8 安全工具 API

#### 2.8.1 SecretsManager 类

**路径**：`utils/security/secrets_manager.py`

**方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `encrypt(value)` | value: str - 要加密的值 | str - 加密后的值 | 加密敏感信息 |
| `decrypt(value)` | value: str - 要解密的值 | str - 解密后的值 | 解密敏感信息 |
| `get_secret(key, default)` | key: str - 密钥名称<br>default: Any - 默认值 | Any - 密钥值或默认值 | 获取密钥 |
| `set_secret(key, value)` | key: str - 密钥名称<br>value: str - 密钥值 | None | 设置密钥 |

## 3. 外部 API

### 3.1 测试目标 API

#### 3.1.1 TodoMVC API

**基础 URL**：`https://demo.playwright.dev/todomvc`

**方法**：

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/` | GET | 访问 TodoMVC 应用 | N/A | HTML 页面 |

#### 3.1.2 示例 API

**基础 URL**：`https://api.example.com`

**方法**：

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/users` | GET | 获取用户列表 | N/A | `{"users": [{"id": 1, "name": "John"}]}` |
| `/api/users` | POST | 创建用户 | `{"name": "John", "email": "john@example.com"}` | `{"id": 1, "name": "John", "email": "john@example.com"}` |
| `/api/users/{id}` | GET | 获取用户详情 | N/A | `{"id": 1, "name": "John", "email": "john@example.com"}` |
| `/api/users/{id}` | PUT | 更新用户 | `{"name": "John Doe", "email": "john.doe@example.com"}` | `{"id": 1, "name": "John Doe", "email": "john.doe@example.com"}` |
| `/api/users/{id}` | DELETE | 删除用户 | N/A | `{"status": "success"}` |

## 4. API 测试

### 4.1 API 测试方法

1. **单元测试**：测试 API 服务的单个方法
2. **集成测试**：测试 API 服务与其他服务的集成
3. **端到端测试**：测试完整的 API 流程

### 4.2 API 测试工具

- **requests**：发送 HTTP 请求
- **pytest**：测试框架
- **pytest-playwright**：浏览器自动化测试
- **allure-pytest**：生成测试报告

### 4.3 API 测试最佳实践

1. **使用模拟服务器**：在测试中使用模拟服务器，避免依赖真实 API
2. **参数化测试**：使用参数化测试，覆盖不同的测试场景
3. **断言验证**：验证响应状态码、响应头和响应体
4. **错误处理**：测试错误情况和边界条件
5. **性能测试**：测试 API 的性能和响应时间
6. **安全测试**：测试 API 的安全性
7. **契约测试**：测试 API 契约

### 4.4 Mock 服务使用指南

1. **初始化 Mock 服务**：
   ```python
   from core.services.api.mock_server import MockServer
   mock_server = MockServer("https://api.example.com")
   ```

2. **添加模拟响应**：
   ```python
   # 模拟成功响应
   mock_server.add_mock_response(
       path="/api/users",
       method="GET",
       response={"users": [{"id": 1, "name": "John"}]},
       status_code=200,
       headers={"Content-Type": "application/json"}
   )

   # 模拟错误响应
   mock_server.add_mock_response(
       path="/api/users/999",
       method="GET",
       response={"error": "User not found"},
       status_code=404,
       headers={"Content-Type": "application/json"}
   )

   # 模拟延迟响应
   mock_server.add_mock_response(
       path="/api/users",
       method="POST",
       response={"id": 2, "name": "Jane"},
       status_code=201,
       headers={"Content-Type": "application/json"},
       delay=1000  # 1秒延迟
   )
   ```

3. **发送请求**：
   ```python
   # 发送 GET 请求
   response = mock_server.get("/api/users", params={"page": 1})
   print(response)  # {"users": [{"id": 1, "name": "John"}]}

   # 发送 POST 请求
   response = mock_server.post("/api/users", data={"name": "Jane", "email": "jane@example.com"})
   print(response)  # {"id": 2, "name": "Jane"}
   ```

4. **验证请求**：
   ```python
   # 获取请求历史
   history = mock_server.get_request_history()
   print(history)

   # 验证请求参数
   assert len(history) > 0
   assert history[0]["path"] == "/api/users"
   assert history[0]["method"] == "GET"
   assert history[0]["params"] == {"page": 1}
   ```

5. **重置 Mock 服务**：
   ```python
   mock_server.reset()
   ```

## 5. 结论

本文档描述了系统中使用的 API 接口，包括内部 API 和外部 API。内部 API 主要用于系统内部模块之间的通信，外部 API 主要用于与外部系统的交互。通过使用这些 API，可以实现高效、稳定的自动化测试。

系统的 API 设计遵循以下原则：
- **模块化**：将功能划分为独立的模块，便于维护和扩展
- **类型注解**：使用类型注解，提高代码可读性和可维护性
- **异常处理**：结构化的异常处理，提高系统稳定性
- **配置管理**：灵活的配置管理，适应不同的测试环境
- **安全管理**：安全的密钥管理和数据脱敏，保护敏感信息

这些 API 接口为系统提供了强大的功能支持，使得测试框架能够适应复杂的测试场景，提供可靠的测试结果。