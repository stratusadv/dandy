from unittest import TestCase, mock

from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from dandy.llm.exceptions import LlmRecoverableException, LlmCriticalException
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
            prompt='Hello, World!',
            intel_class=LlmDefaultIntel,
        )

        self.assertTrue(response.text != '' and response.text is not None)

    @mock.patch('dandy.http.connector.HttpConnector.request_to_response')
    def test_pydantic_validation_error_retry_process_prompt_to_intel(self, mock_post_request: mock.MagicMock):
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200,
            json_data={
                'message': {
                    'content': '{"invalid_key": "Hello, World!"}',
                }
            }
        )

        with self.assertRaises(LlmRecoverableException):
            response = Bot().llm.prompt_to_intel(
                prompt='Hello, World!',
                intel_class=LlmDefaultIntel,
            )

    def test_prompt_to_intel_with_no_prompt_argument(self):
        with self.assertRaises(LlmCriticalException):
            _ = Bot().llm.prompt_to_intel()

    def test_prompt_to_intel_with_message_and_no_prompt_argument(self):
        bot = Bot()

        bot.llm.add_message('user', 'Hello!')

        _ = bot.llm.prompt_to_intel()
