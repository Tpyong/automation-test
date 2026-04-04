"""
测试数据管理模块

提供测试数据初始化、清理和快照功能
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from core.services.database.db_manager import DatabaseManager, get_db_manager
from utils.common.logger import get_logger

logger = get_logger(__name__)


class TestDataManager:
    """测试数据管理器"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or get_db_manager()
        self.data_dir = Path("data/test_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cleanup_functions: List[Callable[[], None]] = []
        self._created_records: Dict[str, List[Any]] = {}

    def register_cleanup(self, cleanup_func: Callable[[], None]) -> None:
        """注册清理函数"""
        self._cleanup_functions.append(cleanup_func)

    def track_record(self, table: str, record_id: Any) -> None:
        """跟踪创建的记录"""
        if table not in self._created_records:
            self._created_records[table] = []
        self._created_records[table].append(record_id)

    def cleanup(self) -> None:
        """执行所有清理操作"""
        logger.info("开始清理测试数据...")

        # 删除跟踪的记录
        for table, record_ids in self._created_records.items():
            for record_id in record_ids:
                try:
                    self.delete_record(table, record_id)
                    logger.debug(f"已删除记录: {table}.{record_id}")
                except Exception as e:
                    logger.warning(f"删除记录失败: {table}.{record_id}, 错误: {e}")

        # 执行注册的清理函数
        for cleanup_func in self._cleanup_functions:
            try:
                cleanup_func()
            except Exception as e:
                logger.warning(f"清理函数执行失败: {e}")

        self._cleanup_functions.clear()
        self._created_records.clear()
        logger.info("测试数据清理完成")

    def delete_record(self, table: str, record_id: Any, id_column: str = "id") -> None:
        """删除记录"""
        # 验证表名和列名，防止SQL注入
        if not table.isalnum() or not id_column.isalnum():
            raise ValueError("表名和列名只能包含字母和数字")
        # 使用方括号包围表名和列名，增强安全性
        sql = f"DELETE FROM [{table}] WHERE [{id_column}] = :id"  # nosec B608
        self.db_manager.execute(sql, {"id": record_id})

    def load_data_from_file(self, filename: str) -> Dict[str, Any]:
        """从文件加载测试数据"""
        file_path = self.data_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"测试数据文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix == ".json":
                data = json.load(f)
                return data if isinstance(data, dict) else {}
            elif file_path.suffix in [".yaml", ".yml"]:
                import yaml

                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")

    def save_data_to_file(self, filename: str, data: Dict[str, Any]) -> None:
        """保存测试数据到文件"""
        file_path = self.data_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            if file_path.suffix == ".json":
                json.dump(data, f, ensure_ascii=False, indent=2)
            elif file_path.suffix in [".yaml", ".yml"]:
                import yaml

                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def create_snapshot(self, tables: List[str], snapshot_name: Optional[str] = None) -> str:
        """创建数据快照"""
        if snapshot_name is None:
            snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        snapshot_data = {}

        for table in tables:
            # 验证表名，防止SQL注入
            if not table.isalnum():
                raise ValueError("表名只能包含字母和数字")
            # 使用方括号包围表名，增强安全性
            sql = f"SELECT * FROM [{table}]"  # nosec B608
            records = self.db_manager.execute(sql)
            snapshot_data[table] = records

        snapshot_file = self.data_dir / f"{snapshot_name}.json"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

        logger.info(f"数据快照已创建: {snapshot_file}")
        return str(snapshot_file)

    def restore_snapshot(self, snapshot_name: str) -> None:
        """恢复数据快照"""
        snapshot_file = self.data_dir / f"{snapshot_name}.json"

        if not snapshot_file.exists():
            raise FileNotFoundError(f"快照文件不存在: {snapshot_file}")

        with open(snapshot_file, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)

        for table, records in snapshot_data.items():
            # 验证表名，防止SQL注入
            if not table.isalnum():
                raise ValueError("表名只能包含字母和数字")
            # 清空表，使用方括号包围表名
            self.db_manager.execute(f"TRUNCATE TABLE [{table}]")

            # 恢复数据
            if records:
                columns = list(records[0].keys())
                # 验证列名，防止SQL注入
                for col in columns:
                    if not col.isalnum():
                        raise ValueError("列名只能包含字母和数字")
                column_str = ", ".join([f"[{col}]" for col in columns])
                placeholders = ", ".join([f":{col}" for col in columns])
                # 使用方括号包围表名和列名
                sql = f"INSERT INTO [{table}] ({column_str}) VALUES ({placeholders})"  # nosec B608

                self.db_manager.execute_many(sql, records)

        logger.info(f"数据快照已恢复: {snapshot_name}")


class TestDataBuilder:
    """测试数据构建器"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or get_db_manager()
        self.data: Dict[str, Any] = {}

    def with_field(self, field: str, value: Any) -> "TestDataBuilder":
        """添加字段"""
        self.data[field] = value
        return self

    def with_defaults(self, table: str) -> "TestDataBuilder":
        """加载表默认值"""
        defaults = self._get_table_defaults(table)
        self.data.update(defaults)
        return self

    def build(self) -> Dict[str, Any]:
        """构建数据"""
        return self.data.copy()

    def insert(self, table: str) -> Any:
        """插入到数据库"""
        if not self.data:
            raise ValueError("没有数据可插入")

        # 验证表名，防止SQL注入
        if not table.isalnum():
            raise ValueError("表名只能包含字母和数字")

        columns = list(self.data.keys())
        # 验证列名，防止SQL注入
        for col in columns:
            if not col.isalnum():
                raise ValueError("列名只能包含字母和数字")
        column_str = ", ".join([f"[{col}]" for col in columns])
        placeholders = ", ".join([f":{col}" for col in columns])

        # 使用方括号包围表名和列名，增强安全性
        sql = f"INSERT INTO [{table}] ({column_str}) VALUES ({placeholders})"  # nosec B608

        with self.db_manager.get_connection() as conn:
            result = conn.execute(sql, self.data)
            conn.commit()
            return result.lastrowid

    def _get_table_defaults(self, table: str) -> Dict[str, Any]:
        """获取表默认值"""
        # 这里可以根据表名返回预设的默认值
        defaults_map = {
            "users": {
                "username": f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "status": "active",
                "created_at": datetime.now().isoformat(),
            },
            "orders": {
                "order_no": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            },
        }
        return defaults_map.get(table, {})


# pytest fixture
def pytest_addoption(parser):
    """添加 pytest 命令行选项"""
    parser.addoption(
        "--db-snapshot",
        action="store",
        default=None,
        help="测试前恢复数据库快照",
    )
