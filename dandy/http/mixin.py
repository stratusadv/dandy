from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.http.service import HttpService


class HttpServiceMixin(BaseServiceMixin):
    http: ClassVar[HttpService] = HttpService()
    _HttpService_instance: HttpService | None = None
