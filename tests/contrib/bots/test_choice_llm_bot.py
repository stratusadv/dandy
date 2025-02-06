from tokenize import Single
from unittest import TestCase

from dandy.processor.processor import BaseProcessor


class TestChoiceLlmBot(TestCase):
    def test_single_choice_llm_bot_import(self):
        from dandy.contrib.llm.bots import SingleChoiceLlmBot
        self.assertTrue(type(SingleChoiceLlmBot) is type(BaseProcessor))

    def test_multiple_choice_llm_bot_import(self):
        from dandy.contrib.llm.bots import MultipleChoiceLlmBot
        self.assertTrue(type(MultipleChoiceLlmBot) is type(BaseProcessor))

