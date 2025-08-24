from unittest import TestCase

from dandy.core.processor.processor import BaseProcessor


class TestBot(TestCase):
    def test_bot_import(self):
        from dandy.bot import Bot
        self.assertTrue(type(Bot) is type(BaseProcessor))
