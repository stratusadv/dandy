from unittest import TestCase, mock

from dandy.llm.conf import llm_configs
from dandy.llm.exceptions import LlmRecoverableException
from dandy.llm.intel import DefaultLlmIntel
from tests.llm.decorators import run_llm_configs


class TestService(TestCase):
    @run_llm_configs()
    def test_process_prompt_to_intel(self, llm_config: str):
        response = llm_configs[llm_config].service.process_prompt_to_intel(
            prompt='Hello, World!',
            intel_class=DefaultLlmIntel,
        )

        self.assertTrue(response.text != '' and response.text is not None)

    @mock.patch('dandy.core.http.service.BaseHttpService.post_request')
    def test_pydantic_validation_error_retry_process_prompt_to_intel(self, mock_post_request: mock.MagicMock):
        mock_post_request.return_value = {
                'message': {
                    'content': '{"invalid_key": "Hello, World!"}',
                }
            }

        with self.assertRaises(LlmRecoverableException):
            response = llm_configs['DEFAULT'].service.process_prompt_to_intel(
                prompt='Hello, World!',
                intel_class=DefaultLlmIntel,
            )
