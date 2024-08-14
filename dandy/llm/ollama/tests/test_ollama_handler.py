import os
from unittest import TestCase

from dandy.llm.ollama.handler import OllamaHandler
from dandy import config


class TestOllamaHandler(TestCase):
    def setUp(self):
        config.setup_ollama(
            url=os.getenv("OLLAMA_URL"),
            port=int(os.getenv("OLLAMA_PORT"))
        )

        self.handler = OllamaHandler()

    def test_get_request(self):
        response = self.handler.post_request({
            "model": "llama3.1",
            "prompt": "Why is the sky blue?",
            "stream": False
        })
        print(response)

    def test_create_connection(self):
        handler = OllamaHandler()
