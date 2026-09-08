from unittest import TestCase, mock

from dandy.conf import settings
from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.intel.intel import BaseIntel, DefaultIntel
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.bot.bot import Bot
from tests.consts import live_llm_test
from tests.llm.decorators import run_llm_configs


class LlmDefaultIntel(BaseIntel):
    text: str


class TestService(TestCase):
    @run_llm_configs()
    def test_process_prompt_to_intel(self, llm_config: str):
        new_llm_config = llm_config

        class ConfigBot(Bot):
            llm_config = new_llm_config

        response = ConfigBot().llm.prompt_to_intel(
            prompt='Hello, World!', intel_class=LlmDefaultIntel
        )

        self.assertTrue(response.text != '' and response.text is not None)

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_pydantic_validation_error_retry_process_prompt_to_intel(
        self, mock_post_request: mock.MagicMock
    ):
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200,
            json_data={'choices': [{'message': {'content': '{"invalid_key": "Hello, World!"}'}}]},
        )

        with self.assertRaises(LlmRecoverableError):
            response = Bot().llm.prompt_to_intel(
                prompt='Hello, World!', intel_class=LlmDefaultIntel
            )

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_plain_text_response_is_stored_in_default_intel(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200,
            json_data={'choices': [{'message': {'content': 'Just a plain text answer.'}}]},
        )

        response = Bot().llm.prompt_to_intel(
            prompt='Explain something in plain text.', intel_class=DefaultIntel
        )

        self.assertEqual(response.text, 'Just a plain text answer.')

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_fenced_json_response_with_narration_is_validated_for_default_intel(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200,
            json_data={
                'choices': [
                    {
                        'message': {
                            'content': (
                                'Let me check the git status.\n\n'
                                '```javascript\n'
                                '{\n'
                                '  "text": "The working tree is clean."\n'
                                '}\n'
                                '```'
                            )
                        }
                    }
                ]
            },
        )

        response = Bot().llm.prompt_to_intel(
            prompt='Check the git status.', intel_class=DefaultIntel
        )

        self.assertEqual(response.text, 'The working tree is clean.')

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_fenced_json_response_is_validated_for_structured_intel(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200,
            json_data={
                'choices': [
                    {'message': {'content': '```json\n{"text": "Parsed from a fence."}\n```'}}
                ]
            },
        )

        response = Bot().llm.prompt_to_intel(prompt='Say hello.', intel_class=LlmDefaultIntel)

        self.assertEqual(response.text, 'Parsed from a fence.')

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_code_fence_that_is_not_the_answer_keeps_raw_default_fallback(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        content = 'Here is a sample config:\n```json\n{"nested": true}\n```\nEnjoy.'

        mock_post_request.return_value = HttpResponseIntel(
            status_code=200, json_data={'choices': [{'message': {'content': content}}]}
        )

        response = Bot().llm.prompt_to_intel(
            prompt='Show me a sample config.', intel_class=DefaultIntel
        )

        self.assertEqual(response.text, content)

    def test_prompt_to_intel_with_no_prompt_argument(self):
        with self.assertRaises(LlmCriticalError):
            _ = Bot().llm.prompt_to_intel()

    @live_llm_test
    def test_prompt_to_intel_with_message_and_no_prompt_argument(self):
        bot = Bot()

        bot.llm.messages.add_message(role='user', text='Hello!')

        _ = bot.llm.prompt_to_intel()
