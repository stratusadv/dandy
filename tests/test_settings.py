from unittest import TestCase

from dandy.conf import settings
from dandy import default_settings

class TestSettings(TestCase):
    def test_settings(self):
        self.assertEqual(
            default_settings.DEFAULT_LLM_PROMPT_RETRY_COUNT,
            settings.DEFAULT_LLM_PROMPT_RETRY_COUNT
        )

