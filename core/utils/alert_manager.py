"""
告警管理模块

提供测试失败告警功能，支持多种告警渠道：邮件、钉钉、企业微信
"""

import json
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AlertConfig:
    """告警配置"""

    # 邮件配置
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: List[str] = []

    # 钉钉配置
    dingtalk_webhook: str = ""
    dingtalk_secret: str = ""

    # 企业微信配置
    wechat_webhook: str = ""

    # 告警阈值
    failure_threshold: int = 1  # 失败测试数阈值
    consecutive_failures: int = 1  # 连续失败次数阈值


class AlertManager:
    """告警管理器"""

    def __init__(self, config: Optional[AlertConfig] = None):
        self.config = config or self._load_config_from_env()
        self.alert_history: List[Dict[str, Any]] = []

    def _load_config_from_env(self) -> AlertConfig:
        """从环境变量加载配置"""
        import os

        email_to = os.getenv("ALERT_EMAIL_TO", "")

        return AlertConfig(
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            email_from=os.getenv("ALERT_EMAIL_FROM", ""),
            email_to=email_to.split(",") if email_to else [],
            dingtalk_webhook=os.getenv("DINGTALK_WEBHOOK", ""),
            dingtalk_secret=os.getenv("DINGTALK_SECRET", ""),
            wechat_webhook=os.getenv("WECHAT_WEBHOOK", ""),
            failure_threshold=int(os.getenv("ALERT_FAILURE_THRESHOLD", "1")),
            consecutive_failures=int(os.getenv("ALERT_CONSECUTIVE_FAILURES", "1")),
        )

    def should_alert(self, failed_count: int, consecutive_failures: int = 1) -> bool:
        """判断是否应该发送告警"""
        return (
            failed_count >= self.config.failure_threshold
            and consecutive_failures >= self.config.consecutive_failures
        )

    def send_alert(
        self,
        title: str,
        message: str,
        failed_tests: List[Dict[str, Any]],
        session_metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """发送告警"""
        success = True

        # 发送邮件告警
        if self.config.email_to:
            try:
                self._send_email_alert(title, message, failed_tests, session_metrics)
            except Exception as e:
                logger.error("发送邮件告警失败: %s", e)
                success = False

        # 发送钉钉告警
        if self.config.dingtalk_webhook:
            try:
                self._send_dingtalk_alert(title, message, failed_tests, session_metrics)
            except Exception as e:
                logger.error("发送钉钉告警失败: %s", e)
                success = False

        # 发送企业微信告警
        if self.config.wechat_webhook:
            try:
                self._send_wechat_alert(title, message, failed_tests, session_metrics)
            except Exception as e:
                logger.error("发送企业微信告警失败: %s", e)
                success = False

        # 记录告警历史
        self.alert_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "message": message,
                "failed_count": len(failed_tests),
                "success": success,
            }
        )

        return success

    def _send_email_alert(
        self,
        title: str,
        message: str,
        failed_tests: List[Dict[str, Any]],
        session_metrics: Optional[Dict[str, Any]],
    ) -> None:
        """发送邮件告警"""
        if not all([self.config.smtp_host, self.config.smtp_user, self.config.email_from]):
            logger.warning("邮件配置不完整，跳过邮件告警")
            return

        # 构建邮件内容
        html_content = self._build_email_content(title, message, failed_tests, session_metrics)

        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"【测试告警】{title}"
        msg["From"] = self.config.email_from
        msg["To"] = ", ".join(self.config.email_to)

        # 添加 HTML 内容
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # 发送邮件
        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.smtp_user, self.config.smtp_password)
            server.send_message(msg)

        logger.info("邮件告警已发送: %s", self.config.email_to)

    def _build_email_content(
        self,
        title: str,
        message: str,
        failed_tests: List[Dict[str, Any]],
        session_metrics: Optional[Dict[str, Any]],
    ) -> str:
        """构建邮件内容"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .summary {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-left: 4px solid #f44336; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f44336; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .error {{ color: #f44336; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ 测试执行失败告警</h1>
        <p>{title}</p>
    </div>
    
    <div class="content">
        <div class="summary">
            <h2>告警信息</h2>
            <p><strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>描述:</strong> {message}</p>
        </div>
"""

        if session_metrics:
            html += f"""
        <div class="summary">
            <h2>执行摘要</h2>
            <p><strong>总测试数:</strong> {session_metrics.get('total_tests', 0)}</p>
            <p><strong>通过:</strong> {session_metrics.get('passed_tests', 0)}</p>
            <p><strong>失败:</strong> {session_metrics.get('failed_tests', 0)}</p>
            <p><strong>跳过:</strong> {session_metrics.get('skipped_tests', 0)}</p>
            <p><strong>通过率:</strong> {session_metrics.get('pass_rate', 0):.1f}%</p>
        </div>
"""

        if failed_tests:
            html += """
        <h2>失败的测试</h2>
        <table>
            <tr>
                <th>测试名称</th>
                <th>错误信息</th>
            </tr>
"""
            for test in failed_tests[:10]:  # 只显示前10个
                error_msg = test.get("error_message", "") or ""
                error_msg = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg
                html += f"""
            <tr>
                <td>{test.get('name', 'Unknown')}</td>
                <td class="error">{error_msg}</td>
            </tr>
"""
            html += """
        </table>
"""

        html += """
    </div>
</body>
</html>
"""
        return html

    def _send_dingtalk_alert(
        self,
        title: str,
        message: str,
        failed_tests: List[Dict[str, Any]],
        session_metrics: Optional[Dict[str, Any]],
    ) -> None:
        """发送钉钉告警"""
        if not self.config.dingtalk_webhook:
            return

        # 构建消息内容
        content = f"""## ⚠️ 测试执行失败告警

**{title}**

{message}

### 执行摘要
- 总测试数: {session_metrics.get('total_tests', 0) if session_metrics is not None else 0}
- 通过: {session_metrics.get('passed_tests', 0) if session_metrics is not None else 0}
- 失败: {session_metrics.get('failed_tests', 0) if session_metrics is not None else 0}
- 通过率: {float(session_metrics.get('pass_rate', 0)) if session_metrics is not None else 0:.1f}%

### 失败的测试
"""

        for test in failed_tests[:5]:  # 只显示前5个
            if test:
                content += f"- {test.get('name', 'Unknown')}\n"
            else:
                content += "- Unknown test\n"

        if len(failed_tests) > 5:
            content += f"- ... 还有 {len(failed_tests) - 5} 个失败的测试\n"

        # 发送请求
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": f"【测试告警】{title}", "text": content},
        }

        response = requests.post(self.config.dingtalk_webhook, json=payload, timeout=30)
        response.raise_for_status()

        logger.info("钉钉告警已发送")

    def _send_wechat_alert(
        self,
        title: str,
        message: str,
        failed_tests: List[Dict[str, Any]],
        session_metrics: Optional[Dict[str, Any]],
    ) -> None:
        """发送企业微信告警"""
        if not self.config.wechat_webhook:
            return

        # 构建消息内容
        content = f"""【测试告警】{title}

{message}

执行摘要:
总测试数: {session_metrics.get('total_tests', 0) if session_metrics is not None else 0}
通过: {session_metrics.get('passed_tests', 0) if session_metrics is not None else 0}
失败: {session_metrics.get('failed_tests', 0) if session_metrics is not None else 0}
通过率: {float(session_metrics.get('pass_rate', 0)) if session_metrics is not None else 0:.1f}%

失败的测试:
"""

        for test in failed_tests[:5]:
            if test:
                content += f"- {test.get('name', 'Unknown')}\n"
            else:
                content += "- Unknown test\n"

        # 发送请求
        payload = {"msgtype": "text", "text": {"content": content}}

        response = requests.post(self.config.wechat_webhook, json=payload, timeout=30)
        response.raise_for_status()

        logger.info("企业微信告警已发送")

    def send_test_failure_alert(
        self, failed_tests: List[Dict[str, Any]], session_metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发送测试失败告警"""
        if not failed_tests:
            return True

        failed_count = len(failed_tests)

        if not self.should_alert(failed_count):
            logger.info(
                f"失败测试数 {failed_count} 未达到告警阈值 {self.config.failure_threshold}，跳过告警"
            )
            return True

        title = f"测试执行失败 ({failed_count} 个测试失败)"
        message = f"自动化测试执行完成，发现 {failed_count} 个测试失败，请尽快处理。"

        return self.send_alert(title, message, failed_tests, session_metrics)

    def save_alert_history(self, output_file: Optional[str] = None) -> str:
        """保存告警历史"""
        if output_file is None:
            output_file = f"reports/alert-history-{datetime.now().strftime('%Y%m%d')}.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.alert_history, f, ensure_ascii=False, indent=2)

        logger.info("告警历史已保存: %s", output_path)
        return str(output_path)


# 全局告警管理器实例
_alert_manager: Optional[AlertManager] = None


def get_alert_manager(config: Optional[AlertConfig] = None) -> AlertManager:
    """获取全局告警管理器实例"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(config)
    return _alert_manager
