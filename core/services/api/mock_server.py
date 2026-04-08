"""
Mock 服务器模块
提供轻量级的 API Mock 服务
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse

from utils.common.logger import get_logger

logger = get_logger(__name__)


class MockResponse:
    """Mock 响应"""

    def __init__(
        self,
        status_code: int = 200,
        body: Optional[Union[Dict[str, Any], List[Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        delay: float = 0.0,
    ):
        """
        初始化 Mock 响应

        Args:
            status_code: 响应状态码
            body: 响应体，可以是字典、列表或字符串
            headers: 响应头
            delay: 响应延迟（秒）
        """
        self.status_code = status_code
        self.body = body or {}
        self.headers = headers or {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }
        self.delay = delay

    def __str__(self) -> str:
        """返回响应的字符串表示"""
        return f"MockResponse(status_code={self.status_code}, body={self.body})"


class MockEndpoint:
    """Mock 端点"""

    def __init__(self, method: str, path: str, response: MockResponse, name: Optional[str] = None):
        """
        初始化 Mock 端点

        Args:
            method: HTTP 方法（GET, POST, PUT, DELETE, PATCH）
            path: URL 路径
            response: Mock 响应
            name: 端点名称
        """
        self.method = method.upper()
        self.path = path
        self.response = response
        self.name = name or f"{method}_{path}"
        self.call_count = 0
        self.last_request: Optional[Dict[str, Any]] = None
        self.request_history: List[Dict[str, Any]] = []

    def __str__(self) -> str:
        """返回端点的字符串表示"""
        return f"MockEndpoint({self.method} {self.path})"


class MockRequestHandler(BaseHTTPRequestHandler):
    """Mock 请求处理器"""

    def __init__(self, *args, **kwargs):
        """
        初始化请求处理器

        Args:
            *args: 位置参数
            **kwargs: 关键字参数，包含 mock_server
        """
        self.mock_server = kwargs.pop("mock_server")
        super().__init__(*args, **kwargs)

    def do_GET(self):  # pylint: disable=invalid-name
        """处理 GET 请求"""
        self._handle_request("GET")

    def do_POST(self):  # pylint: disable=invalid-name
        """处理 POST 请求"""
        self._handle_request("POST")

    def do_PUT(self):  # pylint: disable=invalid-name
        """处理 PUT 请求"""
        self._handle_request("PUT")

    def do_DELETE(self):  # pylint: disable=invalid-name
        """处理 DELETE 请求"""
        self._handle_request("DELETE")

    def do_PATCH(self):  # pylint: disable=invalid-name
        """处理 PATCH 请求"""
        self._handle_request("PATCH")

    def do_OPTIONS(self):  # pylint: disable=invalid-name
        """处理 OPTIONS 请求（CORS 预检）"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _handle_request(self, method: str):
        """处理请求

        Args:
            method: HTTP 方法
        """
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # 查找匹配的端点
        endpoint = self.mock_server._find_endpoint(method, path)

        if endpoint:
            # 记录请求
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""

            request_data = {
                "method": method,
                "path": path,
                "query_params": parse_qs(parsed_path.query),
                "headers": dict(self.headers),
                "body": body.decode("utf-8") if body else None,
                "client_address": self.client_address,
            }

            endpoint.call_count += 1
            endpoint.last_request = request_data
            endpoint.request_history.append(request_data)

            logger.info("Mock 端点被调用: %s %s (调用次数: %d)", method, path, endpoint.call_count)

            # 发送响应
            self._send_response(endpoint.response)
        else:
            # 未找到匹配的端点
            logger.warning("未找到 Mock 端点: %s %s", method, path)
            self._send_response(
                MockResponse(
                    status_code=404,
                    body={
                        "error": "Not Found",
                        "message": f"No mock endpoint found for {method} {path}",
                    },
                )
            )

    def _send_response(self, response: MockResponse):
        """发送响应

        Args:
            response: Mock 响应
        """
        if response.delay > 0:
            time.sleep(response.delay)

        self.send_response(response.status_code)

        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()

        if response.body:
            # 根据响应头的 Content-Type 决定如何序列化响应体
            content_type = response.headers.get("Content-Type", "application/json")
            if "application/json" in content_type:
                self.wfile.write(json.dumps(response.body, ensure_ascii=False).encode("utf-8"))
            else:
                if isinstance(response.body, str):
                    self.wfile.write(response.body.encode("utf-8"))
                else:
                    self.wfile.write(str(response.body).encode("utf-8"))

    def log_message(self, format, *args):
        """重写日志方法，使用我们的 logger"""
        logger.debug("%s - %s", self.address_string(), format % args)


