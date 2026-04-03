#!/usr/bin/env python3
import os
import re
from typing import Dict, Optional


class TestConfigWizard:
    """测试配置向导"""

    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "envs")
        self.example_file = os.path.join(self.config_dir, ".env.example")
        self.target_file = os.path.join(self.config_dir, ".env")

    def load_example_config(self) -> Dict[str, str]:
        """加载示例配置文件"""
        config = {}

        if os.path.exists(self.example_file):
            with open(self.example_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            config[key.strip()] = value.strip()

        return config

    def get_valid_input(
        self, prompt: str, default: str, validation_pattern: Optional[str] = None
    ) -> str:
        """获取有效的用户输入"""
        while True:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default

            if validation_pattern:
                if re.match(validation_pattern, user_input):
                    return user_input
                else:
                    print("输入格式无效，请重新输入")
            else:
                return user_input

    def get_yes_no_input(self, prompt: str, default: bool = True) -> bool:
        """获取是/否输入"""
        default_str = "Y" if default else "N"
        while True:
            user_input = input(f"{prompt} [{default_str}]: ").strip().upper()
            if not user_input:
                return default
            if user_input in ["Y", "YES"]:
                return True
            if user_input in ["N", "NO"]:
                return False
            print("请输入 Y 或 N")

    def run(self):
        """运行配置向导"""
        print("=" * 60)
        print("        测试配置向导")
        print("=" * 60)
        print("本向导将帮助您快速配置测试环境")
        print("\n")

        # 加载示例配置
        config = self.load_example_config()

        # 基础配置
        print("=== 基础配置 ===")
        config["BASE_URL"] = self.get_valid_input(
            "请输入测试基础URL", config.get("BASE_URL", "https://demo.playwright.dev/todomvc")
        )

        browser_choices = ["chromium", "firefox", "webkit"]
        print(f"\n浏览器选择: {', '.join(browser_choices)}")
        config["BROWSER"] = self.get_valid_input(
            "请输入浏览器类型", config.get("BROWSER", "chromium"), f"({'|'.join(browser_choices)})"
        )

        config["HEADLESS"] = str(
            self.get_yes_no_input(
                "是否以无头模式运行浏览器", config.get("HEADLESS", "false").lower() == "true"
            )
        ).lower()

        config["SLOW_MO"] = self.get_valid_input(
            "请输入浏览器操作延迟（毫秒）", config.get("SLOW_MO", "0"), r"^\d+$"
        )

        config["TIMEOUT"] = self.get_valid_input(
            "请输入默认超时时间（毫秒）", config.get("TIMEOUT", "30000"), r"^\d+$"
        )

        # 视口配置
        print("\n=== 视口配置 ===")
        config["VIEWPORT_WIDTH"] = self.get_valid_input(
            "请输入视口宽度", config.get("VIEWPORT_WIDTH", "1920"), r"^\d+$"
        )

        config["VIEWPORT_HEIGHT"] = self.get_valid_input(
            "请输入视口高度", config.get("VIEWPORT_HEIGHT", "1080"), r"^\d+$"
        )

        # API 配置
        print("\n=== API 配置 ===")
        config["API_BASE_URL"] = self.get_valid_input(
            "请输入API基础URL", config.get("API_BASE_URL", "https://api.example.com")
        )

        config["API_TIMEOUT"] = self.get_valid_input(
            "请输入API超时时间（毫秒）", config.get("API_TIMEOUT", "30000"), r"^\d+$"
        )

        # 录屏配置
        print("\n=== 录屏配置 ===")
        config["VIDEO_ENABLED"] = str(
            self.get_yes_no_input(
                "是否启用录屏功能", config.get("VIDEO_ENABLED", "false").lower() == "true"
            )
        ).lower()

        # 数据库配置
        print("\n=== 数据库配置 ===")
        if self.get_yes_no_input("是否配置数据库连接", False):
            config["DB_HOST"] = self.get_valid_input(
                "请输入数据库主机", config.get("DB_HOST", "localhost")
            )
            config["DB_PORT"] = self.get_valid_input(
                "请输入数据库端口", config.get("DB_PORT", "3306"), r"^\d+$"
            )
            config["DB_USER"] = self.get_valid_input(
                "请输入数据库用户名", config.get("DB_USER", "root")
            )
            config["DB_PASSWORD"] = input("请输入数据库密码: ").strip()
            config["DB_NAME"] = self.get_valid_input(
                "请输入数据库名称", config.get("DB_NAME", "test_db")
            )

        # 测试环境配置
        print("\n=== 测试环境配置 ===")
        env_choices = ["development", "staging", "production"]
        print(f"环境选择: {', '.join(env_choices)}")
        config["TEST_ENV"] = self.get_valid_input(
            "请输入测试环境", config.get("TEST_ENV", "development"), f"({'|'.join(env_choices)})"
        )

        # 显示配置摘要
        print("\n" + "=" * 60)
        print("        配置摘要")
        print("=" * 60)
        for key, value in config.items():
            # 隐藏密码
            display_value = "******" if key == "DB_PASSWORD" else value
            print(f"{key}: {display_value}")

        # 确认保存
        if self.get_yes_no_input("是否保存配置", True):
            # 保存配置文件
            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write("# ===========================================\n")
                f.write("# 测试框架环境变量配置\n")
                f.write("# 由配置向导生成\n")
                f.write("# ===========================================\n\n")

                # 按类别分组写入
                categories = {
                    "基础配置": ["BASE_URL", "BROWSER", "HEADLESS", "SLOW_MO", "TIMEOUT"],
                    "视口配置": ["VIEWPORT_WIDTH", "VIEWPORT_HEIGHT"],
                    "API 配置": ["API_BASE_URL", "API_TIMEOUT"],
                    "录屏配置": ["VIDEO_ENABLED"],
                    "数据库配置": ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"],
                    "测试环境配置": ["TEST_ENV"],
                }

                for category, keys in categories.items():
                    f.write(f"# {category}\n")
                    for key in keys:
                        if key in config:
                            f.write(f"{key}={config[key]}\n")
                    f.write("\n")

            print(f"\n配置已保存到: {self.target_file}")
            print("\n配置向导完成！")
        else:
            print("\n配置已取消")


if __name__ == "__main__":
    wizard = TestConfigWizard()
    wizard.run()
