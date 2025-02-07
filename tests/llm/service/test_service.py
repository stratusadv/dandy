from unittest import TestCase

from dandy.llm.conf import llm_configs


class TestService(TestCase):
    def test_assistant_prompt(self):
        str_response = llm_configs.LLAMA_3_1_8B.service.assistant_str_prompt_to_str('Hello, World!')

        self.assertTrue(str_response != '' and str_response is not None)