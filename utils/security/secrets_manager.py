"""
敏感信息管理模块
提供配置加密/解密功能
"""

import base64
import binascii
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils.common.logger import get_logger

logger = get_logger(__name__)


class SecretsManager:
    """敏感信息管理器"""

    # 加密标记前缀
    ENCRYPTED_PREFIX = "ENC:"

    def __init__(self, key: Optional[bytes] = None, salt: Optional[bytes] = None):
        """
        初始化 SecretsManager

        Args:
            key: 加密密钥（可选，从环境变量或密钥文件读取）
            salt: 盐值（可选）
        """
        self.salt = salt or self._get_or_generate_salt()
        self.key = key or self._get_or_generate_key()
        self.cipher = Fernet(self.key)
        logger.info("SecretsManager 初始化完成")

    def _get_or_generate_salt(self) -> bytes:
        """获取或生成盐值"""
        project_root = Path(__file__).parent.parent.parent
        salt_file = project_root / "config" / "secrets" / ".secrets.salt"

        # 确保目录存在
        salt_file.parent.mkdir(parents=True, exist_ok=True)

        if salt_file.exists():
            with open(salt_file, "rb") as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(salt_file, "wb") as f:
                f.write(salt)
            logger.info(f"生成新的盐值文件: {salt_file}")
            return salt

    def _get_or_generate_key(self) -> bytes:
        """获取或生成加密密钥"""
        # 优先从环境变量获取密钥
        env_key = os.getenv("TEST_SECRET_KEY")
        if env_key:
            try:
                return base64.urlsafe_b64decode(env_key)
            except Exception as e:
                logger.warning(f"环境变量中的密钥无效: {e}")

        # 其次从密钥文件获取
        project_root = Path(__file__).parent.parent.parent
        key_file = project_root / "config" / "secrets" / ".secrets.key"
        
        # 确保目录存在
        key_file.parent.mkdir(parents=True, exist_ok=True)
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()

        # 最后，从密码派生密钥
        password = os.getenv("TEST_MASTER_PASSWORD", "default-master-password-change-me")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        # 保存密钥文件
        with open(key_file, "wb") as f:
            f.write(key)
        logger.info(f"生成新的密钥文件: {key_file}")
        logger.warning(f"⚠️  请妥善保管 {key_file} 和 {key_file.with_suffix('.salt')} 文件，不要提交到版本控制！")

        return key

    def encrypt(self, plaintext: str) -> str:
        """
        加密字符串

        Args:
            plaintext: 明文

        Returns:
            加密后的字符串（带 ENC: 前缀）
        """
        encrypted = self.cipher.encrypt(plaintext.encode())
        encrypted_b64 = base64.urlsafe_b64encode(encrypted).decode()
        return f"{self.ENCRYPTED_PREFIX}{encrypted_b64}"

    def decrypt(self, ciphertext: str) -> str:
        """
        解密字符串

        Args:
            ciphertext: 密文（带 ENC: 前缀）

        Returns:
            明文
        """
        if not ciphertext.startswith(self.ENCRYPTED_PREFIX):
            return ciphertext

        try:
            encrypted_b64 = ciphertext[len(self.ENCRYPTED_PREFIX) :]
            encrypted = base64.urlsafe_b64decode(encrypted_b64)
            plaintext = self.cipher.decrypt(encrypted).decode()
            return plaintext
        except InvalidToken:
            logger.error("解密失败: 无效的加密令牌")
            raise ValueError("解密失败: 无效的加密令牌，请检查密钥是否正确")
        except (binascii.Error, ValueError) as e:
            logger.error(f"解密失败: 数据格式错误 - {e}")
            raise ValueError(f"解密失败: 数据格式错误 - {e}")
        except Exception as e:
            logger.error(f"解密失败: 未知错误 - {e}")
            raise

    def is_encrypted(self, value: str) -> bool:
        """检查值是否已加密"""
        return isinstance(value, str) and value.startswith(self.ENCRYPTED_PREFIX)

    def encrypt_env_file(self, input_path: str, output_path: Optional[str] = None):
        """
        加密环境变量文件中的敏感信息

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选，默认覆盖输入文件）
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 敏感字段列表
        sensitive_fields = [
            "password",
            "pass",
            "secret",
            "token",
            "key",
            "api_key",
            "apikey",
            "authorization",
            "auth",
            "credential",
            "db_password",
        ]

        lines = []
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key_lower = key.lower()

                    # 检查是否是敏感字段
                    is_sensitive = any(field in key_lower for field in sensitive_fields)

                    if is_sensitive and not self.is_encrypted(value):
                        encrypted_value = self.encrypt(value)
                        lines.append(f"{key}={encrypted_value}")
                        logger.info(f"加密字段: {key}")
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

        output_file = Path(output_path) if output_path else input_file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        logger.info(f"环境变量文件已加密: {output_file}")

    def decrypt_env_file(self, input_path: str, output_path: Optional[str] = None):
        """
        解密环境变量文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选，默认覆盖输入文件）
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")

        lines = []
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if self.is_encrypted(value):
                        decrypted_value = self.decrypt(value)
                        lines.append(f"{key}={decrypted_value}")
                        logger.info(f"解密字段: {key}")
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

        output_file = Path(output_path) if output_path else input_file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        logger.info(f"环境变量文件已解密: {output_file}")


# 全局 SecretsManager 实例
_SECRETS_MANAGER: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """
    获取全局 SecretsManager 实例

    Returns:
        SecretsManager 实例
    """
    global _SECRETS_MANAGER
    if _SECRETS_MANAGER is None:
        _SECRETS_MANAGER = SecretsManager()
    return _SECRETS_MANAGER


def decrypt_value(value: str) -> str:
    """
    便捷函数：解密单个值

    Args:
        value: 可能加密的值

    Returns:
        解密后的值
    """
    manager = get_secrets_manager()
    return manager.decrypt(value)
