import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import allure
import pytest
from playwright.sync_api import BrowserContext, Page

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # noqa: E402

# 导入核心模块
from config.settings import Settings  # noqa: E402
from utils.common.logger import get_logger  # noqa: E402

# 延迟导入可选模块，按需加载
_ALLURE_HELPER: Any = None
_REPORT_GENERATOR: Any = None
_DB_MANAGER: Any = None
_TEST_DATA_MANAGER: Any = None
_TEST_ADVISOR: Any = None


def _get_allure_helper() -> Any:
    """延迟加载 AllureHelper"""
    global _ALLURE_HELPER
    if _ALLURE_HELPER is None:
        from utils.reporting.allure_helper import AllureHelper

        _ALLURE_HELPER = AllureHelper()
    return _ALLURE_HELPER


def _get_report_generator() -> Any:
    """延迟加载 ReportGenerator"""
    global _REPORT_GENERATOR
    if _REPORT_GENERATOR is None:
        from utils.reporting.report_generator import get_report_generator

        _REPORT_GENERATOR = get_report_generator()
    return _REPORT_GENERATOR


def _get_db_manager() -> Any:
    """延迟加载 DatabaseManager"""
    global _DB_MANAGER
    if _DB_MANAGER is None:
        from core.services.database.db_manager import get_db_manager

        _DB_MANAGER = get_db_manager()
    return _DB_MANAGER


def _get_test_data_manager() -> Any:
    """延迟加载 TestDataManager"""
    global _TEST_DATA_MANAGER
    if _TEST_DATA_MANAGER is None:
        from utils.data.test_data_manager import TestDataManager

        _TEST_DATA_MANAGER = TestDataManager(_get_db_manager())
    return _TEST_DATA_MANAGER


def _get_test_advisor() -> Any:
    """延迟加载 TestAdvisor"""
    global _TEST_ADVISOR
    if _TEST_ADVISOR is None:
        from utils.reporting.test_advisor import get_test_advisor

        _TEST_ADVISOR = get_test_advisor()
    return _TEST_ADVISOR


logger = get_logger(__name__)


def pytest_configure(config: Any) -> None:
    # 首先加载环境变量
    from config.settings import load_env_file

    load_env_file(".env.base")
    load_env_file(".env")

    # 设置Allure报告结果目录为reports/allure-results
    config.option.allure_report_dir = "reports/allure-results"
    # 清理Allure报告目录，避免报告累积
    import shutil

    allure_results_dir = "reports/allure-results"
    if os.path.exists(allure_results_dir):
        shutil.rmtree(allure_results_dir)
        logger.info("已清理Allure报告目录: %s", allure_results_dir)
    # 重新创建目录
    os.makedirs(allure_results_dir, exist_ok=True)
    logger.info("已创建 Allure 报告目录：%s", allure_results_dir)

    # 从环境变量读取浏览器配置
    browsers_env = os.getenv("PLAYWRIGHT_BROWSERS")
    if browsers_env:
        # 解析逗号分隔的浏览器列表
        browsers = [browser.strip() for browser in browsers_env.split(",")]
        # 设置浏览器选项
        config.option.browser = browsers
        logger.info("从环境变量 PLAYWRIGHT_BROWSERS 读取浏览器配置: %s", browsers)

    # 从环境变量读取单个浏览器配置
    browser_env = os.getenv("PLAYWRIGHT_BROWSER")
    if browser_env and not browsers_env:
        config.option.browser = [browser_env.strip()]
        logger.info("从环境变量 PLAYWRIGHT_BROWSER 读取浏览器配置: %s", browser_env)

    # 从 TEST_BROWSER 环境变量读取浏览器配置（兼容 CI 工作流）
    test_browser_env = os.getenv("TEST_BROWSER")
    if test_browser_env and not browsers_env and not browser_env:
        config.option.browser = [test_browser_env.strip()]
        logger.info("从环境变量 TEST_BROWSER 读取浏览器配置: %s", test_browser_env)


