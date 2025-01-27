from abc import ABC, abstractmethod
from typing import List, Dict
import junitparser
from xml.dom.minidom import parseString
from xml.etree import ElementTree
import logging
import boto3

from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.run_test.result_model import JUnitXMLReport, ReportMergeResult
from blazetest.core.test_framework.xml_parsers import TestFrameworkXMLParser
from blazetest.core.utils.exceptions import ReportNotAvailable, ReportNotUploaded

logger = logging.getLogger(__name__)


class BaseReportMerger(ABC):
    """Abstract base class for report mergers"""

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
        xml_parser: TestFrameworkXMLParser = None,
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
        self.xml_parser = xml_parser

    def set_s3_bucket_name(self, s3_bucket_name: str) -> None:
        self.s3_bucket_name = s3_bucket_name

    @abstractmethod
    def merge_reports(self, reports: List[JUnitXMLReport], timestamp: str) -> ReportMergeResult:
        """Merge multiple test reports into a single report"""
        pass

    @abstractmethod
    def get_test_results_by_node_id(self, reports: List[JUnitXMLReport]) -> Dict[str, dict]:
        """Get test results organized by node ID"""
        pass

    def _download_report(self, report_path: str) -> str:
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=report_path)
            report_data = response["Body"].read().decode(self.FILE_ENCODING)
            return report_data
        except Exception as e:
            raise ReportNotAvailable(f"Error downloading report {report_path}: {str(e)}")

    def _upload_report(self, body: str, path: str) -> None:
        try:
            self.s3_client.put_object(Body=body, Bucket=self.s3_bucket_name, Key=path)
        except Exception as e:
            raise ReportNotUploaded(f"Error uploading report {path} to S3: {str(e)}")

    @staticmethod
    def formatted_xml_string(junit_xml: junitparser.JUnitXml) -> str:
        xml_str = junit_xml.tostring()
        root = ElementTree.fromstring(xml_str)
        rough_string = ElementTree.tostring(root, encoding="utf-8")
        re_parsed = parseString(rough_string)
        return re_parsed.toprettyxml(indent="  ")
