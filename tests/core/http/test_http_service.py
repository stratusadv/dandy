from unittest import TestCase, mock
from httpx import Response

from dandy.core.http.config import HttpConfig
from dandy.core.http.exceptions import HttpCriticalException
from dandy.core.http.service import BaseHttpService
from dandy.core.http.url import Url


class TestHttpService(TestCase):
    @mock.patch('httpx.request')
    @mock.patch.multiple(BaseHttpService, __abstractmethods__=set())
    def test_post_request(self, mock_httpx_request: mock.MagicMock):
        base_http = BaseHttpService(HttpConfig(Url(host='https://test.com')))

        mock_httpx_request.return_value = Response(status_code=500)
        with self.assertRaises(HttpCriticalException):
           response = base_http.post_request({
               'foo': 'bar'
           })

        mock_httpx_request.return_value = Response(status_code=0)
        with self.assertRaises(HttpCriticalException):
            response = base_http.post_request({
                'foo': 'bar'
            })