"""
报告管理器
负责测试报告的生成和管理
"""
from typing import Any

from utils.common.logger import get_logger

logger = get_logger(__name__)


class ReportManager:
    """报告管理器"""

    def __init__(self):
        """初始化报告管理器"""
        self._report_generator = None
        self._test_advisor = None

    def initialize(self) -> None:
        """初始化报告管理器"""
        self._report_generator = self._get_report_generator()
        self._report_generator.start_session()
        logger.info("报告生成器会话已开始")

    def finalize(self, exitstatus: int) -> dict:
        """
        完成报告生成

        Args:
            exitstatus: 测试退出状态

        Returns:
            报告文件路径字典
        """
        if not self._report_generator:
            return {}

        self._report_generator.end_session()
        logger.info("报告生成器会话已结束")

        reports = {
            "html_report": self._report_generator.generate_html_report(),
            "json_report": self._report_generator.generate_json_report(),
            "history_file": self._report_generator.save_history(),
            "trend_report": self._report_generator.generate_trend_report(),
        }

        self._generate_advisor_report()

        return reports

    def add_result(self, nodeid: str, outcome: str, duration: float = 0.0, error_msg: Any = None) -> None:
        """
        添加测试结果

        Args:
            nodeid: 测试用例ID
            outcome: 测试结果
            duration: 执行时长
            error_msg: 错误信息
        """
        if self._report_generator:
            self._report_generator.add_result(nodeid, outcome, duration, error_msg)

    def _get_report_generator(self) -> Any:
        """获取报告生成器实例"""
        from utils.reporting.report_generator import get_report_generator

        return get_report_generator()

    def _generate_advisor_report(self) -> None:
        """生成智能测试建议报告"""
        try:
            test_advisor = self._get_test_advisor()
            advisor_report = test_advisor.generate_advisor_report()
            logger.info("  - 智能测试建议报告: %s", advisor_report)
        except Exception as e:
            logger.warning("生成智能测试建议报告时出错: %s", e)

    def _get_test_advisor(self) -> Any:
        """获取测试建议器实例"""
        if self._test_advisor is None:
            from utils.reporting.test_advisor import get_test_advisor

            self._test_advisor = get_test_advisor()
        return self._test_advisor