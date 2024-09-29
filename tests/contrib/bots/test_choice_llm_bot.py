from tokenize import Single
from unittest import TestCase

from dandy.handler.handler import Handler


class TestChoiceLlmBot(TestCase):
    def test_single_choice_llm_bot_import(self):
        from dandy.contrib.bots import SingleChoiceLlmBot
        self.assertTrue(type(SingleChoiceLlmBot) is type(Handler))

    def test_multiple_choice_llm_bot_import(self):
        from dandy.contrib.bots import MultipleChoiceLlmBot
        self.assertTrue(type(MultipleChoiceLlmBot) is type(Handler))

