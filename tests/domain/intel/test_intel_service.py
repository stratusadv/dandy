from unittest import TestCase

from dandy.application.bot.bot import Bot


class TestIntelService(TestCase):
    def test_reset_callable(self):
        bot = Bot()

        bot.intel.reset()
