from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestBot(TestCase):
    def test_bot_import(self):
        from dandy.processor.bot.bot import Bot
        self.assertTrue(type(Bot) is type(BaseProcessor))
