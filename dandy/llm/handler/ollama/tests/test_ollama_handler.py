import os
from unittest import TestCase

from dandy.llm.handler.ollama.handler import OllamaHandler
from dandy import config

from dandy.schema.tests.schemas import PersonSchema
from dandy.llm.tests.prompts import cartoon_character_prompt

class TestOllamaHandler(TestCase):
    def setUp(self):
        config.setup_ollama(
            url=os.getenv("OLLAMA_URL"),
            port=int(os.getenv("OLLAMA_PORT"))
        )

    def test_get_request(self):
        person = OllamaHandler.process_prompt_to_schema(cartoon_character_prompt(), PersonSchema)
        print(PersonSchema)
        self.assertNotEqual(person.first_name, None)
