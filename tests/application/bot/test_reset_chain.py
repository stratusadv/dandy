from unittest import TestCase, mock

from dandy.application.bot.bot import Bot


class TestBotResetChain(TestCase):
    def test_bot_reset(self) -> None:
        bot = Bot()

        bot._LlmService_instance = mock.Mock()
        bot._HttpService_instance = mock.Mock()
        bot._IntelService_instance = mock.Mock()
        bot._DecisionService_instance = mock.Mock()
        bot._FileService_instance = mock.Mock()

        bot.reset()

        bot._LlmService_instance.reset.assert_called_once()
        bot._HttpService_instance.reset.assert_called_once()
        bot._IntelService_instance.reset.assert_called_once()
        bot._FileService_instance.reset.assert_called_once()

        bot._DecisionService_instance.reset.assert_not_called()

    def test_llm_sub_mixin_resets(self) -> None:
        bot = Bot()

        bot.llm.decision.reset()
        bot.llm.tools.reset()
        bot.llm.diligence.reset()

        self.assertFalse(bot.llm.diligence.post_handler.is_activated)
        self.assertFalse(bot.llm.diligence.pre_handler.is_activated)
