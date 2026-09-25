from dandy.shared.service.mixin import BaseServiceMixin
from dandy.infrastructure.http.service import HttpService


class HttpServiceMixin(BaseServiceMixin):
    @property
    def http(self) -> HttpService:
        return self._get_service_instance(HttpService)

    def reset(self) -> None:
        super().reset()
        self.http.reset()
