from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestBot(TestCase):
    def test_bot_import(self):
        from dandy.bot import BaseBot
        self.assertTrue(type(BaseBot) is type(BaseProcessor))
