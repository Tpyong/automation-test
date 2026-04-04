# 元素定位器管理使用指南

## 概述

本框架支持 Playwright 官方推荐的语义化定位方式，让测试代码更加稳定、可读、易维护。

## Playwright 官方推荐的定位顺序

按优先级从高到低：

1. **role** - 按 ARIA 角色定位（最推荐）
2. **label** - 按标签文本定位
3. **placeholder** - 按 placeholder 定位
4. **text** - 按文本内容定位
5. **title** - 按 title 属性定位
6. **alt** - 按 alt 属性定位
7. **test\_id** - 按 test id 定位
8. **css** - CSS 选择器
9. **xpath** - XPath 选择器

## 定位器文件格式

### YAML 格式（推荐）

```yaml
# locators/login_page.yaml

# 1. role 定位（最推荐）- 适用于按钮、链接等
login_button:
  role: button
  name: "登录"

# 2. label 定位 - 适用于表单元素
username_input:
  label: "用户名"

# 3. placeholder 定位
search_input:
  placeholder: "请输入搜索内容"

# 4. text 定位
forgot_password_link:
  text: "忘记密码？"
  exact: false  # 可选：是否精确匹配

# 5. title 定位
help_icon:
  title: "帮助"

# 6. alt 定位 - 适用于图片
logo_image:
  alt: "公司Logo"

# 7. test_id 定位（最稳定）
submit_btn:
  test_id: "submit-button"

# 8. CSS 选择器（备用）
error_message:
  css: ".error-message"

# 9. XPath 选择器（特殊情况）
complex_element:
  xpath: "//div[@class='form-group'][1]/input"
```

### JSON 格式

```json
{
  "login_button": {
    "role": "button",
    "name": "登录"
  },
  "username_input": {
    "label": "用户名"
  },
  "error_message": {
    "css": ".error-message"
  }
}
```

## 使用方式

### 方式一：使用 SmartPage（推荐）

```python
from core.pages.locators import SmartPage
from playwright.sync_api import Page

class LoginPage(SmartPage):
    def __init__(self, page: Page):
        super().__init__(page, page_name="login_page")
    
    def login(self, username: str, password: str):
        # 自动识别并使用最佳定位方式
        self.fill("username_input", username)  # 使用 label 定位
        self.fill("password_input", password)  # 使用 label 定位
        self.click("login_button")             # 使用 role 定位
```

### 方式二：直接使用 LocatorManager

```python
from core.pages.locators import LocatorManager
from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.locators = LocatorManager("login_page")
    
    def login(self, username: str, password: str):
        # 获取定位器配置
        username_config = self.locators.username_input
        
        # 根据配置类型使用不同定位方式
        if isinstance(username_config, dict):
            if "label" in username_config:
                self.page.get_by_label(username_config["label"]).fill(username)
            elif "role" in username_config:
                self.page.get_by_role(
                    username_config["role"], 
                    name=username_config.get("name")
                ).fill(username)
        else:
            # 传统 CSS 选择器
            self.page.locator(username_config).fill(username)
```

## 定位方式详解

### 1. Role 定位（最推荐）

适用于：按钮、链接、表单、导航等

```yaml
submit_button:
  role: button
  name: "提交"

navigation:
  role: navigation

search_form:
  role: form
  name: "搜索表单"
```

**支持的 role 值**：

- `button` - 按钮
- `link` - 链接
- `textbox` - 文本输入框
- `checkbox` - 复选框
- `radio` - 单选框
- `combobox` - 下拉框
- `navigation` - 导航
- `form` - 表单
- `heading` - 标题
- `list` - 列表
- `listitem` - 列表项
- `table` - 表格
- 等等...

### 2. Label 定位

适用于：表单元素

```yaml
username_input:
  label: "用户名"

email_input:
  label: "邮箱地址"
  exact: true  # 精确匹配
```

**HTML 示例**：

```html
<label for="username">用户名</label>
<input id="username" type="text">

<!-- 或 -->
<label>
  用户名
  <input type="text">
</label>
```

### 3. Placeholder 定位

适用于：没有 label 的输入框

```yaml
search_input:
  placeholder: "请输入搜索内容"

phone_input:
  placeholder: "请输入手机号"
```

**HTML 示例**：

```html
<input type="text" placeholder="请输入搜索内容">
```

### 4. Text 定位

适用于：链接、按钮等可见文本

```yaml
forgot_password_link:
  text: "忘记密码？"
  exact: false  # 模糊匹配

register_link:
  text: "立即注册"
  exact: true   # 精确匹配
```

### 5. Title 定位

适用于：有 title 属性的元素

```yaml
help_icon:
  title: "帮助"

user_avatar:
  title: "用户头像"
```

