from unittest import TestCase, mock

from dandy.application.agent.agent import Agent
from dandy.application.bot.bot import Bot
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.request.exceptions import LlmCriticalError
from dandy.shared.exceptions import DandyError
from dandy.infrastructure.http.intel import HttpResponseIntel
from dandy.infrastructure.llm.config import LlmConfig


class TestSetConfigNamedSwitch(TestCase):
    def test_named_switch_changes_config(self) -> None:
        bot = Bot()

        self.assertEqual(bot.llm.config.name, 'DEFAULT')
        self.assertEqual(bot.llm.config.context_size, 65536)

        bot.llm.set_config('THINKING')

        self.assertEqual(bot.llm.config.name, 'THINKING')
        self.assertEqual(bot.llm_config, 'THINKING')
        self.assertEqual(bot.llm.config.context_size, 262144)
        self.assertEqual(bot.llm.options.max_completion_tokens, 13107)

    def test_set_config_returns_the_live_config(self) -> None:
        bot = Bot()

        llm_config = bot.llm.set_config('THINKING')

        self.assertIs(bot.llm.config, llm_config)

    def test_named_switch_preserves_history(self) -> None:
        bot = Bot()

        bot.llm.messages.add_message(role='user', text='Remember this.')
        history_before = bot.llm.messages

        bot.llm.set_config('THINKING')

        self.assertIs(bot.llm.messages, history_before)
        self.assertEqual(len(bot.llm.messages), 1)
        self.assertEqual(bot.llm.messages[0].text_content, 'Remember this.')

    def test_set_config_unknown_name_raises(self) -> None:
        bot = Bot()

        with self.assertRaises(DandyError):
            bot.llm.set_config('NOPE')

    def test_failed_set_config_leaves_config_unchanged(self) -> None:
        bot = Bot()

        bot.llm.set_config('THINKING')

        with self.assertRaises(LlmCriticalError):
            bot.llm.set_config('DEFAULT', temperature=9.0)

        self.assertEqual(bot.llm.config.name, 'THINKING')
        self.assertEqual(bot.llm_config, 'THINKING')


class TestSetConfigOverrides(TestCase):
    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_overrides_reach_the_wire(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200, json_data={'choices': [{'message': {'content': '{"text": "ok"}'}}]}
        )

        bot = Bot()

        bot.llm.set_config(
            'DEFAULT',
            host='https://alt.example',
            port=8443,
            api_key='sk-test',
            model='gpt-override',
            context_size=120000,
            temperature=0.2,
        )

        response = bot.llm.prompt_to_intel(prompt='Hello!', intel_class=DefaultIntel)

        self.assertIsInstance(response, DefaultIntel)

        request_intel = mock_post_request.call_args.kwargs['request_intel']

        self.assertEqual(request_intel.url.host, 'https://alt.example')
        self.assertEqual(request_intel.url.port, 8443)
        self.assertEqual(request_intel.bearer_token, 'sk-test')
        self.assertEqual(request_intel.headers['Authorization'], 'Bearer sk-test')
        self.assertEqual(request_intel.json_data['model'], 'gpt-override')
        self.assertEqual(request_intel.json_data['temperature'], 0.2)
        self.assertEqual(bot.llm.config.context_size, 120000)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_in_place_config_changes_reach_wire(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.return_value = HttpResponseIntel(
            status_code=200, json_data={'choices': [{'message': {'content': '{"text": "ok"}'}}]}
        )

        bot = Bot()

        bot.llm.config.model = 'gpt-inplace'
        bot.llm.config.api_key = 'sk-inplace'

        bot.llm.prompt_to_intel(prompt='Hello!', intel_class=DefaultIntel)

        request_intel = mock_post_request.call_args.kwargs['request_intel']

        self.assertEqual(request_intel.json_data['model'], 'gpt-inplace')
        self.assertEqual(request_intel.headers['Authorization'], 'Bearer sk-inplace')

    def test_unknown_override_raises(self) -> None:
        bot = Bot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.set_config('DEFAULT', temprature=0.5)

    def test_out_of_range_option_override_raises(self) -> None:
        bot = Bot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.set_config('DEFAULT', temperature=9.0)

    def test_wrong_type_override_raises(self) -> None:
        bot = Bot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.set_config('DEFAULT', model=123)

        with self.assertRaises(LlmCriticalError):
            bot.llm.set_config('DEFAULT', port='8443')

    def test_reset_preserves_instance_option_override(self) -> None:
        bot = Bot()

        bot.llm.set_config('DEFAULT', temperature=0.2)
        bot.llm.messages.add_message(role='user', text='Hello!')

        bot.llm.reset()

        self.assertEqual(len(bot.llm.messages), 0)
        self.assertEqual(bot.llm.options.temperature, 0.2)

    def test_reset_preserves_instance_identity_override(self) -> None:
        bot = Bot()

        bot.llm.set_config('DEFAULT', model='gpt-override')

        bot.llm.reset()

        self.assertEqual(bot.llm.config.model, 'gpt-override')


class TestConfigDirectAssignment(TestCase):
    def test_direct_assignment_swaps_config(self) -> None:
        bot = Bot()

        bot.llm.messages.add_message(role='user', text='Hello!')

        bot.llm.config = LlmConfig('THINKING')

        self.assertEqual(bot.llm.config.name, 'THINKING')
        self.assertEqual(bot.llm_config, 'THINKING')
        self.assertEqual(len(bot.llm.messages), 1)

    def test_assignment_rejects_non_llm_config(self) -> None:
        bot = Bot()

        with self.assertRaises(LlmCriticalError):
            bot.llm.config = 'THINKING'

        self.assertEqual(bot.llm.config.name, 'DEFAULT')


class TestConfigInstanceIndependence(TestCase):
    def test_config_change_is_per_instance(self) -> None:
        bot_a = Bot()
        bot_b = Bot()

        bot_a.llm.set_config('THINKING')

        self.assertEqual(bot_a.llm.config.name, 'THINKING')
        self.assertEqual(bot_b.llm.config.name, 'DEFAULT')
        self.assertEqual(bot_b.llm_config, 'DEFAULT')


class TestConfigLiveTracking(TestCase):
    def test_decision_tracks_live_config(self) -> None:
        bot = Bot()

        self.assertIs(bot.llm.decision.decision.llm_config, bot.llm.config)

        bot.llm.set_config('THINKING')

        self.assertIs(bot.llm.decision.decision.llm_config, bot.llm.config)
        self.assertEqual(bot.llm.decision.decision.llm_config.name, 'THINKING')

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_agent_llm_property_tracks_context(self, mock_post_request: mock.MagicMock) -> None:
        content = '{"text": "All done.", "done": true}'

        mock_post_request.return_value = HttpResponseIntel(
            status_code=200, json_data={'choices': [{'message': {'content': content}}]}
        )

        bot = Bot()
        agent = Agent(bot)

        self.assertIs(agent.llm, bot.llm)
        self.assertEqual(agent.max_context_tokens, 65536)

        agent.llm.set_config('THINKING')

        self.assertEqual(agent.max_context_tokens, 65536)

        result = agent.turn('Do the thing')

        self.assertEqual(agent.max_context_tokens, 262144)
        self.assertTrue(result.done)
