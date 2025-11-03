from unittest import TestCase

from dandy.processor.bot.bot import Bot


class TestLlmReset(TestCase):
    def test_llm_service_reset(self):
        bot = Bot()

        self.assertEqual(len(bot.llm.messages), 1)

        bot.llm.add_message('user', 'Hello!')
        self.assertEqual(len(bot.llm.messages), 2)

        bot.llm.reset_service()
        self.assertEqual(len(bot.llm.messages), 1)

    def test_llm_reset_messages_alias_behavior(self):
        bot = Bot()

        bot.llm.add_message('user', 'A')
        self.assertEqual(len(bot.llm.messages), 2)

        bot.llm.reset_messages()
        self.assertEqual(len(bot.llm.messages), 0)

