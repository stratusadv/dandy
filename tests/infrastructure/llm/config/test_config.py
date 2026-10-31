from unittest import TestCase, mock

from dandy.infrastructure.llm.config import LlmConfig
from dandy.shared.settings import settings


class TestLlmConfigContextSize(TestCase):
    def test_default_config_reads_context_size(self) -> None:
        config = LlmConfig('DEFAULT')

        self.assertEqual(config.context_size, 65536)

    def test_context_size_inherits_from_default(self) -> None:
        config = LlmConfig('THINKING')

        self.assertEqual(config.context_size, 65536)


class TestLlmConfigOptions(TestCase):
    def test_max_completion_tokens_comes_from_options(self) -> None:
        config = LlmConfig('DEFAULT')
        request_body = config.generate_request_body()

        self.assertEqual(request_body.max_completion_tokens, config.options.max_completion_tokens)

    def test_max_completion_tokens_override_is_sent(self) -> None:
        config = LlmConfig('DEFAULT')
        config.options.max_completion_tokens = 1234

        request_body = config.generate_request_body()

        self.assertEqual(request_body.max_completion_tokens, 1234)

    def test_prompt_retry_count_defaults_to_two(self) -> None:
        config = LlmConfig('DEFAULT')

        self.assertEqual(config.prompt_retry_count, 2)

    def test_prompt_retry_count_reads_from_config_settings(self) -> None:
        original_configs = settings.LLM_CONFIGS
        new_configs = dict(original_configs)
        new_configs['DEFAULT'] = dict(original_configs['DEFAULT'])
        new_configs['DEFAULT']['PROMPT_RETRY_COUNT'] = 5

        with mock.patch.object(settings, 'LLM_CONFIGS', new_configs):
            config = LlmConfig('DEFAULT')

        self.assertEqual(config.prompt_retry_count, 5)

    def test_prompt_retry_count_is_not_an_llm_option(self) -> None:
        config = LlmConfig('DEFAULT')

        self.assertNotIn('prompt_retry_count', config.options.model_dump())