def _prepare_allure_categories() -> None:
    """
    准备 Allure categories.json 配置文件

    从 config/categories.json 复制到 reports/allure-results/
    确保每次生成报告时都有正确的分类配置
    """
    import shutil

    # 获取项目根目录（tests 的父目录）
    project_root = Path(__file__).parent.parent
    source_file = project_root / "config" / "categories.json"
    target_file = project_root / "reports" / "allure-results" / "categories.json"

    # 确保目标目录存在
    target_file.parent.mkdir(parents=True, exist_ok=True)

    # 复制配置文件
    if source_file.exists():
        shutil.copy2(source_file, target_file)
        logger.info("已复制 Allure categories.json: %s -> %s", source_file, target_file)
    else:
        logger.warning("未找到 Allure categories.json 配置文件：%s", source_file)
        logger.warning("Allure 报告将不会显示缺陷分类")


def pytest_sessionstart(session: Any) -> None:
    logger.info("=" * 50)
    logger.info("测试会话开始")
    logger.info("=" * 50)

    # 自动复制 Allure categories.json 配置文件
    _prepare_allure_categories()

    settings = Settings()
    config_summary = settings.get_config_summary()
    logger.info("配置摘要：%s", config_summary)

    report_gen = _get_report_generator()
    report_gen.start_session()
    logger.info("报告生成器会话已开始")


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    logger.info("=" * 50)
    logger.info("测试会话结束，退出码: %d", exitstatus)
    logger.info("=" * 50)

    report_gen = _get_report_generator()
    report_gen.end_session()
    logger.info("报告生成器会话已结束")

    html_report = report_gen.generate_html_report()
    json_report = report_gen.generate_json_report()
    history_file = report_gen.save_history()
    trend_report = report_gen.generate_trend_report()

    try:
        test_advisor = _get_test_advisor()
        advisor_report = test_advisor.generate_advisor_report()
        logger.info("  - 智能测试建议报告: %s", advisor_report)
    except Exception as e:
        logger.warning("生成智能测试建议报告时出错: %s", e)

    try:
        settings = Settings()
        if settings.video_enabled:
            video_root_dir = os.path.join("reports", "videos", datetime.now().strftime("%Y%m%d"))
            if os.path.exists(video_root_dir):
                for suite_dir in os.listdir(video_root_dir):
                    suite_path = os.path.join(video_root_dir, suite_dir)
                    if os.path.isdir(suite_path):
                        for test_dir in os.listdir(suite_path):
                            test_path = os.path.join(suite_path, test_dir)
                            if os.path.isdir(test_path):
                                video_files = [f for f in os.listdir(test_path) if f.endswith(".webm")]
                                if video_files:
                                    non_empty_videos = []
                                    for video_file in video_files:
                                        video_path = os.path.join(test_path, video_file)
                                        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                                            non_empty_videos.append(video_file)
                                        else:
                                            try:
                                                os.remove(video_path)
                                                logger.info("已删除空视频文件: %s", video_file)
                                            except Exception as e:
                                                logger.warning("删除空视频文件时出错: %s", e)

                                    if non_empty_videos:
                                        test_name_parts = test_dir.split("_")
                                        timestamp_start_index = -1
                                        for i, part in enumerate(reversed(test_name_parts)):
                                            if len(part) == 6 and part.isdigit():
                                                timestamp_start_index = len(test_name_parts) - i - 2
                                                break

                                        if timestamp_start_index > 0:
                                            test_name_part = "_".join(test_name_parts[:timestamp_start_index])
                                        else:
                                            last_underscore = test_dir.rfind("_")
                                            if last_underscore > 0:
                                                test_name_part = test_dir[:last_underscore]
                                            else:
                                                test_name_part = test_dir

                                        for video_file in non_empty_videos:
                                            try:
                                                original_video_path = os.path.join(test_path, video_file)
                                                mtime = os.path.getmtime(original_video_path)
                                                timestamp = datetime.fromtimestamp(mtime).strftime("%H%M%S")
                                                new_video_name = f"{test_name_part}_{timestamp}.webm"
                                                new_video_path = os.path.join(suite_path, new_video_name)

                                                if os.path.exists(new_video_path):
                                                    try:
                                                        os.remove(new_video_path)
                                                        logger.info("已删除已存在的视频文件: %s", new_video_name)
                                                    except Exception as e:
                                                        logger.warning("删除已存在的视频文件时出错: %s", e)

                                                os.rename(original_video_path, new_video_path)
                                                logger.info("视频文件已移动并重命名: %s", new_video_name)
                                            except Exception as e:
                                                logger.error("移动并重命名视频文件时出错: %s", e)

        video_root_dir = os.path.join("reports", "videos", datetime.now().strftime("%Y%m%d"))
        if os.path.exists(video_root_dir):
            for suite_dir in os.listdir(video_root_dir):
                suite_path = os.path.join(video_root_dir, suite_dir)
                if os.path.isdir(suite_path):
                    for test_dir in os.listdir(suite_path):
                        test_path = os.path.join(suite_path, test_dir)
                        if os.path.isdir(test_path) and not os.listdir(test_path):
                            try:
                                os.rmdir(test_path)
                                logger.info("已删除空测试目录: %s", test_dir)
                            except Exception as e:
                                logger.warning("删除空测试目录时出错: %s", e)
                    if not os.listdir(suite_path):
                        try:
                            os.rmdir(suite_path)
                            logger.info("已删除空套件目录: %s", suite_dir)
                        except Exception as e:
                            logger.warning("删除空套件目录时出错: %s", e)
    except Exception as e:
        logger.error("处理视频文件时出错: %s", e)

    try:
        db_manager = _get_db_manager()
        db_manager.close()
        logger.info("数据库连接池已关闭")
    except Exception as e:
        logger.warning("关闭数据库连接池时出错: %s", e)

    logger.info("测试汇总报告已生成:")
    logger.info("  - HTML: %s", html_report)
    logger.info("  - JSON: %s", json_report)
    logger.info("  - 历史记录: %s", history_file)
    if trend_report:
        logger.info("  - 趋势报告: %s", trend_report)


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


