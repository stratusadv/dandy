from dandy.intel import BaseIntel


class BaseAgentTaskIntel(BaseIntel):
    is_complete: bool = False
    description: str
    result: str