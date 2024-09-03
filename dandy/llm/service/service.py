import http.client
import json
from abc import ABC, abstractmethod
from typing import Type, Optional
from urllib.parse import urlencode, urlparse

from dandy.core.type_vars import ModelType
from dandy.llm.prompt import Prompt
from dandy.llm.service.settings import ServiceSettings
from dandy.llm.utils import encode_path_parameters


class Service(ABC):
    @classmethod
    @abstractmethod
    def get_estimated_token_count_for_prompt(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
            prefix_system_prompt: Optional[Prompt] = None
    ) -> int:
        ...

    @classmethod
    @abstractmethod
    def get_settings(cls) -> ServiceSettings:
        ...

    @classmethod
    @abstractmethod
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
            prefix_system_prompt: Optional[Prompt] = None
    ) -> ModelType:
        ...

    @classmethod
    def create_connection(cls) -> http.client.HTTPSConnection:
        cls.validate_settings()

        parsed_url = urlparse(cls.get_settings().url)

        if parsed_url.scheme == '':
            parsed_url = urlparse('https://' + cls.get_settings().url)

        if parsed_url.scheme == "https":
            connection = http.client.HTTPSConnection(parsed_url.netloc, port=cls.get_settings().port)
        else:
            connection = http.client.HTTPConnection(parsed_url.netloc, port=cls.get_settings().port)

        return connection

    @classmethod
    def process_request(cls, method, path, encoded_body: bytes = None) -> dict:
        cls.validate_settings()

        connection = cls.create_connection()

        if encoded_body:
            connection.request(method, path, body=encoded_body, headers=cls.get_settings().headers)
        else:
            connection.request(method, path, headers=cls.get_settings().headers)

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
        path_parameters = '/'.join(encode_path_parameters(cls.get_settings().path_parameters))

        url_path = f'/{path_parameters}'

        if cls.get_settings().query_parameters:
            query = urlencode(cls.get_settings().query_parameters)
            url_path += '?' + query

        return url_path

    @classmethod
    def validate_settings(cls):
        if cls.get_settings().url is None:
            raise ValueError('Url not set')

        if cls.get_settings().port is None:
            raise ValueError('Port not set')
