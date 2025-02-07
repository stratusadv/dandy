from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestLlmBot(TestCase):
    def test_llm_bot_import(self):
        from dandy.llm.bot import LlmBot
        self.assertTrue(type(LlmBot) is type(BaseProcessor))

