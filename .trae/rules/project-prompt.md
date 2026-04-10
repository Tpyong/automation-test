### 背景
你需要基于以下测试框架规则，根据 PRD 生成可直接运行的自动化测试代码。

### 测试框架规则
1. 技术栈：Python 3.12.10 + pytest 9.0.2 + playwright 1.58.0+ + Allure 2.36.0
2. 目录规范：
   - 测试用例文件：tests/e2e/test_[模块名].py
   - 页面类文件：core/pages/specific/[模块名]_page.py
   - 测试数据文件：resources/data/[模块名]_data.yaml
   - 定位器文件：resources/locators/[模块名]_page.yaml
3. 命名规范：
   - 测试函数命名：test_[功能点]_[场景]
   - 页面类命名：[模块名]Page
   - 文件命名：小写字母 + 下划线格式
4. 编码规范：
   - 必须使用 tests/conftest.py 提供的 fixture（如 settings、page）
   - 必须使用 tests/utils/ 下的工具类
   - 必须使用 core/pages/locators.py 中的 SmartPage 类和定位器管理功能
   - 所有元素定位使用 PageObject 模式
   - 断言使用 pytest.assert
   - 必须添加 Allure 注解（@allure.feature/@allure.story/@allure.step）

### 参考样例
请参考以下项目样例文件的风格和结构：
- tests/e2e/test_todomvc_example.py
- tests/e2e/test_semantic_locators_example.py
- core/pages/specific/login_page_example.py
- core/pages/specific/login_page_semantic_example.py
- resources/data/fixtures/login_data_example.yaml
- resources/locators/web/login_page_example.yaml
- resources/locators/web/login_page_semantic_example.yaml
- resources/locators/web/todo_page_example.yaml

### 输出要求
1. 代码需符合 PEP8 规范，无语法错误
2. 注释清晰，关键步骤需添加 @allure.step 说明
3. 输出完整的文件内容（可直接保存为对应路径的文件）