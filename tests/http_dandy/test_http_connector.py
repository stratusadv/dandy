from unittest import TestCase, mock
import requests

from dandy.http.exceptions import HttpConnectorCriticalException
from dandy.http.connector import HttpConnector
from dandy.http.intelligence.intel import HttpRequestIntel
from dandy.http.url import Url


class TestHttpConnector(TestCase):
    @mock.patch("requests.request")
    def test_post_request(self, mock_requests: mock.MagicMock):
        http_connector = HttpConnector()

        mock_response = mock.Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        _ = http_connector.request_to_response(
            HttpRequestIntel(method="GET", url=Url(host="https://www.google.com/"))
        )

        mock_response.status_code = 500
        mock_requests.return_value = mock_response

        with self.assertRaises(HttpConnectorCriticalException):
            _ = http_connector.request_to_response(
                HttpRequestIntel(method="GET", url=Url(host="https://www.google.com/"))
            )

        mock_response.status_code = 0
        mock_requests.return_value = mock_response

        with self.assertRaises(HttpConnectorCriticalException):
            _ = http_connector.request_to_response(
                HttpRequestIntel(
                    method='GET',
                    url=Url(
                        host='https://www.google.com/'
                    )
                )
            )
