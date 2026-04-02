import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from core.utils.logger import get_logger
from core.utils.path_helper import PathHelper

# 延迟导入可选模块，按需加载
_allure_helper: Any = None
_report_generator: Any = None
_browser_pool: Any = None
_db_manager: Any = None
_test_data_manager: Any = None
_test_advisor: Any = None


def _get_allure_helper() -> Any:
    """延迟加载 AllureHelper"""
    global _allure_helper
    if _allure_helper is None:
        from core.utils.allure_helper import AllureHelper

        _allure_helper = AllureHelper()
    return _allure_helper


def _get_report_generator() -> Any:
    """延迟加载 ReportGenerator"""
    global _report_generator
    if _report_generator is None:
        from core.utils.report_generator import get_report_generator

        _report_generator = get_report_generator()
    return _report_generator


def _get_browser_pool() -> Any:
    """延迟加载 BrowserPool"""
    global _browser_pool
    if _browser_pool is None:
        from core.utils.browser_pool import get_browser_pool

        _browser_pool = get_browser_pool()
    return _browser_pool


def _get_db_manager() -> Any:
    """延迟加载 DatabaseManager"""
    global _db_manager
    if _db_manager is None:
        from core.utils.db_manager import get_db_manager

        _db_manager = get_db_manager()
    return _db_manager


def _get_test_data_manager() -> Any:
    """延迟加载 TestDataManager"""
    global _test_data_manager
    if _test_data_manager is None:
        from core.utils.test_data_manager import TestDataManager

        _test_data_manager = TestDataManager(_get_db_manager())
    return _test_data_manager


def _get_test_advisor() -> Any:
    """延迟加载 TestAdvisor"""
    global _test_advisor
    if _test_advisor is None:
        from core.utils.test_advisor import get_test_advisor

        _test_advisor = get_test_advisor()
    return _test_advisor


logger = get_logger(__name__)


def pytest_configure(config: Any) -> None:
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
    logger.info("已创建Allure报告目录: %s", allure_results_dir)


def pytest_sessionstart(session: Any) -> None:
    logger.info("=" * 50)
    logger.info("测试会话开始")
    logger.info("=" * 50)

    from config.settings import Settings

    settings = Settings()
    config_summary = settings.get_config_summary()
    logger.info("配置摘要: %s", config_summary)

    report_gen = _get_report_generator()
    report_gen.start_session()
    logger.info("报告生成器会话已开始")


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    logger.info("=" * 50)
    logger.info(f"测试会话结束，退出码: {exitstatus}")
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
        logger.info(f"  - 智能测试建议报告: {advisor_report}")
    except Exception as e:
        logger.warning(f"生成智能测试建议报告时出错: {e}")

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
                                video_files = [
                                    f for f in os.listdir(test_path) if f.endswith(".webm")
                                ]
                                if video_files:
                                    non_empty_videos = []
                                    for video_file in video_files:
                                        video_path = os.path.join(test_path, video_file)
                                        if (
                                            os.path.exists(video_path)
                                            and os.path.getsize(video_path) > 0
                                        ):
                                            non_empty_videos.append(video_file)
                                        else:
                                            try:
                                                os.remove(video_path)
                                                logger.info(f"已删除空视频文件: {video_file}")
                                            except Exception as e:
                                                logger.warning(f"删除空视频文件时出错: {e}")

                                    if non_empty_videos:
                                        test_name_parts = test_dir.split("_")
                                        timestamp_start_index = -1
                                        for i, part in enumerate(reversed(test_name_parts)):
                                            if len(part) == 6 and part.isdigit():
                                                timestamp_start_index = len(test_name_parts) - i - 2
                                                break

                                        if timestamp_start_index > 0:
                                            test_name_part = "_".join(
                                                test_name_parts[:timestamp_start_index]
                                            )
                                        else:
                                            last_underscore = test_dir.rfind("_")
                                            if last_underscore > 0:
                                                test_name_part = test_dir[:last_underscore]
                                            else:
                                                test_name_part = test_dir

                                        for video_file in non_empty_videos:
                                            try:
                                                original_video_path = os.path.join(
                                                    test_path, video_file
                                                )
                                                mtime = os.path.getmtime(original_video_path)
                                                timestamp = datetime.fromtimestamp(mtime).strftime(
                                                    "%H%M%S"
                                                )
                                                new_video_name = (
                                                    f"{test_name_part}_{timestamp}.webm"
                                                )
                                                new_video_path = os.path.join(
                                                    suite_path, new_video_name
                                                )

                                                if os.path.exists(new_video_path):
                                                    try:
                                                        os.remove(new_video_path)
                                                        logger.info(
                                                            f"已删除已存在的视频文件: {new_video_name}"
                                                        )
                                                    except Exception as e:
                                                        logger.warning(
                                                            f"删除已存在的视频文件时出错: {e}"
                                                        )

                                                os.rename(original_video_path, new_video_path)
                                                logger.info(
                                                    f"视频文件已移动并重命名: {new_video_name}"
                                                )
                                            except Exception as e:
                                                logger.error(f"移动并重命名视频文件时出错: {e}")

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
                                logger.info(f"已删除空测试目录: {test_dir}")
                            except Exception as e:
                                logger.warning(f"删除空测试目录时出错: {e}")
                    if not os.listdir(suite_path):
                        try:
                            os.rmdir(suite_path)
                            logger.info(f"已删除空套件目录: {suite_dir}")
                        except Exception as e:
                            logger.warning(f"删除空套件目录时出错: {e}")
    except Exception as e:
        logger.error(f"处理视频文件时出错: {e}")

    pool = _get_browser_pool()
    pool.cleanup()
    logger.info("浏览器实例池已清理")

    try:
        db_manager = _get_db_manager()
        db_manager.close()
        logger.info("数据库连接池已关闭")
    except Exception as e:
        logger.warning(f"关闭数据库连接池时出错: {e}")

    logger.info(f"测试汇总报告已生成:")
    logger.info(f"  - HTML: {html_report}")
    logger.info(f"  - JSON: {json_report}")
    logger.info(f"  - 历史记录: {history_file}")
    if trend_report:
        logger.info(f"  - 趋势报告: {trend_report}")


