"""
数据库连接管理模块

提供数据库连接池管理、事务支持和测试数据管理功能
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Union

from core.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConfig:
    """数据库配置"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "test_db",
        charset: str = "utf8mb4",
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """从环境变量创建配置"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "test_db"),
        )
    
    def to_connection_string(self) -> str:
        """生成连接字符串"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )


class DatabaseManager:
    """数据库管理器"""
    
    _instance: Optional["DatabaseManager"] = None
    _engine: Any = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        if hasattr(self, '_initialized'):
            return
        
        self.config = config or DatabaseConfig.from_env()
        self._initialized = True
        logger.info(f"DatabaseManager 初始化完成: {self.config.host}:{self.config.port}/{self.config.database}")
    
    def initialize(self) -> None:
        """初始化数据库连接池"""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.pool import QueuePool
            
            self._engine = create_engine(
                self.config.to_connection_string(),
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=False,
            )
            logger.info("数据库连接池初始化完成")
        except ImportError:
            logger.warning("SQLAlchemy 未安装，数据库功能不可用")
            self._engine = None
    
    @property
    def engine(self) -> Any:
        """获取数据库引擎"""
        if self._engine is None:
            self.initialize()
        return self._engine
    
    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """获取数据库连接（上下文管理器）"""
        if self._engine is None:
            raise RuntimeError("数据库未初始化")
        
        conn = self._engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_session(self) -> Generator[Any, None, None]:
        """获取数据库会话（上下文管理器）"""
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行 SQL 查询"""
        with self.get_connection() as conn:
            result = conn.execute(sql, params or {})
            return [dict(row) for row in result.mappings()]
    
    def execute_many(self, sql: str, params_list: List[Dict[str, Any]]) -> int:
        """批量执行 SQL"""
        with self.get_connection() as conn:
            result = conn.execute(sql, params_list)
            return result.rowcount
    
    def close(self) -> None:
        """关闭数据库连接池"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("数据库连接池已关闭")


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config)
    return _db_manager
