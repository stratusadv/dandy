from typing_extensions import List, Self

from dandy.intel import BaseIntel
from dandy.llm.agent.enums import AgentType


class AgentTaskIntel(BaseIntel):
    title: str
    description: str
    agent_type: AgentType
    sub_tasks: List[Self]