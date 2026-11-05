from __future__ import annotations

import requests

from dandy.shared.cancellation import stop_signal
from dandy.shared.exceptions import RUN_STOPPED_MESSAGE, RunStoppedError
from dandy.shared.settings import settings
from dandy.shared.connector.connector import BaseConnector
from dandy.infrastructure.http.exceptions import HttpConnectorRecoverableError
from dandy.infrastructure.http.intel import HttpRequestIntel, HttpResponseIntel


class HttpConnector(BaseConnector):
    @staticmethod
    def request_to_response(request_intel: HttpRequestIntel) -> HttpResponseIntel:
        response_intel: HttpResponseIntel = HttpResponseIntel(
            status_code=0, reason='Unknown Reasons or Connection Timeouts', text='', json_data={}
        )
        last_error: requests.exceptions.RequestException | None = None

        for _ in range(settings.HTTP_CONNECTION_RETRY_COUNT + 1):
            if stop_signal.is_set():
                raise RunStoppedError(RUN_STOPPED_MESSAGE)

            try:
                response_intel = request_intel.to_http_response_intel()

                if response_intel.status_code in (200, 201):
                    return response_intel

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as error:
                last_error = error
                continue

        reason = response_intel.reason

        if last_error is not None and response_intel.status_code == 0:
            reason = f'{type(last_error).__name__}: {last_error}'

        message = (
            f'HttpConnector request failed with status code {response_intel.status_code} '
            f'and the following message "{reason}" '
            f'and body text "{response_intel.text}" '
            f'after {settings.HTTP_CONNECTION_RETRY_COUNT} attempts'
        )
        raise HttpConnectorRecoverableError(message)
