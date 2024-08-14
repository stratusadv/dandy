import json
from abc import ABC, abstractmethod
import http.client
from urllib.parse import urlencode, urlparse

from dandy.llm.utils import encode_parameters


class Handler(ABC):
    url: str
    port: int
    headers: dict
    path_parameters: list
    query_parameters: dict

    def __new__(cls, *args, **kwargs):
        cls.setup()
        return super().__new__(cls)

    @classmethod
    @abstractmethod
    def setup(cls):
        pass

    @classmethod
    def create_connection(cls) -> http.client.HTTPSConnection:
        parsed_url = urlparse(cls.url)

        if parsed_url.scheme == '':
            parsed_url = urlparse('https://' + cls.url)

        if parsed_url.scheme == "https":
            connection = http.client.HTTPSConnection(parsed_url.netloc, port=cls.port)
        else:
            connection = http.client.HTTPConnection(parsed_url.netloc, port=cls.port)

        return connection

    @classmethod
    def process_request(cls, method, path, encoded_body: bytes = None) -> dict:
        if cls.url is None:
            raise ValueError('Url not set')

        if cls.port is None:
            raise ValueError('Port not set')

        connection = cls.create_connection()

        if encoded_body:
            connection.request(method, path, body=encoded_body, headers=cls.headers)
        else:
            connection.request(method, path, headers=cls.headers)

        response = connection.getresponse()

        print(response.headers)

        if response.status != 200 and response.status != 201:
            raise Exception(f"Request failed with status code {response.status}")

        json_data = json.loads(response.read().decode("utf-8"))

        connection.close()

        return json_data

    @classmethod
    def get_request(cls) -> dict:
        return cls.process_request("GET", cls.generate_url_path())

    @classmethod
    def post_request(cls, body) -> dict:
        encoded_body = json.dumps(body).encode('utf-8')
        return cls.process_request("POST", cls.generate_url_path(), encoded_body)

    @classmethod
    def generate_url_path(cls) -> str:
        path_parameters = '/'.join(encode_parameters(cls.path_parameters))

        url_path = f'/{path_parameters}'

        if cls.query_parameters:
            query = urlencode(cls.query_parameters)
            url_path += '?' + query

        return url_path