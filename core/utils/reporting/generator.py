"""测试报告生成器"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.utils.logger import get_logger
from core.utils.reporting.models import TestResult
from core.utils.reporting.history_manager import HistoryManager
from core.utils.reporting.worker_merger import WorkerMerger

logger = get_logger(__name__)


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

        # 初始化组件
        self.history_manager = HistoryManager(self.output_dir)
        self.worker_merger = WorkerMerger(self.temp_dir)

        # 初始化 Jinja2 环境
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        logger.info(f"报告生成器初始化完成，输出目录: {output_dir}, worker_id: {self.worker_id}")

    def start_session(self) -> None:
        """开始测试会话"""
        self.start_time = datetime.now()
        self.results = []
        logger.info("测试会话开始")

    def end_session(self) -> None:
        """结束测试会话"""
        self.stop_time = datetime.now()

        if self.worker_id != "master":
            self._save_worker_results()
        else:
            # 合并所有 worker 的结果
            self.results, self.start_time, self.stop_time = self.worker_merger.merge(
                self.results, self.start_time, self.stop_time
            )

        logger.info("测试会话结束")

    def add_result(self, nodeid: str, outcome: str, duration: float = 0.0, error_msg: Optional[str] = None) -> None:
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
        使用 Jinja2 模板渲染 HTML 内容

        Args:
            summary: 测试结果摘要

        Returns:
            HTML 字符串
        """
        s = summary["summary"]
        pass_rate = s["pass_rate"]

        # 确定状态颜色
        status_color = "#28a745" if pass_rate >= 90 else "#ffc107" if pass_rate >= 70 else "#dc3545"

        # 读取 CSS 文件
        css_path = Path(__file__).parent / "static" / "css" / "report.css"
        css_content = css_path.read_text(encoding="utf-8")

        # 准备模板上下文
        context = {
            "summary": summary,
            "status_color": status_color,
            "css_content": css_content,
        }

        # 渲染模板
        template = self.env.get_template("summary.html")
        return template.render(**context)

    def save_history(self) -> str:
        """保存测试结果到历史记录"""
        summary = self.get_summary()
        results = [result.to_dict() for result in self.results]
        return self.history_manager.save(summary, results)

    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取历史测试结果

        Args:
            days: 历史天数

        Returns:
            历史测试结果列表
        """
        return self.history_manager.get(days)

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
        data = self._prepare_trend_data(history_data)

        # 计算统计数据
        avg_pass_rate = round(sum(data["pass_rates"]) / len(data["pass_rates"]), 2) if data["pass_rates"] else 0
        avg_total_tests = round(sum(data["total_tests"]) / len(data["total_tests"]), 0) if data["total_tests"] else 0
        avg_failed_tests = round(sum(data["failed_tests"]) / len(data["failed_tests"]), 0) if data["failed_tests"] else 0
        avg_skipped_tests = round(sum(data["skipped_tests"]) / len(data["skipped_tests"]), 0) if data["skipped_tests"] else 0
        avg_duration = round(sum(data["durations"]) / len(data["durations"]), 2) if data["durations"] else 0
        max_pass_rate = round(max(data["pass_rates"]), 2) if data["pass_rates"] else 0

        # 生成时间
        generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 读取 CSS 文件
        css_path = Path(__file__).parent / "static" / "css" / "report.css"
        css_content = css_path.read_text(encoding="utf-8")

        # 准备模板上下文
        context = {
            "generate_time": generate_time,
            "days": days,
            "history_count": len(history_data),
            "avg_pass_rate": avg_pass_rate,
            "avg_total_tests": avg_total_tests,
            "avg_failed_tests": avg_failed_tests,
            "avg_skipped_tests": avg_skipped_tests,
            "avg_duration": avg_duration,
            "max_pass_rate": max_pass_rate,
            "chart_data": data,
            "css_content": css_content,
        }

        # 渲染模板
        template = self.env.get_template("trend.html")
        html = template.render(**context)

        # 保存趋势报告
        report_path = self.output_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"测试趋势报告已生成: {report_path}")
        return str(report_path)

    def _prepare_trend_data(self, history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        准备趋势数据

        Args:
            history_data: 历史数据列表

        Returns:
            趋势数据字典
        """
        timestamps = []
        pass_rates = []
        total_tests = []
        failed_tests = []
        durations = []
        skipped_tests = []
        module_data = {}

        for data in history_data:
            timestamps.append(data["timestamp"])
            summary = data["summary"]["summary"]
            pass_rates.append(summary["pass_rate"])
            total_tests.append(summary["total"])
            failed_tests.append(summary["failed"])
            durations.append(summary["duration"])
            skipped_tests.append(summary["skipped"])

            # 收集模块数据
            for module, module_stats in data["summary"].get("module_stats", {}).items():
                if module not in module_data:
                    module_data[module] = {"pass_rates": [], "durations": []}
                module_pass_rate = (module_stats["passed"] / module_stats["total"] * 100) if module_stats["total"] > 0 else 0
                module_data[module]["pass_rates"].append(module_pass_rate)
                module_data[module]["durations"].append(summary["duration"])

        return {
            "timestamps": timestamps,
            "pass_rates": pass_rates,
            "total_tests": total_tests,
            "failed_tests": failed_tests,
            "durations": durations,
            "skipped_tests": skipped_tests,
            "module_data": module_data,
        }

    def _save_worker_results(self) -> None:
        """保存当前 worker 的结果到临时文件"""
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
