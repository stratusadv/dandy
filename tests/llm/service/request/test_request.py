from unittest import TestCase

from dandy.llm.conf import llm_configs

class TestRequest(TestCase):
    def test_ollama_config_request_body(self):
        request_body = llm_configs.LLAMA_3_1_8B.generate_request_body(
            temperature=llm_configs.LLAMA_3_1_8B.options.temperature,
            seed=llm_configs.LLAMA_3_1_8B.options.seed,
        )

        request_body.add_message(
            'system',
            'You are a helpful assistant.'
        )

        self.assertEqual(request_body.messages[0].content, 'You are a helpful assistant.')

