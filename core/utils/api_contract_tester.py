"""
API 契约测试模块

提供 API 契约验证、OpenAPI/Swagger 验证和 API 性能测试功能
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import RequestException

from core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class APIContract:
    """API 契约定义"""

    path: str
    method: str
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    status_codes: List[int] = field(default_factory=lambda: [200])

    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, Any]] = None


@dataclass
class APITestResult:
    """API 测试结果"""

    path: str
    method: str
    status_code: int
    response_time: float
    response_body: Any
    headers: Dict[str, str]
    validation_errors: List[str] = field(default_factory=list)
    passed: bool = True


class APIContractTester:
    """API 契约测试器"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.contracts: Dict[str, APIContract] = {}

    def load_openapi_spec(self, spec_path: Union[str, Path]) -> None:
        """从 OpenAPI/Swagger 文件加载契约"""
        spec_file = Path(spec_path)

        if not spec_file.exists():
            raise FileNotFoundError(f"OpenAPI 规范文件不存在: {spec_path}")

        with open(spec_file, "r", encoding="utf-8") as f:
            if spec_file.suffix == ".json":
                spec = json.load(f)
            else:
                import yaml

                spec = yaml.safe_load(f)

        self._parse_openapi_spec(spec)
        logger.info("已加载 OpenAPI 规范: %d 个 API", len(self.contracts))

    def _parse_openapi_spec(self, spec: Dict[str, Any]) -> None:
        """解析 OpenAPI 规范"""
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    contract = APIContract(
                        path=path,
                        method=method.upper(),
                        request_schema=details.get("requestBody", {}).get("content", {}),
                        response_schema=details.get("responses", {}),
                        status_codes=list(details.get("responses", {}).keys()),
                    )
                    key = f"{method.upper()}:{path}"
                    self.contracts[key] = contract

    def add_contract(self, contract: APIContract) -> None:
        """添加 API 契约"""
        key = f"{contract.method}:{contract.path}"
        self.contracts[key] = contract

    def test_api(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Optional[int] = None,
    ) -> APITestResult:
        """测试单个 API"""
        url = f"{self.base_url}{path}"
        start_time = time.time()

        try:
            response = self.session.request(
                method=method, url=url, json=data, params=params, headers=headers, timeout=30
            )
            response_time = time.time() - start_time

            # 验证状态码
            validation_errors = []
            if expected_status and response.status_code != expected_status:
                validation_errors.append(
                    f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}"
                )

            # 尝试解析响应体
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = response.text

            result = APITestResult(
                path=path,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                response_body=response_body,
                headers=dict(response.headers),
                validation_errors=validation_errors,
                passed=len(validation_errors) == 0,
            )

            return result

        except requests.RequestException as e:
            response_time = time.time() - start_time
            return APITestResult(
                path=path,
                method=method,
                status_code=0,
                response_time=response_time,
                response_body=str(e),
                headers={},
                validation_errors=[f"请求失败: {str(e)}"],
                passed=False,
            )

    def validate_contract(self, path: str, method: str, result: APITestResult) -> List[str]:
        """验证 API 响应是否符合契约"""
        key = f"{method}:{path}"
        contract = self.contracts.get(key)

        if not contract:
            return [f"未找到契约定义: {key}"]

        errors = []

        # 验证状态码
        if result.status_code not in contract.status_codes:
            errors.append(f"状态码 {result.status_code} 不在预期范围内: {contract.status_codes}")

        # 验证响应体结构（简化版）
        if contract.response_schema and isinstance(result.response_body, dict):
            errors.extend(
                self._validate_response_structure(result.response_body, contract.response_schema)
            )

        return errors

    def _validate_response_structure(
        self, response: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[str]:
        """验证响应体结构"""
        errors = []

        # 简化验证：检查必需字段是否存在
        if "required" in schema:
            for required_field in schema["required"]:
                if required_field not in response:
                    errors.append(f"缺少必需字段: {required_field}")

        return errors

    def run_all_contract_tests(self) -> Dict[str, List[APITestResult]]:
        """运行所有契约测试"""
        results: Dict[str, List[APITestResult]] = {"passed": [], "failed": []}

        for key, contract in self.contracts.items():
            logger.info("测试 API: %s", key)

            result = self.test_api(path=contract.path, method=contract.method)

            # 验证契约
            contract_errors = self.validate_contract(contract.path, contract.method, result)
            result.validation_errors.extend(contract_errors)
            result.passed = len(result.validation_errors) == 0

            if result.passed:
                results["passed"].append(result)
                logger.info("✅ API 测试通过: %s", key)
            else:
                results["failed"].append(result)
                logger.error("❌ API 测试失败: %s, 错误: %s", key, result.validation_errors)

        return results


class APIPerformanceTester:
    """API 性能测试器"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def load_test(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        iterations: int = 100,
        concurrency: int = 10,
    ) -> Dict[str, Any]:
        """
        负载测试

        Args:
            path: API 路径
            method: HTTP 方法
            data: 请求体
            params: 查询参数
            headers: 请求头
            iterations: 总请求次数
            concurrency: 并发数

        Returns:
            性能测试结果
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        url = f"{self.base_url}{path}"
        response_times = []
        errors = []

        def make_request() -> float:
            start_time = time.time()
            try:
                response = self.session.request(
                    method=method, url=url, json=data, params=params, headers=headers, timeout=30
                )
                response.raise_for_status()
                return time.time() - start_time
            except RequestException as e:
                errors.append(str(e))
                return -1

        logger.info(
            "开始负载测试: %s %s, 迭代次数: %d, 并发: %d", method, path, iterations, concurrency
        )

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_request) for _ in range(iterations)]

            for future in as_completed(futures):
                result = future.result()
                if result >= 0:
                    response_times.append(result)

        # 计算统计信息
        if response_times:
            response_times.sort()
            total_requests = len(response_times)

            results = {
                "total_requests": total_requests,
                "failed_requests": len(errors),
                "error_rate": len(errors) / iterations * 100,
                "avg_response_time": sum(response_times) / total_requests,
                "min_response_time": response_times[0],
                "max_response_time": response_times[-1],
                "p50_response_time": response_times[int(total_requests * 0.5)],
                "p95_response_time": response_times[int(total_requests * 0.95)],
                "p99_response_time": response_times[int(total_requests * 0.99)],
                "requests_per_second": (
                    total_requests / sum(response_times) if sum(response_times) > 0 else 0
                ),
            }
        else:
            results = {
                "total_requests": 0,
                "failed_requests": len(errors),
                "error_rate": 100.0,
                "errors": errors,
            }

        logger.info("负载测试完成: 平均响应时间 %.3fs", results.get("avg_response_time", 0))
        return results

    def stress_test(
        self, path: str, method: str = "GET", duration: int = 60, target_rps: int = 100
    ) -> Dict[str, Any]:
        """
        压力测试

        Args:
            path: API 路径
            method: HTTP 方法
            duration: 测试持续时间（秒）
            target_rps: 目标每秒请求数

        Returns:
            压力测试结果
        """
        import threading

        url = f"{self.base_url}{path}"
        stop_event = threading.Event()
        results: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
        }
        lock = threading.Lock()

        def worker():
            while not stop_event.is_set():
                start_time = time.time()
                try:
                    response = self.session.request(method=method, url=url, timeout=30)
                    response_time = time.time() - start_time

                    with lock:
                        results["total_requests"] = int(results["total_requests"]) + 1
                        if response.status_code == 200:
                            results["successful_requests"] = int(results["successful_requests"]) + 1
                            results["response_times"].append(response_time)
                        else:
                            results["failed_requests"] = int(results["failed_requests"]) + 1
                except RequestException as e:
                    with lock:
                        results["total_requests"] = int(results["total_requests"]) + 1
                        results["failed_requests"] = int(results["failed_requests"]) + 1
                        results["errors"].append(str(e))

        logger.info(
            "开始压力测试: %s %s, 持续时间: %ds, 目标 RPS: %d", method, path, duration, target_rps
        )

        # 启动工作线程
        threads = []
        for _ in range(target_rps // 10):  # 每个线程处理约 10 RPS
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)

        # 运行指定时间
        time.sleep(duration)
        stop_event.set()

        # 等待线程结束
        for t in threads:
            t.join(timeout=5)

        # 计算统计信息
        if results["response_times"]:
            response_times = sorted(results["response_times"])
            total = len(response_times)

            summary = {
                "total_requests": results["total_requests"],
                "successful_requests": results["successful_requests"],
                "failed_requests": results["failed_requests"],
                "success_rate": results["successful_requests"] / results["total_requests"] * 100,
                "actual_rps": results["total_requests"] / duration,
                "avg_response_time": sum(response_times) / total,
                "min_response_time": response_times[0],
                "max_response_time": response_times[-1],
                "p50_response_time": response_times[int(total * 0.5)],
                "p95_response_time": response_times[int(total * 0.95)],
                "p99_response_time": response_times[int(total * 0.99)],
            }
        else:
            summary = {
                "total_requests": results["total_requests"],
                "successful_requests": 0,
                "failed_requests": results["failed_requests"],
                "success_rate": 0.0,
                "errors": (
                    results["errors"][:10] if results.get("errors") else []
                ),  # 只保留前 10 个错误
            }

        logger.info(
            "压力测试完成: 成功率 %.1f%%, 实际 RPS: %.1f",
            summary.get("success_rate", 0),
            summary.get("actual_rps", 0),
        )
        return summary
