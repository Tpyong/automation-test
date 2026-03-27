"""
测试结果汇总报告生成器
生成 HTML 格式的简洁测试结果报告
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
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
        self.worker_id: Optional[str] = os.environ.get("PYTEST_XDIST_WORKER", "master")
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)

        logger.info(f"报告生成器初始化完成，输出目录: {output_dir}, worker_id: {self.worker_id}")

    def start_session(self):
        """开始测试会话"""
        self.start_time = datetime.now()
        self.results = []
        logger.info("测试会话开始")

    def end_session(self):
        """结束测试会话"""
        self.stop_time = datetime.now()

        # 保存当前worker的结果到临时文件
        if self.worker_id != "master":
            self._save_worker_results()
        else:
            # 主进程合并所有worker的结果
            self._merge_worker_results()

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

    def _save_worker_results(self):
        """保存当前worker的结果到临时文件"""
        worker_file = self.temp_dir / f"worker_{self.worker_id}.json"
        results_data = [result.to_dict() for result in self.results]
        data = {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "stop_time": self.stop_time.isoformat() if self.stop_time else None,
            "results": results_data,
        }

        with open(worker_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Worker {self.worker_id} 结果已保存到: {worker_file}")

    def _merge_worker_results(self):
        """合并所有worker的结果"""
        merged_results = []
        min_start_time = None
        max_stop_time = None

        # 收集所有worker的结果文件
        worker_files = list(self.temp_dir.glob("worker_*.json"))
        logger.info(f"发现 {len(worker_files)} 个worker结果文件")

        for worker_file in worker_files:
            try:
                with open(worker_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 解析开始和结束时间
                if data.get("start_time"):
                    start_time = datetime.fromisoformat(data["start_time"])
                    if min_start_time is None or start_time < min_start_time:
                        min_start_time = start_time

                if data.get("stop_time"):
                    stop_time = datetime.fromisoformat(data["stop_time"])
                    if max_stop_time is None or stop_time > max_stop_time:
                        max_stop_time = stop_time

                # 解析测试结果
                for result_data in data.get("results", []):
                    result = TestResult.from_dict(result_data)
                    merged_results.append(result)

                logger.info(f"已合并 {worker_file} 的结果")
            except Exception as e:
                logger.error(f"合并 {worker_file} 结果时出错: {e}")

        # 更新合并后的结果
        self.results = merged_results
        self.start_time = min_start_time
        self.stop_time = max_stop_time

        # 清理临时文件
        for worker_file in worker_files:
            try:
                worker_file.unlink()
            except Exception as e:
                logger.error(f"删除临时文件 {worker_file} 时出错: {e}")

        logger.info(f"合并完成，共 {len(merged_results)} 个测试结果")

    def save_history(self):
        """保存测试结果到历史记录"""
        history_dir = self.output_dir / "history"
        history_dir.mkdir(exist_ok=True)

        # 生成历史记录文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = history_dir / f"history_{timestamp}.json"

        # 构建历史记录数据
        summary = self.get_summary()
        history_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": [result.to_dict() for result in self.results],
        }

        # 保存到历史文件
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        logger.info(f"测试结果已保存到历史记录: {history_file}")
        return str(history_file)

    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取历史测试结果

        Args:
            days: 历史天数

        Returns:
            历史测试结果列表
        """
        history_dir = self.output_dir / "history"
        if not history_dir.exists():
            return []

        history_files = list(history_dir.glob("history_*.json"))
        history_data = []

        # 计算时间范围
        cutoff_time = datetime.now() - timedelta(days=days)

        for history_file in history_files:
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 检查时间是否在范围内
                timestamp = datetime.fromisoformat(data["timestamp"])
                if timestamp >= cutoff_time:
                    history_data.append(data)
            except Exception as e:
                logger.error(f"读取历史文件 {history_file} 时出错: {e}")

        # 按时间排序
        history_data.sort(key=lambda x: x["timestamp"])
        return history_data

    def generate_trend_report(self, days: int = 7, filename: str = "test-trend.html") -> str:
        """
        生成测试趋势报告

        Args:
            days: 历史天数
            filename: 报告文件名

        Returns:
            报告文件路径
        """
        history_data = self.get_history(days)
        if not history_data:
            logger.warning("没有足够的历史数据生成趋势报告")
            return ""

        # 准备趋势数据
        timestamps = []
        pass_rates = []
        total_tests = []
        failed_tests = []
        durations = []

        for data in history_data:
            timestamps.append(data["timestamp"])
            summary = data["summary"]["summary"]
            pass_rates.append(summary["pass_rate"])
            total_tests.append(summary["total"])
            failed_tests.append(summary["failed"])
            durations.append(summary["duration"])

        # 构建HTML内容
        html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试趋势报告</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header .time {{
            color: #666;
            font-size: 14px;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .section h2 {{
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            width: 100%;
            height: 400px;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 14px;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 测试趋势报告</h1>
            <div class="time">
                <div>生成时间: {generate_time}</div>
                <div>历史数据范围: {days} 天</div>
                <div>历史记录数量: {history_count}</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 通过率趋势</h2>
            <div class="chart-container">
                <canvas id="passRateChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>📊 测试数量趋势</h2>
            <div class="chart-container">
                <canvas id="testCountChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>📊 执行时长趋势</h2>
            <div class="chart-container">
                <canvas id="durationChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>📦 统计概览</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{avg_pass_rate}%</div>
                    <div class="label">平均通过率</div>
                </div>
                <div class="stat-card">
                    <div class="number">{avg_total_tests}</div>
                    <div class="label">平均测试数量</div>
                </div>
                <div class="stat-card">
                    <div class="number">{avg_failed_tests}</div>
                    <div class="label">平均失败数量</div>
                </div>
                <div class="stat-card">
                    <div class="number">{avg_duration}s</div>
                    <div class="label">平均执行时长</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 处理时间标签
        const timestamps = {timestamps_json};
        const formattedLabels = timestamps.map(t => {{
            const date = new Date(t);
            return date.toLocaleString('zh-CN', {{"month": "numeric", "day": "numeric", "hour": "2-digit", "minute": "2-digit" }});
        }});

        // 通过率趋势图
        const passRateCtx = document.getElementById('passRateChart').getContext('2d');
        new Chart(passRateCtx, {{
            type: 'line',
            data: {{
                labels: formattedLabels,
                datasets: [{{
                    label: '通过率 (%)',
                    data: {pass_rates_json},
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '测试通过率趋势'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: '通过率 (%)'
                        }}
                    }}
                }}
            }}
        }});

        // 测试数量趋势图
        const testCountCtx = document.getElementById('testCountChart').getContext('2d');
        new Chart(testCountCtx, {{
            type: 'bar',
            data: {{
                labels: formattedLabels,
                datasets: [{{
                    label: '总测试数',
                    data: {total_tests_json},
                    backgroundColor: '#17a2b8'
                }}, {{
                    label: '失败测试数',
                    data: {failed_tests_json},
                    backgroundColor: '#dc3545'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '测试数量趋势'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '测试数量'
                        }}
                    }}
                }}
            }}
        }});

        // 执行时长趋势图
        const durationCtx = document.getElementById('durationChart').getContext('2d');
        new Chart(durationCtx, {{
            type: 'line',
            data: {{
                labels: formattedLabels,
                datasets: [{{
                    label: '执行时长 (秒)',
                    data: {durations_json},
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '执行时长趋势'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '执行时长 (秒)'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

        # 计算统计数据
        avg_pass_rate = round(sum(pass_rates) / len(pass_rates), 2) if pass_rates else 0
        avg_total_tests = round(sum(total_tests) / len(total_tests), 0) if total_tests else 0
        avg_failed_tests = round(sum(failed_tests) / len(failed_tests), 0) if failed_tests else 0
        avg_duration = round(sum(durations) / len(durations), 2) if durations else 0

        # 生成时间
        generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 转换数据为JSON
        import json

        timestamps_json = json.dumps(timestamps)
        pass_rates_json = json.dumps(pass_rates)
        total_tests_json = json.dumps(total_tests)
        failed_tests_json = json.dumps(failed_tests)
        durations_json = json.dumps(durations)

        # 填充模板
        html = html_template.format(
            generate_time=generate_time,
            days=days,
            history_count=len(history_data),
            avg_pass_rate=avg_pass_rate,
            avg_total_tests=avg_total_tests,
            avg_failed_tests=avg_failed_tests,
            avg_duration=avg_duration,
            timestamps_json=timestamps_json,
            pass_rates_json=pass_rates_json,
            total_tests_json=total_tests_json,
            failed_tests_json=failed_tests_json,
            durations_json=durations_json,
        )

        # 保存趋势报告
        report_path = self.output_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"测试趋势报告已生成: {report_path}")
        return str(report_path)


# 全局报告生成器实例
_REPORT_GENERATOR = None


def get_report_generator(output_dir: str = "reports") -> ReportGenerator:
    """
    获取全局报告生成器实例

    Args:
        output_dir: 报告输出目录

    Returns:
        报告生成器实例
    """
    global _REPORT_GENERATOR
    if _REPORT_GENERATOR is None:
        _REPORT_GENERATOR = ReportGenerator(output_dir)
    return _REPORT_GENERATOR
