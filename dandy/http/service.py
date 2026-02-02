from dandy.core.service.service import BaseService
from dandy.http.connector import HttpConnector
from dandy.http.intelligence.intel import HttpResponseIntel, HttpRequestIntel


class HttpService(BaseService['dandy.http.mixin.HttpServiceMixin']):
    def __post_init__(self):
        self._http_connector = HttpConnector()

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
                data=data,
                files=files,
                json_data=json,
            )
        )

    def request_intel_to_response_intel(self, request_intel: HttpRequestIntel) -> HttpResponseIntel:
        return self._http_connector.request_to_response(request_intel)

    def reset(self):
        pass
