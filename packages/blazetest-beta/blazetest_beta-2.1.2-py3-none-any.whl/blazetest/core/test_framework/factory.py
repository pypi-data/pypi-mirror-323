from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.test_framework.base import TestFrameworkManager
from blazetest.core.test_framework.java_junit import JUnitFrameworkManager
from blazetest.core.test_framework.java_testng import TestNGFrameworkManager
from blazetest.core.test_framework.xml_parsers import (
    JUnitXMLParser,
    PytestXMLParser,
    TestFrameworkXMLParser,
    TestNGXMLParser,
)
from blazetest.core.test_framework.pytest import PytestFrameworkManager


class TestFrameworkFactory:
    """
    Factory for creating test framework managers

    Supported frameworks:
    - pytest
    - junit

    :param config: Blazetest configuration

    :raises ValueError: If the selected framework is unknown
    """

    def __init__(self, config: BlazetestConfig):
        self.config = config

    def get_test_framework(self) -> TestFrameworkManager:
        if self.config.framework.selected == "pytest":
            return PytestFrameworkManager(collection_args=self.config.framework.pytest.collection_args)
        elif self.config.framework.selected == "junit":
            return JUnitFrameworkManager(
                discovery_selectors=self.config.framework.junit.discovery_selectors,
                config_params=self.config.framework.junit.config_params,
                project_name=self.config.general.project_name,
            )
        elif self.config.framework.selected == "testng":
            return TestNGFrameworkManager(
                discovery_selectors=[],
                config_params=self.config.framework.testng.params,
                project_name=self.config.general.project_name,
            )
        else:
            raise ValueError(f"Unknown test framework: {self.config.framework}")

    def get_test_framework_xml_parser(self) -> TestFrameworkXMLParser:
        if self.config.framework.selected == "pytest":
            return PytestXMLParser()
        elif self.config.framework.selected == "junit":
            return JUnitXMLParser()
        elif self.config.framework.selected == "testng":
            return TestNGXMLParser()
        else:
            raise ValueError(f"Unknown test framework: {self.config.framework}")

    def get_dockerfile(self) -> str:
        if self.config.framework.selected == "pytest":
            return "Dockerfile"
        elif self.config.framework.selected == "junit":
            build_tool = self.config.general.build_tool
            java_version = self.config.general.java_version
            dockerfile_name = f"java-{java_version}-{build_tool}-junit.Dockerfile"
            return dockerfile_name
        elif self.config.framework.selected == "testng":
            build_tool = self.config.general.build_tool
            java_version = self.config.general.java_version
            dockerfile_name = f"java-{java_version}-{build_tool}-testng.Dockerfile"
            return dockerfile_name
        else:
            raise ValueError(f"Unknown test framework: {self.config.framework}")