**HTML 示例**：

```html
<img src="help.png" title="帮助">
<button title="用户头像">
  <img src="avatar.png">
</button>
```

### 6. Alt 定位

适用于：图片

```yaml
logo_image:
  alt: "公司Logo"

banner_image:
  alt: "活动横幅"
```

**HTML 示例**：

```html
<img src="logo.png" alt="公司Logo">
```

### 7. Test ID 定位（最稳定）

适用于：需要稳定定位的元素

```yaml
submit_btn:
  test_id: "submit-button"

username_field:
  test_id: "username-input"
```

**HTML 示例**：

```html
<button data-testid="submit-button">提交</button>
<input data-testid="username-input" type="text">
```

**优点**：

- 不受样式变化影响
- 不受文本变化影响
- 不受结构变化影响

**缺点**：

- 需要开发配合添加 `data-testid` 属性

### 8. CSS 选择器（备用）

适用于：其他方式无法定位的情况

```yaml
error_message:
  css: ".error-message"

submit_button:
  css: "button[type='submit']"

first_item:
  css: ".list-item:first-child"
```

### 9. XPath 选择器（特殊情况）

适用于：复杂定位场景

```yaml
complex_element:
  xpath: "//div[@class='form-group'][1]/input"

parent_child:
  xpath: "//parent::div/child::span"
```

## 混合使用示例

一个元素可以有多种定位方式，按优先级自动选择：

```yaml
login_button:
  # 首选：role 定位
  role: button
  name: "登录"
  # 备选：CSS 选择器
  css: ".btn-login"
  # 备选：test_id
  test_id: "login-btn"
```

## 最佳实践

### 1. 优先使用语义化定位

```yaml
# ✅ 推荐 - 使用 role
submit_button:
  role: button
  name: "提交"

# ❌ 避免 - 使用 CSS
submit_button:
  css: ".btn-submit:nth-child(2)"
```

### 2. 为关键元素添加 test\_id

```yaml
# ✅ 推荐 - 使用 test_id
user_profile:
  test_id: "user-profile-link"

# 对应 HTML
# <a href="/profile" data-testid="user-profile-link">个人中心</a>
```

### 3. 使用精确匹配提高稳定性

```yaml
# ✅ 推荐 - 精确匹配
submit_button:
  text: "提交"
  exact: true

# ❌ 避免 - 模糊匹配可能匹配到多个元素
submit_button:
  text: "提交"
  exact: false
```

### 4. 避免使用过于复杂的 XPath

```yaml
# ✅ 推荐 - 简洁的 XPath
username_input:
  xpath: "//input[@id='username']"

# ❌ 避免 - 过于复杂的 XPath
username_input:
  xpath: "//div[@class='container']/div[@class='row']/div[@class='col']/form/div[3]/input"
```

### 5. 为动态元素使用稳定的属性

```yaml
# ✅ 推荐 - 使用稳定的 test_id
dynamic_list_item:
  test_id: "list-item"

# ❌ 避免 - 使用可能变化的索引
list_item:
  css: ".list-item:nth-child(5)"
```

## 调试技巧

### 查看元素定位器配置

```python
login_page = LoginPage(page)
config = login_page.get_locator_info("username_input")
print(config)
# 输出: {'label': '用户名'}
```

### 在浏览器开发者工具中测试定位器

```javascript
// 测试 role 定位
document.querySelector('[role="button"]')

// 测试 label 关联
// 查看 label 的 for 属性是否匹配 input 的 id

// 测试 test_id
document.querySelector('[data-testid="submit-button"]')
```

## 常见问题

### Q: 为什么推荐使用 role 定位？

A:

1. **语义化**：符合无障碍标准
2. **稳定性**：不受样式变化影响
3. **可读性**：代码更易理解
4. **维护性**：页面结构调整时更稳定

### Q: 如何处理动态生成的元素？

A:

1. 使用 `test_id` 定位（推荐）
2. 使用稳定的文本内容定位
3. 使用父元素的 role + 相对定位

### Q: 定位器文件应该放在哪里？

A:

- 放在 `locators/` 目录下
- 按页面命名，如 `login_page.yaml`
- 支持子目录，如 `locators/admin/dashboard.yaml`

### Q: 如何迁移现有的 CSS 定位器？

A:

1. 分析页面结构，找出语义化属性
2. 优先替换为 role、label 等语义化定位
3. 为关键元素添加 test\_id
4. 保留 CSS 作为备选方案

## 示例项目

查看以下示例文件：

- `locators/login_page_semantic.yaml` - 语义化定位器示例
- `core/pages/login_page_semantic.py` - 使用语义化定位的页面对象
- `tests/e2e/test_todomvc.py` - 测试用例示例

