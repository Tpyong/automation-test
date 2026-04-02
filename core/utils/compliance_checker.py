"""
合规检查模块

提供合规性检查、数据保护和隐私合规功能
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.utils.logger import get_logger

logger = get_logger(__name__)


class ComplianceStandard(Enum):
    """合规标准"""

    GDPR = "gdpr"  # 欧盟数据保护条例
    CCPA = "ccpa"  # 加州消费者隐私法
    HIPAA = "hipaa"  # 医疗保险便携性和责任法案
    PCI_DSS = "pci_dss"  # 支付卡行业数据安全标准
    SOC2 = "soc2"  # 服务组织控制报告
    ISO27001 = "iso27001"  # 信息安全管理体系
    GDPR_CHINA = "gdpr_china"  # 中国网络安全法


@dataclass
class ComplianceRule:
    """合规规则"""

    rule_id: str
    name: str
    description: str
    standard: ComplianceStandard
    severity: str  # low, medium, high, critical
    check_function: str
    remediation: str
    enabled: bool = True


@dataclass
class ComplianceViolation:
    """合规违规"""

    rule: ComplianceRule
    timestamp: datetime
    details: Dict[str, Any]
    severity: str
    remediation: str


class ComplianceChecker:
    """合规检查器"""

    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: List[ComplianceViolation] = []
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """加载默认合规规则"""
        default_rules = [
            ComplianceRule(
                rule_id="GDPR-001",
                name="个人数据加密",
                description="个人敏感数据必须加密存储",
                standard=ComplianceStandard.GDPR,
                severity="high",
                check_function="check_data_encryption",
                remediation="使用强加密算法（如AES-256）加密敏感数据",
            ),
            ComplianceRule(
                rule_id="GDPR-002",
                name="数据访问控制",
                description="必须实施适当的数据访问控制",
                standard=ComplianceStandard.GDPR,
                severity="high",
                check_function="check_access_control",
                remediation="实施基于角色的访问控制（RBAC）",
            ),
            ComplianceRule(
                rule_id="GDPR-003",
                name="数据保留期限",
                description="个人数据不得超过必要期限保存",
                standard=ComplianceStandard.GDPR,
                severity="medium",
                check_function="check_data_retention",
                remediation="实施数据保留策略，定期清理过期数据",
            ),
            ComplianceRule(
                rule_id="PCI-001",
                name="支付数据保护",
                description="支付卡数据必须符合PCI DSS标准",
                standard=ComplianceStandard.PCI_DSS,
                severity="critical",
                check_function="check_payment_data",
                remediation="使用PCI兼容的支付处理系统",
            ),
            ComplianceRule(
                rule_id="SEC-001",
                name="密码强度",
                description="密码必须满足最小强度要求",
                standard=ComplianceStandard.ISO27001,
                severity="medium",
                check_function="check_password_strength",
                remediation="要求密码至少8位，包含大小写字母、数字和特殊字符",
            ),
            ComplianceRule(
                rule_id="SEC-002",
                name="会话超时",
                description="用户会话必须设置合理的超时时间",
                standard=ComplianceStandard.ISO27001,
                severity="medium",
                check_function="check_session_timeout",
                remediation="设置会话超时时间不超过30分钟",
            ),
            ComplianceRule(
                rule_id="SEC-003",
                name="敏感数据脱敏",
                description="日志中不得包含敏感数据明文",
                standard=ComplianceStandard.GDPR,
                severity="high",
                check_function="check_data_masking",
                remediation="在记录日志前对敏感数据进行脱敏处理",
            ),
            ComplianceRule(
                rule_id="SEC-004",
                name="HTTPS强制",
                description="所有数据传输必须使用HTTPS",
                standard=ComplianceStandard.ISO27001,
                severity="high",
                check_function="check_https_usage",
                remediation="强制使用HTTPS，禁用HTTP",
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

        logger.info(f"已加载 {len(default_rules)} 条默认合规规则")

    def add_rule(self, rule: ComplianceRule) -> None:
        """添加合规规则"""
        self.rules[rule.rule_id] = rule
        logger.info(f"添加合规规则: {rule.rule_id} - {rule.name}")

    def check_data_encryption(self, data: Dict[str, Any]) -> bool:
        """检查数据是否加密"""
        sensitive_fields = ["password", "credit_card", "ssn", "email"]

        for field in sensitive_fields:
            if field in data:
                value = str(data[field])
                # 简单检查：加密数据通常以特定前缀开头
                if not value.startswith(("ENC:", "AES:", "RSA:")):
                    return False

        return True

    def check_access_control(self, context: Dict[str, Any]) -> bool:
        """检查访问控制"""
        required_fields = ["user_id", "role", "permissions"]
        return all(field in context for field in required_fields)

    def check_data_retention(self, data_age_days: int, max_days: int = 90) -> bool:
        """检查数据保留期限"""
        return data_age_days <= max_days

    def check_password_strength(self, password: str) -> bool:
        """检查密码强度"""
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return all([has_upper, has_lower, has_digit, has_special])

    def check_session_timeout(self, timeout_minutes: int) -> bool:
        """检查会话超时"""
        return 0 < timeout_minutes <= 30

    def check_data_masking(self, log_data: str) -> bool:
        """检查数据脱敏"""
        # 检查是否包含敏感数据模式
        sensitive_patterns = [
            r"\b\d{16}\b",  # 信用卡号
            r"\b\d{17}[\dXx]\b",  # 身份证号
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 邮箱
        ]

        import re

        for pattern in sensitive_patterns:
            if re.search(pattern, log_data):
                return False

        return True

    def check_https_usage(self, url: str) -> bool:
        """检查HTTPS使用"""
        return url.startswith("https://")

    def run_compliance_check(self, context: Dict[str, Any]) -> List[ComplianceViolation]:
        """运行合规检查"""
        violations = []

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            try:
                check_method = getattr(self, rule.check_function, None)
                if check_method is None:
                    logger.warning(f"检查函数不存在: {rule.check_function}")
                    continue

                # 执行检查
                passed = check_method(context)

                if not passed:
                    violation = ComplianceViolation(
                        rule=rule,
                        timestamp=datetime.now(),
                        details={"context": context},
                        severity=rule.severity,
                        remediation=rule.remediation,
                    )
                    violations.append(violation)

                    logger.warning(f"合规违规: {rule.rule_id} - {rule.name}")

            except Exception as e:
                logger.error(f"合规检查失败: {rule.rule_id}, 错误: {e}")

        self.violations.extend(violations)
        return violations

    def get_violations_by_standard(self, standard: ComplianceStandard) -> List[ComplianceViolation]:
        """按标准获取违规"""
        return [v for v in self.violations if v.rule.standard == standard]

    def get_violations_by_severity(self, severity: str) -> List[ComplianceViolation]:
        """按严重级别获取违规"""
        return [v for v in self.violations if v.severity == severity]

    def generate_compliance_report(self) -> Dict[str, Any]:
        """生成合规报告"""
        report: Dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_rules": len(self.rules),
                "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
                "total_violations": len(self.violations),
                "by_standard": {},
                "by_severity": {},
            },
            "violations": [],
            "recommendations": [],
        }
        # 为嵌套字典添加显式类型注解
        report["summary"]["by_standard"] = {}
        report["summary"]["by_severity"] = {}
        report["violations"] = []
        report["recommendations"] = []

        # 按标准统计
        for standard in ComplianceStandard:
            count = len(self.get_violations_by_standard(standard))
            if count > 0:
                report["summary"]["by_standard"][standard.value] = count

        # 按严重级别统计
        for severity in ["low", "medium", "high", "critical"]:
            count = len(self.get_violations_by_severity(severity))
            if count > 0:
                report["summary"]["by_severity"][severity] = count

        # 违规详情
        for violation in self.violations:
            report["violations"].append(
                {
                    "rule_id": violation.rule.rule_id,
                    "rule_name": violation.rule.name,
                    "standard": violation.rule.standard.value,
                    "severity": violation.severity,
                    "timestamp": violation.timestamp.isoformat(),
                    "remediation": violation.remediation,
                }
            )

        # 生成建议
        if report["summary"]["total_violations"] > 0:
            report["recommendations"].append(
                {
                    "priority": "high",
                    "action": "立即处理所有高严重级别违规",
                    "details": f"发现 {report['summary']['by_severity'].get('high', 0)} 个高级别违规",
                }
            )

        return report

    def save_compliance_report(self, output_file: Optional[str] = None) -> str:
        """保存合规报告"""
        if output_file is None:
            output_file = (
                f"reports/compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.generate_compliance_report()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"合规报告已保存: {output_path}")
        return str(output_path)


# 全局合规检查器
_compliance_checker: Optional[ComplianceChecker] = None


def get_compliance_checker() -> ComplianceChecker:
    """获取全局合规检查器"""
    global _compliance_checker
    if _compliance_checker is None:
        _compliance_checker = ComplianceChecker()
    return _compliance_checker
