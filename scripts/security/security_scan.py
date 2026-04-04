#!/usr/bin/env python3
"""
安全扫描脚本

集成多种安全扫描工具：
- safety: 检查依赖包安全漏洞
- bandit: 检查 Python 代码安全问题
- pip-audit: 审计依赖包
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.common.logger import get_logger

logger = get_logger(__name__)


class SecurityScanner:
    """安全扫描器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: Dict[str, Any] = {}

    def run_safety_check(self) -> Dict[str, Any]:
        """运行 safety 检查"""
        logger.info("开始 safety 依赖安全扫描...")

        try:
            result = subprocess.run(
                ["safety", "check", "--json"], capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                logger.info("✅ Safety 扫描通过，未发现安全漏洞")
                return {"status": "passed", "vulnerabilities": []}
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    logger.warning(f"⚠️ Safety 发现 {len(vulnerabilities)} 个安全漏洞")
                    return {"status": "failed", "vulnerabilities": vulnerabilities}
                except json.JSONDecodeError:
                    logger.error(f"Safety 扫描失败: {result.stderr}")
                    return {"status": "error", "message": result.stderr}

        except FileNotFoundError:
            logger.error("safety 未安装，请先安装: pip install safety")
            return {"status": "error", "message": "safety not installed"}
        except subprocess.TimeoutExpired:
            logger.error("Safety 扫描超时")
            return {"status": "error", "message": "timeout"}

    def run_bandit_check(self) -> Dict[str, Any]:
        """运行 bandit 代码安全扫描"""
        logger.info("开始 bandit 代码安全扫描...")

        try:
            output_file = self.output_dir / "bandit-report.json"

            result = subprocess.run(
                [
                    "bandit",
                    "-r",
                    ".",
                    "-f",
                    "json",
                    "-o",
                    str(output_file),
                    "--skip",
                    "B101,B311",  # 跳过 assert 和随机数警告
                    "-ll",  # 只报告中高级别问题
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # 读取报告
            if output_file.exists():
                with open(output_file, "r", encoding="utf-8") as f:
                    report = json.load(f)
            else:
                report = {"results": [], "metrics": {}}

            issue_count = len(report.get("results", []))

            if result.returncode == 0:
                logger.info("✅ Bandit 扫描通过，未发现安全问题")
                return {"status": "passed", "issues": [], "metrics": report.get("metrics", {})}
            else:
                logger.warning(f"⚠️ Bandit 发现 {issue_count} 个安全问题")
                return {
                    "status": "failed",
                    "issues": report.get("results", []),
                    "metrics": report.get("metrics", {}),
                }

        except FileNotFoundError:
            logger.error("bandit 未安装，请先安装: pip install bandit")
            return {"status": "error", "message": "bandit not installed"}
        except subprocess.TimeoutExpired:
            logger.error("Bandit 扫描超时")
            return {"status": "error", "message": "timeout"}

    def run_pip_audit(self) -> Dict[str, Any]:
        """运行 pip-audit 依赖审计"""
        logger.info("开始 pip-audit 依赖审计...")

        try:
            result = subprocess.run(
                ["pip-audit", "--format=json", "--desc"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            try:
                audit_results = json.loads(result.stdout)
                vulnerabilities = audit_results.get("vulnerabilities", [])

                if not vulnerabilities:
                    logger.info("✅ pip-audit 审计通过，未发现漏洞")
                    return {"status": "passed", "vulnerabilities": []}
                else:
                    logger.warning(f"⚠️ pip-audit 发现 {len(vulnerabilities)} 个漏洞")
                    return {"status": "failed", "vulnerabilities": vulnerabilities}

            except json.JSONDecodeError:
                logger.error(f"pip-audit 解析失败: {result.stdout}")
                return {"status": "error", "message": "parse error"}

        except FileNotFoundError:
            logger.error("pip-audit 未安装，请先安装: pip install pip-audit")
            return {"status": "error", "message": "pip-audit not installed"}
        except subprocess.TimeoutExpired:
            logger.error("pip-audit 审计超时")
            return {"status": "error", "message": "timeout"}

    def generate_report(self) -> str:
        """生成综合安全报告"""
        report_file = (
            self.output_dir / f"security-report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        summary = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(self.results),
                "passed": sum(1 for r in self.results.values() if r.get("status") == "passed"),
                "failed": sum(1 for r in self.results.values() if r.get("status") == "failed"),
                "errors": sum(1 for r in self.results.values() if r.get("status") == "error"),
            },
            "details": self.results,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"安全扫描报告已生成: {report_file}")
        return str(report_file)

    def run_all_scans(self) -> bool:
        """运行所有安全扫描"""
        logger.info("=" * 60)
        logger.info("开始全面安全扫描")
        logger.info("=" * 60)

        # Safety 扫描
        self.results["safety"] = self.run_safety_check()

        # Bandit 扫描
        self.results["bandit"] = self.run_bandit_check()

        # pip-audit 审计
        self.results["pip_audit"] = self.run_pip_audit()

        # 生成报告
        report_file = self.generate_report()

        # 输出摘要
        logger.info("=" * 60)
        logger.info("安全扫描完成")
        logger.info("=" * 60)
        logger.info(f"报告文件: {report_file}")
        logger.info(
            f"通过: {self.results['safety'].get('status') == 'passed' and self.results['bandit'].get('status') == 'passed'}"
        )

        # 返回是否通过
        return all(r.get("status") == "passed" for r in self.results.values())


def main():
    """主函数"""
    scanner = SecurityScanner()
    passed = scanner.run_all_scans()

    if passed:
        logger.info("✅ 所有安全扫描通过")
        sys.exit(0)
    else:
        logger.error("❌ 安全扫描发现问题")
        sys.exit(1)


if __name__ == "__main__":
    main()