@pytest.fixture(scope="session")
def settings() -> Settings:
    """获取配置"""
    return Settings()


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, Any, None]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: Playwright, settings: Settings) -> Generator[Browser, Any, None]:
    """使用浏览器实例池的浏览器fixture"""
    browser_type = settings.browser_type
    headless = settings.headless
    slow_mo = settings.slow_mo
    viewport = settings.viewport

    logger.info(f"初始化浏览器池: {browser_type}, headless: {headless}, viewport: {viewport}")

    pool = _get_browser_pool()
    pool.initialize(playwright, browser_type, headless, slow_mo)

    browser_obj = pool.acquire_browser()
    if not browser_obj:
        raise RuntimeError("无法获取浏览器实例")

    logger.info(f"成功获取浏览器实例: {id(browser_obj)}")

    yield browser_obj

    pool.release_browser(browser_obj)
    logger.info(f"浏览器实例已释放: {id(browser_obj)}")


@pytest.fixture(scope="function")
def browser_context_args(request: Any, settings: Settings) -> Dict[str, Any]:
    """扩展 pytest-playwright 的 browser_context_args fixture，添加自定义配置"""
    args: Dict[str, Any] = {
        "viewport": settings.viewport,
        "ignore_https_errors": True,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
    }

    test_node = request.node
    test_fixtures = getattr(test_node, "fixturenames", [])
    uses_browser = any(
        fixture in test_fixtures for fixture in ["page", "browser", "browser_context"]
    )

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

        args["record_video_dir"] = video_dir
        args["record_video_size"] = settings.video_size
        logger.info(f"为测试 {test_node.name} 启用录屏功能，视频保存目录: {video_dir}")

    return args


@pytest.fixture(scope="function")
def page(context: BrowserContext, request: Any, settings: Settings) -> Generator[Page, Any, None]:
    page_obj = context.new_page()
    page_obj.set_default_timeout(30000)

    yield page_obj

    try:
        screenshot_path = PathHelper.get_screenshot_path(request.node.name)
        page_obj.screenshot(path=screenshot_path, full_page=True)
        setattr(request.node, "screenshot_path", screenshot_path)
        print(f"[DEBUG] 测试截图已保存: {screenshot_path}")
    except Exception as e:
        print(f"[DEBUG] 保存测试截图时出错: {e}")

    page_obj.close()


