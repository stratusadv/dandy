from unittest import TestCase
from dandy.llm import LlmConfigOptions
from dandy.conf import settings


class TestConfigOptions(TestCase):
    def setUp(self):
        self.config_options = LlmConfigOptions(
            temperature=1.0,
            max_input_tokens=1000,
            max_output_tokens=None,
            prompt_retry_count=3,
            randomize_seed=True,
        )

    def test_merge_to_copy(self):
        new_config_options = LlmConfigOptions(
            prompt_retry_count=8,
            randomize_seed=False,
        )

        merged_config_options = new_config_options.merge_to_copy(self.config_options)

        self.assertEqual(merged_config_options.prompt_retry_count, 8)
        self.assertEqual(merged_config_options.randomize_seed, False)
        self.assertEqual(merged_config_options.temperature, 1.0)

    def test_default_settings(self):
        self.assertEqual(self.config_options.max_output_tokens, settings.DEFAULT_LLM_MAX_OUTPUT_TOKENS)

    def test_random_seed(self):
        self.assertTrue(0 <= self.config_options.seed, 2**63 - 1)