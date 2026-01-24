from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.processor.agent.agent import Agent


class AgentService(BaseService['Agent']):
    obj: Agent

    def reset_service(self):
        pass
