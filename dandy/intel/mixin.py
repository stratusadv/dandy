from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.service import IntelService


class IntelServiceMixin(BaseServiceMixin):
    @property
    def intel(self) -> IntelService:
        return self._get_service_instance(IntelService)

    def reset_services(self):
        super().reset_services()
        self.intel.reset_service()
