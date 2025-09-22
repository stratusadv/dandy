from dataclasses import dataclass
from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.service import IntelService


@dataclass(kw_only=True)
class IntelServiceMixin(BaseServiceMixin):
    intel: ClassVar[IntelService] = IntelService()
    _IntelService_instance: IntelService | None = None
