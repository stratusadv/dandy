from unittest import TestCase, mock
from httpx import Response

from dandy.http.exceptions import HttpConnectorCriticalException
from dandy.http.connector import HttpConnector
from dandy.http.intelligence.intel import HttpRequestIntel
from dandy.http.url import Url


class TestHttpService(TestCase):
    @mock.patch('httpx.Client.send')
    def test_post_request(self, mock_httpx_client_send: mock.MagicMock):
        http_connector = HttpConnector()

        mock_httpx_client_send.return_value = Response(
            status_code=200
        )

        _ = http_connector.request_to_response(
            HttpRequestIntel(
                method='GET',
                url=Url(
                    host='https://www.google.com/'
                )
            )
        )

        mock_httpx_client_send.return_value = Response(
            status_code=500
        )

        with self.assertRaises(HttpConnectorCriticalException):
            _ = http_connector.request_to_response(
                HttpRequestIntel(
                    method='GET',
                    url=Url(
                        host='https://www.google.com/'
                    )
                )
            )

        mock_httpx_client_send.return_value = Response(
            status_code=0
        )

        with self.assertRaises(HttpConnectorCriticalException):
            _ = http_connector.request_to_response(
                HttpRequestIntel(
                    method='GET',
                    url=Url(
                        host='https://www.google.com/'
                    )
                )
            )
