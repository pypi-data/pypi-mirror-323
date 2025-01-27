from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
import time
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

from blazetest.core.config import MAX_LAMBDA_WORKERS
from blazetest.core.cloud.aws.aws_lambda import AWSLambda
from blazetest.core.project_config.project_config import BlazetestConfig
from blazetest.core.report_merger.base import BaseReportMerger
from blazetest.core.report_merger.factory import ReportMergerFactory
from blazetest.core.run_test.result_model import (
    TestSessionResult,
    InvocationResult,
    JUnitXMLReport,
    ReportMergeResult,
    TestSessionResultManager,
)
from blazetest.core.run_test.test_strategies import TestStrategyFactory, TestExecutionStrategy
from blazetest.core.test_framework.base import TestFrameworkManager
from blazetest.core.utils.exceptions import (
    ReportNotAvailable,
    ReportNotUploaded,
    NoTestsToRun,
    ReportNotMerged,
)
from blazetest.core.utils.logging_config import ColoredOutput
from blazetest.core.utils.utils import (
    FILTER_ALL,
    FILTER_FAILED,
    FILTER_FLAKY,
    get_n_node_ids,
    flatten,
)

logger = logging.getLogger(__name__)


@dataclass
class TestExecutionContext:
    """Contains test execution configuration and state"""

    function_name: str = None
    s3_bucket: str = None
    retry_test_results: List[InvocationResult] = None
    node_ids: List[str] = None
    longest_node_id_length: int = 0
    timestamp: str = None
    tests_result_manager: TestSessionResultManager = None

    def __post_init__(self):
        self.retry_test_results = []
        self.node_ids = []


class TestResultLogger:
    """Handles test result logging with color coding"""

    @staticmethod
    def log_test_result(node_id: str, result: str, padding: int):
        """Log test result with appropriate coloring"""
        color_map = {
            "passed": ColoredOutput.GREEN,
            "skipped": ColoredOutput.YELLOW,
            "failed": ColoredOutput.RED,
            "error": ColoredOutput.RED,
        }
        color = color_map.get(result, ColoredOutput.RED)
        print(f"* [{node_id:{padding}}] ... Finished " f"{color.value}[{result}]{ColoredOutput.RESET.value}")


class ParallelTestExecutor:
    """Handles parallel execution of tests using thread pool"""

    def __init__(
        self,
        uuid: str,
        config: BlazetestConfig,
        context: TestExecutionContext,
        lambda_function: AWSLambda,
        execution_strategy: TestExecutionStrategy,
        result_logger: TestResultLogger,
    ):
        self.uuid = uuid
        self.config = config
        self.context = context
        self.lambda_function = lambda_function
        self.execution_strategy = execution_strategy
        self.result_logger = result_logger

    def run_parallel(self, node_ids: List[str], retry: bool = False) -> InvocationResult:
        start_time = time.time()
        print(
            f"* Observing {len(node_ids)} tests completion status "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value}"
        )

        batched_node_ids = get_n_node_ids(node_ids=node_ids, items_per_sublist=self.config.general.tests_per_dispatch)

        logger.info(
            f"Running with {self.config.general.tests_per_dispatch} tests "
            f"per dispatch with {len(batched_node_ids)} Lambda invocations"
        )

        with ThreadPoolExecutor(max_workers=MAX_LAMBDA_WORKERS) as executor:
            results = list(executor.map(lambda nodes: self.invoke_lambda(nodes, retry), batched_node_ids))

        return InvocationResult.parse(results=flatten(results), start_time=start_time)

    def invoke_lambda(self, node_ids: List[str], retry: bool) -> List[Tuple[str, Dict]]:
        """Execute tests via Lambda function"""
        for node_id in node_ids:
            print(f"* [{node_id}] ... Running")

        report_path = self.execution_strategy.get_report_path(node_id=node_ids[0], base_path="/tmp/junitxml/{}.xml")

        execution_args = self.execution_strategy.prepare_execution_args(
            config=self.config, node_ids=node_ids, report_path=report_path
        )

        invocation_results = self.lambda_function.invoke(
            function_name=self.context.function_name,
            session_uuid=self.uuid,
            timestamp=self.context.timestamp,
            retry=retry,
            **execution_args,
        )

        if not invocation_results:
            logger.error("No results received for the invocations")
            return []

        return [(result["node_id"], result) for result in invocation_results if self._log_and_process_result(result)]

    def _log_and_process_result(self, result: Dict) -> bool:
        if not result:
            return False
        self.result_logger.log_test_result(
            result["node_id"], result["test_result"], self.context.longest_node_id_length
        )
        return True