@allure.step("附加测试附件")
def _attach_test_artifacts(item: Any) -> None:
    """
    附加测试附件到 Allure 报告
    """
    import os

    try:
        test_name = getattr(item, "test_name", item.nodeid.split("::")[-1].replace("/", "_").replace("\\", "_"))
        logger.debug("开始附加附件到 Allure 报告，测试名称: %s", test_name)
    except Exception as e:
        test_name = "unknown_test"
        logger.debug("获取测试名称时出错: %s", e)

    # 1. 附加截图
    try:
        screenshot_path = getattr(item, "screenshot_path", None)
        logger.debug("截图路径: %s", screenshot_path)
        if screenshot_path and os.path.exists(screenshot_path):
            logger.debug("截图文件存在，大小: %s bytes", os.path.getsize(screenshot_path))
            allure.attach.file(
                screenshot_path,
                name=f"{test_name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.debug("截图已附加到 Allure 报告: %s", screenshot_path)
        else:
            logger.debug("截图路径不存在或为空: %s", screenshot_path)
    except Exception as e:
        logger.debug("附加截图到 Allure 报告时出错: %s", e)

    # 2. 附加视频
    try:
        from config.settings import Settings

        settings = Settings()
        logger.info("视频功能是否启用: %s", settings.video_enabled)
        if settings.video_enabled:
            video_dir = getattr(item, "video_dir", None)
            logger.info("视频目录: %s", video_dir)

            # 尝试在原始视频目录中查找视频文件
            video_found = False
            if video_dir and os.path.exists(video_dir):
                logger.info("视频目录存在，开始检查视频文件")
                import time

                # 增加等待时间，确保视频文件完全写入
                time.sleep(3)
                logger.info("等待 3 秒后开始检查视频文件")

                # 重试机制：尝试多次检查视频文件
                max_retries = 3
                for retry in range(max_retries):
                    if os.path.exists(video_dir):
                        video_files = [f for f in os.listdir(video_dir) if f.endswith(".webm")]
                        logger.info("视频文件数量: %s (尝试 %d/%d)", len(video_files), retry + 1, max_retries)
                        if video_files:
                            for video_file in video_files:
                                video_path = os.path.join(video_dir, video_file)
                                logger.info("视频文件路径: %s", video_path)
                                if os.path.exists(video_path):
                                    file_size = os.path.getsize(video_path)
                                    logger.info("视频文件存在，大小: %s bytes", file_size)
                                    if file_size > 0:
                                        logger.info("视频文件大小大于 0，附加到 Allure 报告")
                                        allure.attach.file(
                                            video_path,
                                            name=f"{test_name}_video",
                                            attachment_type=allure.attachment_type.WEBM,
                                        )
                                        logger.info("视频文件已附加到 Allure 报告: %s", video_path)
                                        video_found = True
                                        # 找到有效视频文件后跳出循环
                                        break
                                if os.path.exists(video_path):
                                    if os.path.getsize(video_path) == 0:
                                        logger.warning("视频文件大小为 0: %s", video_path)
                                else:
                                    logger.warning("视频文件不存在: %s", video_path)
                            # 如果找到有效视频文件，跳出重试循环
                            if video_found:
                                break
                        else:
                            logger.warning("视频目录中没有视频文件: %s", video_dir)
                    else:
                        logger.warning("视频目录不存在: %s", video_dir)
                    # 如果不是最后一次重试，等待后再次检查
                    if retry < max_retries - 1 and not video_found:
                        time.sleep(2)
                        logger.info("等待 2 秒后再次检查视频文件")

            # 如果在原始视频目录中没有找到视频文件，尝试在套件目录中查找
            if not video_found and video_dir:
                try:
                    # 从视频目录路径中提取套件目录
                    import os

                    parts = video_dir.split(os.sep)
                    if len(parts) >= 4:
                        suite_dir = os.path.join(parts[0], parts[1], parts[2], parts[3])
                        logger.info("尝试在套件目录中查找视频文件: %s", suite_dir)

                        if os.path.exists(suite_dir):
                            # 提取测试名称部分，用于匹配视频文件
                            test_name_part = test_name.split("[")[0]
                            logger.info("测试名称部分: %s", test_name_part)

                            # 在套件目录中查找匹配的视频文件
                            for file in os.listdir(suite_dir):
                                if file.endswith(".webm") and test_name_part in file:
                                    video_path = os.path.join(suite_dir, file)
                                    logger.info("在套件目录中找到视频文件: %s", video_path)
                                    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                                        logger.info("视频文件存在，大小: %s bytes", os.path.getsize(video_path))
                                        allure.attach.file(
                                            video_path,
                                            name=f"{test_name}_video",
                                            attachment_type=allure.attachment_type.WEBM,
                                        )
                                        logger.info("视频文件已附加到 Allure 报告: %s", video_path)
                                        video_found = True
                                        break
                except Exception as e:
                    logger.error("在套件目录中查找视频文件时出错: %s", e)

            if not video_found:
                logger.warning("未找到视频文件")
        else:
            logger.info("视频功能未启用")
    except Exception as e:
        logger.error("附加视频文件到 Allure 报告时出错: %s", e)
        import traceback

        logger.error(traceback.format_exc())

    logger.debug("附件附加完成")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_teardown(item: Any, nextitem: Any) -> Generator[None, Any, None]:
    """
    测试拆卸阶段
    """
    yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Generator[None, Any, Any]:
    """
    Allure官方推荐的最佳实践：在call阶段之后统一附加截图和视频
    确保所有附件都在同一阶段，不会分散在不同位置
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call":
        logger.debug("收集测试结果: %s - %s", item.nodeid, rep.outcome)

        # 记录测试结果到报告生成器
        try:
            report_gen = _get_report_generator()
            error_msg = str(rep.longrepr) if rep.failed else None
            duration = rep.duration if rep.duration else 0.0
            report_gen.add_result(nodeid=item.nodeid, outcome=rep.outcome, duration=duration, error_msg=error_msg)
            logger.debug("测试结果已添加到报告生成器")
        except Exception as e:
            logger.debug("添加测试结果到报告生成器时出错: %s", e)

    # 在 teardown 阶段附加测试附件，确保截图已经生成
    if rep.when == "teardown":
        logger.debug("在 teardown 阶段附加测试附件")
        _attach_test_artifacts(item)


@pytest.fixture(autouse=True)
def allure_step(request: Any) -> Generator[None, Any, None]:
    start_time = datetime.now()
    setattr(request.node, "start_time", start_time)

    with allure.step(f"开始执行测试: {request.node.name}"):
        yield
    with allure.step(f"结束执行测试: {request.node.name}"):
        pass


@pytest.fixture(scope="function")
def test_data_cleanup(request: Any) -> Generator[Dict[str, Any], Any, None]:
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
    manager = _get_db_manager()
    yield manager


@pytest.fixture(scope="function")
def db_session(db_manager: Any) -> Generator[Any, Any, None]:
    with db_manager.get_session() as session:
        yield session
        session.rollback()


@pytest.fixture(scope="function")
def test_data_manager(db_manager: Any) -> Generator[Any, Any, None]:
    manager = _get_test_data_manager()
    yield manager
    manager.cleanup()


@pytest.fixture(scope="function")
def mock_server() -> Generator[Any, Any, None]:
    from core.services.api.mock_server import MockServer

    server = MockServer()
    server.start()
    yield server
    server.stop()
