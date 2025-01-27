from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.report_merger.base import BaseReportMerger
from blazetest.core.report_merger.junit_merger import JUnitReportMerger
from blazetest.core.report_merger.pytest_merger import PyTestReportMerger
from blazetest.core.test_framework.xml_parsers import PytestXMLParser, JUnitXMLParser, TestNGXMLParser


class ReportMergerFactory:
    """Factory for creating appropriate report merger based on test framework"""

    @staticmethod
    def create_report_merger(
        framework: str,
        resource_prefix: str,
        region: str,
        s3_bucket_name: str = None,
        config: BlazetestConfig = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ) -> BaseReportMerger:
        """Create appropriate report merger based on framework"""
        framework = framework.lower()

        if framework == "pytest":
            xml_parser = PytestXMLParser()
        elif framework == "junit":
            xml_parser = JUnitXMLParser()
        elif framework == "testng":
            xml_parser = TestNGXMLParser()
        else:
            raise ValueError(f"Unsupported test framework: {framework}")

        merger_map = {
            "junit": JUnitReportMerger,
            "testng": JUnitReportMerger,
            "pytest": PyTestReportMerger,
        }
        merger_class = merger_map.get(framework)
        if merger_class is None:
            raise ValueError(f"Unsupported test framework: {framework}")

        return merger_class(
            resource_prefix=resource_prefix,
            region=region,
            s3_bucket_name=s3_bucket_name,
            config=config,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            xml_parser=xml_parser,
        )
