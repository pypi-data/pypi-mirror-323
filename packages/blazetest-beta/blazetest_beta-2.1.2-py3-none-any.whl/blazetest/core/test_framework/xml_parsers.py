import abc

from junitparser import junitparser
from junitparser.xunit2 import JUnitXml


class TestFrameworkXMLParser(abc.ABC):
    @abc.abstractmethod
    def get_xml_test_case(self, report: str, node_id: str):
        raise NotImplementedError


class JUnitXMLParser(TestFrameworkXMLParser):
    def get_xml_test_case(self, report: JUnitXml, node_id: str):
        """
        Returns test case from JUnit XML report by node ID

        :param report: JUnit XML report
        :param node_id: Node ID of the test
        :return: Test case from JUnit XML report
        """
        expected_class_name = node_id.split("#")[0]  # Get everything before #
        expected_method_name = node_id.split("#")[1] + "()"  # Get method name and add ()

        for test_case in report:
            if type(test_case) != junitparser.TestCase:
                continue

            xml_class_name = test_case.classname
            xml_method_name = test_case.name

            # Compare the values
            if xml_class_name == expected_class_name and xml_method_name == expected_method_name:
                return test_case
        raise ValueError(
            f"Test case not found in XML report. "
            f"Looking for class={expected_class_name}, method={expected_method_name}"
        )


class TestNGXMLParser(TestFrameworkXMLParser):
    def get_xml_test_case(self, report: str, node_id: str):
        """
        Returns test case from TestNG XML report by node ID

        :param report: TestNG XML report
        :param node_id: Node ID of the test
        :return: Test case from TestNG XML report
        """
        expected_class_name = node_id.split("#")[0]  # Get everything before #
        expected_method_name = node_id.split("#")[1]  # Get method name

        for test_case in report:
            if type(test_case) != junitparser.TestCase:
                continue

            xml_class_name = test_case.classname
            xml_method_name = test_case.name

            # Compare the values
            if xml_class_name == expected_class_name and xml_method_name == expected_method_name:
                return test_case
        raise ValueError(
            f"Test case not found in XML report. "
            f"Looking for class={expected_class_name}, method={expected_method_name}"
        )


class PytestXMLParser(TestFrameworkXMLParser):
    def get_xml_test_case(self, report: JUnitXml, node_id: str):
        for test_suites in report:
            for test_case in test_suites:
                if test_case.classname and test_case.name:
                    case_node_id = f"{test_case.classname}.{test_case.name}"
                    node_id = node_id.replace(".py", "").replace("/", ".").replace("::", ".")
                    if case_node_id == node_id:
                        return test_case
        raise ValueError(f"Test case with node_id: {node_id} not found")
