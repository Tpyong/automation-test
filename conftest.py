import os
import sys
import allure
import pytest
from datetime import datetime
from typing import Generator, Callable, Optional
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from core.utils.logger import get_logger
from core.utils.path_helper import PathHelper

# 延迟导入可选模块，按需加载
_allure_helper = None
_report_generator = None
_browser_pool = None

def _get_allure_helper():
    """延迟加载 AllureHelper"""
    global _allure_helper
    if _allure_helper is None:
        from core.utils.allure_helper import AllureHelper
        _allure_helper = AllureHelper()
    return _allure_helper

def _get_report_generator():
    """延迟加载 ReportGenerator"""
    global _report_generator
    if _report_generator is None:
        from core.utils.report_generator import get_report_generator
        _report_generator = get_report_generator()
    return _report_generator

def _get_browser_pool():
    """延迟加载 BrowserPool"""
    global _browser_pool
    if _browser_pool is None:
        from core.utils.browser_pool import get_browser_pool
        _browser_pool = get_browser_pool()
    return _browser_pool

logger = get_logger(__name__)


def pytest_configure(config):
    # config.option.allure_report_dir = "reports/allure-report"
    # 不设置allure_report_dir，避免pytest自动生成Allure报告
    # 报告生成由专门的allure-report作业处理
    pass


def pytest_sessionstart(session):
    logger.info("=" * 50)
    logger.info("测试会话开始")
    logger.info("=" * 50)
    
    # 记录配置摘要
    from config.settings import Settings
    settings = Settings()
    config_summary = settings.get_config_summary()
    logger.info(f"配置摘要: {config_summary}")
    
    # 开始收集测试结果
    report_gen = _get_report_generator()
    report_gen.start_session()
    logger.info("报告生成器会话已开始")


def pytest_sessionfinish(session, exitstatus):
    logger.info("=" * 50)
    logger.info(f"测试会话结束，退出码: {exitstatus}")
    logger.info("=" * 50)
    
    # 生成测试结果汇总报告
    report_gen = _get_report_generator()
    report_gen.end_session()
    logger.info("报告生成器会话已结束")
    
    # 生成 HTML 和 JSON 报告
    html_report = report_gen.generate_html_report()
    json_report = report_gen.generate_json_report()
    
    # 保存测试结果到历史记录
    history_file = report_gen.save_history()
    
    # 生成测试趋势报告
    trend_report = report_gen.generate_trend_report()
    
    # 清理浏览器实例池
    pool = _get_browser_pool()
    pool.cleanup()
    logger.info("浏览器实例池已清理")
    
    logger.info(f"测试汇总报告已生成:")
    logger.info(f"  - HTML: {html_report}")
    logger.info(f"  - JSON: {json_report}")
    logger.info(f"  - 历史记录: {history_file}")
    if trend_report:
        logger.info(f"  - 趋势报告: {trend_report}")


def pytest_runtest_makereport(item, call):
    if call.when == "call":
        if call.excinfo is not None:
            logger.error(f"测试用例 {item.nodeid} 执行失败: {call.excinfo.value}")
        else:
            logger.info(f"测试用例 {item.nodeid} 执行成功")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: Playwright, settings: Settings) -> Generator[Browser, None, None]:
    """使用浏览器实例池的浏览器fixture"""
    browser_type = settings.browser_type
    headless = settings.headless
    slow_mo = settings.slow_mo
    viewport = settings.viewport

    logger.info(f"初始化浏览器池: {browser_type}, headless: {headless}, viewport: {viewport}")

    # 初始化浏览器池
    pool = _get_browser_pool()
    pool.initialize(playwright, browser_type, headless, slow_mo)

    # 获取浏览器实例
    browser = pool.acquire_browser()
    if not browser:
        raise RuntimeError("无法获取浏览器实例")

    logger.info(f"成功获取浏览器实例: {id(browser)}")
    
    yield browser

    # 释放浏览器实例回池中
    pool.release_browser(browser)
    logger.info(f"浏览器实例已释放: {id(browser)}")


