from dandy.shared.service.mixin import BaseServiceMixin
from dandy.domain.intel.service import IntelService


class IntelServiceMixin(BaseServiceMixin):
    @property
    def intel(self) -> IntelService:
        return self._get_service_instance(IntelService)

    def reset(self) -> None:
        super().reset()
        self.intel.reset()
