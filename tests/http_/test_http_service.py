from unittest import TestCase, mock

from bottle import http_date

from dandy.http.service import HttpService
from dandy.http.intelligence.intel import HttpRequestIntel, HttpResponseIntel


class TestHttpService(TestCase):
    @mock.patch('dandy.http.service.HttpService._http_connector.request_to_response')
    def test_get_calls_connector_with_expected_request(self, mock_request_to_response: mock.MagicMock):
        http_service = HttpService()

        expected_response = HttpResponseIntel(
            status_code=200,
            response_phrase='OK',
            text='ok',
            json_data={'ok': True},
        )

        def assert_request_and_return(request_intel: HttpRequestIntel):
            # Verify the HttpRequestIntel passed into connector
            self.assertIsInstance(request_intel, HttpRequestIntel)
            self.assertEqual(request_intel.method, 'GET')
            self.assertEqual(request_intel.url, 'https://api.example.com/resource')
            self.assertEqual(request_intel.params, {'q': 'search'})
            self.assertEqual(request_intel.headers, {'X-Test': 'yes'})
            self.assertEqual(request_intel.cookies, {'session': 'abc'})
            # Body-related fields should be None for GET
            self.assertIsNone(request_intel.content)
            self.assertIsNone(request_intel.data)
            self.assertIsNone(request_intel.files)
            self.assertIsNone(request_intel.json_data)
            return expected_response

        mock_request_to_response.side_effect = assert_request_and_return

        response = http_service.get(
            url='https://api.example.com/resource',
            params={'q': 'search'},
            headers={'X-Test': 'yes'},
            cookies={'session': 'abc'},
        )

        self.assertIs(response, expected_response)
        mock_request_to_response.assert_called_once()

    @mock.patch('dandy.http.service.HttpService._http_connector.request_to_response')
    def test_post_calls_connector_with_expected_request(self, mock_request_to_response: mock.MagicMock):
        http_service = HttpService()

        expected_response = HttpResponseIntel(
            status_code=201,
            reason='Created',
            text='created',
            json_data={'id': 1},
        )

        def assert_request_and_return(request_intel: HttpRequestIntel):
            self.assertIsInstance(request_intel, HttpRequestIntel)
            self.assertEqual(request_intel.method, 'POST')
            self.assertEqual(request_intel.url, 'https://api.example.com/items')
            self.assertEqual(request_intel.params, {'verbose': '1'})
            self.assertEqual(request_intel.headers, {'Content-Type': 'application/json'})
            self.assertEqual(request_intel.cookies, {'auth': 'token'})
            self.assertEqual(request_intel.content, 'raw-bytes')
            self.assertEqual(request_intel.data, {'k': 'v'})
            self.assertEqual(request_intel.files, {'file': b'data'})
            self.assertEqual(request_intel.json_data, {'name': 'Item'})
            return expected_response

        mock_request_to_response.side_effect = assert_request_and_return

        response = http_service.post(
            url='https://api.example.com/items',
            params={'verbose': '1'},
            headers={'Content-Type': 'application/json'},
            cookies={'auth': 'token'},
            content='raw-bytes',
            data={'k': 'v'},
            files={'file': b'data'},
            json={'name': 'Item'},
        )

        self.assertIs(response, expected_response)
        mock_request_to_response.assert_called_once()
