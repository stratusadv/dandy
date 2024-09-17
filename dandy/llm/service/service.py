from __future__ import annotations

import http.client
import json
from time import sleep
from typing import Type, Optional, Union, TYPE_CHECKING

from pydantic import ValidationError

from dandy.core.type_vars import ModelType
from dandy.llm.exceptions import LlmException, LlmValidationException
from dandy.llm.prompt import Prompt
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_model_prompt
from dandy.llm.service.request import BaseRequest

if TYPE_CHECKING:
    from dandy.llm.config import LlmConfig


class Service:
    def __init__(self, config: LlmConfig):
        self._config = config

    def create_connection(self) -> Union[http.client.HTTPConnection, http.client.HTTPSConnection]:
        connection_kwargs = {
            'host': self._config.url.parsed_url.netloc,
            'port': self._config.port
        }

        if self._config.url.is_https:
            connection = http.client.HTTPSConnection(**connection_kwargs)
        else:
            connection = http.client.HTTPConnection(**connection_kwargs)

        return connection

    def assistant_prompt_str_to_str(
            self,
            prompt_str: str,
    ) -> str:
        request = BaseRequest(
            model=self._config.model,
            format='string',
        )

        request.add_message(
            role='system',
            content='You are a helpful assistant.'
        )

        request.add_message(
            role='user',
            content=prompt_str
        )

        return self._config.get_response_content(
            self.post_request(request.model_dump())
        )


    def process_prompt_to_model_object(
            self,
            prompt: Prompt,
            model: Type[ModelType],
            prefix_system_prompt: Optional[Prompt] = None
    ) -> ModelType:

        for _ in range(2):

            request = BaseRequest(model=self._config.model)

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

            message_content = self._config.get_response_content(
                self.post_request(request.model_dump())
            )

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

                    message_content = self._config.get_response_content(
                        self.post_request(request.model_dump())
                    )

                    return model.model_validate_json(message_content)

                except ValidationError as e:
                    pass
        else:
            raise LlmValidationException

    def process_request(self, method, path, encoded_body: bytes = None) -> dict:
        response = None

        for _ in range(self._config.retry_count):
            connection = self.create_connection()

            if encoded_body:
                connection.request(method, path, body=encoded_body, headers=self._config.headers)
            else:
                connection.request(method, path, headers=self._config.headers)

            response = connection.getresponse()

            if response.status == 200 or response.status == 201:
                json_data = json.loads(response.read().decode("utf-8"))
                connection.close()
                break

            connection.close()
            sleep(0.1)

        else:
            raise LlmException(f"Llm service request failed with status code {response.status} after {self._config.retry_count} attempts")

        return json_data

    def get_request(self) -> dict:
        return self.process_request("GET", self._config.url.path)

    def post_request(self, body) -> dict:
        encoded_body = json.dumps(body).encode('utf-8')
        return self.process_request("POST", self._config.url.path, encoded_body)

