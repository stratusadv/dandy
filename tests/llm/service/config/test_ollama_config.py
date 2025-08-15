import os
from unittest import TestCase

from dandy.llm.intel import DefaultLlmIntel
from dandy.llm.config import OllamaLlmConfig
from dandy.llm.exceptions import LlmCriticalException
from dandy.llm.conf import llm_configs

class TestConfig(TestCase):
    def test_ollama_config_request_body(self):
        self.assertEqual(
            llm_configs.DEFAULT.generate_request_body(
                temperature=llm_configs.DEFAULT.options.temperature,
                seed=llm_configs.DEFAULT.options.seed,
            ).get_temperature(), llm_configs.DEFAULT.options.temperature)

    def test_ollama_max_completion_tokens(self):
        ollama_config = OllamaLlmConfig(
            host=os.getenv("OLLAMA_HOST"),
            port=int(os.getenv("OLLAMA_PORT", 11434)),
            api_key=os.getenv("OLLAMA_API_KEY"),
            model='llama3.1:8b-instruct-q4_K_M',
            max_output_tokens=10,
            temperature=1.0,
            prompt_retry_count=3,
        )

        response = ollama_config.service.process_prompt_to_intel(
            prompt='Tell me what you think about hamburgers in one word?',
            intel_class=DefaultLlmIntel
        )

        self.assertTrue(len(response.text) <= 30)

    def test_ollama_config_empty_host(self):
        try:
            _ = OllamaLlmConfig(
                host='',
                port=123,
                model='model_mc_modelface',
                temperature=1.0,
                prompt_retry_count=3,
            )
        except LlmCriticalException:
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
        except LlmCriticalException:
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
        except LlmCriticalException:
            self.assertTrue(True)
