from __future__ import annotations



from dandy.conf import settings
from dandy.core.connector.connector import BaseConnector
from dandy.http.exceptions import HttpConnectorCriticalException
from dandy.http.intelligence.intel import HttpRequestIntel, HttpResponseIntel


class HttpConnector(BaseConnector):
    @staticmethod
    def request_to_response(request_intel: HttpRequestIntel) -> HttpResponseIntel:
        response_intel: HttpResponseIntel = HttpResponseIntel(
            status_code=0,
            reason="Unknown Reasons",
            text="",
            json_data={},
        )

        for _ in range(settings.HTTP_CONNECTION_RETRY_COUNT + 1):
            response_intel = request_intel.to_http_response_intel()

            if response_intel.status_code in (200, 201):
                return response_intel

        if response_intel.status_code != 0:
            message = f'HttpConnector request failed with status code {response_intel.status_code} and the following message "{response_intel.reason}" after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts'
            raise HttpConnectorCriticalException(message)

        message = f"HttpConnector request failed after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts for {response_intel.reason}"
        raise HttpConnectorCriticalException(message)


