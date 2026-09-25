from unittest import TestCase

from dandy.shared.exceptions import DandyCriticalError, DandyRecoverableError


class TestBotExceptions(TestCase):
    def test_bot_exception_import(self):
        from dandy.application.bot.exceptions import BotCriticalError, BotRecoverableError

        self.assertTrue(type(BotCriticalError) is type(DandyCriticalError))
        self.assertTrue(type(BotRecoverableError) is type(DandyRecoverableError))

