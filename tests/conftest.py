import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import allure
import pytest
from playwright.sync_api import BrowserContext, Page

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 导入核心模块
from config.settings import Settings, load_env_file
from tests.utils.attachment_manager import AttachmentManager
from tests.utils.report_manager import ReportManager
from tests.utils.video_manager import VideoManager
from utils.common.logger import get_logger

logger = get_logger(__name__)

# 全局管理器实例
_report_manager: ReportManager = None
_attachment_manager: AttachmentManager = None
_video_manager: VideoManager = None


def pytest_configure(config: Any) -> None:
    """pytest 配置钩子"""
    # 加载环境变量
    load_env_file(".env.base")
    load_env_file(".env")

    # 设置 Allure 报告目录
    config.option.allure_report_dir = "reports/allure-results"
    _prepare_allure_report_dir()

    # 配置浏览器选项
    _configure_browser_options(config)


def _prepare_allure_report_dir() -> None:
    """准备 Allure 报告目录"""
    import shutil

    allure_results_dir = "reports/allure-results"
    if os.path.exists(allure_results_dir):
        shutil.rmtree(allure_results_dir)
        logger.info("已清理Allure报告目录: %s", allure_results_dir)

    os.makedirs(allure_results_dir, exist_ok=True)
    logger.info("已创建 Allure 报告目录：%s", allure_results_dir)


def _configure_browser_options(config: Any) -> None:
    """配置浏览器选项"""
    browsers_env = os.getenv("PLAYWRIGHT_BROWSERS")
    if browsers_env:
        browsers = [browser.strip() for browser in browsers_env.split(",")]
        config.option.browser = browsers
        logger.info("从环境变量 PLAYWRIGHT_BROWSERS 读取浏览器配置: %s", browsers)
        return

    browser_env = os.getenv("PLAYWRIGHT_BROWSER")
    if browser_env:
        config.option.browser = [browser_env.strip()]
        logger.info("从环境变量 PLAYWRIGHT_BROWSER 读取浏览器配置: %s", browser_env)
        return

    test_browser_env = os.getenv("TEST_BROWSER")
    if test_browser_env:
        config.option.browser = [test_browser_env.strip()]
        logger.info("从环境变量 TEST_BROWSER 读取浏览器配置: %s", test_browser_env)


def pytest_sessionstart(session: Any) -> None:
    """测试会话开始钩子"""
    logger.info("=" * 50)
    logger.info("测试会话开始")
    logger.info("=" * 50)

    # 准备 Allure categories.json
    _prepare_allure_categories()

    # 初始化报告管理器
    global _report_manager
    _report_manager = ReportManager()
    _report_manager.initialize()

    # 记录配置摘要
    settings = Settings()
    config_summary = settings.get_config_summary()
    logger.info("配置摘要：%s", config_summary)


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    """测试会话结束钩子"""
    logger.info("=" * 50)
    logger.info("测试会话结束，退出码: %d", exitstatus)
    logger.info("=" * 50)

    # 完成报告生成
    global _report_manager
    if _report_manager:
        reports = _report_manager.finalize(exitstatus)
        logger.info("测试汇总报告已生成:")
        logger.info("  - HTML: %s", reports.get("html_report"))
        logger.info("  - JSON: %s", reports.get("json_report"))
        logger.info("  - 历史记录: %s", reports.get("history_file"))
        if reports.get("trend_report"):
            logger.info("  - 趋势报告: %s", reports.get("trend_report"))

    # 处理视频文件
    _process_video_files()

    # 关闭数据库连接
    _close_database()


def _prepare_allure_categories() -> None:
    """准备 Allure categories.json 配置文件"""
    import shutil

    project_root = Path(__file__).parent.parent
    source_file = project_root / "config" / "categories.json"
    target_file = project_root / "reports" / "allure-results" / "categories.json"

    target_file.parent.mkdir(parents=True, exist_ok=True)

    if source_file.exists():
        shutil.copy2(source_file, target_file)
        logger.info("已复制 Allure categories.json: %s -> %s", source_file, target_file)
    else:
        logger.warning("未找到 Allure categories.json 配置文件：%s", source_file)


def _process_video_files() -> None:
    """处理视频文件"""
    try:
        settings = Settings()
        if settings.video_enabled:
            global _video_manager
            _video_manager = VideoManager()
            _video_manager.clean_empty_videos()
            _video_manager.clean_empty_directories()
    except Exception as e:
        logger.error("处理视频文件时出错: %s", e)


def _close_database() -> None:
    """关闭数据库连接"""
    try:
        from core.services.database.db_manager import get_db_manager

        db_manager = get_db_manager()
        db_manager.close()
        logger.info("数据库连接池已关闭")
    except Exception as e:
        logger.warning("关闭数据库连接池时出错: %s", e)


@pytest.fixture(scope="session")
def settings() -> Settings:
    """获取配置"""
    return Settings()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """扩展 pytest-playwright 的 browser_type_launch_args fixture，从环境变量读取配置"""
    # 首先检查 HEADLESS 环境变量（CI 工作流使用）
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() == "true"
        logger.info(f"从环境变量 HEADLESS 读取无头模式配置: {headless}")
    else:
        # 然后检查 PLAYWRIGHT_HEADLESS 环境变量
        headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        logger.info(f"从环境变量 PLAYWRIGHT_HEADLESS 读取无头模式配置: {headless}")

    # 强制在 CI 环境中使用无头模式
    is_ci = os.getenv("CI", "false").lower() == "true"
    if is_ci:
        headless = True
        logger.info("CI 环境中强制使用无头模式")

    return {
        **browser_type_launch_args,
        "headless": headless,
    }


