from pydantic import PrivateAttr

from dandy.intel.intel import BaseIntel


class AgentTaskIntel(BaseIntel):
    _number: int = PrivateAttr(default=0)

    description: str
    desired_result_description: str
    processors_key: int
    actual_result: str = ''
    is_complete: bool = False

    def set_complete(self):
        self.is_complete = True

    def set_incomplete(self):
        self.is_complete = False

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, value: int):
        self._number = value