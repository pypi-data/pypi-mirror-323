import logging
import os
from collections import defaultdict
from typing import List, Dict

import junitparser
from blazetest.core.utils.utils import xml_to_html
from junitparser import JUnitXml

from blazetest.core.config import CWD

from blazetest.core.utils.logging_config import ColoredOutput

from blazetest.core.report_merger.base import BaseReportMerger
from blazetest.core.run_test.result_model import JUnitXMLReport, ReportMergeResult

logger = logging.getLogger(__name__)


class JUnitReportMerger(BaseReportMerger):
    """Report merger for JUnit format"""

    def get_test_results_by_node_id(self, reports: List[JUnitXMLReport]) -> Dict[str, dict]:
        tests_results = defaultdict(lambda: defaultdict(list))

        print(
            f"\n* Downloading and merging {len(reports)} test reports "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )

        for report in reports:
            if not report.report_path:
                continue

            report_data = self._download_report(report.report_path)
            junit_report = junitparser.JUnitXml.fromstring(report_data)

            if report.test_result == "passed":
                tests_results[report.test_node_id]["passed"].append(
                    self.xml_parser.get_xml_test_case(junit_report, node_id=report.test_node_id)
                )
            elif report.test_result == "skipped":
                tests_results[report.test_node_id]["skipped"].append(
                    self.xml_parser.get_xml_test_case(junit_report, node_id=report.test_node_id)
                )
            else:
                tests_results[report.test_node_id]["failed"].append(
                    self.xml_parser.get_xml_test_case(junit_report, node_id=report.test_node_id)
                )

        return tests_results

    def merge_reports(self, reports: List[JUnitXMLReport], timestamp: str) -> ReportMergeResult:
        tests_results = self.get_test_results_by_node_id(reports)
        return self._create_merge_result(tests_results, timestamp)

    def _create_merge_result(self, tests_results: Dict[str, dict], timestamp: str) -> ReportMergeResult:
        final_report = junitparser.JUnitXml()
        flake_report = junitparser.JUnitXml()

        final_testsuite = junitparser.TestSuite()
        flake_testsuite = junitparser.TestSuite()

        passed, flaky, failed = 0, 0, 0
        passed_ids, flaky_ids, failed_ids = [], [], []

        for node_id, results in tests_results.items():
            if not results["failed"] and not results["skipped"]:
                final_testsuite.add_testcase(results["passed"][0])
                passed += 1
                passed_ids.append(node_id)
            elif results["passed"]:
                test_case = self._create_flake_test_case(results)
                flake_testsuite.add_testcase(test_case)

                if not self.config.general.flaky.remove_flakes:
                    final_testsuite.add_testcase(test_case)
                    flaky += 1
                    flaky_ids.append(node_id)

                self.flake_detected = True
                failed += 1
                failed_ids.append(node_id)
            else:
                final_testsuite.add_testcase(results["failed"][0])
                failed += 1
                failed_ids.append(node_id)

        final_report.add_testsuite(final_testsuite)
        flake_report.add_testsuite(flake_testsuite)

        return self._create_result_object(
            final_report, flake_report, timestamp, passed, flaky, failed, passed_ids, flaky_ids, failed_ids
        )

    def _create_flake_test_case(self, test_result: dict) -> junitparser.TestCase:
        test_case = test_result["passed"][0]
        tests_count = len(test_result["passed"]) + len(test_result["failed"])

        properties = junitparser.Properties()
        properties.add_property(junitparser.Property("flake", "true"))
        properties.add_property(junitparser.Property("flake_rate", f"{len(test_result['passed'])}/{tests_count}"))

        test_case.append(properties)
        return test_case

    def _save_report_artifact(self, report_path: str, report: JUnitXml):
        artifacts_dir = CWD
        if self.config.general.artifacts_dir:
            artifacts_dir = os.path.join(CWD, self.config.general.artifacts_dir)

        with open(os.path.join(artifacts_dir, report_path.replace("/", "-")), "w") as f:
            f.write(self.formatted_xml_string(report))

        html_content = xml_to_html(report)
        with open(os.path.join(artifacts_dir, report_path.replace("/", "-").replace(".xml", ".html")), "w") as f:
            f.write(html_content)

    def _create_result_object(
        self, final_report, flake_report, timestamp, passed, flaky, failed, passed_ids, flaky_ids, failed_ids
    ) -> ReportMergeResult:
        final_report_filepath = self.FINAL_REPORT_FILEPATH.format(
            timestamp=timestamp, resource_prefix=self.resource_prefix
        )
        flake_report_filepath = self.FLAKE_REPORT_FILEPATH.format(
            timestamp=timestamp, resource_prefix=self.resource_prefix
        )

        print(
            f"* Uploading merged JUnitXML test report to S3 bucket "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )

        self._upload_report(self.formatted_xml_string(final_report), final_report_filepath)
        self._save_report_artifact(final_report_filepath, final_report)

        if self.flake_detected:
            self._upload_report(self.formatted_xml_string(flake_report), flake_report_filepath)
            self._save_report_artifact(flake_report_filepath, flake_report)

        print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}\n")

        return ReportMergeResult(
            final_report_path=final_report_filepath,
            flake_report_path=flake_report_filepath if self.flake_detected else None,
            passed=passed,
            flaky=flaky,
            failed=failed,
            passed_ids=passed_ids,
            flaky_ids=flaky_ids,
            failed_ids=failed_ids,
        )
