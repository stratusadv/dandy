from __future__ import annotations

import json
from abc import ABC
from time import sleep
from typing_extensions import TYPE_CHECKING

import httpx
from httpx import Response

from dandy.conf import settings
from dandy.core.http.exceptions import HttpCriticalException

if TYPE_CHECKING:
    from dandy.core.http.config import HttpConfig


class BaseHttpService(ABC):
    def __init__(self, config: HttpConfig):
        self._config = config

    def post_request(self, json_body_dict: dict) -> dict:
        response: Response = Response(status_code=0)

        for _ in range(settings.HTTP_CONNECTION_RETRY_COUNT + 1):

            response = httpx.request(
                'POST',
                self._config.url.to_str(),
                headers=self._config.headers,
                content=json.dumps(json_body_dict).encode('utf-8'),
                timeout=settings.DEFAULT_LLM_REQUEST_TIMEOUT
            )

            if response.status_code == 200 or response.status_code == 201:
                json_data = json.loads(response.text)
                return json_data

            sleep(0.1)

        else:
            if response.status_code != 0:
                raise HttpCriticalException(
                    f'HTTP service request failed with status code {response.status_code} and the following message "{response.text}" after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts')
            else:
                raise HttpCriticalException(
                    f'HTTP service request failed after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts for unknown reasons')
