from dandy.intel import BaseIntel


class AgentTaskIntel(BaseIntel):
    description: str
    desired_result: str
    actual_result: str = ''
    _is_complete: bool = False

    def set_complete(self):
        self._is_complete = True

    def set_incomplete(self):
        self._is_complete = False