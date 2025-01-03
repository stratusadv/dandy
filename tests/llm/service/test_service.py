from unittest import TestCase

from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1_8B


class TestService(TestCase):
    def test_assistant_prompt(self):
        str_response = OLLAMA_LLAMA_3_1_8B.service.assistant_str_prompt_to_str('Hello, World!')

        self.assertTrue(str_response != '' and str_response is not None)