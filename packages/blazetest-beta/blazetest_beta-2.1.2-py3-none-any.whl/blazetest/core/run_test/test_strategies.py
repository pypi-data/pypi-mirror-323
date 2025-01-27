from abc import ABC, abstractmethod
from typing import List, Dict

from blazetest.core.project_config.model import BlazetestConfig


class TestExecutionStrategy(ABC):
    """Abstract base class for test execution strategies"""

    @abstractmethod
    def prepare_execution_args(self, config: BlazetestConfig, node_ids: List[str], report_path: str) -> Dict:
        """Prepare execution arguments for the test framework"""
        pass

    @abstractmethod
    def get_report_path(self, node_id: str, base_path: str) -> str:
        """Get report path for the test execution"""
        pass


class PythonTestStrategy(TestExecutionStrategy):
    """Strategy for Python/PyTest execution"""

    def prepare_execution_args(self, config: BlazetestConfig, node_ids: List[str], report_path: str) -> Dict:
        return {
            "runtime": "python",
            "execution_args": self._remove_junit_report_path(config.framework.pytest.execution_args),
            "node_ids": node_ids,
            "report_path": report_path,
        }

    def get_report_path(self, node_id: str, base_path: str) -> str:
        node_id = self._sanitize_node_id(node_id)
        return base_path.format(node_id)

    def _remove_junit_report_path(self, args: List[str]) -> List[str]:
        """Remove any existing JUnit XML report path arguments"""
        return [arg for arg in args if not arg.startswith("--junitxml")]

    def _sanitize_node_id(self, node_id: str) -> str:
        """Sanitize node ID for file path usage"""
        replacements = ["::", ".", "/"]
        for symbol in replacements:
            node_id = node_id.replace(symbol, "-")
        return node_id


class JavaTestStrategy(TestExecutionStrategy):
    """Strategy for Java/JUnit execution"""

    def prepare_execution_args(self, config: BlazetestConfig, node_ids: List[str], report_path: str) -> Dict:
        return {
            "runtime": "java",
            "execution_args": config.framework.junit.config_params,
            "node_ids": node_ids,
            "report_path": report_path,
        }

    def get_report_path(self, node_id: str, base_path: str) -> str:
        return base_path


class TestStrategyFactory:
    """Factory for creating test execution strategies"""

    @staticmethod
    def create_strategy(runtime: str) -> TestExecutionStrategy:
        if runtime == "python":
            return PythonTestStrategy()
        elif runtime == "java":
            return JavaTestStrategy()
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")
