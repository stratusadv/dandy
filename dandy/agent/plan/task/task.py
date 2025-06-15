from dandy.intel import BaseIntel


class AgentTaskIntel(BaseIntel):
    description: str
    desired_result_description: str
    strategy_resource_key: str
    actual_result: str = ''
    is_complete: bool = False

    def set_complete(self):
        self.is_complete = True

    def set_incomplete(self):
        self.is_complete = False