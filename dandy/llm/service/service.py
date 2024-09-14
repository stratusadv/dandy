import http.client
import json
from abc import ABC, abstractmethod
from http.client import responses
from time import sleep
from typing import Type, Optional, Union
from urllib.parse import urlencode, urlparse

from pydantic import ValidationError

from dandy import config
from dandy.core.type_vars import ModelType
from dandy.llm.prompt import Prompt
from dandy.llm.exceptions import LlmException
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, service_system_model_prompt
from dandy.llm.service.request import BaseRequest
from dandy.llm.service.settings import ServiceSettings
from dandy.llm.utils import encode_path_parameters


class Service(ABC):
    @classmethod
    def get_settings(cls) -> ServiceSettings:
        return ServiceSettings(
            url=config.ollama_service_config.url,
            port=config.ollama_service_config.port,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            path_parameters=[
                'api',
                'chat',
            ],
            query_parameters=None
        )


    @classmethod
    def create_connection(cls) -> Union[http.client.HTTPConnection, http.client.HTTPSConnection]:
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
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
            prefix_system_prompt: Optional[Prompt] = None
    ) -> ModelType:

        request = BaseRequest(model='llama3.1')

        request.add_message(
            role='system',
            content=service_system_model_prompt(
                model=model,
                prefix_system_prompt=prefix_system_prompt
            ).to_str()
        )

        request.add_message(
            role='user',
            content=service_user_prompt(prompt).to_str()
        )

        print(request.model_dump())

        response = cls.post_request(request.model_dump())

        message_content = response['message']['content']

        try:
            return model.model_validate_json(message_content)

        except ValidationError as e:
            try:
                request.add_message(
                    role='system',
                    content=message_content
                )
                request.add_message(
                    role='user',
                    content=service_system_validation_error_prompt(e).to_str()
                )

                response = cls.post_request(request.model_dump())

                message_content = response['message']['content']

                return model.model_validate_json(message_content)

            except ValidationError as e:
                raise ValidationError(f'Could not validate response from Ollama. {e}')

    @classmethod
    def process_request(cls, method, path, encoded_body: bytes = None) -> dict:
        cls.validate_settings()

        response = None

        for _ in range(cls.get_settings().retry_count):
            connection = cls.create_connection()

            if encoded_body:
                connection.request(method, path, body=encoded_body, headers=cls.get_settings().headers)
            else:
                connection.request(method, path, headers=cls.get_settings().headers)

            response = connection.getresponse()


            if response.status == 200 or response.status == 201:
                json_data = json.loads(response.read().decode("utf-8"))
                connection.close()
                break

            connection.close()
            sleep(0.1)

        else:
            raise LlmException(f"Llm service request failed with status code {response.status} after {cls.get_settings().retry_count} attempts")

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
