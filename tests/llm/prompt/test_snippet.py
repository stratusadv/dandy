from unittest import TestCase
from dandy.llm.prompt.snippet import TextSnippet


class TestSnippet(TestCase):
    def test_text_snippet(self):
        new_snippet = TextSnippet(text='Hello World')

        self.assertEqual(new_snippet.to_str(), 'Hello World\n')
