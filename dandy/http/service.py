from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService
from dandy.http.connector import HttpConnector
from dandy.http.intelligence.intel import HttpResponseIntel, HttpRequestIntel

if TYPE_CHECKING:
    from dandy.http.mixin import HttpServiceMixin


class HttpService(BaseService["HttpServiceMixin"]):
    _http_connector = HttpConnector()

    obj: HttpServiceMixin

    def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        cookies: dict | None = None,
    ) -> HttpResponseIntel:
        return self._http_connector.request_to_response(
            HttpRequestIntel(
                method="GET",
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
            )
        )

    def post(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        cookies: dict | None = None,
        content: str | None = None,
        data: dict | None = None,
        files: dict | None = None,
        json: dict | None = None,
    ) -> HttpResponseIntel:
        return self._http_connector.request_to_response(
            HttpRequestIntel(
                method="POST",
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                content=content,
                data=data,
                files=files,
                json_data=json,
            )
        )

    def request_intel_to_response_intel(self, request_intel: HttpRequestIntel) -> HttpResponseIntel:
        return self._http_connector.request_to_response(request_intel)

    def reset_service(self):
        pass
