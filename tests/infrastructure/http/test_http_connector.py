from unittest import TestCase, mock

import requests

from dandy.infrastructure.http.connector import HttpConnector
from dandy.infrastructure.http.exceptions import HttpConnectorRecoverableError
from dandy.infrastructure.http.intel import HttpRequestIntel, HttpResponseIntel


def response(status_code: int, reason: str = 'Reason', text: str = 'Body') -> HttpResponseIntel:
    return HttpResponseIntel(status_code=status_code, reason=reason, text=text, json_data={})


class TestHttpConnector(TestCase):
    def make_request_intel(self) -> HttpRequestIntel:
        return HttpRequestIntel(method='POST', url='https://example.com/v1/test')

    @mock.patch('dandy.infrastructure.http.intel.HttpRequestIntel.to_http_response_intel')
    def test_returns_200_response_on_first_attempt(self, mock_to_response: mock.MagicMock) -> None:
        mock_to_response.return_value = response(200)

        result = HttpConnector.request_to_response(self.make_request_intel())

        self.assertEqual(result.status_code, 200)
        self.assertEqual(mock_to_response.call_count, 1)

    @mock.patch('dandy.infrastructure.http.intel.HttpRequestIntel.to_http_response_intel')
    def test_returns_201_response_on_first_attempt(self, mock_to_response: mock.MagicMock) -> None:
        mock_to_response.return_value = response(201)

        result = HttpConnector.request_to_response(self.make_request_intel())

        self.assertEqual(result.status_code, 201)
        self.assertEqual(mock_to_response.call_count, 1)

    @mock.patch('dandy.infrastructure.http.intel.HttpRequestIntel.to_http_response_intel')
    def test_retries_timeouts_then_succeeds(self, mock_to_response: mock.MagicMock) -> None:
        mock_to_response.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            response(200),
        ]

        result = HttpConnector.request_to_response(self.make_request_intel())

        self.assertEqual(result.status_code, 200)
        self.assertEqual(mock_to_response.call_count, 3)

    @mock.patch('dandy.infrastructure.http.intel.HttpRequestIntel.to_http_response_intel')
    def test_retries_non_2xx_then_succeeds(self, mock_to_response: mock.MagicMock) -> None:
        mock_to_response.side_effect = [response(500), response(503), response(200)]

        result = HttpConnector.request_to_response(self.make_request_intel())

        self.assertEqual(result.status_code, 200)
        self.assertEqual(mock_to_response.call_count, 3)

    @mock.patch('dandy.infrastructure.http.intel.HttpRequestIntel.to_http_response_intel')
    def test_timeout_exhaustion_raises_recoverable_error(
        self, mock_to_response: mock.MagicMock
    ) -> None:
        mock_to_response.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(HttpConnectorRecoverableError) as context:
            HttpConnector.request_to_response(self.make_request_intel())

        self.assertEqual(mock_to_response.call_count, 5)
        self.assertIn('after 4 attempts', str(context.exception))
        self.assertIn('status code 0', str(context.exception))

    @mock.patch('dandy.infrastructure.http.intel.HttpRequestIntel.to_http_response_intel')
    def test_non_2xx_exhaustion_error_includes_response_details(
        self, mock_to_response: mock.MagicMock
    ) -> None:
        mock_to_response.return_value = response(500, reason='Server Error', text='Bad Day')

        with self.assertRaises(HttpConnectorRecoverableError) as context:
            HttpConnector.request_to_response(self.make_request_intel())

        self.assertEqual(mock_to_response.call_count, 5)
        message = str(context.exception)
        self.assertIn('status code 500', message)
        self.assertIn('"Server Error"', message)
        self.assertIn('"Bad Day"', message)
        self.assertIn('after 4 attempts', message)


class TestHttpResponseIntel(TestCase):
    def make_requests_response(
        self, status_code: int, reason: str, text: str, json_data: dict | None
    ) -> mock.MagicMock:
        fake_response = mock.MagicMock()
        fake_response.status_code = status_code
        fake_response.reason = reason
        fake_response.text = text
        if json_data is None:
            fake_response.json.side_effect = ValueError('Not JSON')
        else:
            fake_response.json.return_value = json_data
        return fake_response

    def test_from_requests_response_parses_json_body(self) -> None:
        result = HttpResponseIntel.from_requests_response(
            self.make_requests_response(200, 'OK', '{"a": 1}', {'a': 1})
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.reason, 'OK')
        self.assertEqual(result.json_data, {'a': 1})

    def test_from_requests_response_falls_back_to_empty_json(self) -> None:
        result = HttpResponseIntel.from_requests_response(
            self.make_requests_response(200, 'OK', 'not json', None)
        )

        self.assertEqual(result.json_data, {})

    def test_json_str_returns_text(self) -> None:
        response_intel = HttpResponseIntel(status_code=200, text='{"a": 1}')

        self.assertEqual(response_intel.json_str, '{"a": 1}')
