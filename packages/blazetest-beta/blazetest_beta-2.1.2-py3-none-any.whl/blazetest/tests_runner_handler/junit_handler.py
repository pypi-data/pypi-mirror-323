import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

import xml.etree.ElementTree as ET
import boto3

PWD = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(format="%(process)d-%(levelname)s-%(message)s", level=logging.INFO)


class S3Upload:
    def __init__(self, region: str):
        self.client = boto3.client(
            "s3",
            region_name=region,
        )

    def upload_file_to_s3_bucket(
        self,
        filepath: str,
        destination_filename: str,
        timestamp: str,
        s3_bucket: str,
        session_uuid: str,
        retry: bool,
    ) -> str:
        dst_folder = os.path.join(session_uuid, f"{timestamp}/target/junitxml")
        dst_filepath = os.path.join(dst_folder, destination_filename)

        if retry:
            dst_filepath = os.path.join(dst_folder, f"flaky-{destination_filename}")

        try:
            with open(filepath, "rb") as f:
                self.client.put_object(
                    Body=f,
                    Bucket=s3_bucket,
                    Key=dst_filepath,
                )
        except FileNotFoundError as err:
            logger.error(f"Seems like the test was not properly executed: {err}")
            raise err

        return dst_filepath


class TestExecutor(ABC):
    """Abstract base class for test execution"""

    @abstractmethod
    def execute_tests(self, args: List[str]) -> int:
        """Execute tests with given arguments"""
        pass

    @abstractmethod
    def parse_test_results(self, xml_file_path: str, s3_path: str, node_ids: List[str]) -> List[Dict]:
        """Parse test results from XML report"""
        pass


