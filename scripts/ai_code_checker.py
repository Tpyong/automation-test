#!/usr/bin/env python3
"""
AI 代码检查脚本

用于检查 AI 是否遵守代码编写约束，确保没有修改核心文件

使用方法:
    python scripts/ai_code_checker.py

返回码:
    0 - 检查通过
    1 - 检查失败，发现禁止的修改
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Set


# 禁止修改的文件列表
FORBIDDEN_FILES = [
    "tests/conftest.py",
    "config/settings.py",
    "tests/utils/video_manager.py",
    "tests/utils/attachment_manager.py",
    "tests/utils/report_manager.py",
    "tests/utils/__init__.py",
    "core/pages/base/base_page.py",
    "core/pages/base/__init__.py",
    "utils/common/logger.py",
    "utils/common/path_helper.py",
    "utils/common/exception_handler.py",
    "utils/data/test_data_loader.py",
    "utils/data/test_data_manager.py",
    "utils/data/data_provider.py",
    "utils/data/data_factory.py",
    "utils/data/data_cache.py",
    "utils/browser/browser_pool.py",
    "utils/browser/smart_waiter.py",
    "utils/reporting/allure_helper.py",
    "utils/reporting/report_generator.py",
    "utils/reporting/test_advisor.py",
]

# 允许创建/修改的文件模式
ALLOWED_PATTERNS = [
    "tests/e2e/test_*.py",
    "core/pages/specific/*.py",
    "resources/data/*.yaml",
    "resources/locators/*.yaml",
    "output/testcases_docs/*.md",
    "output/snapshots/*",
]


def get_modified_files() -> List[str]:
    """
    获取修改的文件列表

    Returns:
        修改的文件路径列表
    """
    try:
        # 使用 git diff 获取修改的文件
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        modified_files = result.stdout.strip().split("\n")
        return [f for f in modified_files if f]
    except subprocess.CalledProcessError:
        print("⚠️  无法获取 git diff 信息，尝试使用 git status")
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            modified_files = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # 解析 git status 输出，提取文件名
                    # 格式: XY filename 或 XY filename -> new_filename
                    parts = line.split()
                    if len(parts) >= 2:
                        filename = parts[-1]
                        modified_files.append(filename)
            return modified_files
        except subprocess.CalledProcessError:
            print("❌ 无法获取修改的文件列表")
            return []


def get_new_files() -> List[str]:
    """
    获取新增的文件列表

    Returns:
        新增的文件路径列表
    """
    try:
        # 使用 git status 获取新增的文件
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        new_files = []
        for line in result.stdout.strip().split("\n"):
            if line.startswith("??") or line.startswith("A "):
                # 解析 git status 输出，提取文件名
                parts = line.split()
                if len(parts) >= 2:
                    filename = parts[-1]
                    new_files.append(filename)
        return new_files
    except subprocess.CalledProcessError:
        print("❌ 无法获取新增的文件列表")
        return []


def check_forbidden_modifications(modified_files: List[str]) -> List[str]:
    """
    检查是否有禁止的修改

    Args:
        modified_files: 修改的文件列表

    Returns:
        禁止修改的文件列表
    """
    forbidden_modifications = []
    for file in modified_files:
        # 规范化路径
        normalized_file = file.replace("\\", "/")
        if normalized_file in FORBIDDEN_FILES:
            forbidden_modifications.append(file)
    return forbidden_modifications


def check_allowed_patterns(new_files: List[str]) -> List[str]:
    """
    检查新增文件是否在允许的范围内

    Args:
        new_files: 新增的文件列表

    Returns:
        不在允许范围内的文件列表
    """
    import fnmatch

    not_allowed_files = []
    for file in new_files:
        # 规范化路径
        normalized_file = file.replace("\\", "/")

        # 检查是否匹配允许的模式
        is_allowed = False
        for pattern in ALLOWED_PATTERNS:
            if fnmatch.fnmatch(normalized_file, pattern):
                is_allowed = True
                break

        if not is_allowed:
            not_allowed_files.append(file)

    return not_allowed_files


def print_check_results(
    modified_files: List[str],
    new_files: List[str],
    forbidden_modifications: List[str],
    not_allowed_files: List[str],
) -> None:
    """
    打印检查结果

    Args:
        modified_files: 修改的文件列表
        new_files: 新增的文件列表
        forbidden_modifications: 禁止修改的文件列表
        not_allowed_files: 不在允许范围内的文件列表
    """
    print("=" * 60)
    print("AI 代码检查结果")
    print("=" * 60)

    print("\n📁 修改的文件:")
    if modified_files:
        for file in modified_files:
            print(f"  - {file}")
    else:
        print("  (无)")

    print("\n📁 新增的文件:")
    if new_files:
        for file in new_files:
            print(f"  - {file}")
    else:
        print("  (无)")

    print("\n" + "=" * 60)

    # 检查禁止的修改
    if forbidden_modifications:
        print("\n❌ 错误：发现禁止的修改")
        print("以下文件只能使用，禁止修改:")
        for file in forbidden_modifications:
            print(f"  - {file}")
        print("\n请遵守代码编写约束，不要修改核心文件。")
        print("如需修改，请记录到问题追踪文件并上报。")
    else:
        print("\n✅ 检查通过：没有修改禁止的文件")

    # 检查不在允许范围内的文件
    if not_allowed_files:
        print("\n⚠️  警告：发现不在允许范围内的新增文件")
        print("以下文件不在允许创建的范围内:")
        for file in not_allowed_files:
            print(f"  - {file}")
        print("\n允许创建的文件类型:")
        for pattern in ALLOWED_PATTERNS:
            print(f"  - {pattern}")
    else:
        print("✅ 检查通过：所有新增文件都在允许范围内")

    print("\n" + "=" * 60)


def main() -> int:
    """
    主函数

    Returns:
        返回码 (0 表示成功，1 表示失败)
    """
    print("🔍 开始检查 AI 代码约束...")

    # 获取修改和新增的文件
    modified_files = get_modified_files()
    new_files = get_new_files()

    # 检查禁止的修改
    forbidden_modifications = check_forbidden_modifications(modified_files)

    # 检查允许的模式
    not_allowed_files = check_allowed_patterns(new_files)

    # 打印检查结果
    print_check_results(
        modified_files, new_files, forbidden_modifications, not_allowed_files
    )

    # 返回结果
    if forbidden_modifications or not_allowed_files:
        print("\n❌ 检查失败，请修复上述问题")
        return 1
    else:
        print("\n✅ 检查通过，所有约束都已遵守")
        return 0


if __name__ == "__main__":
    sys.exit(main())
