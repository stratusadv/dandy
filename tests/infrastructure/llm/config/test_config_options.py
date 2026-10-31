from unittest import TestCase

from dandy.domain.request.exceptions import LlmCriticalError
from dandy.domain.request.options import LlmOptions


class TestLlmOptions(TestCase):
    def setUp(self):
        self.config_options = LlmOptions(temperature=1.0, top_p=0.5, max_tokens=100)

    def test_openai_options_are_accepted(self) -> None:
        options = LlmOptions(
            frequency_penalty=0.1,
            logit_bias={'1234': 3},
            logprobs=True,
            max_completion_tokens=200,
            n=1,
            presence_penalty=0.2,
            response_format={'type': 'json_object'},
            seed=42,
            stop=['\n'],
            temperature=0.7,
            top_logprobs=5,
            top_p=0.9,
        )

        self.assertEqual(options.logit_bias, {'1234': 3})
        self.assertTrue(options.logprobs)
        self.assertEqual(options.max_completion_tokens, 200)
        self.assertEqual(options.n, 1)
        self.assertEqual(options.response_format, {'type': 'json_object'})
        self.assertEqual(options.seed, 42)
        self.assertEqual(options.stop, ['\n'])
        self.assertEqual(options.top_logprobs, 5)

    def test_out_of_range_temperature_raises(self) -> None:
        with self.assertRaises(LlmCriticalError):
            LlmOptions(temperature=3.0)

    def test_out_of_range_penalty_raises(self) -> None:
        with self.assertRaises(LlmCriticalError):
            LlmOptions(frequency_penalty=-3.0)

    def test_negative_n_raises(self) -> None:
        with self.assertRaises(LlmCriticalError):
            LlmOptions(n=0)

    def test_prompt_retry_count_is_not_a_declared_option(self) -> None:
        self.assertNotIn('prompt_retry_count', LlmOptions.model_fields)
