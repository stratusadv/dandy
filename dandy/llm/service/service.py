import http.client
import json
from time import sleep
from typing import Type, Optional, Union
from urllib.parse import urlencode, urlparse

from pydantic import ValidationError

from dandy.core.type_vars import ModelType
from dandy.llm.exceptions import LlmException
from dandy.llm.prompt import Prompt
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_model_prompt
from dandy.llm.service.request import BaseRequest
from dandy.llm.service.settings import ServiceSettings
from dandy.llm.utils import encode_path_parameters


class Service:
    def __init__(self, settings: ServiceSettings):
        self._settings = settings

    def create_connection(self) -> Union[http.client.HTTPConnection, http.client.HTTPSConnection]:
        self.validate_settings()

        parsed_url = urlparse(self._settings.url)

        if parsed_url.scheme == '':
            parsed_url = urlparse('https://' + self._settings.url)

        if parsed_url.scheme == "https":
            connection = http.client.HTTPSConnection(parsed_url.netloc, port=self._settings.port)
        else:
            connection = http.client.HTTPConnection(parsed_url.netloc, port=self._settings.port)

        return connection

    def process_prompt_to_model_object(
            self,
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

        # print(request.model_dump())

        response = self.post_request(request.model_dump())

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

                response = self.post_request(request.model_dump())

                message_content = response['message']['content']

                return model.model_validate_json(message_content)

            except ValidationError as e:
                raise ValidationError(f'Could not validate response from Ollama. {e}')

    def process_request(self, method, path, encoded_body: bytes = None) -> dict:
        self.validate_settings()

        response = None

        for _ in range(self._settings.retry_count):
            connection = self.create_connection()

            if encoded_body:
                connection.request(method, path, body=encoded_body, headers=self._settings.headers)
            else:
                connection.request(method, path, headers=self._settings.headers)

            response = connection.getresponse()


            if response.status == 200 or response.status == 201:
                json_data = json.loads(response.read().decode("utf-8"))
                connection.close()
                break

            connection.close()
            sleep(0.1)

        else:
            raise LlmException(f"Llm service request failed with status code {response.status} after {self._settings.retry_count} attempts")

        return json_data

    def get_request(self) -> dict:
        return self.process_request("GET", self.generate_url_path())

    def post_request(self, body) -> dict:
        encoded_body = json.dumps(body).encode('utf-8')
        return self.process_request("POST", self.generate_url_path(), encoded_body)

    def generate_url_path(self) -> str:
        path_parameters = '/'.join(encode_path_parameters(self._settings.path_parameters))

        url_path = f'/{path_parameters}'

        if self._settings.query_parameters:
            query = urlencode(self._settings.query_parameters)
            url_path += '?' + query

        return url_path

    def validate_settings(self):
        if self._settings.url is None:
            raise ValueError('Url not set')

        if self._settings.port is None:
            raise ValueError('Port not set')
