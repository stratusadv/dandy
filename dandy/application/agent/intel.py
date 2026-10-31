from dandy.domain.intel.intel import BaseIntel


class AgentTurnIntel(BaseIntel):
    text: str
    done: bool = False
