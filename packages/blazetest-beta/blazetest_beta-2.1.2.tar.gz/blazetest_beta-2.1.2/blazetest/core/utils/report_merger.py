import logging
import os
from collections import defaultdict
from typing import List, Dict
from xml.dom.minidom import parseString

import boto3
import junitparser
from junitparser import JUnitXml, TestCase, Properties, Property
from xml.etree import ElementTree

from blazetest.core.config import CWD
from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.run_test.result_model import JUnitXMLReport, ReportMergeResult
from blazetest.core.test_framework.factory import TestFrameworkFactory
from blazetest.core.utils.logging_config import ColoredOutput
from blazetest.core.utils.exceptions import ReportNotAvailable, ReportNotUploaded
from blazetest.core.utils.utils import xml_to_html

logger = logging.getLogger(__name__)


class ReportMerger:
    """
    Merges reports from S3 Bucket into one file and saves back to the bucket.
    """

    FILE_ENCODING = "utf-8"

    flake_detected: bool = False

    FINAL_REPORT_FILEPATH = "{timestamp}/target/merged/test-session-{resource_prefix}.xml"
    FLAKE_REPORT_FILEPATH = "{timestamp}/target/flake/test-session-{resource_prefix}.xml"

    def __init__(
        self,
        resource_prefix: str,
        region: str,
        s3_bucket_name: str = None,
        config: BlazetestConfig = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ):
        self.s3_client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.s3_bucket_name = s3_bucket_name
        self.resource_prefix = resource_prefix
        self.config = config
        self.test_xml_parser = TestFrameworkFactory(config=config).get_test_framework_xml_parser()

    def set_s3_bucket_name(self, s3_bucket_name: str) -> None:
        self.s3_bucket_name = s3_bucket_name

    def merge_reports(self, reports: List[JUnitXMLReport], timestamp: str) -> ReportMergeResult:
        print(
            f"\n* Downloading {len(reports)} test reports "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )
        tests_results = self.get_test_results_by_node_id(reports)
        print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}")

        print(
            f"* Merging test reports into single JUnitXML test report "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )
        merge_result = self.get_final_reports(tests_results)
        print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}")

        final_report_filepath = self.FINAL_REPORT_FILEPATH.format(
            timestamp=timestamp, resource_prefix=self.resource_prefix
        )
        flake_report_filepath = self.FLAKE_REPORT_FILEPATH.format(
            timestamp=timestamp, resource_prefix=self.resource_prefix
        )

        reports = [
            (merge_result["final_report"], final_report_filepath),
            (merge_result["flake_report"], flake_report_filepath),
        ]

        print(
            f"* Uploading merged JUnitXML test report to S3 bucket "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )
        for report, report_path in reports:
            self.__upload_report(
                body=self.formatted_xml_string(report),
                path=report_path,
            )

            artifacts_dir = CWD
            if self.config.general.artifacts_dir:
                artifacts_dir = os.path.join(CWD, self.config.general.artifacts_dir)

            with open(os.path.join(artifacts_dir, report_path.replace("/", "-")), "w") as f:
                f.write(self.formatted_xml_string(report))

            html_content = xml_to_html(report)
            with open(os.path.join(artifacts_dir, report_path.replace("/", "-").replace(".xml", ".html")), "w") as f:
                f.write(html_content)

        print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}\n")

        return ReportMergeResult(
            final_report_path=final_report_filepath,
            flake_report_path=flake_report_filepath,
            passed=merge_result["passed"],
            flaky=merge_result["flaky"],
            failed=merge_result["failed"],
            passed_ids=merge_result["passed_ids"],
            flaky_ids=merge_result["flaky_ids"],
            failed_ids=merge_result["failed_ids"],
        )

    def get_test_results_by_node_id(self, reports: List[JUnitXMLReport]) -> Dict[str, dict]:
        tests_results = defaultdict(lambda: defaultdict(list))
        for report in reports:
            report_data = self.__download_report(report.report_path)
            junit_report = junitparser.JUnitXml.fromstring(report_data)

            if report.test_result == "passed":
                tests_results[report.test_node_id]["passed"].append(
                    self.test_xml_parser.get_xml_test_case(junit_report, node_id=report.test_node_id)
                )
            elif report.test_result == "skipped":
                tests_results[report.test_node_id]["skipped"].append(
                    self.test_xml_parser.get_xml_test_case(junit_report, node_id=report.test_node_id)
                )
            else:
                tests_results[report.test_node_id]["failed"].append(
                    self.test_xml_parser.get_xml_test_case(junit_report, node_id=report.test_node_id)
                )

        return tests_results

    @staticmethod
    def formatted_xml_string(junit_xml: JUnitXml) -> str:
        xml_str = junit_xml.tostring()
        root = ElementTree.fromstring(xml_str)
        rough_string = ElementTree.tostring(root, encoding="utf-8")
        re_parsed = parseString(rough_string)
        return re_parsed.toprettyxml(indent="  ")

    def get_final_reports(self, tests_results: Dict[str, dict]) -> Dict:
        final_report = junitparser.JUnitXml()
        flake_report = junitparser.JUnitXml()

        final_testsuite = junitparser.TestSuite()
        flake_testsuite = junitparser.TestSuite()

        passed, flaky, failed, skipped = 0, 0, 0, 0
        passed_ids, flaky_ids, failed_ids, skipped_ids = [], [], [], []

        for node_id in tests_results:
            test_result = tests_results[node_id]

            if len(test_result["failed"]) == 0 and len(test_result["skipped"]) == 0:
                final_testsuite.add_testcase(test_result["passed"][0])

                passed += 1
                passed_ids.append(node_id)
                continue

            elif len(test_result["passed"]) > 0:
                flake_test_case = self.get_test_case_with_flake_property(test_result=test_result)
                flake_testsuite.add_testcase(flake_test_case)

                if self.config.general.flaky.remove_flakes is False:
                    final_testsuite.add_testcase(flake_test_case)
                    flaky += 1

                    flaky_ids.append(node_id)
                    failed_ids.append(node_id)
                else:
                    failed += 1
                    failed_ids.append(node_id)

                self.flake_detected = True

            elif len(test_result["skipped"]) > 0:
                skipped += 1
                skipped_ids.append(node_id)

            else:
                final_testsuite.add_testcase(test_result["failed"][0])

                failed += 1
                failed_ids.append(node_id)

        final_report.add_testsuite(final_testsuite)
        flake_report.add_testsuite(flake_testsuite)

        return {
            "final_report": final_report,
            "flake_report": flake_report,
            "passed": passed,
            "passed_ids": passed_ids,
            "flaky": flaky,
            "flaky_ids": flaky_ids,
            "failed": failed,
            "failed_ids": failed_ids,
            "skipped": skipped,
            "skipped_ids": skipped_ids,
        }

    @staticmethod
    def get_test_case_with_flake_property(test_result: dict) -> TestCase:
        test_case: TestCase = test_result["passed"][0]
        tests_count = len(test_result["passed"]) + len(test_result["failed"])

        is_flake = Property("flake", "true")
        flake_rate = Property("flake_rate", f"{len(test_result['passed'])}/{tests_count}")

        properties = Properties()
        properties.add_property(is_flake)
        properties.add_property(flake_rate)

        test_case.append(properties)
        return test_case

    def __download_report(self, report_path: str) -> str:
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=report_path)
            report_data = response["Body"].read().decode(self.FILE_ENCODING)
            return report_data
        except Exception as e:
            raise ReportNotAvailable(f"Error downloading report {report_path}: {str(e)}")

    def __upload_report(self, body: str, path: str) -> None:
        try:
            self.s3_client.put_object(Body=body, Bucket=self.s3_bucket_name, Key=path)
        except Exception as e:
            raise ReportNotUploaded(f"Error uploading report {path} to S3: {str(e)}")
