from unittest import TestCase

from dandy.infrastructure.http.intel import HttpRequestIntel, HttpResponseIntel
from dandy.infrastructure.http.url import Url


class TestHttpRequestIntel(TestCase):
    def test_json_str_serializes_json_data(self) -> None:
        request_intel = HttpRequestIntel(
            method='POST', url='https://example.com', json_data={'a': 1}
        )

        self.assertEqual(request_intel.json_str, '{"a": 1}')

    def test_generate_headers_adds_bearer_token(self) -> None:
        request_intel = HttpRequestIntel(
            method='POST',
            url='https://example.com',
            bearer_token='secret',  # noqa: S106
        )

        self.assertEqual(request_intel.headers, {'Authorization': 'Bearer secret'})

    def test_generate_headers_merges_with_existing_headers(self) -> None:
        request_intel = HttpRequestIntel(
            method='POST',
            url='https://example.com',
            headers={'X-Custom': 'value'},
            bearer_token='secret',  # noqa: S106
        )

        self.assertEqual(
            request_intel.headers, {'X-Custom': 'value', 'Authorization': 'Bearer secret'}
        )

    def test_no_bearer_token_leaves_headers_none(self) -> None:
        request_intel = HttpRequestIntel(method='POST', url='https://example.com')

        self.assertIsNone(request_intel.headers)

    def test_as_requests_request_with_string_url(self) -> None:
        request_intel = HttpRequestIntel(
            method='POST',
            url='https://example.com/v1/test',
            params={'page': '1'},
            json_data={'a': 1},
        )

        request = request_intel.as_requests_request()

        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url, 'https://example.com/v1/test')
        self.assertEqual(request.params, {'page': '1'})
        self.assertEqual(request.json, {'a': 1})

    def test_as_requests_request_converts_url_object_to_str(self) -> None:
        url = Url(host='https://example.com', path_parameters=['v1', 'test'])
        request_intel = HttpRequestIntel(method='GET', url=url)

        request = request_intel.as_requests_request()

        self.assertEqual(request.url, url.to_str())
        self.assertEqual(request_intel.url, url.to_str())


class TestHttpResponseIntelJsonStr(TestCase):
    def test_json_str_returns_text(self) -> None:
        response_intel = HttpResponseIntel(status_code=200, text='{"a": 1}')

        self.assertEqual(response_intel.json_str, '{"a": 1}')