class JavaTestExecutor:
    def __init__(self):
        self.junit_jar = "/var/task/junit-platform-console-standalone-1.11.2.jar"
        self.test_jar = "/var/task/blazetest-junit-webdriver-sample-0.0.1-SNAPSHOT-test-jar-with-dependencies.jar"

    def execute_tests(self, args: List[str]) -> int:
        cmd = ["java", "-jar", self.junit_jar, "-cp", self.test_jar, *args]

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)

            logger.info(f"Executing Java command: {' '.join(cmd)}")

            # Log only actual test execution output, filter out known warnings
            output_lines = []
            for line in process.stdout.splitlines():
                # Skip known warning messages
                if any(
                    warning in line
                    for warning in [
                        "SLF4J:",
                        "WARNING: Unable to find CDP implementation",
                        "WARNING: Unable to find version of CDP",
                        "WARNING: Delegated to the 'execute' command",
                        "This behaviour has been deprecated",
                    ]
                ):
                    continue
                output_lines.append(line)

            if output_lines:
                logger.info("Test execution output:\n" + "\n".join(output_lines))

            if process.stderr:
                logger.warning(f"Java process errors:\n{process.stderr}")

            return process.returncode

        except subprocess.SubprocessError as e:
            logger.error(f"Failed to execute Java tests: {str(e)}")
            return 1

    def parse_test_results(self, xml_file_path: str, s3_path: str, node_ids: List[str]) -> List[Dict]:
        """
        Parse JUnit XML results for multiple test cases.

        Args:
            xml_file_path: Path to the XML report file
            s3_path: S3 path where report is stored
            node_ids: List of test node IDs that were executed

        Returns:
            List of test result dictionaries containing:
            - node_id: Test identifier
            - test_result: Test execution result (passed/failed/error/skipped)
            - report_path: Path to the test report
            - execution_time: Test execution duration
            - error_message: Error message if test failed (optional)
            - stack_trace: Stack trace if test failed (optional)
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            test_results = []

            # Get all testcase elements
            testcases = root.findall(".//testcase")
            if not testcases:
                logger.error("No testcases found in the XML file")
                return [{"node_id": node_id, "test_result": "error", "report_path": s3_path} for node_id in node_ids]

            for testcase in testcases:
                # Extract test details
                classname = testcase.get("classname", "")
                name = testcase.get("name", "").replace("()", "")  # Remove () from method name
                execution_time = float(testcase.get("time", 0))

                # Build test result
                test_result = {
                    "node_id": f"{classname}#{name}",
                    "test_result": "passed",
                    "report_path": s3_path,
                    "execution_time": execution_time,
                }

                # Check for failures, errors, or skips
                if (failure := testcase.find("failure")) is not None:
                    test_result.update(
                        {
                            "test_result": "failure",
                            "error_message": failure.get("message", ""),
                            "stack_trace": failure.text,
                        }
                    )
                    logger.error(f"Test failed: {test_result['node_id']} - {test_result['error_message']}")

                elif (error := testcase.find("error")) is not None:
                    test_result.update(
                        {"test_result": "error", "error_message": error.get("message", ""), "stack_trace": error.text}
                    )
                    logger.error(f"Test error: {test_result['node_id']} - {test_result['error_message']}")

                elif (skipped := testcase.find("skipped")) is not None:
                    test_result.update({"test_result": "skipped", "skip_message": skipped.get("message", "")})
                    logger.info(f"Test skipped: {test_result['node_id']} - {test_result['skip_message']}")

                test_results.append(test_result)

            # Validate that we found results for all expected tests
            found_node_ids = {result["node_id"] for result in test_results}
            expected_node_ids = set(node_ids)

            # Handle missing results
            missing_node_ids = expected_node_ids - found_node_ids
            if missing_node_ids:
                logger.warning(f"Missing test results for node IDs: {missing_node_ids}")
                for node_id in missing_node_ids:
                    test_results.append(
                        {
                            "node_id": node_id,
                            "test_result": "error",
                            "report_path": s3_path,
                            "error_message": "No test result found in XML report",
                        }
                    )

            # Sort results to match input node_ids order
            node_id_to_result = {result["node_id"]: result for result in test_results}
            ordered_results = []
            for node_id in node_ids:
                if result := node_id_to_result.get(node_id):
                    ordered_results.append(result)
                else:
                    ordered_results.append(
                        {
                            "node_id": node_id,
                            "test_result": "error",
                            "report_path": s3_path,
                            "error_message": "No test result found",
                        }
                    )

            return ordered_results

        except ET.ParseError as e:
            logger.error(f"Failed to parse test results XML {xml_file_path}: {str(e)}")
            return [
                {
                    "node_id": node_id,
                    "test_result": "error",
                    "report_path": s3_path,
                    "error_message": f"XML parse error: {str(e)}",
                }
                for node_id in node_ids
            ]
        except Exception as e:
            logger.error(f"Unexpected error parsing test results: {str(e)}")
            return [
                {
                    "node_id": node_id,
                    "test_result": "error",
                    "report_path": s3_path,
                    "error_message": f"Parsing error: {str(e)}",
                }
                for node_id in node_ids
            ]


def run_tests(event: Dict, context: Optional[Dict] = None) -> Dict:
    setup_logging()

    runtime = event.get("runtime", "python")
    execution_args: List[str] = event["execution_args"]
    node_ids: List[str] = event["node_ids"]
    report_path: str = event["report_path"] if runtime == "python" else "/tmp/TEST-junit-jupiter.xml"
    region: str = event["region"]
    session_uuid: str = event["session_uuid"]
    timestamp: str = event["start_timestamp"]
    retry: bool = event["retry"]

    s3 = S3Upload(region=region)
    s3_bucket = os.environ.get("S3_BUCKET")

    executor = JavaTestExecutor()

    logger.info(f"Invoking {runtime} tests: {node_ids} with args: {execution_args}")

    args = ["--reports-dir", "/tmp", *execution_args]
    for node_id in node_ids:
        args.extend(["--select-method", node_id])

    exit_code = executor.execute_tests(args)
    logger.info(f"Test execution completed with exit code: {exit_code}")

    s3_path = s3.upload_file_to_s3_bucket(
        filepath=report_path,
        destination_filename=f"TEST-{node_ids[0].replace('.', '-')}.xml",
        session_uuid=session_uuid,
        s3_bucket=s3_bucket,
        timestamp=timestamp,
        retry=retry,
    )

    test_results = executor.parse_test_results(report_path, s3_path, node_ids)
    logger.info(f"Test results: {test_results}")

    return {
        "statusCode": 200,
        "body": json.dumps(test_results),
    }
