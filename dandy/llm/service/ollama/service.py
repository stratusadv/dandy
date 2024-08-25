import json
from typing import Type, TypeVar

from dandy import config
from dandy.core.type_vars import ModelType
from dandy.llm.service import Service
from dandy.llm.service.ollama.prompts import ollama_system_prompt
from dandy.llm.service.settings import ServiceSettings
from dandy.llm.prompt import Prompt


class OllamaService(Service):
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
                'generate',
            ],
            query_parameters=None
        )

    @classmethod
    def process_prompt_to_model_object(cls, prompt: Prompt, model: Type[ModelType]) -> ModelType:
        print(ollama_system_prompt(prompt, model).to_str())

        body = {
            'model': 'llama3.1',
            'prompt': ollama_system_prompt(prompt, model).to_str(),
            'stream': False,
            'format': 'json',
            'temperature': 0.5
        }

        response = cls.post_request(body)

        print(response['response'])

        return model.model_validate_json(response['response'])

