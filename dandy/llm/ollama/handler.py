import json
from typing import Type, TypeVar

from dandy import config
from dandy.llm.handler import Handler
from dandy.llm.ollama.prompts import ollama_system_prompt
from dandy.llm.prompt import Prompt
from dandy.schema import Schema


SchemaType = TypeVar('SchemaType', bound=Schema)


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
    def setup(cls):
        cls.url = config.ollama.url
        cls.port = config.ollama.port
        cls.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        cls.path_parameters = [
            'api',
            'generate',
        ]
        cls.query_parameters = None
