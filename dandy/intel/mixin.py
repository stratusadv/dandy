from dataclasses import dataclass
from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.http.service import HttpService


@dataclass(kw_only=True)
class IntelServiceMixin(BaseServiceMixin):
    intel: ClassVar[HttpService] = HttpService()
    _IntelService_instance: HttpService | None = None
