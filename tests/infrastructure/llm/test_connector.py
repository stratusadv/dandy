import copy
from unittest import TestCase, mock

from dandy.domain.intel.intel import BaseIntel, DefaultIntel
from dandy.domain.request.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.domain.message.message import MessageHistory
from dandy.domain.request.request import LlmRequestBody
from dandy.domain.tool.intel import ToolCallsIntel
from dandy.domain.tool.tool import BaseTool
from dandy.infrastructure.http.intel import HttpResponseIntel
from dandy.infrastructure.llm.config import LlmConfig
from dandy.infrastructure.llm.connector import LlmConnector, _extract_code_fence_json_body
from dandy.shared.settings import settings


class AnswerIntel(BaseIntel):
    text: str


class EchoTool(BaseTool):
    name = 'echo'
    description = 'Echo text back.'

    def handle(self, text: str) -> str:
        return text


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200, json_data={'choices': [{'message': {'content': content}}]}
    )


def tool_call_response(name: str, arguments: str, content: str | None = None) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': content,
                        'tool_calls': [
                            {'id': 'call_1', 'function': {'name': name, 'arguments': arguments}}
                        ],
                    }
                }
            ]
        },
    )


def message_roles(request_intel: LlmRequestBody) -> list[str]:
    return [message['role'] for message in request_intel.json_data['messages']]


