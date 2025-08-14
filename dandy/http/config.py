from base64 import b64encode

from typing import Union

from dandy.http.url import Url
from dandy.core.config.config import BaseConfig


class HttpConnectorConfig(BaseConfig):
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
            self.headers['Authorization'] = f'Basic {self._encode_basic_auth(basic_auth)}'

        self.register_settings(
            'url',
            'headers',
            'basic_auth',
        )

    @staticmethod
    def _encode_basic_auth(basic_auth: str) -> str:
        return b64encode(f"Bearer:{basic_auth}".encode()).decode()