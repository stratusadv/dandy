

from dandy.core.http.url import Url


class HttpConfig:
    def __init__(
            self,
            url: Url,
            headers: dict | None = None,
            basic_auth: str | None = None,
    ):
        self.url = url

        if headers is None:
            self.headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        else:
            self.headers = headers

        if basic_auth is not None:
            self.headers["Authorization"] = f"Bearer {basic_auth}"
