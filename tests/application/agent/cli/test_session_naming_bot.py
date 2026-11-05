import json
import unittest
from unittest import mock

from dandy.application.agent.cli.intelligence.bots.session_naming_bot import SessionNamingBot
from dandy.application.agent.intel import SessionNameIntel
from dandy.domain.prompt.prompt import Prompt
from dandy.infrastructure.http.intel import HttpRequestIntel, HttpResponseIntel
from dandy.shared.settings.load import get_cli_llm_config


def _content_response(name: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={'choices': [{'message': {'content': json.dumps({'name': name})}}]},
    )


class TestSessionNamingBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = SessionNamingBot()

    def test_process_returns_the_parsed_name(self) -> None:
        with mock.patch(
            'dandy.infrastructure.http.connector.HttpConnector.request_to_response',
            return_value=_content_response('Fixing The Broken Login Flow'),
        ):
            intel = self.bot.process('Fix the login bug')

        self.assertIsInstance(intel, SessionNameIntel)
        self.assertEqual(intel.name, 'Fixing The Broken Login Flow')

    def test_process_accepts_a_prompt(self) -> None:
        with mock.patch(
            'dandy.infrastructure.http.connector.HttpConnector.request_to_response',
            return_value=_content_response('Fixing The Broken Login Flow'),
        ):
            intel = self.bot.process(Prompt().text('Fix the login bug'))

        self.assertEqual(intel.name, 'Fixing The Broken Login Flow')

    def test_naming_bot_uses_the_simple_cli_config(self) -> None:
        self.assertEqual(self.bot.llm_config, get_cli_llm_config('SIMPLE'))

    def test_request_body_contains_the_request_and_strict_json_mode(self) -> None:
        captured_requests = []

        def capture(request_intel: HttpRequestIntel) -> HttpResponseIntel:
            captured_requests.append(request_intel.json_data)
            return _content_response('Fixing The Broken Login Flow')

        with mock.patch(
            'dandy.infrastructure.http.connector.HttpConnector.request_to_response',
            side_effect=capture,
        ):
            self.bot.process('Fix the login bug')

        self.assertEqual(len(captured_requests), 1)
        request_body = captured_requests[0]

        self.assertIsNotNone(request_body['response_format'])
        self.assertNotIn('tools', request_body)

        user_messages = [
            message for message in request_body['messages'] if message['role'] == 'user'
        ]
        self.assertEqual(len(user_messages), 1)
        user_text = ''.join(part.get('text') or '' for part in user_messages[0]['content'])

        self.assertIn('Fix the login bug', user_text)
        self.assertIn('8 to 10 words', user_text)

    def test_second_process_call_starts_a_fresh_conversation(self) -> None:
        captured_requests = []

        def capture(request_intel: HttpRequestIntel) -> HttpResponseIntel:
            captured_requests.append(request_intel.json_data)
            return _content_response('Fixing The Broken Login Flow')

        with mock.patch(
            'dandy.infrastructure.http.connector.HttpConnector.request_to_response',
            side_effect=capture,
        ):
            self.bot.process('Fix the login bug')
            self.bot.reset()
            self.bot.process('Add a dark mode toggle')

        self.assertEqual(len(captured_requests), 2)
        second_messages = captured_requests[1]['messages']
        second_user_messages = [
            message for message in second_messages if message['role'] == 'user'
        ]

        self.assertEqual(len(second_user_messages), 1)
        second_user_text = ''.join(
            part.get('text') or '' for part in second_user_messages[0]['content']
        )
        self.assertIn('Add a dark mode toggle', second_user_text)
        self.assertNotIn('Fix the login bug', second_user_text)


if __name__ == '__main__':
    unittest.main()