class TestLlmConnector(TestCase):
    def make_connector(
        self, intel_class: type | None = None, system_prompt: str = 'System prompt.'
    ) -> LlmConnector:
        return LlmConnector(
            recorder_event_id='test-connector',
            llm_config=LlmConfig('DEFAULT'),
            intel_class=intel_class,
            system_prompt=system_prompt,
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_prepends_system_message_on_empty_history(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        connector = self.make_connector(intel_class=AnswerIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(result.text, 'Hello')
        self.assertEqual(
            message_roles(mock_post_request.call_args.kwargs['request_intel']), ['system', 'user']
        )
        self.assertEqual(connector.request_body.messages[0].text_content, 'System prompt.')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_appends_assistant_message_after_success(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        connector = self.make_connector(intel_class=AnswerIntel)

        connector.prompt_to_intel(prompt='Hi')

        roles = [message.role for message in connector.request_body.messages]
        self.assertEqual(roles, ['system', 'user', 'assistant'])
        self.assertEqual(connector.request_body.messages[2].text_content, '{"text": "Hello"}')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_does_not_duplicate_leading_system_message(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        history = MessageHistory()
        history.add_message(role='system', text='Custom system')
        history.add_message(role='user', text='Earlier question')

        connector = self.make_connector(intel_class=AnswerIntel)

        connector.prompt_to_intel(prompt='New question', message_history=history)

        roles = message_roles(mock_post_request.call_args.kwargs['request_intel'])
        self.assertEqual(roles, ['system', 'user', 'user'])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_prepends_system_when_history_has_no_system(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        history = MessageHistory()
        history.add_message(role='user', text='Earlier question')

        connector = self.make_connector(intel_class=AnswerIntel)

        connector.prompt_to_intel(prompt='New question', message_history=history)

        roles = message_roles(mock_post_request.call_args.kwargs['request_intel'])
        self.assertEqual(roles, ['system', 'user', 'user'])

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_attaches_falsy_empty_history_when_replacing(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        history = MessageHistory()
        connector = self.make_connector(intel_class=AnswerIntel)

        connector.prompt_to_intel(
            prompt='Hi', message_history=history, replace_message_history=True
        )

        self.assertIs(connector.request_body.messages, history)
        self.assertEqual([message.role for message in history], ['system', 'user', 'assistant'])

    def test_prompt_to_intel_requires_at_least_one_user_message(self) -> None:
        connector = self.make_connector(intel_class=AnswerIntel)

        with self.assertRaises(LlmCriticalError):
            connector.prompt_to_intel(prompt=None)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_fenced_json_response_is_validated(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response(
            'Here is the answer:\n```javascript\n{"text": "Fenced"}\n```'
        )

        connector = self.make_connector(intel_class=AnswerIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(result.text, 'Fenced')
        self.assertEqual(mock_post_request.call_count, 1)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_retries_when_fenced_body_fails_validation(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response('```javascript\n{"wrong": 1}\n```'),
            content_response('{"text": "Recovered"}'),
        ]

        connector = self.make_connector(intel_class=AnswerIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(result.text, 'Recovered')
        self.assertEqual(mock_post_request.call_count, 2)
        retry_message_text = (
            mock_post_request.call_args_list[1]
            .kwargs['request_intel']
            .json_data['messages'][-1]['content'][0]['text']
        )
        self.assertIn('The JSON in the response you provided was not valid', retry_message_text)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_ignores_non_json_code_fences(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response('```python\nprint("hello")\n```'),
            content_response('{"text": "Recovered"}'),
        ]

        connector = self.make_connector(intel_class=AnswerIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(result.text, 'Recovered')
        self.assertEqual(mock_post_request.call_count, 2)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_default_intel_falls_back_to_prose(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('Just some plain prose, no JSON here.')

        connector = self.make_connector(intel_class=DefaultIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertIsInstance(result, DefaultIntel)
        self.assertEqual(result.text, 'Just some plain prose, no JSON here.')
        self.assertEqual(mock_post_request.call_count, 1)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_default_intel_retries_on_wrong_key_json(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response('{"message": "not the right key"}'),
            content_response('{"text": "Recovered"}'),
        ]

        connector = self.make_connector(intel_class=DefaultIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(result.text, 'Recovered')
        self.assertEqual(mock_post_request.call_count, 2)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_default_intel_retries_on_empty_response(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [
            content_response(''),
            content_response('{"text": "Recovered"}'),
        ]

        connector = self.make_connector(intel_class=DefaultIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(result.text, 'Recovered')
        self.assertEqual(mock_post_request.call_count, 2)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_retry_exhaustion_raises_recoverable_error(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('still not valid')

        connector = self.make_connector(intel_class=AnswerIntel)

        with self.assertRaises(LlmRecoverableError) as context:
            connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(mock_post_request.call_count, 3)
        self.assertIn('after 2 attempts', str(context.exception))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_retry_exhaustion_with_zero_retry_count(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('still not valid')

        new_configs = copy.deepcopy(settings.LLM_CONFIGS)
        new_configs['DEFAULT']['PROMPT_RETRY_COUNT'] = 0

        with mock.patch.object(settings, 'LLM_CONFIGS', new_configs):
            connector = LlmConnector(
                recorder_event_id='test-connector',
                llm_config=LlmConfig('DEFAULT'),
                intel_class=AnswerIntel,
                system_prompt='System prompt.',
            )

            with self.assertRaises(LlmRecoverableError) as context:
                connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(mock_post_request.call_count, 1)
        self.assertIn('after 0 attempts', str(context.exception))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_sets_tools_and_clears_response_format(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        connector = self.make_connector(intel_class=AnswerIntel)

        connector.prompt_to_intel(prompt='Hi', tools=[EchoTool], tool_choice='auto')

        request_intel = mock_post_request.call_args.kwargs['request_intel']
        self.assertEqual(request_intel.json_data['tools'][0]['function']['name'], 'echo')
        self.assertEqual(request_intel.json_data['tool_choice'], 'auto')
        self.assertNotIn('response_format', request_intel.json_data)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_keeps_response_format_without_tools(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        connector = self.make_connector(intel_class=AnswerIntel)

        connector.prompt_to_intel(prompt='Hi')

        request_intel = mock_post_request.call_args.kwargs['request_intel']
        self.assertIn('response_format', request_intel.json_data)
        self.assertNotIn('tools', request_intel.json_data)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_returns_tool_calls_intel(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = tool_call_response(
            'echo', '{"text": "hi"}', content='Echos are coming.'
        )

        connector = self.make_connector(intel_class=AnswerIntel)

        result = connector.prompt_to_intel(
            prompt='Hi', tools=[EchoTool], replace_message_history=True
        )

        self.assertIsInstance(result, ToolCallsIntel)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 'call_1')
        self.assertEqual(result[0].name, 'echo')
        self.assertEqual(result[0].arguments, '{"text": "hi"}')
        self.assertEqual(result.summary, 'Echos are coming.')

        last_message = connector.request_body.messages[-1]
        self.assertEqual(last_message.role, 'assistant')
        self.assertEqual(last_message.tool_calls[0]['function']['name'], 'echo')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_rejects_both_intel_class_and_intel_object(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        connector = self.make_connector()

        with self.assertRaises(LlmCriticalError):
            connector.prompt_to_intel(
                prompt='Hi', intel_class=AnswerIntel, intel_object=AnswerIntel(text='x')
            )

        self.assertEqual(mock_post_request.call_count, 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_rejects_missing_intel_class(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        connector = self.make_connector()

        with self.assertRaises(LlmCriticalError):
            connector.prompt_to_intel(prompt='Hi')

        self.assertEqual(mock_post_request.call_count, 0)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_prompt_to_intel_uses_constructor_intel_class_when_none_given(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        connector = self.make_connector(intel_class=AnswerIntel)

        result = connector.prompt_to_intel(prompt='Hi')

        self.assertIsInstance(result, AnswerIntel)

    def test_has_retry_attempts_available_tracks_attempts(self) -> None:
        connector = self.make_connector()

        self.assertTrue(connector.has_retry_attempts_available)

        connector.prompt_retry_attempt = 1
        self.assertTrue(connector.has_retry_attempts_available)

        connector.prompt_retry_attempt = 2
        self.assertFalse(connector.has_retry_attempts_available)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_reset_clears_request_body_messages(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.return_value = content_response('{"text": "Hello"}')

        connector = self.make_connector(intel_class=AnswerIntel)
        connector.prompt_to_intel(prompt='Hi')
        self.assertGreater(len(connector.request_body.messages), 0)

        connector.reset()

        self.assertEqual(len(connector.request_body.messages), 0)


class TestExtractCodeFenceJsonBody(TestCase):
    def test_single_fence_with_valid_json_returns_body(self) -> None:
        response = 'Preamble line.\n```javascript\n{"text": "hi"}\n```'

        self.assertEqual(_extract_code_fence_json_body(response), '{"text": "hi"}')

    def test_single_tilde_fence_with_valid_json_returns_body(self) -> None:
        response = '~~~json\n{"text": "hi"}\n~~~'

        self.assertEqual(_extract_code_fence_json_body(response), '{"text": "hi"}')

    def test_no_fence_returns_none(self) -> None:
        self.assertIsNone(_extract_code_fence_json_body('{"text": "hi"}'))

    def test_multiple_fences_returns_none(self) -> None:
        response = '```json\n{"text": "hi"}\n```\n```\nmore\n```'

        self.assertIsNone(_extract_code_fence_json_body(response))

    def test_fence_with_invalid_json_returns_none(self) -> None:
        response = '```python\nprint("hello")\n```'

        self.assertIsNone(_extract_code_fence_json_body(response))
