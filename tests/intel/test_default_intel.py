from unittest import TestCase

from dandy.intel.intel import BaseIntel


class TestDefaultIntel(TestCase):

    def test_default_intel_text(self):
        class DefaultLlmIntel(BaseIntel):
            text: str

        test_text = 'Test Default Intel'

        default_intel = DefaultLlmIntel(text=test_text)

        self.assertEqual(default_intel.text, test_text)
