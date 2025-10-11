from unittest import TestCase

from dandy.core.exceptions import DandyCriticalException, DandyRecoverableException


class TestBotExceptions(TestCase):
    def test_bot_exception_import(self):
        from dandy.processor.bot.exceptions import BotCriticalException, BotRecoverableException

        self.assertTrue(type(BotCriticalException) is type(DandyCriticalException))
        self.assertTrue(type(BotRecoverableException) is type(DandyRecoverableException))

