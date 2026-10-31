from copy import deepcopy
from typing import Callable
from unittest import TestCase, mock

from dandy.application.agent.agent import Agent
from dandy.domain.request.request import LlmRequestBody
from dandy.infrastructure.http.intel import HttpResponseIntel
from tests.application.agent.intelligence.llm_responses import content_response, tool_call_response
from tests.application.skill.intelligence.skills import NotesSkill, WeatherSkill
from tests.application.tool.intelligence.tools import ToolBot


def make_fake_request_to_response(
    responses: list[HttpResponseIntel],
) -> tuple[list[dict], Callable[..., HttpResponseIntel]]:
    """Record a deep copy of each request body as the connector mutates one shared."""
    recorded: list[dict] = []
    queue = list(responses)

    def fake_request_to_response(request_intel: LlmRequestBody) -> HttpResponseIntel:
        recorded.append(deepcopy(request_intel.json_data))
        return queue.pop(0)

    return recorded, fake_request_to_response


def request_tool_names(body: dict) -> list[str]:
    return [tool['function']['name'] for tool in body.get('tools') or []]


def message_text(message: dict) -> str:
    content = message.get('content')

    if isinstance(content, list):
        return ''.join(part.get('text') or '' for part in content)

    return content or ''


def system_text(body: dict) -> str:
    return message_text(body['messages'][0])


class TestAgentPassiveSkills(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_passive_skill_metadata_in_first_turn_system_message(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        recorded, fake = make_fake_request_to_response(
            [content_response('{"text": "It is sunny.", "done": true}')]
        )
        mock_post_request.side_effect = fake

        agent = Agent(ToolBot(), skills=[WeatherSkill])
        agent.turn('What is the weather in Austin?')

        first_tools = request_tool_names(recorded[0])
        self.assertIn('activate_skill', first_tools)
        self.assertNotIn('weather_current', first_tools)

        passive_line = 'weather: Get current weather. Use when the user asks about the weather.'
        self.assertIn(passive_line, system_text(recorded[0]))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_passive_skill_activation_persists_across_turns(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        recorded, fake = make_fake_request_to_response(
            [
                tool_call_response('activate_skill', '{"name": "weather"}'),
                content_response('{"text": "It is sunny.", "done": false}'),
                content_response('{"text": "Also sunny.", "done": true}'),
            ]
        )
        mock_post_request.side_effect = fake

        agent = Agent(ToolBot(), skills=[WeatherSkill])
        agent.turn('What is the weather in Austin?')
        agent.turn('And in Dallas?')

        second_turn_tools = request_tool_names(recorded[2])
        self.assertIn('weather_current', second_turn_tools)
        self.assertNotIn('activate_skill', second_turn_tools)

        second_turn_messages = recorded[2]['messages']
        tool_texts = [
            message_text(message) for message in second_turn_messages if message['role'] == 'tool'
        ]
        self.assertTrue(
            any('Answer weather questions using the weather tool.' in text for text in tool_texts)
        )

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_clear_resets_skill_activation(self, mock_post_request: mock.MagicMock) -> None:
        recorded, fake = make_fake_request_to_response(
            [
                tool_call_response('activate_skill', '{"name": "weather"}'),
                content_response('{"text": "It is sunny.", "done": false}'),
                content_response('{"text": "Fresh start.", "done": true}'),
            ]
        )
        mock_post_request.side_effect = fake

        agent = Agent(ToolBot(), skills=[WeatherSkill])
        agent.turn('What is the weather in Austin?')
        agent.clear()

        result = agent.turn('And in Dallas?')

        self.assertEqual(result.text, 'Fresh start.')

        post_clear_tools = request_tool_names(recorded[2])
        self.assertIn('activate_skill', post_clear_tools)
        self.assertNotIn('weather_current', post_clear_tools)


class TestAgentActiveSkills(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_active_skill_tools_and_prompt_from_first_turn(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        recorded, fake = make_fake_request_to_response(
            [content_response('{"text": "Saved.", "done": true}')]
        )
        mock_post_request.side_effect = fake

        agent = Agent(ToolBot(), skills=[NotesSkill])
        agent.turn('Save a note.')

        first_tools = request_tool_names(recorded[0])
        self.assertIn('notes_save', first_tools)
        self.assertIn('notes_recall', first_tools)
        self.assertNotIn('activate_skill', first_tools)

        skill_prompt = 'Store notes with notes_save and find them with notes_recall.'
        self.assertIn(skill_prompt, system_text(recorded[0]))
