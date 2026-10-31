from dandy.shared.service.mixin import BaseServiceMixin
from dandy.application.decision.service import DecisionService


class DecisionServiceMixin(BaseServiceMixin):
    @property
    def decision(self) -> DecisionService:
        return self._get_service_instance(DecisionService)

    def reset(self):
        super().reset()
        self.decision.reset()