class RetryHandler:
    """Handles retry logic for failed tests"""

    def __init__(self, config: BlazetestConfig, context: TestExecutionContext, parallel_executor: ParallelTestExecutor):
        self.config = config
        self.context = context
        self.parallel_executor = parallel_executor

    def retry_failed_tests(self, failed_tests: List[str], flaky_test_retry_enabled: bool):
        if not (flaky_test_retry_enabled and failed_tests):
            return

        logger.info(
            f"Retrying running {len(failed_tests)} failed tests "
            f"{self.config.general.flaky.failure_retry_attempts} times"
        )
        self._execute_retries(failed_tests)

    def _execute_retries(self, failed_tests: List[str], retry_num: int = 0):
        if retry_num >= self.config.general.flaky.failure_retry_attempts:
            return

        retry_results = self.parallel_executor.run_parallel(node_ids=failed_tests, retry=True)
        self.context.retry_test_results.append(retry_results)

        self._log_retry_results(retry_num, retry_results)

        if self._should_stop_retrying(retry_results):
            return

        self._execute_retries(
            failed_tests=self._get_next_retry_tests(retry_results, failed_tests), retry_num=retry_num + 1
        )

    def _log_retry_results(self, retry_num: int, results: InvocationResult):
        logger.info(
            f"Retry {retry_num + 1} results: "
            f"Passed: {results.passed_tests_count}, "
            f"Failed: {results.failed_tests_count}, "
            f"Skipped: {results.skipped_tests_count}"
        )

    def _should_stop_retrying(self, results: InvocationResult) -> bool:
        return results.failed_tests_count == 0 and self.config.general.flaky.exit_on_flake_detection

    def _get_next_retry_tests(self, results: InvocationResult, current_tests: List[str]) -> List[str]:
        if self.config.general.flaky.exit_on_flake_detection:
            return results.failed_tests_node_ids
        return current_tests


class TestReportManager:
    """Handles report merging and management"""

    def __init__(self, context: TestExecutionContext, report_merger: BaseReportMerger):
        self.context = context
        self.report_merger = report_merger

    def merge_reports(self, reports: List[JUnitXMLReport]) -> ReportMergeResult:
        self.report_merger.set_s3_bucket_name(s3_bucket_name=self.context.s3_bucket)

        try:
            result = self.report_merger.merge_reports(
                reports=reports,
                timestamp=self.context.timestamp,
            )
            logger.info(f"Report merged and saved to s3://{self.context.s3_bucket}/{result.final_report_path}")
            return result
        except (ReportNotAvailable, ReportNotUploaded) as e:
            raise ReportNotMerged(f"Error merging reports: {str(e)}. Try rerunning the session.")

    def collect_all_reports(self, main_result: InvocationResult) -> List[JUnitXMLReport]:
        reports = main_result.junit_xml_reports_paths
        for retry_result in self.context.retry_test_results:
            reports += retry_result.junit_xml_reports_paths
        return reports


