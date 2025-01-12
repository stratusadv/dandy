from unittest import TestCase

from dandy.cli.llm.assistant.assistant import assistant
from dandy.llm.conf import llm_configs


class TestAssistant(TestCase):
    def test_assistant(self):
        assistant(
            llm_config=llm_configs.DEFAULT,
            user_prompt='What is something fun you can do with the python coding language?'
        )

        self.assertTrue(True)
