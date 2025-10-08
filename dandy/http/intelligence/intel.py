from typing import Any, Self

import requests

from dandy.http.url import Url
from dandy.intel.intel import BaseIntel


class HttpResponseIntel(BaseIntel):
    status_code: int
    response_phrase: str | None = None
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
            response_phrase=requests_response.reason,
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

    def as_request_kwargs(self) -> dict:
        if isinstance(self.url, Url):
            url = self.url.to_str()
        else:
            url = self.url

        return {
            'method': self.method,
            'url': url,
            'params': self.params,
            'headers': self.headers,
            'cookies': self.cookies,
            'data': self.content if self.content else self.data,
            'files': self.files,
            'json': self.json_data,
            'stream': self.stream,
        }

    def generate_headers(self):
        if self.bearer_token is not None:
            if self.headers is None:
                self.headers = {}

            self.headers['Authorization'] = f'Bearer {self.bearer_token}'
