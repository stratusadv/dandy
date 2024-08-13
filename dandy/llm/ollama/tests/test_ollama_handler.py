import os
from unittest import TestCase

from dandy.llm.ollama.handler import OllamaHandler
from dandy import config


class TestOllamaHandler(TestCase):
    def setUp(self):
        config.setup_ollama(
            address=os.getenv("OLLAMA_ADDRESS"),
            port=int(os.getenv("OLLAMA_PORT"))
        )

        self.handler = OllamaHandler()

    def test_create_connection(self):
        handler = OllamaHandler()

