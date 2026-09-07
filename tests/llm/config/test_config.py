from unittest import TestCase

from dandy.llm.config import LlmConfig


class TestLlmConfigContextSize(TestCase):
    def test_default_config_reads_context_size(self) -> None:
        config = LlmConfig('DEFAULT')

        self.assertEqual(config.context_size, 65536)

    def test_max_completion_tokens_is_derived_from_context_size(self) -> None:
        config = LlmConfig('DEFAULT')

        self.assertEqual(config.max_completion_tokens, 16384)

    def test_context_size_inherits_from_default(self) -> None:
        config = LlmConfig('THINKING')

        self.assertEqual(config.context_size, 65536)
        self.assertEqual(config.max_completion_tokens, 16384)

    def test_request_body_gets_derived_max_completion_tokens(self) -> None:
        request_body = LlmConfig('DEFAULT').generate_request_body()

        self.assertEqual(request_body.max_completion_tokens, 16384)

    def test_max_completion_tokens_is_not_an_option(self) -> None:
        config = LlmConfig('DEFAULT')

        self.assertNotIn('max_completion_tokens', config.options.model_dump())
