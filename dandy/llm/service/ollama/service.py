from typing import Type, Optional

from pydantic import ValidationError

from dandy import config
from dandy.core.type_vars import ModelType
from dandy.llm.prompt import Prompt
from dandy.llm.service import Service
from dandy.llm.service.ollama.prompts import ollama_system_model_prompt, ollama_user_prompt
from dandy.llm.service.ollama.request import OllamaRequest
from dandy.llm.service.prompts import pydantic_validation_error_prompt
from dandy.llm.service.settings import ServiceSettings


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

        ollama_request = OllamaRequest(model='llama3.1')

        ollama_request.add_message(
            role='system',
            content=ollama_system_model_prompt(
                model=model,
                prefix_system_prompt=prefix_system_prompt
            ).to_str()
        )

        ollama_request.add_message(
            role='user',
            content=ollama_user_prompt(prompt).to_str()
        )

        print(ollama_request.model_dump())

        response = cls.post_request(ollama_request.model_dump())

        message_content = response['message']['content']

        try:
            return model.model_validate_json(message_content)

        except ValidationError as e:
            try:
                ollama_request.add_message(
                    role='system',
                    content=message_content
                )
                ollama_request.add_message(
                    role='user',
                    content=pydantic_validation_error_prompt(e).to_str()
                )

                response = cls.post_request(ollama_request.model_dump())

                message_content = response['message']['content']

                return model.model_validate_json(message_content)

            except ValidationError as e:
                raise ValidationError(f'Could not validate response from Ollama. {e}')
