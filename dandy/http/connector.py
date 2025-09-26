from __future__ import annotations

from time import sleep

import httpx

from dandy.conf import settings
from dandy.core.connector.connector import BaseConnector
from dandy.http.exceptions import HttpConnectorCriticalException
from dandy.http.intelligence.intel import HttpRequestIntel, HttpResponseIntel


class HttpConnector(BaseConnector):
    @staticmethod
    def request_to_response(
            request_intel: HttpRequestIntel
    ) -> HttpResponseIntel:
        response_intel: HttpResponseIntel = HttpResponseIntel(
            status_code=0,
            response_phrase='',
            text='',
            json_data={},
        )

        with httpx.Client(
                timeout=settings.HTTP_CONNECTION_TIMEOUT_SECONDS,
        ) as client:
            for _ in range(settings.HTTP_CONNECTION_RETRY_COUNT + 1):
                response_intel = HttpResponseIntel.from_httpx_response(
                    client.send(
                        request_intel.as_httpx_request()
                    )
                )

                if response_intel.status_code == 200 or response_intel.status_code == 201:
                    return response_intel

                sleep(0.1)

            else:
                if response_intel.status_code == 0:
                    message = f'HttpConnector request failed after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts for unknown reasons'
                    raise HttpConnectorCriticalException(message)
                else:
                    message = f'HttpConnector request failed with status code {response_intel.status_code} and the following message "{response_intel.response_phrase}" after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts'
                    raise HttpConnectorCriticalException(message)