@pytest.fixture(scope="function")
def browser_context_args(request: Any, settings: Settings, browser_context_args) -> Dict[str, Any]:
    """扩展 pytest-playwright 的 browser_context_args fixture，添加自定义配置"""
    args: Dict[str, Any] = {
        **browser_context_args,
        "viewport": settings.viewport,
        "ignore_https_errors": True,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
    }

    test_node = request.node
    test_fixtures = getattr(test_node, "fixturenames", [])
    uses_browser = any(fixture in test_fixtures for fixture in ["page", "browser", "browser_context"])

    if settings.video_enabled and uses_browser:
        test_file = test_node.fspath.basename if hasattr(test_node, "fspath") else "unknown"
        if hasattr(test_node, "fspath"):
            test_suite = os.path.splitext(test_file)[0]
        else:
            test_suite = "unknown"

        test_name = test_node.name.replace("/", "_").replace("\\", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        video_dir = os.path.join(
            "reports",
            "videos",
            datetime.now().strftime("%Y%m%d"),
            test_suite,
            f"{test_name}_{timestamp}",
        )
        os.makedirs(video_dir, exist_ok=True)

        setattr(test_node, "video_dir", video_dir)
        setattr(test_node, "test_name", test_name)

        # 配置视频录制，确保录制整个浏览器窗口
        args["record_video_dir"] = video_dir
        # 使用与视口大小匹配的视频尺寸，确保录制整个浏览器窗口
        args["record_video_size"] = settings.viewport
        logger.info(
            "为测试 %s 启用录屏功能，视频保存目录: %s，视频尺寸: %s", test_node.name, video_dir, settings.viewport
        )

    return args


@pytest.fixture(scope="function")
def page(context: BrowserContext, request: Any, settings: Settings) -> Generator[Page, Any, None]:
    """扩展 pytest-playwright 的 page fixture，添加自定义功能"""
    page_obj = context.new_page()
    page_obj.set_default_timeout(30000)

    yield page_obj

    try:
        screenshot_dir = Path("reports", "screenshots", datetime.now().strftime("%Y%m%d"))
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{request.node.name}.png"
        page_obj.screenshot(path=screenshot_path, full_page=True)
        setattr(request.node, "screenshot_path", screenshot_path)
        logger.info("测试截图已保存: %s", screenshot_path)
    except Exception as e:
        logger.warning("保存测试截图时出错: %s", e)

    page_obj.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Generator[None, Any, Any]:
    """测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call":
        # 记录测试结果到报告生成器
        global _report_manager
        if _report_manager:
            error_msg = str(rep.longrepr) if rep.failed else None
            duration = rep.duration if rep.duration else 0.0
            _report_manager.add_result(item.nodeid, rep.outcome, duration, error_msg)

    # 在 teardown 阶段附加测试附件
    if rep.when == "teardown":
        global _attachment_manager
        if _attachment_manager is None:
            _attachment_manager = AttachmentManager()
        _attachment_manager.attach_all_artifacts(item)


@pytest.fixture(autouse=True)
def allure_step(request: Any) -> Generator[None, Any, None]:
    """Allure 步骤 fixture"""
    start_time = datetime.now()
    setattr(request.node, "start_time", start_time)

    with allure.step(f"开始执行测试: {request.node.name}"):
        yield
    with allure.step(f"结束执行测试: {request.node.name}"):
        pass


@pytest.fixture(scope="function")
def test_data_cleanup(request: Any) -> Generator[Dict[str, Any], Any, None]:
    """测试数据清理 fixture"""
    cleanup_data: Dict[str, Any] = {"items": [], "cleanup_funcs": []}

    yield cleanup_data

    logger.info("开始清理测试数据: %s", request.node.name)

    for cleanup_func in cleanup_data.get("cleanup_funcs", []):
        try:
            cleanup_func()
            logger.info("清理函数执行成功")
        except Exception as e:
            logger.error("清理函数执行失败: %s", e)

    logger.info("测试数据清理完成: %s", request.node.name)


@pytest.fixture(scope="function")
def setup_teardown(request: Any) -> Generator[Callable[..., None], Any, None]:
    """Setup/Teardown fixture"""
    teardown_funcs: List[Callable[..., None]] = []

    def register_setup_teardown(
        setup_func: Optional[Callable[..., None]] = None,
        teardown_func: Optional[Callable[..., None]] = None,
    ) -> None:
        if setup_func:
            try:
                setup_func()
                logger.info("Setup 执行成功: %s", request.node.name)
            except Exception as e:
                logger.error("Setup 执行失败: %s", e)
                raise

        if teardown_func:
            teardown_funcs.append(teardown_func)

    yield register_setup_teardown

    for teardown_func in reversed(teardown_funcs):
        try:
            teardown_func()
            logger.info("Teardown 执行成功: %s", request.node.name)
        except Exception as e:
            logger.error("Teardown 执行失败: %s", e)


@pytest.fixture(scope="session")
def db_manager() -> Generator[Any, Any, None]:
    """数据库管理器 fixture"""
    from core.services.database.db_manager import get_db_manager

    manager = get_db_manager()
    yield manager


@pytest.fixture(scope="function")
def db_session(db_manager: Any) -> Generator[Any, Any, None]:
    """数据库会话 fixture"""
    with db_manager.get_session() as session:
        yield session
        session.rollback()


@pytest.fixture(scope="function")
def test_data_manager(db_manager: Any) -> Generator[Any, Any, None]:
    """测试数据管理器 fixture"""
    from utils.data.test_data_manager import TestDataManager

    manager = TestDataManager(db_manager)
    yield manager
    manager.cleanup()


@pytest.fixture(scope="function")
def mock_server() -> Generator[Any, Any, None]:
    """Mock 服务器 fixture"""
    from core.services.api.mock_server import MockServer

    server = MockServer()
    server.start()
    yield server
    server.stop()