class TestRunner:
    """Main class for running tests using Lambda functions with support for multiple frameworks"""

    TMP_REPORT_FOLDER = "/tmp/junitxml/{}.xml"
    FOLDER_NAME_TIMESTAMP = "%Y-%m-%d_%H-%M-%S"

    def __init__(
        self,
        config: BlazetestConfig,
        uuid: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        test_framework_manager: TestFrameworkManager = None,
    ):
        self.config = config
        self.uuid = uuid
        self.test_framework_manager = test_framework_manager

        # Initialize context
        self.ctx = TestExecutionContext(timestamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

        # Initialize base components
        self.execution_strategy = TestStrategyFactory.create_strategy(config.general.runtime)
        self.result_logger = TestResultLogger()

        # Initialize AWS components
        resource_prefix = config.cloud.aws.get_resource_name(uuid=uuid)
        self.lambda_function = self._init_lambda_function(resource_prefix, aws_access_key_id, aws_secret_access_key)
        self.report_merger = self._init_report_merger(resource_prefix, aws_access_key_id, aws_secret_access_key)

        # Initialize execution components with explicit dependencies
        self.parallel_executor = ParallelTestExecutor(
            config=config,
            context=self.ctx,
            lambda_function=self.lambda_function,
            execution_strategy=self.execution_strategy,
            result_logger=self.result_logger,
            uuid=self.uuid,
        )

        self.retry_handler = RetryHandler(config=config, context=self.ctx, parallel_executor=self.parallel_executor)

        self.report_manager = TestReportManager(context=self.ctx, report_merger=self.report_merger)

    def _init_lambda_function(
        self, resource_prefix: str, aws_access_key_id: str, aws_secret_access_key: str
    ) -> AWSLambda:
        return AWSLambda(
            region=self.config.cloud.aws.region,
            resource_prefix=resource_prefix,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def _init_report_merger(
        self, resource_prefix: str, aws_access_key_id: str, aws_secret_access_key: str
    ) -> BaseReportMerger:
        return ReportMergerFactory.create_report_merger(
            framework=self.config.framework.selected,
            resource_prefix=resource_prefix,
            region=self.config.cloud.aws.region,
            config=self.config,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def collect_tests(self, test_session: TestSessionResult = None, test_filter: str = FILTER_ALL):
        """Collect tests based on filter"""
        if test_filter == FILTER_ALL:
            self.ctx.node_ids = self.test_framework_manager.get_collected_tests()
        elif test_filter == FILTER_FAILED:
            self.ctx.node_ids = test_session.failed_tests_ids
        elif test_filter == FILTER_FLAKY:
            self.ctx.node_ids = test_session.flaky_tests_ids

        if not self.ctx.node_ids:
            raise NoTestsToRun("Ending session as there are no tests to run")

        logger.info(f"Found {len(self.ctx.node_ids)} tests to run")
        self.ctx.longest_node_id_length = max(len(node_id) for node_id in self.ctx.node_ids)

    def run_tests(
        self,
        flaky_test_retry_enabled: bool = True,
        rerun: bool = False,
    ) -> Optional[TestSessionResult]:
        """Main test execution flow"""
        self.set_function_name(rerun=rerun)
        self._log_execution_start()

        # Execute tests and handle retries
        invocation_result = self.parallel_executor.run_parallel(node_ids=self.ctx.node_ids)
        if invocation_result.failed_tests_count > 0:
            self.retry_handler.retry_failed_tests(
                failed_tests=invocation_result.failed_tests_node_ids, flaky_test_retry_enabled=flaky_test_retry_enabled
            )

        # Merge reports and create result
        reports = self.report_manager.collect_all_reports(invocation_result)
        report_merge_result = self.report_manager.merge_reports(reports)

        return self._create_test_session_result(invocation_result, report_merge_result)

    def _log_and_process_result(self, result: Dict) -> bool:
        """Log test result and return True if valid result"""
        if not result:
            return False
        self.result_logger.log_test_result(result["node_id"], result["test_result"], self.ctx.longest_node_id_length)
        return True

    def set_function_name(self, rerun: bool = False):
        """Set Lambda function name based on execution mode"""
        if not rerun:
            self.ctx.function_name = self.lambda_function.get_created_lambda_function_details()
            return

        test_session = self.ctx.tests_result_manager.get_test_session_by_uuid(uuid=self.uuid)
        if test_session is None:
            logger.error(f"No test session with the given UUID found: {self.uuid}")
            return

        self.ctx.function_name = test_session.lambda_function_name
        self.ctx.s3_bucket = test_session.s3_bucket

    def _log_execution_start(self):
        """Log execution start details"""
        logger.info(f"Lambda function: {self.ctx.function_name}, " f"S3 bucket: {self.ctx.s3_bucket}")
        logger.info("Invoking tests and running in parallel..")

    def _create_test_session_result(
        self, invocation_result: InvocationResult, report_merge_result: ReportMergeResult
    ) -> TestSessionResult:
        """Create final test session result"""
        return TestSessionResult(
            uuid=self.uuid,
            lambda_function_name=self.ctx.function_name,
            tests_count=len(self.ctx.node_ids),
            tests_passed=report_merge_result.passed,
            failed_tests_count=invocation_result.failed_tests_count,
            failed_tests_ids=report_merge_result.failed_ids,
            flaky_tests_count=report_merge_result.flaky,
            flaky_tests_ids=report_merge_result.flaky_ids,
            flake_detected=self.report_merger.flake_detected,
            pytest_duration=invocation_result.pytest_duration,
            s3_bucket=self.ctx.s3_bucket,
            start_timestamp=self.ctx.timestamp,
            end_timestamp=self._get_timestamp_now(),
            junit_report_path=report_merge_result.final_report_path,
            flake_report_path=report_merge_result.flake_report_path if self.report_merger.flake_detected else None,
            config=self.config,
        )

    def set_s3_bucket_name(self, s3_bucket_name: str):
        """Set S3 bucket name"""
        self.ctx.s3_bucket = s3_bucket_name

    def set_tests_result_manager(self, tests_result_manager: TestSessionResultManager):
        """Set test result manager"""
        self.ctx.tests_result_manager = tests_result_manager

    def _get_timestamp_now(self) -> str:
        """Get current timestamp in specified format"""
        return datetime.now().strftime(self.FOLDER_NAME_TIMESTAMP)
