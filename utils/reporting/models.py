"""报告数据模型"""

from datetime import datetime
from typing import Any, Dict, Optional


class TestResult:
    """单个测试结果"""

    def __init__(self, nodeid: str, outcome: str, duration: float = 0.0):
        self.nodeid = nodeid
        self.outcome = outcome
        self.duration = duration
        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None
        self.error_msg: Optional[str] = None

        # 解析 nodeid 获取模块和测试名
        parts = nodeid.split("::")
        self.file_path = parts[0] if len(parts) > 0 else ""
        self.class_name = parts[1] if len(parts) > 1 else ""
        self.test_name = parts[-1] if len(parts) > 2 else nodeid

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodeid": self.nodeid,
            "outcome": self.outcome,
            "duration": self.duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "stop_time": self.stop_time.isoformat() if self.stop_time else None,
            "error_msg": self.error_msg,
            "file_path": self.file_path,
            "class_name": self.class_name,
            "test_name": self.test_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        """从字典创建实例"""
        result = cls(data["nodeid"], data["outcome"], data.get("duration", 0.0))
        if data.get("start_time"):
            result.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("stop_time"):
            result.stop_time = datetime.fromisoformat(data["stop_time"])
        result.error_msg = data.get("error_msg")
        return result
