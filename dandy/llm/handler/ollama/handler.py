import json
from typing import Type, TypeVar

from dandy import config
from dandy.llm.handler import Handler
from dandy.llm.handler.ollama.prompts import ollama_system_prompt
from dandy.llm.handler.settings import HandlerSettings
from dandy.llm.prompt import Prompt
from dandy.schema.type_vars import SchemaType


class OllamaHandler(Handler):
    @classmethod
    def process_prompt_to_schema(cls, prompt: Prompt, schema_class: Type[SchemaType]) -> SchemaType:
        body = {
            'model': 'llama3.1',
            'prompt': ollama_system_prompt(prompt, schema_class).to_str(),
            'stream': False,
            'format': 'json',
        }

        response = cls.post_request(body)

        return schema_class.from_dict(json.loads(response['response']))

    @classmethod
    def get_settings(cls) -> HandlerSettings:
        return HandlerSettings(
            url=config.ollama.url,
            port=config.ollama.port,
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
