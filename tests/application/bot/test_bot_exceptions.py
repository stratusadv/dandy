from unittest import TestCase

from dandy.shared.exceptions import DandyError, DandyExternalError, DandyUsageError
from dandy.application.bot.exceptions import BotError


class TestBotExceptions(TestCase):
    def test_bot_error_is_a_dandy_usage_error(self) -> None:
        error = BotError('boom')

        self.assertIsInstance(error, DandyUsageError)
        self.assertIsInstance(error, DandyError)
        self.assertNotIsInstance(error, DandyExternalError)
        self.assertEqual(str(error), 'boom')

    def test_dandy_error_catches_bot_error(self) -> None:
        with self.assertRaises(DandyError):
            raise BotError('caught as a dandy error')
