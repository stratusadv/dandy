from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestBot(TestCase):
    def test_bot_import(self):
        from dandy.bot import Bot
        self.assertTrue(type(Bot) is type(BaseProcessor))

    def test_llm_bot_import(self):
        from dandy.llm.bot import LlmBot
        self.assertTrue(type(LlmBot) is type(BaseProcessor))

