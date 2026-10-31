from copy import deepcopy
from typing import Callable
from unittest import TestCase, mock

from dandy.infrastructure.http.intel import HttpResponseIntel
from dandy.application.bot.bot import Bot
from dandy.domain.request.exceptions import LlmCriticalError
from dandy.domain.request.request import LlmRequestBody
from dandy.domain.tool.tool import BaseTool

from tests.application.tool.intelligence.intel import FinalAnswerIntel
from tests.application.skill.intelligence.skills import NotesSkill, WeatherSkill


class ActiveSkillBot(Bot):
    skills = [NotesSkill]


class PassiveSkillBot(Bot):
    skills = [WeatherSkill]


class CollidingTool(BaseTool):
    name = 'weather_current'
    description = 'A user tool that collides with the weather skill tool.'

    def handle(self, location: str = '') -> str:
        return f'The weather in {location} is sunny.'


def tool_call_response(
    tool_name: str, arguments: str, tool_call_id: str = 'call_1', content: str | None = None
) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': content,
                        'tool_calls': [
                            {
                                'id': tool_call_id,
                                'type': 'function',
                                'function': {'name': tool_name, 'arguments': arguments},
                            }
                        ],
                    }
                }
            ]
        },
    )


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200, json_data={'choices': [{'message': {'content': content}}]}
    )


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


class TestActiveSkillInToolLoop(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_active_skill_tools_and_prompt_from_first_round(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        recorded, fake = make_fake_request_to_response(
            [
                tool_call_response('notes_save', '{"note": "buy milk"}'),
                content_response('{"text": "Saved."}'),
            ]
        )
        mock_post_request.side_effect = fake

        result = ActiveSkillBot().llm.tools.prompt_to_intel(
            prompt='Save a note.', intel_class=FinalAnswerIntel
        )

        self.assertEqual(result.text, 'Saved.')

        first_tools = request_tool_names(recorded[0])
        self.assertIn('notes_save', first_tools)
        self.assertIn('notes_recall', first_tools)
        self.assertNotIn('activate_skill', first_tools)
        self.assertNotIn('response_format', recorded[0])

        skill_prompt = 'Store notes with notes_save and find them with notes_recall.'
        self.assertIn(skill_prompt, system_text(recorded[0]))

        second_messages = recorded[1]['messages']
        tool_messages = [m for m in second_messages if m.get('role') == 'tool']
        self.assertEqual(tool_messages[0]['content'], 'Saved: buy milk')


class TestBotWithoutSkills(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_bot_without_skills_keeps_response_format(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.side_effect = [content_response('{"text": "Hi."}')]

        ActiveSkillBot().llm.prompt_to_intel(prompt='Hi.', intel_class=FinalAnswerIntel)

        body = mock_post_request.call_args.kwargs['request_intel'].json_data
        self.assertIn('response_format', body)
        self.assertNotIn('tools', body)


class TestPassiveSkillActivationInToolLoop(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_passive_skill_activated_mid_loop(self, mock_post_request: mock.MagicMock) -> None:
        recorded, fake = make_fake_request_to_response(
            [
                tool_call_response(
                    'activate_skill', '{"name": "weather"}', tool_call_id='call_act'
                ),
                tool_call_response(
                    'weather_current', '{"location": "Austin"}', tool_call_id='call_cur'
                ),
                content_response('{"text": "Sunny."}'),
            ]
        )
        mock_post_request.side_effect = fake

        result = PassiveSkillBot().llm.tools.prompt_to_intel(
            prompt='What is the weather in Austin?', intel_class=FinalAnswerIntel
        )

        self.assertEqual(result.text, 'Sunny.')

        first_tools = request_tool_names(recorded[0])
        self.assertIn('activate_skill', first_tools)
        self.assertNotIn('weather_current', first_tools)

        passive_line = 'weather: Get current weather. Use when the user asks about the weather.'
        self.assertIn(passive_line, system_text(recorded[0]))

        second_tools = request_tool_names(recorded[1])
        self.assertIn('weather_current', second_tools)
        self.assertNotIn('activate_skill', second_tools)

        second_messages = recorded[1]['messages']
        activation_result = next(
            m
            for m in second_messages
            if m.get('role') == 'tool' and m.get('tool_call_id') == 'call_act'
        )
        self.assertIn(
            'Answer weather questions using the weather tool.', activation_result['content']
        )

        third_messages = recorded[2]['messages']
        weather_result = next(
            m
            for m in third_messages
            if m.get('role') == 'tool' and m.get('tool_call_id') == 'call_cur'
        )
        self.assertEqual(weather_result['content'], 'The current weather in Austin is sunny.')


class TestSkillToolNameCollision(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_user_tool_colliding_with_skill_tool_raises_before_http(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        with self.assertRaises(LlmCriticalError):
            PassiveSkillBot().llm.tools.prompt_to_intel(
                prompt='Weather?', tools=[CollidingTool()], intel_class=FinalAnswerIntel
            )

        self.assertEqual(mock_post_request.call_count, 0)
