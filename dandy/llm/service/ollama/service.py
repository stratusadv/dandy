import json
from random import randint
from typing import Type, TypeVar, Optional

from pydantic import ValidationError

from dandy import config
from dandy.core.type_vars import ModelType
from dandy.llm.service import Service
from dandy.llm.service.messages import ServiceMessages
from dandy.llm.service.ollama.prompts import ollama_system_model_prompt, ollama_user_prompt
from dandy.llm.service.prompts import pydantic_validation_error_prompt
from dandy.llm.service.settings import ServiceSettings
from dandy.llm.prompt import Prompt


def generate_ollama_request_body(messages: ServiceMessages) -> dict:
    return {
        'model': 'llama3.1',
        'messages': messages.model_dump_list(),
        'stream': False,
        'format': 'json',
        'temperature': 0.1,
        'seed': randint(0, 99999),
    }


class OllamaService(Service):
    @classmethod
    def get_estimated_token_count_for_prompt(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
            prefix_system_prompt: Optional[Prompt] = None) -> int:
        return ollama_system_model_prompt(
            model=model,
            prefix_system_prompt=prefix_system_prompt
        ).estimated_token_count + ollama_user_prompt(prompt).estimated_token_count

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
    def process_prompt_to_model_object(
            cls,
            prompt: Prompt,
            model: Type[ModelType],
            prefix_system_prompt: Optional[Prompt] = None
    ) -> ModelType:

        messages = ServiceMessages()

        messages.add(
            role='system',
            content=ollama_system_model_prompt(
                model=model,
                prefix_system_prompt=prefix_system_prompt
            ).to_str()
        )

        messages.add(
            role='user',
            content=ollama_user_prompt(prompt).to_str()
        )

        response = cls.post_request(generate_ollama_request_body(messages))

        message_content = response['message']['content']

        try:
            return model.model_validate_json(message_content)

        except ValidationError as e:
            try:
                messages.add(
                    role='system',
                    content=message_content
                )
                messages.add(
                    role='user',
                    content=pydantic_validation_error_prompt(e).to_str()
                )

                response = cls.post_request(generate_ollama_request_body(messages))

                message_content = response['message']['content']

                return model.model_validate_json(message_content)

            except ValidationError as e:
                raise ValidationError(f'Could not validate response from Ollama. {e}')
