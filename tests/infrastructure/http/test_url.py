from unittest import TestCase

from dandy.infrastructure.http.url import Url


class TestUrl(TestCase):
    def test_to_str_with_defaults(self) -> None:
        url = Url(host='https://api.example.com')

        self.assertEqual(url.to_str(), 'https://api.example.com:443')

    def test_to_str_includes_port(self) -> None:
        url = Url(host='http://api.example.com', port=8080)

        self.assertEqual(url.to_str(), 'http://api.example.com:8080')

    def test_str_uses_to_str(self) -> None:
        url = Url(host='https://api.example.com')

        self.assertEqual(str(url), url.to_str())

    def test_is_https(self) -> None:
        self.assertTrue(Url(host='https://api.example.com').is_https)
        self.assertFalse(Url(host='http://api.example.com').is_https)

    def test_path_parameters_are_joined_and_quoted(self) -> None:
        url = Url(host='https://api.example.com', path_parameters=['v1', 'chat', 'a b'])

        self.assertEqual(url.path, '/v1/chat/a%20b')
        self.assertEqual(url.to_str(), 'https://api.example.com:443/v1/chat/a%20b')

    def test_path_strips_trailing_slash_from_host(self) -> None:
        url = Url(host='https://api.example.com/base/', path_parameters=['v1'])

        self.assertEqual(url.path_parameters_to_str, '/base/v1')

    def test_query_parameters_are_urlencoded(self) -> None:
        url = Url(
            host='https://api.example.com',
            path_parameters=['v1'],
            query_parameters={'key': 'value', 'other': 'x'},
        )

        self.assertEqual(url.query_parameters_to_str, '?key=value&other=x')
        self.assertEqual(url.to_str(), 'https://api.example.com:443/v1?key=value&other=x')

    def test_path_is_empty_without_parameters(self) -> None:
        url = Url(host='https://api.example.com')

        self.assertEqual(url.path, '')