@allure.step("附加测试附件")
def _attach_test_artifacts(item: Any) -> None:
    """
    附加测试附件到 Allure 报告
    """
    try:
        test_name = getattr(
            item, "test_name", item.nodeid.split("::")[-1].replace("/", "_").replace("\\", "_")
        )
        print(f"[DEBUG] 开始附加附件到 Allure 报告，测试名称: {test_name}")
    except Exception as e:
        test_name = "unknown_test"
        print(f"[DEBUG] 获取测试名称时出错: {e}")

    # 1. 附加截图
    try:
        screenshot_path = getattr(item, "screenshot_path", None)
        print(f"[DEBUG] 截图路径: {screenshot_path}")
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"[DEBUG] 截图文件存在，大小: {os.path.getsize(screenshot_path)} bytes")
            allure.attach.file(
                screenshot_path,
                name=f"{test_name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            print(f"[DEBUG] 截图已附加到 Allure 报告: {screenshot_path}")
        else:
            print(f"[DEBUG] 截图路径不存在或为空: {screenshot_path}")
    except Exception as e:
        print(f"[DEBUG] 附加截图到 Allure 报告时出错: {e}")

    # 2. 附加视频
    try:
        from config.settings import Settings

        settings = Settings()
        print(f"[DEBUG] 视频功能是否启用: {settings.video_enabled}")
        if settings.video_enabled:
            video_dir = getattr(item, "video_dir", None)
            print(f"[DEBUG] 视频目录: {video_dir}")
            if video_dir and os.path.exists(video_dir):
                print(f"[DEBUG] 视频目录存在")
                import time

                time.sleep(1)

                video_files = [f for f in os.listdir(video_dir) if f.endswith(".webm")]
                print(f"[DEBUG] 视频文件数量: {len(video_files)}")
                if video_files:
                    for video_file in video_files:
                        video_path = os.path.join(video_dir, video_file)
                        print(f"[DEBUG] 视频文件路径: {video_path}")
                        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                            print(
                                f"[DEBUG] 视频文件存在，大小: {os.path.getsize(video_path)} bytes"
                            )
                            allure.attach.file(
                                video_path,
                                name=f"{test_name}_video",
                                attachment_type=allure.attachment_type.WEBM,
                            )
                            print(f"[DEBUG] 视频文件已附加到 Allure 报告: {video_path}")
                            break
                        else:
                            print(f"[DEBUG] 视频文件不存在或为空: {video_path}")
                else:
                    print(f"[DEBUG] 视频目录中没有视频文件: {video_dir}")
            else:
                print(f"[DEBUG] 视频目录不存在: {video_dir}")
        else:
            print("[DEBUG] 视频功能未启用")
    except Exception as e:
        print(f"[DEBUG] 附加视频文件到 Allure 报告时出错: {e}")

    print("[DEBUG] 附件附加完成")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_teardown(item: Any, nextitem: Any) -> Generator[None, Any, None]:
    """
    Allure官方推荐的最佳实践：在teardown的yield之后附加视频
    确保所有fixture清理完成后再附加视频
    """
    yield

    # 附加测试附件
    _attach_test_artifacts(item)


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
        print(f"[DEBUG] 收集测试结果: {item.nodeid} - {rep.outcome}")

        # 记录测试结果到报告生成器
        try:
            report_gen = _get_report_generator()
            error_msg = str(rep.longrepr) if rep.failed else None
            duration = rep.duration if rep.duration else 0.0
            report_gen.add_result(
                nodeid=item.nodeid, outcome=rep.outcome, duration=duration, error_msg=error_msg
            )
            print(f"[DEBUG] 测试结果已添加到报告生成器")
        except Exception as e:
            print(f"[DEBUG] 添加测试结果到报告生成器时出错: {e}")


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

    logger.info(f"开始清理测试数据: {request.node.name}")

    for cleanup_func in cleanup_data.get("cleanup_funcs", []):
        try:
            cleanup_func()
            logger.info(f"清理函数执行成功")
        except Exception as e:
            logger.error(f"清理函数执行失败: {e}")

    logger.info(f"测试数据清理完成: {request.node.name}")


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
                logger.info(f"Setup 执行成功: {request.node.name}")
            except Exception as e:
                logger.error(f"Setup 执行失败: {e}")
                raise

        if teardown_func:
            teardown_funcs.append(teardown_func)

    yield register_setup_teardown

    for teardown_func in reversed(teardown_funcs):
        try:
            teardown_func()
            logger.info(f"Teardown 执行成功: {request.node.name}")
        except Exception as e:
            logger.error(f"Teardown 执行失败: {e}")


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
    from core.utils.mock_server import MockServer

    server = MockServer()
    server.start()
    yield server
    server.stop()
