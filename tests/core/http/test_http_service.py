from unittest import TestCase, mock
from httpx import Response

from dandy.connector.http.config import HttpConnectorConfig
from dandy.connector.http.exceptions import HttpConnectorCriticalException
from dandy.connector.http.connector import BaseHttpConnector
from dandy.connector.http.url import Url


class TestHttpService(TestCase):
    @mock.patch('httpx.request')
    @mock.patch.multiple(BaseHttpConnector, __abstractmethods__=set())
    def test_post_request(self, mock_httpx_request: mock.MagicMock):
        base_http = BaseHttpConnector(HttpConnectorConfig(Url(host='https://test.com')))

        mock_httpx_request.return_value = Response(status_code=500)
        with self.assertRaises(HttpConnectorCriticalException):
           response = base_http.post_request({
               'foo': 'bar'
           })

        mock_httpx_request.return_value = Response(status_code=0)
        with self.assertRaises(HttpConnectorCriticalException):
            response = base_http.post_request({
                'foo': 'bar'
            })