import httpx

from dandy.intel.intel import BaseIntel


class HttpResponseIntel(BaseIntel):
    status_code: int
    response_phrase: str
    text: str
    json: dict

    def as_httpx(self) -> httpx.Response:
        pass


class HttpRequestIntel(BaseIntel):
    method: str
    url: str
    params: dict | None = None
    headers: dict | None = None
    cookies: dict | None = None
    content: str | None = None
    data: dict | None = None
    files: dict | None = None
    json: dict | None = None
    stream: bool | None = None

    def as_httpx(self) -> httpx.Request:
        return httpx.Request(
            **self.model_dump()
        )

    def get_response_intel(self) -> HttpResponseIntel:
        with httpx.Client() as client:
            httpx_response = client.send(
                self.as_httpx()
            )

            return HttpResponseIntel(
                status_code=httpx_response.status_code,
                response_phrase=httpx_response.reason_phrase,
                text=httpx_response.text,
                json=httpx_response.json()
            )
