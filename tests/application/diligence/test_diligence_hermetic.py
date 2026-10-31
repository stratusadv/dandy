from unittest import TestCase, mock

from dandy.application.bot.bot import Bot
from dandy.application.diligence.handler import DiligenceHandler
from dandy.application.diligence.second_pass.diligence import SecondPassRemovalDiligence
from dandy.application.diligence.stop_word_removal.diligence import StopWordRemovalDiligence
from dandy.application.diligence.vowel_removal.diligence import VowelRemovalDiligence
from dandy.domain.intel.intel import BaseIntel
from dandy.infrastructure.http.intel import HttpResponseIntel
from dandy.infrastructure.llm.config import LlmConfig
from dandy.infrastructure.llm.connector import LlmConnector


class AnswerIntel(BaseIntel):
    text: str


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200, json_data={'choices': [{'message': {'content': content}}]}
    )


def make_connector() -> LlmConnector:
    connector = LlmConnector(
        recorder_event_id='diligence-test',
        llm_config=LlmConfig('DEFAULT'),
        intel_class=AnswerIntel,
        system_prompt='System prompt.',
    )
    connector.request_body.messages.add_message(role='system', text='System prompt.')
    connector.request_body.messages.add_message(role='user', text='The big moon orbits the earth.')
    return connector


def message_texts(messages: list[dict], role: str) -> list[str]:
    return [
        content['text']
        for message in messages
        if message['role'] == role
        for content in message['content']
        if content.get('type') == 'text'
    ]


class TestDiligenceTransforms(TestCase):
    def test_remove_stop_words(self) -> None:
        self.assertEqual(
            StopWordRemovalDiligence.remove_stop_words('The big moon orbits the earth.'),
            'big moon orbits earth.',
        )

    def test_remove_vowels(self) -> None:
        self.assertEqual(VowelRemovalDiligence.remove_vowels('Hello World'), 'hll wrld')


class TestDiligenceApply(TestCase):
    def test_stop_word_removal_strips_messages_and_merges_into_system(self) -> None:
        connector = make_connector()
        StopWordRemovalDiligence().activate()
        StopWordRemovalDiligence().apply(connector)

        messages = connector.request_body.messages
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, 'system')
        self.assertEqual(messages[1].text_content, 'big moon orbits earth.')
        # remove_stop_words lowercases the text it strips
        self.assertTrue(messages[0].text_content.startswith('system prompt.'))
        self.assertTrue(messages[0].text_content.endswith('Assume Stop Words'))

    def test_stop_word_removal_prepends_system_when_absent(self) -> None:
        connector = LlmConnector(
            recorder_event_id='diligence-test',
            llm_config=LlmConfig('DEFAULT'),
            intel_class=AnswerIntel,
            system_prompt='System prompt.',
        )
        connector.request_body.messages.add_message(
            role='user', text='The big moon orbits the earth.'
        )

        StopWordRemovalDiligence().apply(connector)

        messages = connector.request_body.messages
        self.assertEqual([message.role for message in messages], ['system', 'user'])
        self.assertEqual(messages[0].text_content, 'Assume Stop Words')

    def test_vowel_removal_strips_messages_and_merges_into_system(self) -> None:
        connector = make_connector()
        connector.request_body.messages[1].content[0].text = 'Hello World'
        VowelRemovalDiligence().activate()
        VowelRemovalDiligence().apply(connector)

        messages = connector.request_body.messages
        self.assertEqual(messages[1].text_content, 'hll wrld')
        self.assertTrue(messages[0].text_content.endswith('Assume Vowels'))

    def test_second_pass_adds_review_prompt_and_requires_new_request(self) -> None:
        connector = make_connector()

        SecondPassRemovalDiligence().apply(connector)

        messages = connector.request_body.messages
        self.assertEqual(messages[-1].role, 'user')
        self.assertIn('Review our conversation', messages[-1].text_content)
        self.assertTrue(SecondPassRemovalDiligence.requires_new_llm_request)
        self.assertFalse(StopWordRemovalDiligence.requires_new_llm_request)


