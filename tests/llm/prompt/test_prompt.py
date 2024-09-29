from unittest import TestCase
from dandy.llm import Prompt

class TestPrompt(TestCase):
    def test_prompt(self):
        new_prompt = (
            Prompt()
            .text('Hello World')
        )

        self.assertEqual(new_prompt.to_str(), 'Hello World\n')
