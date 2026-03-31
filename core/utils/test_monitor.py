"""
测试监控模块

提供测试执行监控、指标收集和性能分析功能
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TestMetrics:
    """测试指标"""

    test_name: str
    start_time: float
    end_time: float = 0.0
    status: str = "running"  # running, passed, failed, skipped
    error_message: Optional[str] = None

    @property
    def duration(self) -> float:
        """获取测试执行时长"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time


@dataclass
class TestSessionMetrics:
    """测试会话指标"""

    session_id: str
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    test_metrics: List[TestMetrics] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """获取会话执行时长"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def pass_rate(self) -> float:
        """获取通过率"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def avg_test_duration(self) -> float:
        """获取平均测试执行时长"""
        if not self.test_metrics:
            return 0.0
        return sum(m.duration for m in self.test_metrics) / len(self.test_metrics)


class TestMonitor:
    """测试监控器"""

    def __init__(self, output_dir: str = "reports/monitoring"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[TestSessionMetrics] = None
        self._current_test: Optional[TestMetrics] = None

    def start_session(self, session_id: Optional[str] = None) -> TestSessionMetrics:
        """开始测试会话监控"""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.current_session = TestSessionMetrics(session_id=session_id)
        logger.info(f"测试监控会话开始: {session_id}")
        return self.current_session

    def end_session(self) -> TestSessionMetrics:
        """结束测试会话监控"""
        if self.current_session is None:
            raise RuntimeError("没有活动的测试会话")

        self.current_session.end_time = time.time()
        logger.info(
            f"测试监控会话结束: {self.current_session.session_id}, "
            f"总测试数: {self.current_session.total_tests}, "
            f"通过: {self.current_session.passed_tests}, "
            f"失败: {self.current_session.failed_tests}, "
            f"通过率: {self.current_session.pass_rate:.1f}%"
        )

        # 保存监控数据
        self._save_session_metrics()

        return self.current_session

    def start_test(self, test_name: str) -> TestMetrics:
        """开始测试监控"""
        if self.current_session is None:
            raise RuntimeError("没有活动的测试会话")

        self._current_test = TestMetrics(test_name=test_name, start_time=time.time())
        self.current_session.total_tests += 1
        logger.debug(f"开始监控测试: {test_name}")
        return self._current_test

    def end_test(self, status: str, error_message: Optional[str] = None) -> TestMetrics:
        """结束测试监控"""
        if self._current_test is None:
            raise RuntimeError("没有活动的测试")
        if self.current_session is None:
            raise RuntimeError("没有活动的测试会话")

        self._current_test.end_time = time.time()
        self._current_test.status = status
        self._current_test.error_message = error_message

        # 更新会话统计
        session = self.current_session
        if status == "passed":
            session.passed_tests += 1
        elif status == "failed":
            session.failed_tests += 1
        elif status == "skipped":
            session.skipped_tests += 1

        session.test_metrics.append(self._current_test)

        logger.debug(
            f"测试结束: {self._current_test.test_name}, "
            f"状态: {status}, "
            f"耗时: {self._current_test.duration:.3f}s"
        )

        metrics = self._current_test
        self._current_test = None
        return metrics

    def _save_session_metrics(self) -> None:
        """保存会话指标到文件"""
        if self.current_session is None:
            return

        metrics_file = self.output_dir / f"metrics_{self.current_session.session_id}.json"

        data = {
            "session_id": self.current_session.session_id,
            "start_time": datetime.fromtimestamp(self.current_session.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.current_session.end_time).isoformat(),
            "duration": self.current_session.duration,
            "total_tests": self.current_session.total_tests,
            "passed_tests": self.current_session.passed_tests,
            "failed_tests": self.current_session.failed_tests,
            "skipped_tests": self.current_session.skipped_tests,
            "pass_rate": self.current_session.pass_rate,
            "avg_test_duration": self.current_session.avg_test_duration,
            "tests": [
                {
                    "name": m.test_name,
                    "status": m.status,
                    "duration": m.duration,
                    "error_message": m.error_message,
                }
                for m in self.current_session.test_metrics
            ],
        }

        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"监控数据已保存: {metrics_file}")

    def get_slow_tests(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """获取最慢的测试"""
        if self.current_session is None:
            return []

        sorted_tests = sorted(
            self.current_session.test_metrics, key=lambda x: x.duration, reverse=True
        )

        return [
            {"name": t.test_name, "duration": t.duration, "status": t.status}
            for t in sorted_tests[:top_n]
        ]

    def get_failed_tests(self) -> List[Dict[str, Any]]:
        """获取失败的测试"""
        if self.current_session is None:
            return []

        return [
            {"name": t.test_name, "duration": t.duration, "error_message": t.error_message}
            for t in self.current_session.test_metrics
            if t.status == "failed"
        ]

    def generate_performance_report(self) -> str:
        """生成性能报告"""
        if self.current_session is None:
            raise RuntimeError("没有活动的测试会话")

        session = self.current_session
        report_file = self.output_dir / f"performance_{session.session_id}.html"

        slow_tests = self.get_slow_tests(20)
        failed_tests = self.get_failed_tests()

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>测试性能报告 - {session.session_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .failed {{ color: #f44336; }}
        .passed {{ color: #4CAF50; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
    </style>
</head>
<body>
    <h1>测试性能报告</h1>
    <div class="summary">
        <h2>执行摘要</h2>
        <div class="metric">
            <div>总测试数</div>
            <div class="metric-value">{session.total_tests}</div>
        </div>
        <div class="metric">
            <div>通过</div>
            <div class="metric-value" style="color: #4CAF50;">{session.passed_tests}</div>
        </div>
        <div class="metric">
            <div>失败</div>
            <div class="metric-value" style="color: #f44336;">{session.failed_tests}</div>
        </div>
        <div class="metric">
            <div>跳过</div>
            <div class="metric-value" style="color: #FF9800;">{session.skipped_tests}</div>
        </div>
        <div class="metric">
            <div>通过率</div>
            <div class="metric-value">{session.pass_rate:.1f}%</div>
        </div>
        <div class="metric">
            <div>总耗时</div>
            <div class="metric-value">{session.duration:.2f}s</div>
        </div>
        <div class="metric">
            <div>平均耗时</div>
            <div class="metric-value">{session.avg_test_duration:.3f}s</div>
        </div>
    </div>
    
    <h2>最慢的测试 (Top 20)</h2>
    <table>
        <tr>
            <th>排名</th>
            <th>测试名称</th>
            <th>状态</th>
            <th>耗时 (秒)</th>
        </tr>
"""

        for i, test in enumerate(slow_tests, 1):
            status_class = "passed" if test["status"] == "passed" else "failed"
            html_content += f"""
        <tr>
            <td>{i}</td>
            <td>{test["name"]}</td>
            <td class="{status_class}">{test["status"]}</td>
            <td>{test["duration"]:.3f}</td>
        </tr>
"""

        html_content += """
    </table>
"""

        if failed_tests:
            html_content += """
    <h2>失败的测试</h2>
    <table>
        <tr>
            <th>测试名称</th>
            <th>耗时 (秒)</th>
            <th>错误信息</th>
        </tr>
"""
            for test in failed_tests:
                error_msg = test.get("error_message", "") or ""
                error_msg = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg
                html_content += f"""
        <tr>
            <td>{test["name"]}</td>
            <td>{test["duration"]:.3f}</td>
            <td class="failed">{error_msg}</td>
        </tr>
"""
            html_content += """
    </table>
"""

        html_content += """
</body>
</html>
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"性能报告已生成: {report_file}")
        return str(report_file)


# 全局监控器实例
_test_monitor: Optional[TestMonitor] = None


def get_test_monitor(output_dir: str = "reports/monitoring") -> TestMonitor:
    """获取全局测试监控器实例"""
    global _test_monitor
    if _test_monitor is None:
        _test_monitor = TestMonitor(output_dir)
    return _test_monitor
