"""
数据脱敏模块

提供敏感数据脱敏和检测功能
"""

import re
from typing import Any, Dict, List, Optional

from core.utils.logger import get_logger

logger = get_logger(__name__)


class DataMaskingPatterns:
    """数据脱敏模式"""

    # 身份证号
    ID_CARD_PATTERN = r"(\d{4})\d{10}(\d{4})"
    ID_CARD_REPLACEMENT = r"\1**********\2"

    # 手机号
    PHONE_PATTERN = r"(\d{3})\d{4}(\d{4})"
    PHONE_REPLACEMENT = r"\1****\2"

    # 银行卡号
    BANK_CARD_PATTERN = r"(\d{4})\d{8,12}(\d{4})"
    BANK_CARD_REPLACEMENT = r"\1************\2"

    # 邮箱
    EMAIL_PATTERN = r"(\w{2})\w+(@\w+)"
    EMAIL_REPLACEMENT = r"\1***\2"

    # IP地址
    IP_PATTERN = r"(\d{1,3}\.\d{1,3}\.)\d{1,3}\.\d{1,3}"
    IP_REPLACEMENT = r"\1***.***"

    # 密码
    PASSWORD_PATTERN = r"(password|pwd|passwd)\s*[=:]\s*[^\s&]+"
    PASSWORD_REPLACEMENT = r"\1=********"


class DataMasker:
    """数据脱敏器"""

    def __init__(self):
        self.patterns = {
            "id_card": (
                DataMaskingPatterns.ID_CARD_PATTERN,
                DataMaskingPatterns.ID_CARD_REPLACEMENT,
            ),
            "phone": (DataMaskingPatterns.PHONE_PATTERN, DataMaskingPatterns.PHONE_REPLACEMENT),
            "bank_card": (
                DataMaskingPatterns.BANK_CARD_PATTERN,
                DataMaskingPatterns.BANK_CARD_REPLACEMENT,
            ),
            "email": (DataMaskingPatterns.EMAIL_PATTERN, DataMaskingPatterns.EMAIL_REPLACEMENT),
            "ip": (DataMaskingPatterns.IP_PATTERN, DataMaskingPatterns.IP_REPLACEMENT),
            "password": (
                DataMaskingPatterns.PASSWORD_PATTERN,
                DataMaskingPatterns.PASSWORD_REPLACEMENT,
            ),
        }

    def mask_string(self, text: str, patterns: Optional[List[str]] = None) -> str:
        """对字符串进行脱敏处理"""
        if not text:
            return text

        result = text
        patterns_to_apply = patterns or list(self.patterns.keys())

        for pattern_name in patterns_to_apply:
            if pattern_name in self.patterns:
                pattern, replacement = self.patterns[pattern_name]
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def mask_dict(
        self, data: Dict[str, Any], sensitive_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """对字典进行脱敏处理"""
        if not data:
            return data

        result: Dict[str, Any] = {}
        sensitive_fields = sensitive_fields or []

        for key, value in data.items():
            if key in sensitive_fields:
                # 敏感字段完全脱敏
                result[key] = "********"
            elif isinstance(value, str):
                result[key] = self.mask_string(value)
            elif isinstance(value, dict):
                result[key] = self.mask_dict(value, sensitive_fields)
            elif isinstance(value, list):
                result[key] = self.mask_list(value, sensitive_fields)
            else:
                result[key] = value

        return result

    def mask_list(self, data: List[Any], sensitive_fields: Optional[List[str]] = None) -> List[Any]:
        """对列表进行脱敏处理"""
        if not data:
            return data

        result: List[Any] = []
        for item in data:
            if isinstance(item, str):
                result.append(self.mask_string(item))
            elif isinstance(item, dict):
                result.append(self.mask_dict(item, sensitive_fields))
            elif isinstance(item, list):
                result.append(self.mask_list(item, sensitive_fields))
            else:
                result.append(item)

        return result

    def detect_sensitive_data(self, text: str) -> List[Dict[str, Any]]:
        """检测文本中的敏感数据"""
        findings = []

        for pattern_name, (pattern, _) in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                findings.append(
                    {
                        "type": pattern_name,
                        "value": match.group(),
                        "position": (match.start(), match.end()),
                    }
                )

        return findings


# 全局脱敏器实例
_data_masker: Optional[DataMasker] = None


def get_data_masker() -> DataMasker:
    """获取全局数据脱敏器实例"""
    global _data_masker
    if _data_masker is None:
        _data_masker = DataMasker()
    return _data_masker
