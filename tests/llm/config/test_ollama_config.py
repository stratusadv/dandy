import os
from unittest import TestCase

from dandy.llm.config import OllamaLlmConfig
from dandy.llm.exceptions import LlmException
from example.pirate.intelligence.configs import OLLAMA_LLAMA_3_1


class TestConfig(TestCase):
    def test_ollama_config_request_body(self):
        self.assertEqual(
            OLLAMA_LLAMA_3_1.generate_request_body(
                temperature=OLLAMA_LLAMA_3_1.temperature,
                seed=OLLAMA_LLAMA_3_1.seed,
            ).get_temperature(), OLLAMA_LLAMA_3_1.temperature)

    def test_ollama_max_completion_tokens(self):
        ollama_config = OllamaLlmConfig(
            host=os.getenv("OLLAMA_HOST"),
            port=int(os.getenv("OLLAMA_PORT", 11434)),
            model='llama3.1:8b-instruct-q4_K_M',
            max_completion_tokens=3,
            temperature=1.0,
            prompt_retry_count=3,
        )

        response = ollama_config.service.assistant_str_prompt_to_str('Tell me what you think about hamburgers?')
        self.assertTrue(len(response) <= 16)

    def test_ollama_config_empty_host(self):
        try:
            _ = OllamaLlmConfig(
                host='',
                port=123,
                model='model_mc_modelface',
                temperature=1.0,
                prompt_retry_count=3,
            )
        except LlmException:
            self.assertTrue(True)

    def test_ollama_config_empty_port(self):
        try:
            _ = OllamaLlmConfig(
                host='localhost',
                port=0,
                model='model_mc_modelface',
                temperature=1.0,
                prompt_retry_count=3,
            )
        except LlmException:
            self.assertTrue(True)

    def test_ollama_config_empty_model(self):
        try:
            _ = OllamaLlmConfig(
                host='localhost',
                port=123,
                model='',
                temperature=1.0,
                prompt_retry_count=3,
            )
        except LlmException:
            self.assertTrue(True)
