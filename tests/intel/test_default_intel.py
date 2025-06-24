from unittest import TestCase

from dandy.llm import DefaultLlmIntel


class TestDefaultIntel(TestCase):

    def test_default_intel_text(self):
        test_text = 'Test Default Intel'

        default_intel = DefaultLlmIntel(text=test_text)

        self.assertEqual(default_intel.text, test_text)
