"""测试结果汇总报告生成器"""

from utils.reporting import ReportGenerator

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
