from base64 import b64encode

from typing_extensions import Union, List

from dandy.conf import settings
from dandy.core.http.url import Url


class HttpConfig:
    def __init__(
            self,
            url: Url,
            headers: Union[dict, None] = None,
            basic_auth: Union[str, None] = None,
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
            self.headers['Authorization'] = f'Basic {b64encode(f"Bearer:{basic_auth}".encode()).decode()}'
