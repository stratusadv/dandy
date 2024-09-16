from unittest import TestCase

from dandy.llm.prompt import Prompt


class TestPrompt(TestCase):
    def setUp(self):
        self.prompt = Prompt()

    def test_prompt_text(self):
        self.prompt.text(
            text='Hello World',
            label='Greeting',
            triple_quote=True
        )

        self.assertTrue(True)

