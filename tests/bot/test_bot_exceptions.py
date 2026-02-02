from unittest import TestCase

from dandy.core.exceptions import DandyCriticalError, DandyRecoverableError


class TestBotExceptions(TestCase):
    def test_bot_exception_import(self):
        from dandy.bot.exceptions import BotCriticalError, BotRecoverableError

        self.assertTrue(type(BotCriticalError) is type(DandyCriticalError))
        self.assertTrue(type(BotRecoverableError) is type(DandyRecoverableError))

