from unittest import TestCase

from dandy.handler.handler import Handler


class TestBot(TestCase):
    def test_bot_import(self):
        from dandy.bot import Bot
        self.assertTrue(type(Bot) is type(Handler))

    def test_llm_bot_import(self):
        from dandy.bot import LlmBot
        self.assertTrue(type(LlmBot) is type(Handler))

