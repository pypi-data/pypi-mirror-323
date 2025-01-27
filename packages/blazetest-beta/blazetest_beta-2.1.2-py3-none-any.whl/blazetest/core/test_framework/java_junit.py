import json
import logging
from json import JSONDecodeError
from typing import List

from blazetest.core.config import CWD
from blazetest.core.utils.command_executor import CommandExecutor
from blazetest.core.test_framework.base import TestFrameworkManager
from blazetest.core.utils.exceptions import ProjectNameExtractionFailed
from blazetest.core.utils.utils import extract_project_name_from_pom

logger = logging.getLogger(__name__)


class JUnitTestsExtractionFailed(Exception):
    pass


class JUnitFrameworkManager(TestFrameworkManager):
    """
    Framework manager for Java JUnit tests

    :param discovery_selectors: List of selectors to discover tests
    :param config_params: List of configuration parameters
    :param remove_disabled_tests: Whether to remove disabled tests from collection
    """

    TEST_EXTRACTOR_LIB = "io.railflow.testextractor:TestExtractor:1.3:extract"
    JUNIT_VERSION = 5

    def __init__(
        self,
        discovery_selectors: List[str],
        config_params: List[str],
        remove_disabled_tests: bool = False,
        project_name: str = None,
    ):
        self.discovery_selectors = discovery_selectors
        self.config_params = config_params
        if project_name is None:
            try:
                self.project_name = extract_project_name_from_pom()
            except ProjectNameExtractionFailed as e:
                # Fallback to a default name if extraction fails
                self.project_name = "blazetest-junit-webdriver-sample"
                logger.warning(
                    f"Failed to extract project name from pom.xml: {str(e)}. Using default name: {self.project_name}"
                )
        else:
            self.project_name = project_name

        self.command_executor = CommandExecutor(
            executable="mvn",
            arguments={
                "-e": self.TEST_EXTRACTOR_LIB,
                f"-Dinput={CWD}": None,
                f"-Doutput={CWD}": None,
                f"-Dframework=junit{self.JUNIT_VERSION}": None,
                f"-DremoveDisabledTests={'true' if remove_disabled_tests else 'false'}": None,
            },
        )

    def get_collected_tests(self):
        """
        Executes blazetest_java_utility to extract tests from the project.

        :return: List of test node IDs
        :raises JUnitTestsExtractionFailed: If test extraction fails
        """
        self.command_executor.execute_command()

        try:
            with open(f"{CWD}/{self.project_name}_tests.json", "r") as file:
                collected_tests = json.loads(file.read())
        except FileNotFoundError:
            raise JUnitTestsExtractionFailed(
                f"Failed to extract tests from {self.project_name}. Check logs for more details."
            )
        except JSONDecodeError as err:
            raise JUnitTestsExtractionFailed(f"Failed to decode tests from {self.project_name}_tests.json: {err}")

        test_node_ids = [test["cmd"].split("-Dtest=")[-1].replace("'", "") for test in collected_tests["tests"]]

        return test_node_ids
