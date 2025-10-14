from __future__ import annotations

import httpx

from dandy.conf import settings
from dandy.http.exceptions import HttpConnectorRecoverableException
from dandy.http.intelligence.intel import HttpRequestIntel, HttpResponseIntel


class HttpConnector:
    @staticmethod
    def request_to_response(request_intel: HttpRequestIntel) -> HttpResponseIntel:
        response_intel: HttpResponseIntel = HttpResponseIntel(
            status_code=0,
            response_phrase='Unknown Reasons or Connection Timeouts',
            text='',
            json_data={},
        )

        for _ in range(settings.HTTP_CONNECTION_RETRY_COUNT + 1):
            try:
                response_intel = request_intel.to_http_response_intel()

                if response_intel.status_code in (200, 201):
                    return response_intel

            except httpx.TimeoutException:
                continue

        message = (
            f'HttpConnector request failed with status code {response_intel.status_code} '
            f'and the following message "{response_intel.response_phrase}" '
            f'after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts'
        )
        raise HttpConnectorRecoverableException(message)



