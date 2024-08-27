import json
from typing import Type, TypeVar, Optional

from dandy import config
from dandy.core.type_vars import ModelType
from dandy.llm.service import Service
from dandy.llm.service.ollama.prompts import ollama_system_model_prompt, ollama_user_prompt
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

        body = {
            'model': 'llama3.1',
            'messages': [
                {
                    'role': 'system',
                    'content': ollama_system_model_prompt(
                        model=model,
                        prefix_system_prompt=prefix_system_prompt
                    ).to_str(),
                },
                {
                    'role': 'user',
                    'content': ollama_user_prompt(prompt).to_str(),
                }
            ],
            'stream': False,
            'format': 'json',
            'temperature': 0.5
        }

        print(json.dumps(body, indent=4))

        response = cls.post_request(body)

        return model.model_validate_json(response['message']['content'])
