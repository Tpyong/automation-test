#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from typing import List, Dict, Optional

class InteractiveTestRunner:
    """交互式测试运行器"""
    
    def __init__(self):
        self.test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
        self.test_categories = ['unit', 'integration', 'api', 'e2e']
    
    def list_test_modules(self, category: str) -> List[str]:
        """列出指定类别的测试模块"""
        category_path = os.path.join(self.test_dir, category)
        modules = []
        
        if os.path.exists(category_path):
            for file in os.listdir(category_path):
                if file.endswith('.py') and not file.startswith('__init__'):
                    modules.append(file)
        
        return modules
    
    def list_test_cases(self, category: str, module: str) -> List[str]:
        """列出指定模块中的测试用例"""
        module_path = os.path.join(self.test_dir, category, module)
        cases = []
        
        if os.path.exists(module_path):
            # 使用 pytest --collect-only 来获取测试用例
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', module_path, '--collect-only', '-q', '--json-report'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                try:
                    # 解析 JSON 输出
                    output = result.stderr.split('{"pytest":')[1].strip()
                    output = '{"pytest":' + output
                    data = json.loads(output)
                    
                    for item in data.get('pytest', {}).get('collectors', []):
                        for test in item.get('items', []):
                            cases.append(test.get('name'))
                except:
                    # 如果解析失败，使用简单的方法
                    pass
        
        return cases
    
    def display_menu(self, options: List[str], title: str) -> int:
        """显示菜单并获取用户选择"""
        print(f"\n{title}")
        print("-" * 50)
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        print("0. 返回")
        print("-" * 50)
        
        while True:
            try:
                choice = int(input("请输入选择 (0-{}): ".format(len(options))))
                if 0 <= choice <= len(options):
                    return choice
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
    
    def run_tests(self, category: str, module: str, cases: Optional[List[str]] = None):
        """运行选定的测试"""
        test_path = os.path.join(self.test_dir, category, module)
        cmd = [sys.executable, '-m', 'pytest', test_path]
        
        if cases:
            # 构建测试用例选择表达式
            case_filter = ','.join(cases)
            cmd.extend(['-k', case_filter])
        
        # 添加常用选项
        cmd.extend(['-v', '--tb=short'])
        
        print(f"\n运行测试: {category}/{module}")
        print(f"命令: {' '.join(cmd)}")
        print("-" * 50)
        
        # 执行测试
        subprocess.run(cmd)
    
    def main(self):
        """主函数"""
        print("=" * 60)
        print("        交互式测试运行器")
        print("=" * 60)
        
        while True:
            # 选择测试类别
            category_choice = self.display_menu(self.test_categories, "选择测试类别")
            if category_choice == 0:
                break
            
            category = self.test_categories[category_choice - 1]
            
            # 列出该类别的测试模块
            modules = self.list_test_modules(category)
            if not modules:
                print(f"\n{category} 类别下没有测试模块")
                continue
            
            # 选择测试模块
            module_choice = self.display_menu(modules, f"选择 {category} 测试模块")
            if module_choice == 0:
                continue
            
            module = modules[module_choice - 1]
            
            # 列出测试用例
            cases = self.list_test_cases(category, module)
            
            # 询问是否选择特定用例
            print("\n1. 运行所有用例")
            print("2. 选择特定用例")
            case_option = input("请选择 (1-2): ")
            
            if case_option == '2' and cases:
                case_choice = self.display_menu(cases, "选择测试用例")
                if case_choice == 0:
                    continue
                selected_cases = [cases[case_choice - 1]]
                self.run_tests(category, module, selected_cases)
            else:
                self.run_tests(category, module)
            
            # 询问是否继续
            continue_choice = input("\n是否继续运行其他测试? (y/n): ")
            if continue_choice.lower() != 'y':
                break

if __name__ == "__main__":
    runner = InteractiveTestRunner()
    runner.main()
