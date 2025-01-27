import json
import logging
import os
import subprocess
import uuid
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
        dst_folder = os.path.join(session_uuid, f"{timestamp}/target/testngxml")
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
        self.testng_jar = "/var/task/testng-7.8.0.jar"
        self.jcommander_jar = "/var/task/jcommander-1.82.jar"
        self.test_jar = "/var/task/blazetest-testng-webdriver-sample-0.0.1-SNAPSHOT-test-jar-with-dependencies.jar"
        self.classpath = f"{self.testng_jar}:{self.jcommander_jar}:{self.test_jar}"

    def execute_tests(self, args: List[str]) -> int:
        cmd = ["java", "-cp", self.classpath, "org.testng.TestNG", "-d", "/tmp"]

        methods = []
        for i in range(len(args)):
            if "#" in args[i]:
                class_name, method_name = args[i].split("#")
                methods.append(f"{class_name}.{method_name}")
            else:
                methods.append(args[i])

        if methods:
            cmd.extend(["-methods", ",".join(methods)])

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)

            logger.info(f"Executing Java command: {' '.join(cmd)}")

            # Log only actual test execution output
            output_lines = []
            for line in process.stdout.splitlines():
                if not any(
                    warning in line
                    for warning in [
                        "SLF4J:",
                        "WARNING: Unable to find CDP implementation",
                        "WARNING: Unable to find version of CDP",
                    ]
                ):
                    output_lines.append(line)

            if output_lines:
                logger.info("Test execution output:\n" + "\n".join(output_lines))

            if process.stderr:
                logger.warning(f"Java process errors:\n{process.stderr}")

            return process.returncode

        except subprocess.SubprocessError as e:
            logger.error(f"Failed to execute Java tests: {str(e)}")
            return 1

    def parse_test_results(self, report_details: List[Dict[str, str]], node_ids: List[str]) -> List[Dict]:
        """Parse test results from multiple XML reports.

        Args:
            report_details: List of dicts containing {local_path, s3_path} for each report
            node_ids: List of test node IDs
        """
        try:
            test_results = []
            node_id_results = {}

            for report_info in report_details:
                local_path = report_info["local_path"]
                s3_path = report_info["s3_path"]

                if not os.path.exists(local_path):
                    logger.warning(f"Report file not found: {local_path}")
                    continue

                tree = ET.parse(local_path)
                root = tree.getroot()

                for testcase in root.findall(".//testcase"):
                    classname = testcase.get("classname", "")
                    name = testcase.get("name", "")
                    execution_time = float(testcase.get("time", 0))

                    node_id = f"{classname}#{name}"
                    if node_id not in node_ids:
                        continue

                    result = {
                        "node_id": node_id,
                        "test_result": "passed",
                        "report_path": s3_path,
                        "execution_time": execution_time,
                    }

                    failure = testcase.find("failure")
                    if failure is not None:
                        result.update(
                            {
                                "test_result": "failure",
                                "error_message": failure.get("message", ""),
                                "stack_trace": failure.text.strip() if failure.text else "",
                            }
                        )
                        logger.error(f"Test failed: {node_id} - {result['error_message']}")

                    node_id_results[node_id] = result

            for node_id in node_ids:
                if result := node_id_results.get(node_id):
                    test_results.append(result)
                else:
                    test_results.append(
                        {
                            "node_id": node_id,
                            "test_result": "error",
                            "report_path": None,
                            "error_message": "No test result found in XML reports",
                        }
                    )

            return test_results

        except ET.ParseError as e:
            logger.error(f"Failed to parse XML reports: {str(e)}")
            return [
                {
                    "node_id": node_id,
                    "test_result": "error",
                    "report_path": None,
                    "error_message": f"XML parse error: {str(e)}",
                }
                for node_id in node_ids
            ]
        except Exception as e:
            logger.error(f"Unexpected error parsing results: {str(e)}")
            return [
                {
                    "node_id": node_id,
                    "test_result": "error",
                    "report_path": None,
                    "error_message": f"Parsing error: {str(e)}",
                }
                for node_id in node_ids
            ]


def run_tests(event: Dict, context: Optional[Dict] = None) -> Dict:
    setup_logging()

    runtime = event.get("runtime", "python")
    execution_args: List[str] = event["execution_args"]
    node_ids: List[str] = event["node_ids"]
    region: str = event["region"]
    session_uuid: str = event["session_uuid"]
    timestamp: str = event["start_timestamp"]
    retry: bool = event["retry"]

    s3 = S3Upload(region=region)
    s3_bucket = os.environ.get("S3_BUCKET")

    executor = JavaTestExecutor()

    logger.info(f"Invoking {runtime} tests: {node_ids} with args: {execution_args}")

    exit_code = executor.execute_tests(node_ids)
    logger.info(f"Test execution completed with exit code: {exit_code}")

    report_details = []
    added_local_paths = set()
    for node_id in node_ids:
        class_name = node_id.split("#")[0]
        local_path = f"/tmp/junitreports/TEST-{class_name}.xml"

        if os.path.exists(local_path) and local_path not in added_local_paths:
            s3_path = s3.upload_file_to_s3_bucket(
                filepath=local_path,
                destination_filename=f"TEST-{class_name.replace('.', '-')}-{str(uuid.uuid4())[:8]}.xml",
                session_uuid=session_uuid,
                s3_bucket=s3_bucket,
                timestamp=timestamp,
                retry=retry,
            )
            report_details.append({"local_path": local_path, "s3_path": s3_path})
            added_local_paths.add(local_path)

    test_results = executor.parse_test_results(report_details, node_ids)
    logger.info(f"Test results: {test_results}")

    return {
        "statusCode": 200,
        "body": json.dumps(test_results),
    }
