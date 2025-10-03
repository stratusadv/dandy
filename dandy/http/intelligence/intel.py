from typing import Any, Self

import httpx

from dandy.http.url import Url
from dandy.intel.intel import BaseIntel


class HttpResponseIntel(BaseIntel):
    status_code: int
    response_phrase: str | None = None
    text: str | None = None
    json_data: dict | None = None

    @classmethod
    def from_httpx_response(cls, httpx_response: httpx.Response) -> Self:
        try:
            json_data = httpx_response.json()
        except ValueError:
            json_data = {}

        return HttpResponseIntel(
            status_code=httpx_response.status_code,
            response_phrase=httpx_response.reason_phrase,
            text=httpx_response.text,
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

    def as_httpx_request(self) -> httpx.Request:
        if isinstance(self.url, Url):
            self.url = self.url.to_str()

        return httpx.Request(
            method=self.method,
            url=self.url,
            params=self.params,
            headers=self.headers,
            cookies=self.cookies,
            content=self.content,
            data=self.data,
            files=self.files,
            json=self.json_data,
            stream=self.stream,
        )

    def generate_headers(self):
        if self.bearer_token is not None:
            if self.headers is None:
                self.headers = {}

            self.headers['Authorization'] = f'Bearer {self.bearer_token}'

