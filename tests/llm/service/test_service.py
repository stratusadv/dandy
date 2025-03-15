from unittest import TestCase

from dandy.llm.conf import llm_configs


class TestService(TestCase):
    def run_assistant_prompt(self, llm_config_name: str):
        str_response = llm_configs[llm_config_name].service.assistant_str_prompt_to_str('Hello, World!')

        self.assertTrue(str_response != '' and str_response is not None)

    def test_ollama_service(self):
        self.run_assistant_prompt('LLAMA_3_1_8B')


    def test_openai_service(self):
        self.run_assistant_prompt('GPT_4o_MINI')