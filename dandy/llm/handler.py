import json
from abc import ABC
import http.client
from urllib.parse import urlencode, urlparse

from dandy.llm.utils import encode_parameters


class Handler(ABC):
    address: str
    port: int
    headers: dict

    @classmethod
    def create_connection(cls) -> http.client.HTTPSConnection:
        parsed_url = urlparse(cls.address)
        if parsed_url.scheme == "https":
            connection = http.client.HTTPSConnection(parsed_url.netloc)
        else:
            connection = http.client.HTTPConnection(parsed_url.netloc)

        return connection

    @classmethod
    def process_request(cls, method, path, encoded_body: bytes = None) -> dict:
        if cls.address is None:
            raise ValueError('Address not set')

        if cls.port is None:
            raise ValueError('Port not set')

        connection = cls.create_connection()

        if encoded_body:
            connection.request(method, path, body=encoded_body, headers=cls.headers)
        else:
            connection.request(method, path, headers=cls.headers)

        response = connection.getresponse()

        if response.status != 200 and response.status != 201:
            print(f'PATH: {path}')
            raise Exception(f"Request failed with status code {response.status}")

        json_data = json.loads(response.read().decode("utf-8"))

        connection.close()

        return json_data

    @classmethod
    def get_request(cls, path) -> dict:
        return cls.process_request("GET", path)

    @classmethod
    def post_request(cls, url, body) -> dict:
        encoded_body = json.dumps(body).encode('utf-8')
        return cls.process_request("POST", url, encoded_body)

    @classmethod
    def generate_url_path(cls, *args, **kwargs) -> str:
        query_parameters = kwargs.get('query_params', {})
        path_parameters = '/'.join(encode_parameters(*args))

        url = f'/{path_parameters}/'

        if query_parameters:
            query = urlencode(query_parameters)
            url += '?' + query

        return url