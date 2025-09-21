from dataclasses import dataclass
from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.http.service import HttpService


@dataclass(kw_only=True)
class HttpServiceMixin(BaseServiceMixin):
    http: ClassVar[HttpService] = HttpService()
    _HttpService_instance: HttpService | None = None
