import os
from unittest import TestCase

from dandy.llm.service.ollama.service import OllamaService
from dandy import config

from dandy.llm.tests.models import PersonModel
from dandy.llm.tests.prompts import cartoon_character_prompt


class TestOllamaHandler(TestCase):
    def setUp(self):
        config.setup_ollama(
            url=os.getenv("OLLAMA_URL"),
            port=int(os.getenv("OLLAMA_PORT", 11434))
        )

    def test_get_request(self):
        person = OllamaService.process_prompt_to_model_object(cartoon_character_prompt(), PersonModel)

        print(person.model_dump_json(indent=4))

        self.assertNotEqual(person.first_name, None)
