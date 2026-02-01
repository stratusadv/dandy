from unittest import TestCase

from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class TestBotExceptions(TestCase):
    def test_bot_exception_import(self):
        from dandy.processor.bot.exceptions import BotCriticalException, BotRecoverableException

        self.assertTrue(type(BotCriticalException) is type(DandyCriticalError))
        self.assertTrue(type(BotRecoverableException) is type(DandyRecoverableError))

