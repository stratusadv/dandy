import os
from unittest import TestCase

from dandy import config
from dandy.llm.tests.models import PersonModel
from dandy.llm.tests.prompts import cartoon_character_prompt

TEST_COUNT = 10


class TestLlmService(TestCase):
    def setUp(self):
        config.llm.add_service(
            name='ollama',
            url=os.getenv("OLLAMA_URL"),
            port=int(os.getenv("OLLAMA_PORT", 11434)),
            model='llama3.1',
        )

    def test_get_request(self):
        for _ in range(TEST_COUNT):
            print(f'test iteration {_+1} of {TEST_COUNT}')
            person = config.llm.active_service.process_prompt_to_model_object(cartoon_character_prompt(), PersonModel)

            # print(person.model_dump_json(indent=4))
            self.assertNotEqual(person.first_name, None)
