from unittest import TestCase
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1


class TestConfig(TestCase):
    def test_ollama_config_request_body(self):
        self.assertEqual(
        OLLAMA_LLAMA_3_1.generate_request_body(
            temperature=OLLAMA_LLAMA_3_1.temperature,
            seed=OLLAMA_LLAMA_3_1.seed,
        ).get_temperature(), OLLAMA_LLAMA_3_1.temperature)
