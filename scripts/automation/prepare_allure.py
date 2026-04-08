"""
Allure 报告准备工具

用于在生成 Allure 报告前自动复制 categories.json 配置文件
"""

import os
import shutil
from pathlib import Path

from config.settings import Settings


def prepare_allure_report():
    """准备 Allure 报告所需的配置文件"""

    # 加载配置
    settings = Settings(validate=False)

    # 项目根目录
    project_root = Path(__file__).parent.parent

    # 源文件位置（配置目录）
    source_file = project_root / "config" / "categories.json"

    # 目标文件位置（Allure 结果目录）
    allure_output_dir = os.getenv("ALLURE_OUTPUT_DIR", settings.allure_output_dir)
    target_dir = project_root / allure_output_dir
    target_file = target_dir / "categories.json"

    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 复制配置文件
    if source_file.exists():
        shutil.copy2(source_file, target_file)
        print(f"✓ 已复制 categories.json 到 {target_file}")
    else:
        print(f"⚠ 警告：未找到配置文件 {source_file}")
        print("  请确保 config/categories.json 存在")


if __name__ == "__main__":
    prepare_allure_report()
