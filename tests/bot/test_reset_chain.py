from unittest import TestCase, mock

from dandy.bot.bot import Bot


class TestBotResetChain(TestCase):
    def test_bot_reset(self):
        bot = Bot()

        bot._LlmService_instance = mock.Mock()
        bot._HttpService_instance = mock.Mock()
        bot._IntelService_instance = mock.Mock()
        bot._DecoderService_instance = mock.Mock()
        bot._FileService_instance = mock.Mock()

        bot.reset()

        bot._LlmService_instance.reset.assert_called_once()
        bot._HttpService_instance.reset.assert_called_once()
        bot._IntelService_instance.reset.assert_called_once()
        bot._FileService_instance.reset.assert_called_once()

        bot._DecoderService_instance.reset.assert_not_called()
