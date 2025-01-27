import io
import logging
import sys
from typing import List

import pytest

from blazetest.core.config import CWD
from blazetest.core.test_framework.base import TestFrameworkManager

logger = logging.getLogger(__name__)


class NodeIDCollector:
    node_ids: List[str] = []

    def pytest_collection_modifyitems(self, items):
        self.node_ids = [item.nodeid for item in items]


class NullIO(io.IOBase):
    def write(self, txt):
        pass


def get_collector():
    return NodeIDCollector()


class PytestFrameworkManager(TestFrameworkManager):
    def __init__(self, collection_args: List[str]):
        self.collection_args = collection_args

    def get_collected_tests(self) -> List[str]:
        # Redirect stdout to the NullIO object
        original_stdout = sys.stdout
        sys.stdout = NullIO()

        pytest_args = [f"--rootdir={CWD}", "--collect-only", "--quiet"] + self.collection_args
        logger.debug(f"Collecting tests with following pytest arguments: {pytest_args}")

        collector = get_collector()
        pytest.main(pytest_args, plugins=[collector])

        sys.stdout = original_stdout
        return collector.node_ids
