from typing import Any, Self

import requests

from dandy.conf import settings
from dandy.http.url import Url
from dandy.intel.intel import BaseIntel


class HttpResponseIntel(BaseIntel):
    status_code: int
    reason: str | None = None
    text: str | None = None
    json_data: dict | None = None

    @classmethod
    def from_requests_response(cls, requests_response: requests.Response) -> Self:
        try:
            json_data = requests_response.json()
        except ValueError:
            json_data = {}

        return HttpResponseIntel(
            status_code=requests_response.status_code,
            reason=requests_response.reason,
            text=requests_response.text,
            json_data=json_data
        )

    @property
    def json_str(self) -> str:
        return self.text


class HttpRequestIntel(BaseIntel):
    method: str
    url: str | Url
    params: dict | None = None
    headers: dict | None = {
        'Content-Type': 'text/html'
    }
    cookies: dict | None = None
    content: str | None = None
    data: dict | None = None
    files: dict | None = None
    json_data: dict | None = None
    stream: bool | None = None
    bearer_token: str | None = None

    def model_post_init(self, __context: Any):
        self.generate_headers()

    def to_http_response_intel(self) -> HttpResponseIntel:
        if isinstance(self.url, Url):
            url = self.url.to_str()
        else:
            url = self.url

        response = requests.request(
            method=self.method,
            url=url,
            headers=self.headers,
            # data=request_intel.json_data,
            json=self.json_data,
            timeout=settings.HTTP_CONNECTION_TIMEOUT_SECONDS,
        )

        return HttpResponseIntel.from_requests_response(
            response
        )


    def generate_headers(self):
        if self.bearer_token is not None:
            if self.headers is None:
                self.headers = {}

            self.headers['Authorization'] = f'Bearer {self.bearer_token}'
