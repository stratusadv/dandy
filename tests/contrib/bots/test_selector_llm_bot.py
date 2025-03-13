from unittest import TestCase

from dandy.core.processor.processor import BaseProcessor


class TestChoiceLlmBot(TestCase):
    def test_selector_llm_bot_import(self):
        from dandy.contrib.llm.bots.selector_llm_bot import SelectorLlmBot
        self.assertTrue(type(SelectorLlmBot) is type(BaseProcessor))


