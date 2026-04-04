"""Worker 结果合并"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.common.logger import get_logger
from utils.reporting.models import TestResult

logger = get_logger(__name__)


class WorkerMerger:
    """Worker 结果合并器"""

    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def merge(
        self,
        results: List[TestResult],
        start_time: Optional[datetime],
        stop_time: Optional[datetime],
    ) -> tuple[List[TestResult], Optional[datetime], Optional[datetime]]:
        """合并所有 worker 的结果"""
        merged_results: List[TestResult] = []
        min_start_time: Optional[datetime] = start_time
        max_stop_time: Optional[datetime] = stop_time

        # 收集所有 worker 的结果文件
        worker_files = list(self.temp_dir.glob("worker_*.json"))
        logger.info(f"发现 {len(worker_files)} 个 worker 结果文件")

        # 如果有 worker 结果文件，合并它们
        if worker_files:
            for worker_file in worker_files:
                try:
                    with open(worker_file, "r", encoding="utf-8") as f:
                        data: Dict[str, Any] = json.load(f)

                    # 解析开始和结束时间
                    if data.get("start_time"):
                        worker_start_time = datetime.fromisoformat(data["start_time"])
                        if min_start_time is None or worker_start_time < min_start_time:
                            min_start_time = worker_start_time

                    if data.get("stop_time"):
                        worker_stop_time = datetime.fromisoformat(data["stop_time"])
                        if max_stop_time is None or worker_stop_time > max_stop_time:
                            max_stop_time = worker_stop_time

                    # 解析测试结果
                    for result_data in data.get("results", []):
                        result = TestResult.from_dict(result_data)
                        merged_results.append(result)

                    logger.info(f"已合并 {worker_file} 的结果")
                except Exception as e:
                    logger.error(f"合并 {worker_file} 结果时出错: {e}")

            # 清理临时文件
            for worker_file in worker_files:
                try:
                    worker_file.unlink()
                except Exception as e:
                    logger.error(f"删除临时文件 {worker_file} 时出错: {e}")

            logger.info(f"合并完成，共 {len(merged_results)} 个测试结果")
        else:
            # 如果没有 worker 结果文件，保持当前结果不变
            merged_results = results
            logger.info("没有 worker 结果文件，使用当前结果")

        return merged_results, min_start_time, max_stop_time
