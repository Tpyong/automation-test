"""历史数据管理"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from utils.common.logger import get_logger

logger = get_logger(__name__)


class HistoryManager:
    """历史数据管理器"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.history_dir = output_dir / "history"
        self.history_dir.mkdir(exist_ok=True)

    def save(self, summary: Dict[str, Any], results: List[Any]) -> str:
        """保存测试结果到历史记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.history_dir / f"history_{timestamp}.json"

        history_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": results,
        }

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        logger.info(f"测试结果已保存到历史记录: {history_file}")
        return str(history_file)

    def get(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取历史测试结果"""
        if not self.history_dir.exists():
            return []

        history_files = list(self.history_dir.glob("history_*.json"))
        history_data = []

        cutoff_time = datetime.now() - timedelta(days=days)

        for history_file in history_files:
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                timestamp = datetime.fromisoformat(data["timestamp"])
                if timestamp >= cutoff_time:
                    history_data.append(data)
            except Exception as e:
                logger.error(f"读取历史文件 {history_file} 时出错: {e}")

        history_data.sort(key=lambda x: x["timestamp"])
        return history_data
