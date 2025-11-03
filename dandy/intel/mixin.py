from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.service import IntelService


class IntelServiceMixin(BaseServiceMixin):
    intel: ClassVar[IntelService] = IntelService()
    _IntelService_instance: IntelService | None = None

    def reset_services(self):
        super().reset_services()
        self.intel.reset_service()
