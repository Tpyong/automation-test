"""
测试结果汇总报告生成器
生成 HTML 格式的简洁测试结果报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.utils.logger import get_logger

logger = get_logger(__name__)


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


class ReportGenerator:
    """测试结果汇总报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results: List[TestResult] = []
        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None

        logger.info(f"报告生成器初始化完成，输出目录: {output_dir}")

    def start_session(self):
        """开始测试会话"""
        self.start_time = datetime.now()
        self.results = []
        logger.info("测试会话开始")

    def end_session(self):
        """结束测试会话"""
        self.stop_time = datetime.now()
        logger.info("测试会话结束")

    def add_result(self, nodeid: str, outcome: str, duration: float = 0.0, error_msg: Optional[str] = None):
        """
        添加测试结果

        Args:
            nodeid: 测试用例ID
            outcome: 测试结果（passed, failed, skipped, xfailed, xpassed）
            duration: 执行时长（秒）
            error_msg: 错误信息
        """
        result = TestResult(nodeid, outcome, duration)
        result.error_msg = error_msg
        self.results.append(result)
        logger.debug(f"添加测试结果: {nodeid} - {outcome}")

    def get_summary(self) -> Dict[str, Any]:
        """
        获取测试结果摘要

        Returns:
            摘要字典
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.outcome == "passed")
        failed = sum(1 for r in self.results if r.outcome == "failed")
        skipped = sum(1 for r in self.results if r.outcome == "skipped")
        xfailed = sum(1 for r in self.results if r.outcome == "xfailed")
        xpassed = sum(1 for r in self.results if r.outcome == "xpassed")

        # 计算执行时长
        duration = 0.0
        if self.start_time and self.stop_time:
            duration = (self.stop_time - self.start_time).total_seconds()

        # 计算通过率
        pass_rate = (passed / total * 100) if total > 0 else 0.0

        # 按模块统计
        module_stats = {}
        for result in self.results:
            module = result.file_path
            if module not in module_stats:
                module_stats[module] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
            module_stats[module]["total"] += 1
            if result.outcome == "passed":
                module_stats[module]["passed"] += 1
            elif result.outcome == "failed":
                module_stats[module]["failed"] += 1
            elif result.outcome == "skipped":
                module_stats[module]["skipped"] += 1

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "xfailed": xfailed,
                "xpassed": xpassed,
                "pass_rate": round(pass_rate, 2),
                "duration": round(duration, 2),
            },
            "module_stats": module_stats,
            "failed_tests": [
                {"name": r.test_name, "nodeid": r.nodeid, "error": r.error_msg}
                for r in self.results
                if r.outcome == "failed"
            ],
            "time": {
                "start": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else None,
                "stop": self.stop_time.strftime("%Y-%m-%d %H:%M:%S") if self.stop_time else None,
            },
        }

    def generate_html_report(self, filename: str = "test-summary.html") -> str:
        """
        生成 HTML 格式报告

        Args:
            filename: 报告文件名

        Returns:
            报告文件路径
        """
        summary = self.get_summary()

        html_content = self._build_html_content(summary)

        report_path = self.output_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML 报告已生成: {report_path}")
        return str(report_path)

    def generate_json_report(self, filename: str = "test-summary.json") -> str:
        """
        生成 JSON 格式报告

        Args:
            filename: 报告文件名

        Returns:
            报告文件路径
        """
        summary = self.get_summary()

        report_path = self.output_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON 报告已生成: {report_path}")
        return str(report_path)

    def _build_html_content(self, summary: Dict[str, Any]) -> str:
        """
        构建 HTML 内容

        Args:
            summary: 测试结果摘要

        Returns:
            HTML 字符串
        """
        s = summary["summary"]
        pass_rate = s["pass_rate"]

        # 确定状态颜色
        status_color = "#28a745" if pass_rate >= 90 else "#ffc107" if pass_rate >= 70 else "#dc3545"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试结果汇总</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .header h1 {{ color: #333; font-size: 28px; margin-bottom: 10px; }}
        .header .time {{ color: #666; font-size: 14px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
        .stat-card .number {{ font-size: 36px; font-weight: bold; margin-bottom: 5px; }}
        .stat-card .label {{ color: #666; font-size: 14px; }}
        .stat-card.passed .number {{ color: #28a745; }}
        .stat-card.failed .number {{ color: #dc3545; }}
        .stat-card.skipped .number {{ color: #ffc107; }}
        .stat-card.total .number {{ color: #17a2b8; }}
        .pass-rate {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }}
        .pass-rate .value {{ font-size: 72px; font-weight: bold; color: {status_color}; margin-bottom: 10px; }}
        .pass-rate .label {{ color: #666; font-size: 18px; }}
        .section {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .section h2 {{ color: #333; font-size: 20px; margin-bottom: 20px; }}
        .module-table {{ width: 100%; border-collapse: collapse; }}
        .module-table th, .module-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        .module-table th {{ background: #f8f9fa; font-weight: 600; }}
        .module-table .passed {{ color: #28a745; font-weight: 600; }}
        .module-table .failed {{ color: #dc3545; font-weight: 600; }}
        .failed-list {{ list-style: none; }}
        .failed-list li {{ padding: 10px; background: #fff5f5; border-left: 4px solid #dc3545; margin-bottom: 10px; border-radius: 0 4px 4px 0; }}
        .failed-list .test-name {{ font-weight: 600; color: #dc3545; margin-bottom: 5px; }}
        .failed-list .error {{ color: #666; font-size: 14px; font-family: monospace; }}
        .no-failed {{ color: #28a745; font-size: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 测试结果汇总</h1>
            <div class="time">
                <div>开始时间: {summary['time']['start']}</div>
                <div>结束时间: {summary['time']['stop']}</div>
                <div>执行时长: {s['duration']} 秒</div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card total">
                <div class="number">{s['total']}</div>
                <div class="label">总计</div>
            </div>
            <div class="stat-card passed">
                <div class="number">{s['passed']}</div>
                <div class="label">通过</div>
            </div>
            <div class="stat-card failed">
                <div class="number">{s['failed']}</div>
                <div class="label">失败</div>
            </div>
            <div class="stat-card skipped">
                <div class="number">{s['skipped']}</div>
                <div class="label">跳过</div>
            </div>
        </div>
        
        <div class="pass-rate">
            <div class="value">{s['pass_rate']}%</div>
            <div class="label">通过率</div>
        </div>
        
        <div class="section">
            <h2>📦 按模块统计</h2>
            <table class="module-table">
                <thead>
                    <tr>
                        <th>模块</th>
                        <th>总计</th>
                        <th>通过</th>
                        <th>失败</th>
                        <th>跳过</th>
                        <th>通过率</th>
                    </tr>
                </thead>
                <tbody>
"""

        # 添加模块统计
        for module, stats in summary["module_stats"].items():
            total = stats["total"]
            passed = stats["passed"]
            failed = stats["failed"]
            skipped = stats["skipped"]
            pass_rate = round(passed / total * 100, 2) if total > 0 else 0
            pass_rate_class = "passed" if pass_rate >= 90 else "failed"

            html += f"""
                    <tr>
                        <td>{module}</td>
                        <td>{total}</td>
                        <td class="passed">{passed}</td>
                        <td class="failed">{failed}</td>
                        <td>{skipped}</td>
                        <td class="{pass_rate_class}">{pass_rate}%</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
"""

        # 添加失败用例列表
        if summary["failed_tests"]:
            html += """
        <div class="section">
            <h2>❌ 失败用例</h2>
            <ul class="failed-list">
"""
            for test in summary["failed_tests"]:
                error = test["error"] or "未知错误"
                html += f"""
                <li>
                    <div class="test-name">{test['name']}</div>
                    <div class="error">{error}</div>
                </li>
"""
            html += """
            </ul>
        </div>
"""
        else:
            html += """
        <div class="section">
            <h2>✅ 失败用例</h2>
            <div class="no-failed">🎉 没有失败的测试用例！</div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""
        return html


# 全局报告生成器实例
_report_generator = None


def get_report_generator(output_dir: str = "reports") -> ReportGenerator:
    """
    获取全局报告生成器实例

    Args:
        output_dir: 报告输出目录

    Returns:
        报告生成器实例
    """
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator(output_dir)
    return _report_generator
