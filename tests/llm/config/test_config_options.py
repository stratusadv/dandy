from unittest import TestCase
from dandy.llm.options import LlmOptions
from dandy.conf import settings


class TestConfigOptions(TestCase):
    def setUp(self):
        self.config_options = LlmOptions(
            temperature=1.0,
            max_completion_tokens=None,
            prompt_retry_count=3,
        )

    # def test_merge_to_copy(self):
    #     new_config_options = LlmOptions(
    #         prompt_retry_count=8,
    #     )
    #
    #     merged_config_options = new_config_options.merge_to_copy(self.config_options)
    #
    #     self.assertEqual(merged_config_options.prompt_retry_count, 8)
    #     self.assertEqual(merged_config_options.randomize_seed, False)
    #     self.assertEqual(merged_config_options.temperature, 1.0)