class TestDiligenceHandler(TestCase):
    def test_is_not_activated_when_empty(self) -> None:
        self.assertFalse(DiligenceHandler().is_activated)

    def test_get_diligence_caches_instance(self) -> None:
        handler = DiligenceHandler()

        self.assertIs(
            handler.get_diligence(StopWordRemovalDiligence),
            handler.get_diligence(StopWordRemovalDiligence),
        )

    def test_apply_only_applies_activated_diligences(self) -> None:
        handler = DiligenceHandler()
        handler.get_diligence(StopWordRemovalDiligence).activate()
        handler.get_diligence(VowelRemovalDiligence)

        connector = make_connector()
        handler.apply(connector)

        self.assertEqual(connector.request_body.messages[1].text_content, 'big moon orbits earth.')

    def test_requires_new_llm_request_follows_activated_diligences(self) -> None:
        handler = DiligenceHandler()
        handler.get_diligence(StopWordRemovalDiligence).activate()
        self.assertFalse(handler.requires_new_llm_request)

        handler.get_diligence(SecondPassRemovalDiligence).activate()
        self.assertTrue(handler.requires_new_llm_request)


class TestDiligenceService(TestCase):
    def test_bot_diligence_service_caches_diligence_instances(self) -> None:
        bot = Bot()

        self.assertIs(bot.llm.diligence.stop_word_removal, bot.llm.diligence.stop_word_removal)
        self.assertIs(
            bot.llm.diligence.post_handler.get_diligence(SecondPassRemovalDiligence),
            bot.llm.diligence.second_pass,
        )

    def test_bot_diligence_reset_deactivates(self) -> None:
        bot = Bot()
        bot.llm.diligence.stop_word_removal.activate()
        self.assertTrue(bot.llm.diligence.post_handler.is_activated)

        bot.llm.diligence.reset()

        self.assertFalse(bot.llm.diligence.post_handler.is_activated)

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_stop_word_removal_applies_to_persistent_history(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "moon"}')

        bot = Bot()
        bot.llm.diligence.stop_word_removal.activate()

        result = bot.llm.prompt_to_intel(
            prompt='The big moon orbits the earth.', intel_class=AnswerIntel
        )

        self.assertEqual(result.text, 'moon')
        self.assertEqual(mock_post_request.call_count, 1)

        # Post-diligence runs after the outgoing request, so it shapes the
        # persistent history (visible on the next request), not this one.
        first_request_messages = (
            mock_post_request.call_args_list[0].kwargs['request_intel'].json_data['messages']
        )
        self.assertEqual(
            message_texts(first_request_messages, 'user'), ['The big moon orbits the earth.\n']
        )

        persisted_messages = bot.llm.messages
        self.assertEqual(persisted_messages[1].text_content, 'big moon orbits earth.')
        self.assertTrue(persisted_messages[0].text_content.endswith('Assume Stop Words'))

        bot.llm.prompt_to_intel(prompt='Again?', intel_class=AnswerIntel)
        second_request_messages = (
            mock_post_request.call_args_list[1].kwargs['request_intel'].json_data['messages']
        )
        self.assertIn('big moon orbits earth.', message_texts(second_request_messages, 'user'))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_vowel_removal_applies_to_outgoing_request(
        self, mock_post_request: mock.MagicMock
    ) -> None:
        mock_post_request.return_value = content_response('{"text": "moon"}')

        bot = Bot()
        bot.llm.diligence.vowel_removal.activate()

        bot.llm.prompt_to_intel(prompt='Hello World', intel_class=AnswerIntel)

        messages = mock_post_request.call_args.kwargs['request_intel'].json_data['messages']
        self.assertIn('hll wrld', ' '.join(message_texts(messages, 'user')))
        self.assertIn('Assume Vowels', ' '.join(message_texts(messages, 'system')))

    @mock.patch('dandy.infrastructure.http.connector.HttpConnector.request_to_response')
    def test_second_pass_triggers_a_second_request(self, mock_post_request: mock.MagicMock) -> None:
        mock_post_request.return_value = content_response('{"text": "moon"}')

        bot = Bot()
        bot.llm.diligence.second_pass.activate()

        result = bot.llm.prompt_to_intel(
            prompt='The big moon orbits the earth.', intel_class=AnswerIntel
        )

        self.assertEqual(result.text, 'moon')
        self.assertEqual(mock_post_request.call_count, 2)

        second_messages = (
            mock_post_request.call_args_list[1].kwargs['request_intel'].json_data['messages']
        )
        self.assertEqual(second_messages[-1]['role'], 'user')
        self.assertIn('Review our conversation', second_messages[-1]['content'][0]['text'])
