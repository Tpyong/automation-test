"""
操作审计日志模块

提供完整的操作审计功能，记录所有关键操作，支持合规检查和审计报告生成
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.common.logger import get_logger

logger = get_logger(__name__)


class AuditEventType(Enum):
    """审计事件类型"""

    TEST_START = "test_start"
    TEST_END = "test_end"
    TEST_FAILURE = "test_failure"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIG_CHANGE = "config_change"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"
    USER_ACTION = "user_action"


class AuditSeverity(Enum):
    """审计事件严重级别"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """审计事件"""

    event_type: AuditEventType
    severity: AuditSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    user: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "source": self.source,
            "target": self.target,
            "details": self.details,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
        }


class AuditLogger:
    """审计日志记录器"""

    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.events: List[AuditEvent] = []
        self._current_session: Optional[str] = None

    def start_session(self, session_id: Optional[str] = None) -> str:
        """开始审计会话"""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self._current_session = session_id

        self.log_event(
            event_type=AuditEventType.SYSTEM_EVENT,
            severity=AuditSeverity.LOW,
            message=f"审计会话开始: {session_id}",
            details={"session_id": session_id},
        )

        logger.info(f"审计会话开始: {session_id}")
        return session_id

    def end_session(self) -> None:
        """结束审计会话"""
        if self._current_session:
            self.log_event(
                event_type=AuditEventType.SYSTEM_EVENT,
                severity=AuditSeverity.LOW,
                message=f"审计会话结束: {self._current_session}",
                details={"session_id": self._current_session},
            )

            # 保存审计日志
            self.save_audit_log()

            logger.info(f"审计会话结束: {self._current_session}")
            self._current_session = None

    def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        message: str,
        user: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> AuditEvent:
        """记录审计事件"""
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            user=user,
            source=source,
            target=target,
            details=details or {},
            session_id=self._current_session,
            correlation_id=correlation_id,
        )

        self.events.append(event)

        # 记录到日志
        log_level = {
            AuditSeverity.LOW: logger.debug,
            AuditSeverity.MEDIUM: logger.info,
            AuditSeverity.HIGH: logger.warning,
            AuditSeverity.CRITICAL: logger.error,
        }.get(severity, logger.info)

        log_level(f"[AUDIT] {event_type.value}: {message}")

        return event

    def log_test_start(self, test_name: str, details: Optional[Dict[str, Any]] = None) -> None:
        """记录测试开始"""
        self.log_event(
            event_type=AuditEventType.TEST_START,
            severity=AuditSeverity.LOW,
            message=f"测试开始: {test_name}",
            target=test_name,
            details=details,
        )

    def log_test_end(self, test_name: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        """记录测试结束"""
        severity = AuditSeverity.LOW if status == "passed" else AuditSeverity.MEDIUM

        self.log_event(
            event_type=AuditEventType.TEST_END,
            severity=severity,
            message=f"测试结束: {test_name} - {status}",
            target=test_name,
            details={"status": status, **(details or {})},
        )

    def log_test_failure(self, test_name: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        """记录测试失败"""
        self.log_event(
            event_type=AuditEventType.TEST_FAILURE,
            severity=AuditSeverity.HIGH,
            message=f"测试失败: {test_name}",
            target=test_name,
            details={"error": error, **(details or {})},
        )

    def log_data_access(self, data_type: str, action: str, user: Optional[str] = None) -> None:
        """记录数据访问"""
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.MEDIUM,
            message=f"数据访问: {data_type} - {action}",
            user=user,
            target=data_type,
            details={"action": action},
        )

    def log_data_modification(
        self,
        data_type: str,
        action: str,
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """记录数据修改"""
        self.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.HIGH,
            message=f"数据修改: {data_type} - {action}",
            user=user,
            target=data_type,
            details={"action": action, **(details or {})},
        )

    def log_config_change(self, config_key: str, old_value: Any, new_value: Any, user: Optional[str] = None) -> None:
        """记录配置变更"""
        self.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            severity=AuditSeverity.HIGH,
            message=f"配置变更: {config_key}",
            user=user,
            target=config_key,
            details={"old_value": str(old_value), "new_value": str(new_value)},
        )

    def log_security_event(
        self,
        event: str,
        severity: AuditSeverity = AuditSeverity.HIGH,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """记录安全事件"""
        self.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=severity,
            message=f"安全事件: {event}",
            details=details or {},
        )

    def get_events_by_type(self, event_type: AuditEventType) -> List[AuditEvent]:
        """按类型获取事件"""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_by_severity(self, severity: AuditSeverity) -> List[AuditEvent]:
        """按严重级别获取事件"""
        return [e for e in self.events if e.severity == severity]

    def get_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AuditEvent]:
        """按日期范围获取事件"""
        return [e for e in self.events if start_date <= e.timestamp <= end_date]

    def save_audit_log(self, filename: Optional[str] = None) -> str:
        """保存审计日志"""
        if filename is None:
            filename = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        log_file = self.log_dir / filename

        data = {
            "session_id": self._current_session,
            "generated_at": datetime.now().isoformat(),
            "total_events": len(self.events),
            "events": [e.to_dict() for e in self.events],
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"审计日志已保存: {log_file}")
        return str(log_file)

    def generate_audit_report(self) -> Dict[str, Any]:
        """生成审计报告"""
        report: Dict[str, Any] = {
            "session_id": self._current_session,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_events": len(self.events),
                "by_type": {},
                "by_severity": {},
                "by_hour": {},
            },
            "critical_events": [],
            "warnings": [],
        }

        # 按类型统计
        for event_type in AuditEventType:
            count = len(self.get_events_by_type(event_type))
            if count > 0:
                report["summary"]["by_type"][event_type.value] = count

        # 按严重级别统计
        for severity in AuditSeverity:
            count = len(self.get_events_by_severity(severity))
            if count > 0:
                report["summary"]["by_severity"][severity.value] = count

        # 按小时统计
        for event in self.events:
            hour = event.timestamp.strftime("%Y-%m-%d %H:00")
            report["summary"]["by_hour"][hour] = report["summary"]["by_hour"].get(hour, 0) + 1

        # 收集关键事件
        critical_events = self.get_events_by_severity(AuditSeverity.CRITICAL)
        report["critical_events"] = [e.to_dict() for e in critical_events]

        # 收集警告
        high_severity_events = self.get_events_by_severity(AuditSeverity.HIGH)
        report["warnings"] = [e.to_dict() for e in high_severity_events]

        return report


class DataRetentionPolicy:
    """数据保留策略"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.retention_days = {
            AuditSeverity.LOW: 30,
            AuditSeverity.MEDIUM: 90,
            AuditSeverity.HIGH: 365,
            AuditSeverity.CRITICAL: 2555,  # 7年
        }

    def set_retention_period(self, severity: AuditSeverity, days: int) -> None:
        """设置保留期限"""
        self.retention_days[severity] = days
        logger.info(f"设置 {severity.value} 级别事件保留期限: {days} 天")

    def cleanup_expired_events(self) -> int:
        """清理过期事件"""
        now = datetime.now()
        initial_count = len(self.audit_logger.events)

        self.audit_logger.events = [event for event in self.audit_logger.events if self._should_retain(event, now)]

        removed_count = initial_count - len(self.audit_logger.events)
        if removed_count > 0:
            logger.info(f"已清理 {removed_count} 个过期审计事件")

        return removed_count

    def _should_retain(self, event: AuditEvent, now: datetime) -> bool:
        """判断事件是否应该保留"""
        retention_days = self.retention_days.get(event.severity, 30)
        expiry_date = event.timestamp + timedelta(days=retention_days)
        return now < expiry_date


# 全局审计日志记录器
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(log_dir: str = "logs/audit") -> AuditLogger:
    """获取全局审计日志记录器"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(log_dir)
    return _audit_logger