@pytest.fixture(scope="function")
def context(browser: Browser, settings: Settings) -> Generator[BrowserContext, None, None]:
    context_options = {
        "viewport": settings.viewport,
        "ignore_https_errors": True,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai"
    }
    
    # 如果启用了录屏，添加录屏配置
    if settings.video_enabled:
        video_dir = os.path.join("videos", datetime.now().strftime("%Y%m%d"))
        os.makedirs(video_dir, exist_ok=True)
        context_options["record_video_dir"] = video_dir
        context_options["record_video_size"] = settings.video_size
        logger.info(f"启用录屏功能，视频保存目录: {video_dir}")
    
    context = browser.new_context(**context_options)

    yield context

    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, request, settings) -> Generator[Page, None, None]:
    page = context.new_page()
    page.set_default_timeout(30000)

    yield page

    # 测试失败时截图
    if request.node.rep_call.failed:
        try:
            screenshot_path = PathHelper.get_screenshot_path(request.node.name)
            page.screenshot(path=screenshot_path, full_page=True)
            _get_allure_helper().attach_screenshot(screenshot_path, name="失败截图")
            logger.info(f"失败截图已保存: {screenshot_path}")
        except Exception as e:
            logger.error(f"保存失败截图时出错: {e}")

    page.close()
    
    # 如果启用了录屏，重命名视频文件并附加到 Allure 报告
    if settings.video_enabled and hasattr(page, 'video') and page.video:
        try:
            original_video_path = page.video.path()
            if original_video_path and os.path.exists(original_video_path):
                # 重命名视频文件为更友好的名称
                video_dir = os.path.dirname(original_video_path)
                new_video_name = f"{request.node.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
                new_video_path = os.path.join(video_dir, new_video_name)
                
                # 使用安全重命名（带重试）
                if PathHelper.safe_rename(original_video_path, new_video_path):
                    # 附加到 Allure 报告
                    _get_allure_helper().attach_video(new_video_path, name=f"测试视频-{request.node.name}")
                    logger.info(f"测试视频已保存: {new_video_path}")
        except Exception as e:
            logger.error(f"保存测试视频时出错: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    
    # 记录测试结果到报告生成器
    if rep.when == "call":
        logger.info(f"收集测试结果: {item.nodeid} - {rep.outcome}")
        report_gen = _get_report_generator()
        error_msg = str(rep.longrepr) if rep.failed else None
        duration = rep.duration if rep.duration else 0.0
        report_gen.add_result(
            nodeid=item.nodeid,
            outcome=rep.outcome,
            duration=duration,
            error_msg=error_msg
        )
        logger.info(f"测试结果已添加到报告生成器")


@pytest.fixture(autouse=True)
def allure_step(request):
    with allure.step(f"开始执行测试: {request.node.name}"):
        yield
    with allure.step(f"结束执行测试: {request.node.name}"):
        pass


# ==================== 测试数据清理机制 ====================

@pytest.fixture(scope="function")
def test_data_cleanup(request) -> Generator[dict, None, None]:
    """
    测试数据清理 fixture
    
    使用示例:
        def test_example(page, test_data_cleanup):
            # 在 test_data_cleanup 字典中存储需要清理的数据
            test_data_cleanup['user_id'] = created_user_id
            test_data_cleanup['cleanup_func'] = delete_user
            # 测试代码...
    """
    cleanup_data = {
        'items': [],  # 存储需要清理的数据项
        'cleanup_funcs': []  # 存储清理函数
    }
    
    yield cleanup_data
    
    # 测试结束后执行清理
    logger.info(f"开始清理测试数据: {request.node.name}")
    
    # 执行注册的清理函数
    for cleanup_func in cleanup_data.get('cleanup_funcs', []):
        try:
            cleanup_func()
            logger.info(f"清理函数执行成功")
        except Exception as e:
            logger.error(f"清理函数执行失败: {e}")
    
    logger.info(f"测试数据清理完成: {request.node.name}")


@pytest.fixture(scope="function")
def setup_teardown(request) -> Generator[Callable, None, None]:
    """
    通用 setup/teardown fixture
    
    使用示例:
        def test_example(page, setup_teardown):
            # 注册 setup 和 teardown
            setup_teardown(lambda: print("setup"), lambda: print("teardown"))
            # 测试代码...
    """
    teardown_funcs = []
    
    def register_setup_teardown(setup_func=None, teardown_func=None):
        """注册 setup 和 teardown 函数"""
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
    
    # 执行 teardown
    for teardown_func in reversed(teardown_funcs):
        try:
            teardown_func()
            logger.info(f"Teardown 执行成功: {request.node.name}")
        except Exception as e:
            logger.error(f"Teardown 执行失败: {e}")


# ==================== Mock 服务器 Fixture ====================

@pytest.fixture(scope="function")
def mock_server():
    """
    Mock 服务器 fixture
    
    使用示例:
        def test_with_mock(mock_server):
            # 添加端点
            mock_server.add_endpoint(
                method='GET',
                path='/api/users',
                status_code=200,
                body={'users': [{'id': 1, 'name': 'test'}]}
            )
            
            # 获取服务器 URL
            base_url = mock_server.get_base_url()
            
            # 测试代码...
    """
    from core.utils.mock_server import MockServer
    server = MockServer()
    server.start()
    yield server
    server.stop()
