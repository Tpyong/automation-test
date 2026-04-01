#!/usr/bin/env python3
"""
敏感信息管理工具
用于加密/解密环境变量文件
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils.logger import get_logger
from core.utils.secrets_manager import get_secrets_manager

logger = get_logger(__name__)


def print_usage() -> None:
    """打印使用说明"""
    print("""
敏感信息管理工具

使用方法:
    python scripts/secrets_tool.py encrypt <env_file> [output_file]
    python scripts/secrets_tool.py decrypt <env_file> [output_file]
    python scripts/secrets_tool.py encrypt-value <plaintext>
    python scripts/secrets_tool.py decrypt-value <ciphertext>

示例:
    # 加密 .env 文件
    python scripts/secrets_tool.py encrypt .env
    
    # 加密并保存到新文件
    python scripts/secrets_tool.py encrypt .env .env.encrypted
    
    # 解密 .env 文件
    python scripts/secrets_tool.py decrypt .env
    
    # 加密单个值
    python scripts/secrets_tool.py encrypt-value "my-password"
    
    # 解密单个值
    python scripts/secrets_tool.py decrypt-value "ENC:gAAAAAB..."
""")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    manager = get_secrets_manager()

    try:
        if command == "encrypt":
            if len(sys.argv) < 3:
                print("错误: 请指定要加密的文件")
                print_usage()
                sys.exit(1)

            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None

            manager.encrypt_env_file(input_file, output_file)
            print(f"✅ 文件已加密: {output_file or input_file}")

        elif command == "decrypt":
            if len(sys.argv) < 3:
                print("错误: 请指定要解密的文件")
                print_usage()
                sys.exit(1)

            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None

            manager.decrypt_env_file(input_file, output_file)
            print(f"✅ 文件已解密: {output_file or input_file}")

        elif command == "encrypt-value":
            if len(sys.argv) < 3:
                print("错误: 请指定要加密的值")
                print_usage()
                sys.exit(1)

            plaintext = sys.argv[2]
            encrypted = manager.encrypt(plaintext)
            print(f"✅ 加密结果:\n{encrypted}")

        elif command == "decrypt-value":
            if len(sys.argv) < 3:
                print("错误: 请指定要解密的值")
                print_usage()
                sys.exit(1)

            ciphertext = sys.argv[2]
            decrypted = manager.decrypt(ciphertext)
            print(f"✅ 解密结果:\n{decrypted}")

        else:
            print(f"错误: 未知命令 '{command}'")
            print_usage()
            sys.exit(1)

    except Exception as e:
        print(f"❌ 错误: {e}")
        logger.error(f"操作失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