class MockServer:
    """Mock 服务器"""

    def __init__(self, host: str = "localhost", port: int = 0):
        """
        初始化 Mock 服务器

        Args:
            host: 主机地址
            port: 端口号（0 表示自动分配）
        """
        self.host = host
        self.port = port
        self.endpoints: Dict[str, MockEndpoint] = {}
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        """启动 Mock 服务器"""
        if self._running:
            logger.warning("Mock 服务器已经在运行中")
            return

        # 创建服务器
        def handler_factory(*args: Any, **kwargs: Any) -> MockRequestHandler:
            return MockRequestHandler(*args, mock_server=self, **kwargs)

        self._server = HTTPServer((self.host, self.port), handler_factory)

        # 如果端口是 0，获取实际分配的端口
        if self.port == 0:
            self.port = self._server.server_address[1]

        # 在后台线程中运行
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self._running = True

        logger.info("Mock 服务器已启动: http://%s:%d", self.host, self.port)

    def stop(self) -> None:
        """停止 Mock 服务器"""
        if not self._running:
            return

        try:
            if self._server:
                self._server.shutdown()
                self._server.server_close()
        except Exception as e:
            logger.warning("关闭服务器时出错: %s", e)

        try:
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1)
                if self._thread.is_alive():
                    logger.warning("Mock 服务器线程未能正常退出")
        except Exception as e:
            logger.warning("等待线程结束时出错: %s", e)

        self._running = False
        logger.info("Mock 服务器已停止")

    def get_base_url(self) -> str:
        """获取服务器基础 URL

        Returns:
            服务器基础 URL
        """
        return f"http://{self.host}:{self.port}"

    def add_endpoint(
        self,
        method: str,
        path: str,
        *,
        status_code: int = 200,
        body: Optional[Union[Dict[str, Any], List[Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        delay: float = 0.0,
        name: Optional[str] = None,
    ) -> MockEndpoint:
        """
        添加 Mock 端点

        Args:
            method: HTTP 方法（GET, POST, PUT, DELETE, PATCH）
            path: URL 路径
            status_code: 响应状态码
            body: 响应体，可以是字典、列表或字符串
            headers: 响应头
            delay: 响应延迟（秒）
            name: 端点名称

        Returns:
            MockEndpoint 实例
        """
        response = MockResponse(status_code=status_code, body=body, headers=headers, delay=delay)

        endpoint = MockEndpoint(method=method, path=path, response=response, name=name)

        key = f"{method.upper()}:{path}"
        self.endpoints[key] = endpoint

        logger.info("添加 Mock 端点: %s %s", method, path)
        return endpoint

    def remove_endpoint(self, method: str, path: str) -> None:
        """移除 Mock 端点

        Args:
            method: HTTP 方法
            path: URL 路径
        """
        key = f"{method.upper()}:{path}"
        if key in self.endpoints:
            del self.endpoints[key]
            logger.info("移除 Mock 端点: %s %s", method, path)

    def clear_endpoints(self) -> None:
        """清空所有端点"""
        self.endpoints.clear()
        logger.info("清空所有 Mock 端点")

    def get_endpoint(self, method: str, path: str) -> Optional[MockEndpoint]:
        """获取端点

        Args:
            method: HTTP 方法
            path: URL 路径

        Returns:
            MockEndpoint 实例，如果不存在则返回 None
        """
        key = f"{method.upper()}:{path}"
        return self.endpoints.get(key)

    def get_call_count(self, method: str, path: str) -> int:
        """获取端点被调用的次数

        Args:
            method: HTTP 方法
            path: URL 路径

        Returns:
            调用次数
        """
        endpoint = self.get_endpoint(method, path)
        return endpoint.call_count if endpoint else 0

    def reset_call_counts(self) -> None:
        """重置所有端点的调用计数"""
        for endpoint in self.endpoints.values():
            endpoint.call_count = 0
            endpoint.request_history = []
        logger.info("重置所有端点调用计数")

    def get_request_history(self, method: str, path: str) -> List[Dict[str, Any]]:
        """获取端点的请求历史

        Args:
            method: HTTP 方法
            path: URL 路径

        Returns:
            请求历史列表
        """
        endpoint = self.get_endpoint(method, path)
        return endpoint.request_history if endpoint else []

    def _find_endpoint(self, method: str, path: str) -> Optional[MockEndpoint]:
        """查找匹配的端点（支持简单的路径参数）

        Args:
            method: HTTP 方法
            path: URL 路径

        Returns:
            MockEndpoint 实例，如果不存在则返回 None
        """
        # 精确匹配
        key = f"{method}:{path}"
        if key in self.endpoints:
            return self.endpoints[key]

        # 通配符匹配（简单实现）
        for endpoint_key, endpoint in self.endpoints.items():
            ep_method, ep_path = endpoint_key.split(":", 1)
            if ep_method == method:
                if self._path_matches(ep_path, path):
                    return endpoint

        return None

    def _path_matches(self, pattern: str, path: str) -> bool:
        """简单的路径匹配（支持 {param} 格式的路径参数）

        Args:
            pattern: 路径模式
            path: 实际路径

        Returns:
            是否匹配
        """
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return False

        for p_part, pa_part in zip(pattern_parts, path_parts):
            if p_part.startswith("{") and p_part.endswith("}"):
                continue
            if p_part != pa_part:
                return False

        return True

    def __enter__(self) -> "MockServer":
        """支持 with 语句"""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """支持 with 语句"""
        self.stop()

    def __str__(self) -> str:
        """返回服务器的字符串表示"""
        status = "运行中" if self._running else "已停止"
        return f"MockServer({self.host}:{self.port}, 状态: {status}, 端点数: {len(self.endpoints)})"


# 全局 Mock 服务器实例
_MOCK_SERVER: Optional[MockServer] = None


def get_mock_server(host: str = "localhost", port: int = 0) -> MockServer:
    """
    获取全局 Mock 服务器实例

    Args:
        host: 主机地址
        port: 端口号

    Returns:
        MockServer 实例
    """
    global _MOCK_SERVER
    if _MOCK_SERVER is None:
        _MOCK_SERVER = MockServer(host=host, port=port)
    return _MOCK_SERVER


def reset_mock_server() -> None:
    """
    重置全局 Mock 服务器实例
    """
    global _MOCK_SERVER
    if _MOCK_SERVER:
        _MOCK_SERVER.stop()
    _MOCK_SERVER = None
    logger.info("重置全局 Mock 服务器实例")
