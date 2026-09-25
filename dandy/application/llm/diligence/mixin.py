from dandy.shared.service.mixin import BaseServiceMixin
from dandy.application.llm.diligence.service import DiligenceService


class DiligenceServiceMixin(BaseServiceMixin):
    @property
    def diligence(self) -> DiligenceService:
        return self._get_service_instance(DiligenceService)

    def reset(self):
        super().reset()
        self.diligence.reset()
