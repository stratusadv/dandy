from typing import ClassVar, Self

from dandy.core.service.mixin import BaseServiceMixin
from dandy.http.service import HttpService


class HttpServiceMixin(BaseServiceMixin):
    @property
    def http(self) -> HttpService:
        return self._get_service(HttpService)

    def reset_services(self):
        super().reset_services()
        self.http.reset_service()
