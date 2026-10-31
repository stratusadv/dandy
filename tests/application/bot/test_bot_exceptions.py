from unittest import TestCase

from dandy.shared.exceptions import DandyCriticalError, DandyError, DandyRecoverableError
from dandy.application.bot.exceptions import BotCriticalError, BotRecoverableError


class TestBotExceptions(TestCase):
    def test_bot_critical_error_is_a_dandy_critical_error(self) -> None:
        error = BotCriticalError('boom')

        self.assertIsInstance(error, DandyCriticalError)
        self.assertIsInstance(error, DandyError)
        self.assertNotIsInstance(error, DandyRecoverableError)
        self.assertEqual(str(error), 'boom')

    def test_bot_recoverable_error_is_a_dandy_recoverable_error(self) -> None:
        error = BotRecoverableError('retry me')

        self.assertIsInstance(error, DandyRecoverableError)
        self.assertIsInstance(error, DandyError)
        self.assertNotIsInstance(error, DandyCriticalError)
        self.assertEqual(str(error), 'retry me')

    def test_dandy_error_catches_bot_exceptions(self) -> None:
        with self.assertRaises(DandyError):
            raise BotCriticalError('caught as a dandy error')

        with self.assertRaises(DandyError):
            raise BotRecoverableError('caught as a dandy error')
