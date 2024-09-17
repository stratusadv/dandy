import os
from unittest import TestCase

from dandy.llm.tests.models import PersonModel
from dandy.llm.tests.prompts import cartoon_character_prompt
from dandy.llm.tests.configs import OLLAMA_LLAMA_3_1, OPENAI_GPT_3_5_TURBO

TEST_COUNT = 1


class TestLlmService(TestCase):
    def test_ollama_request(self):
        for _ in range(TEST_COUNT):
            print(f'test iteration {_+1} of {TEST_COUNT}')
            person = OLLAMA_LLAMA_3_1.service.process_prompt_to_model_object(cartoon_character_prompt(), PersonModel)

            print(person.model_dump_json(indent=4))
            self.assertNotEqual(person.first_name, None)

    # def test_openai_request(self):
    #     for _ in range(TEST_COUNT):
    #         print(f'test iteration {_+1} of {TEST_COUNT}')
    #         person = OPENAI_GPT_3_5_TURBO.service.process_prompt_to_model_object(cartoon_character_prompt(), PersonModel)
    #
    #         print(person.model_dump_json(indent=4))
    #         self.assertNotEqual(person.first_name, None)
