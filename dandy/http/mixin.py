from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.http.service import HttpService


class HttpServiceMixin(BaseServiceMixin):
    _http_service: HttpService = ...

    # http: ClassVar[HttpService] = HttpService()
    # _HttpService_instance: HttpService | None = None

    @property
    def http(self) -> HttpService:
        if self._http_service is ...:
            self._http_service = HttpService(
                obj=self
            )

        return self._http_service

    def reset_services(self):
        super().reset_services()
        self.http.reset_service()
