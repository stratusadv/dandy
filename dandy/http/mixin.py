from typing import ClassVar

from dandy.http.service import HttpService


class HttpProcessorMixin:
    http: ClassVar[HttpService] = HttpService()