from unittest import TestCase
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1_8B


class TestRequest(TestCase):
    def test_ollama_config_request_body(self):
        request_body = OLLAMA_LLAMA_3_1_8B.generate_request_body(
            temperature=OLLAMA_LLAMA_3_1_8B.temperature,
            seed=OLLAMA_LLAMA_3_1_8B.seed,
        )

        request_body.add_message(
            'system',
            'You are a helpful assistant.'
        )

        self.assertEqual(request_body.messages[0].content, 'You are a helpful assistant.')

