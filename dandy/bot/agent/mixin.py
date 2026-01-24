from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.processor.agent.service import AgentService


class AgentServiceMixin(BaseServiceMixin):
    services: ClassVar[AgentService] = AgentService()
    _AgentService_instance: AgentService | None = None

    def reset_services(self):
        super().reset_services()
        self.services.reset_service()
