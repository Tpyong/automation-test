#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from core.utils.logger import get_logger

logger = get_logger(__name__)


class TestAdvisor:
    """智能测试建议器"""

    def __init__(self, history_dir: str = "reports/history"):
        """
        初始化测试建议器

        Args:
            history_dir: 历史测试结果目录
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def get_history_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取历史测试数据

        Args:
            days: 历史天数

        Returns:
            历史测试数据列表
        """
        history_files = list(self.history_dir.glob("history_*.json"))
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
            except (json.JSONDecodeError, ValueError, IOError) as e:
                logger.error("读取历史文件 %s 时出错: %s", history_file, e)

        # 按时间排序
        history_data.sort(key=lambda x: x["timestamp"])
        return history_data

    def analyze_test_performance(self, history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析测试性能

        Args:
            history_data: 历史测试数据

        Returns:
            性能分析结果
        """
        if not history_data:
            return {}

        # 分析测试执行时间
        test_durations: Dict[str, List[float]] = {}
        test_failure_counts: Dict[str, int] = {}

        for data in history_data:
            for result in data.get("results", []):
                test_name = result["test_name"]
                duration = result.get("duration", 0)
                outcome = result.get("outcome", "")

                # 累积执行时间
                if test_name not in test_durations:
                    test_durations[test_name] = []
                test_durations[test_name].append(float(duration))

                # 累积失败次数
                if outcome == "failed":
                    if test_name not in test_failure_counts:
                        test_failure_counts[test_name] = 0
                    test_failure_counts[test_name] += 1

        # 计算平均执行时间
        avg_durations = {}
        for test_name, durations in test_durations.items():
            avg_durations[test_name] = sum(durations) / len(durations)

        return {"test_durations": avg_durations, "test_failure_counts": test_failure_counts}

    def analyze_module_performance(
        self, history_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        分析模块性能

        Args:
            history_data: 历史测试数据

        Returns:
            模块性能分析结果
        """
        if not history_data:
            return {}

        module_stats: Dict[str, Dict[str, Any]] = {}

        for data in history_data:
            for module, stats in data["summary"].get("module_stats", {}).items():
                if module not in module_stats:
                    module_stats[module] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "duration": 0,
                        "runs": 0,
                        "avg_duration": 0.0,
                        "pass_rate": 0.0,
                    }

                module_stats[module]["total"] += stats.get("total", 0)
                module_stats[module]["passed"] += stats.get("passed", 0)
                module_stats[module]["failed"] += stats.get("failed", 0)
                module_stats[module]["skipped"] += stats.get("skipped", 0)
                module_stats[module]["duration"] += data["summary"]["summary"].get("duration", 0)
                module_stats[module]["runs"] += 1

        # 计算平均值和通过率
        for module, stats in module_stats.items():
            runs = stats["runs"]
            if runs > 0:
                stats["avg_duration"] = float(stats["duration"] / runs)
                stats["pass_rate"] = float(
                    (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                )
            else:
                stats["avg_duration"] = 0.0
                stats["pass_rate"] = 0.0

        return module_stats

    def generate_suggestions(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        生成测试优化建议

        Args:
            days: 分析的历史天数

        Returns:
            建议列表
        """
        history_data = self.get_history_data(days)
        if not history_data:
            return [
                {
                    "type": "info",
                    "title": "没有足够的历史数据",
                    "description": "请先运行一些测试以积累历史数据",
                    "priority": "low",
                }
            ]

        suggestions: List[Dict[str, Any]] = []

        # 分析测试性能
        performance_analysis = self.analyze_test_performance(history_data)
        module_analysis = self.analyze_module_performance(history_data)

        # 1. 识别执行时间较长的测试
        slow_tests = [
            (test, duration)
            for test, duration in performance_analysis.get("test_durations", {}).items()
            if duration > 5.0
        ]

        if slow_tests:
            slow_tests.sort(key=lambda x: x[1], reverse=True)
            top_slow_tests = slow_tests[:5]

            suggestions.append(
                {
                    "type": "performance",
                    "title": "优化执行时间较长的测试",
                    "description": f"以下测试执行时间较长: {', '.join([f'{test} ({duration:.2f}s)' for test, duration in top_slow_tests])}",
                    "priority": "medium",
                    "action": "考虑优化这些测试的执行逻辑，或使用并行执行",
                }
            )

        # 2. 识别频繁失败的测试
        frequent_failures = [
            (test, count)
            for test, count in performance_analysis.get("test_failure_counts", {}).items()
            if count >= 3
        ]

        if frequent_failures:
            frequent_failures.sort(key=lambda x: x[1], reverse=True)
            top_failures = frequent_failures[:5]

            suggestions.append(
                {
                    "type": "reliability",
                    "title": "修复频繁失败的测试",
                    "description": f"以下测试频繁失败: {', '.join([f'{test} ({count}次)' for test, count in top_failures])}",
                    "priority": "high",
                    "action": "检查这些测试的稳定性，修复根本原因",
                }
            )

        # 3. 识别表现不佳的模块
        poor_modules = [
            (module, stats)
            for module, stats in module_analysis.items()
            if stats.get("pass_rate", 0) < 80
        ]

        if poor_modules:
            poor_modules.sort(key=lambda x: x[1].get("pass_rate", 0))
            top_poor_modules = poor_modules[:3]

            suggestions.append(
                {
                    "type": "module",
                    "title": "改善表现不佳的模块",
                    "description": f"以下模块通过率较低: {', '.join([f'{module} ({stats.get("pass_rate", 0):.1f}%)' for module, stats in top_poor_modules])}",
                    "priority": "high",
                    "action": "重点关注这些模块的测试质量",
                }
            )

        # 4. 分析测试执行趋势
        if len(history_data) >= 5:
            # 计算最近5次测试的通过率趋势
            recent_runs = history_data[-5:]
            pass_rates = [run["summary"]["summary"].get("pass_rate", 0) for run in recent_runs]

            # 检查趋势
            if pass_rates[-1] < pass_rates[0] - 10:
                suggestions.append(
                    {
                        "type": "trend",
                        "title": "通过率呈下降趋势",
                        "description": f"最近测试通过率从 {pass_rates[0]:.1f}% 下降到 {pass_rates[-1]:.1f}%",
                        "priority": "high",
                        "action": "检查最近的代码变更，找出导致通过率下降的原因",
                    }
                )
            elif pass_rates[-1] > pass_rates[0] + 10:
                suggestions.append(
                    {
                        "type": "trend",
                        "title": "通过率呈上升趋势",
                        "description": f"最近测试通过率从 {pass_rates[0]:.1f}% 上升到 {pass_rates[-1]:.1f}%",
                        "priority": "low",
                        "action": "继续保持当前的测试质量",
                    }
                )

        # 5. 测试覆盖建议
        total_tests = sum(1 for data in history_data for _ in data.get("results", []))
        if total_tests < 20:
            suggestions.append(
                {
                    "type": "coverage",
                    "title": "增加测试覆盖范围",
                    "description": f"当前测试数量较少，仅有 {total_tests} 个测试用例",
                    "priority": "medium",
                    "action": "考虑增加更多测试用例，覆盖更多功能点",
                }
            )

        # 6. 并行执行建议
        avg_duration = sum(
            data["summary"]["summary"].get("duration", 0) for data in history_data
        ) / len(history_data)
        if avg_duration > 60:
            suggestions.append(
                {
                    "type": "performance",
                    "title": "考虑使用并行执行",
                    "description": f"测试平均执行时间较长 ({avg_duration:.1f} 秒)",
                    "priority": "medium",
                    "action": "使用 pytest-xdist 进行并行测试，减少执行时间",
                }
            )

        # 如果没有其他建议，添加一个正面的建议
        if not suggestions:
            suggestions.append(
                {
                    "type": "info",
                    "title": "测试状态良好",
                    "description": "所有测试表现正常，没有明显的问题",
                    "priority": "low",
                    "action": "继续保持当前的测试质量",
                }
            )

        return suggestions

    def generate_advisor_report(
        self, days: int = 30, filename: str = "test-advisor-report.html"
    ) -> str:
        """
        生成测试建议报告

        Args:
            days: 分析的历史天数
            filename: 报告文件名

        Returns:
            报告文件路径
        """
        suggestions = self.generate_suggestions(days)

        # 统计不同优先级的建议数量
        high_priority = sum(1 for s in suggestions if s.get("priority") == "high")
        medium_priority = sum(1 for s in suggestions if s.get("priority") == "medium")
        low_priority = sum(1 for s in suggestions if s.get("priority") == "low")

        # 生成建议卡片
        suggestion_cards = []
        for suggestion in suggestions:
            priority = suggestion.get("priority", "low")
            suggestion_cards.append(f"""
            <div class="suggestion-card {priority}">
                <div class="priority {priority}">{priority.upper()} PRIORITY</div>
                <div class="title">{suggestion.get('title')}</div>
                <div class="description">{suggestion.get('description')}</div>
                <div class="action">建议: {suggestion.get('action', '')}</div>
            </div>
            """)

        # 生成时间
        generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建HTML报告
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能测试建议报告</title>
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
        .suggestion-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #17a2b8;
            transition: transform 0.2s;
        }}
        .suggestion-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .suggestion-card.high {{
            border-left-color: #dc3545;
        }}
        .suggestion-card.medium {{
            border-left-color: #ffc107;
        }}
        .suggestion-card.low {{
            border-left-color: #28a745;
        }}
        .suggestion-card .title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }}
        .suggestion-card .description {{
            color: #666;
            margin-bottom: 10px;
        }}
        .suggestion-card .action {{
            color: #17a2b8;
            font-style: italic;
        }}
        .suggestion-card .priority {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .priority.high {{
            background: #f8d7da;
            color: #721c24;
        }}
        .priority.medium {{
            background: #fff3cd;
            color: #856404;
        }}
        .priority.low {{
            background: #d4edda;
            color: #155724;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
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
            color: #17a2b8;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 智能测试建议报告</h1>
            <div class="time">
                <div>生成时间: {generate_time}</div>
                <div>分析历史数据范围: {days} 天</div>
                <div>建议数量: {len(suggestions)}</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 建议概览</h2>
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="number">{high_priority}</div>
                    <div class="label">高优先级建议</div>
                </div>
                <div class="stat-card">
                    <div class="number">{medium_priority}</div>
                    <div class="label">中优先级建议</div>
                </div>
                <div class="stat-card">
                    <div class="number">{low_priority}</div>
                    <div class="label">低优先级建议</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>💡 具体建议</h2>
            {''.join(suggestion_cards)}
        </div>
    </div>
</body>
</html>
"""

        # 保存报告
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info("智能测试建议报告已生成: %s", report_path)
        return str(report_path)


# 全局测试建议器实例
_TEST_ADVISOR = None


def get_test_advisor(history_dir: str = "reports/history") -> TestAdvisor:
    """
    获取全局测试建议器实例

    Args:
        history_dir: 历史测试结果目录

    Returns:
        测试建议器实例
    """
    global _TEST_ADVISOR
    if _TEST_ADVISOR is None:
        _TEST_ADVISOR = TestAdvisor(history_dir)
    return _TEST_ADVISOR
