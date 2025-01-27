import abc
from typing import List


class TestFrameworkManager(abc.ABC):
    @abc.abstractmethod
    def get_collected_tests(self) -> List[str]:
        raise NotImplementedError
