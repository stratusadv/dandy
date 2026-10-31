from pathlib import Path
import json
import tempfile
from unittest import TestCase

from dandy.shared.constants import RECORDING_POSTFIX_NAME
from dandy.application.bot.bot import Bot
from dandy.domain.intel.intel import BaseIntel
from dandy.infrastructure.recorder.decorators import (
    recorder_to_html_file,
    recorder_to_json_file,
    recorder_to_markdown_file,
)
from dandy.infrastructure.recorder.diligence_events import recorder_add_llm_diligence_event
from dandy.infrastructure.recorder.events import Event, EventType, EventStore, EventAttribute
from dandy.infrastructure.recorder.exceptions import RecorderCriticalError
from dandy.infrastructure.recorder.recorder import Recorder
from tests.consts import live_llm_test

RENDERER_AND_EXTENSIONS = (('html', '.html'), ('json', '.json'), ('markdown', '.md'))

RECORDING_NAME = 'test_recorder'

RECORDING_OUTPUT_FILE_PATH = Path(
    Recorder.get_default_recording_path(), f'{RECORDING_NAME}{RECORDING_POSTFIX_NAME}'
)


def get_capital_intel(country: str) -> BaseIntel:
    capital_city_intel = Bot().llm.prompt_to_intel(
        prompt=f'Please tell me just the name only of the city that is the capital of {country}?'
    )

    return Bot().llm.prompt_to_intel(
        prompt=f'Please describe the following city: {capital_city_intel.text}'
    )


class TestRecorder(TestCase):
    @classmethod
    def setUpClass(cls):
        for _, extension in RENDERER_AND_EXTENSIONS:
            if Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).is_file():
                Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).unlink()

    @live_llm_test
    def test_recorder(self):

        Recorder.start_recording(RECORDING_NAME)

        _ = get_capital_intel('Canada')

        Recorder.stop_recording(RECORDING_NAME)

        self.assertNotEqual(Recorder.to_html_str(RECORDING_NAME), '')

    @live_llm_test
    def test_record_to_html_file_decorator(self):
        @recorder_to_html_file(RECORDING_NAME)
        def html_function():
            _ = get_capital_intel('Canada')

        html_function()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.html'), 'r') as f:
            self.assertNotEqual(f.read(), '')

    @live_llm_test
    def test_record_to_json_file_decorator(self):
        @recorder_to_json_file(RECORDING_NAME)
        def json_function():
            _ = get_capital_intel('Canada')

        json_function()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.json'), 'r') as f:
            self.assertNotEqual(f.read(), '')

    @live_llm_test
    def test_record_to_md_file_decorator(self):
        @recorder_to_markdown_file(RECORDING_NAME)
        def markdown_function():
            _ = get_capital_intel('Canada')

        markdown_function()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.md'), 'r') as f:
            self.assertNotEqual(f.read(), '')

    def test_no_event_recording(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        self.assertNotEqual(Recorder.to_html_str(RECORDING_NAME), '')

    @live_llm_test
    def test_recording_to_str(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = get_capital_intel('Canada')

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, _ in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_str')
            self.assertNotEqual(render_method(RECORDING_NAME), '')
            self.assertIsNotNone(render_method(RECORDING_NAME))

    @live_llm_test
    def test_recorder_to_file_with_emoji(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = Bot().llm.prompt_to_intel(
            # This another prompt that seems to freeze the LLM indefinitely !!!
            # prompt='How many countries are in the 🌎? please respond with emojis!',
            prompt='How many countries are in the 🌎? please respond with numbers and emojis!'
        )

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, extension in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_file')

            render_method(RECORDING_NAME, Recorder.get_default_recording_path())

            with open(
                RECORDING_OUTPUT_FILE_PATH.with_suffix(extension), 'r', encoding='utf-8'
            ) as f:
                self.assertNotEqual(f.read(), '')

    def test_invalid_recorder_name_throws_critical_exception(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        Recorder.check_recording_is_valid(RECORDING_NAME)

        invalid_recorder_name = f'invalid_{RECORDING_NAME}'

        with self.assertRaises(RecorderCriticalError):
            Recorder.check_recording_is_valid(invalid_recorder_name)


class TestRecorderHermetic(TestCase):
    def setUp(self) -> None:
        self.recording_name = 'hermetic_recording'

    def tearDown(self) -> None:
        if self.recording_name in Recorder.recordings:
            Recorder.delete_recording(self.recording_name)

    def make_event(
        self, event_id: str, event_type: EventType = EventType.SUCCESS, token_usage: int = 0
    ) -> Event:
        return Event(
            id=event_id,
            object_name='HermeticBot',
            callable_name='process',
            type=event_type,
            token_usage=token_usage,
        )

    def test_start_stop_recording_collects_events(self) -> None:
        Recorder.start_recording(self.recording_name)
        Recorder.add_event(self.make_event('evt-1'))
        Recorder.add_event(self.make_event('evt-2', EventType.FAILURE, token_usage=7))
        Recorder.stop_recording(self.recording_name)

        recording = Recorder.get_recording(self.recording_name)
        self.assertFalse(recording.is_running)
        self.assertEqual(recording.event_count, 2)
        self.assertEqual(recording.token_usage, 7)

        self.assertIn('HermeticBot', Recorder.to_html_str(self.recording_name))

        json_payload = json.loads(Recorder.to_json_str(self.recording_name))
        self.assertEqual(json_payload['event_count'], 2)
        self.assertEqual(len(json_payload['event_store']['events']), 2)

        self.assertIn('HermeticBot', Recorder.to_markdown_str(self.recording_name))

    def test_add_event_is_no_op_when_nothing_running(self) -> None:
        Recorder.add_event(self.make_event('evt-solo'))

        if self.recording_name in Recorder.recordings:
            self.assertEqual(Recorder.get_recording(self.recording_name).event_store.event_count, 0)

    def test_diligence_event_builder_records_event(self) -> None:
        Recorder.start_recording(self.recording_name)

        recorder_add_llm_diligence_event(
            event_id='evt-diligence',
            diligence_name='StopWordRemoval',
            event_attributes=[EventAttribute(key='removed', value=3)],
        )

        Recorder.stop_recording(self.recording_name)

        recording = Recorder.get_recording(self.recording_name)
        self.assertEqual(recording.event_count, 1)

        event = recording.event_store.events[0]
        self.assertEqual(event.id, 'evt-diligence')
        self.assertEqual(event.object_name, 'LLM Diligence')
        self.assertEqual(event.callable_name, 'StopWordRemoval')
        self.assertEqual(event.type, EventType.OTHER)
        self.assertEqual(event.attributes[0].key, 'removed')
        self.assertEqual(event.attributes[0].value, 3)

    def test_is_recording_reflects_running_recordings(self) -> None:
        Recorder.start_recording(self.recording_name)

        self.assertTrue(Recorder.is_recording())

        Recorder.stop_recording(self.recording_name)
        self.assertFalse(Recorder.get_recording(self.recording_name).is_running)

    def test_check_recording_is_valid_missing_raises(self) -> None:
        with self.assertRaises(RecorderCriticalError) as context:
            Recorder.check_recording_is_valid('never_started_recording')

        self.assertIn('does not exist', str(context.exception))

    def test_delete_recording_removes_it(self) -> None:
        Recorder.start_recording(self.recording_name)

        Recorder.delete_recording(self.recording_name)

        with self.assertRaises(RecorderCriticalError):
            Recorder.check_recording_is_valid(self.recording_name)

    def test_stop_recording_missing_raises(self) -> None:
        with self.assertRaises(RecorderCriticalError):
            Recorder.stop_recording('never_started_recording')

    def test_invalid_renderer_raises(self) -> None:
        Recorder.start_recording(self.recording_name)

        with self.assertRaises(RecorderCriticalError) as context:
            Recorder.to_file(self.recording_name, 'bogus', Path(tempfile.gettempdir()))

        self.assertIn('does not exist', str(context.exception))

    def test_to_file_renders_each_renderer(self) -> None:
        Recorder.start_recording(self.recording_name)
        Recorder.add_event(self.make_event('evt-1'))
        Recorder.stop_recording(self.recording_name)

        with tempfile.TemporaryDirectory() as temp_dir:
            recording = Recorder.get_recording(self.recording_name)

            for renderer in ('html', 'json', 'markdown'):
                extension = Recorder.renderers[renderer](recording=recording).file_extension

                Recorder.to_file(self.recording_name, renderer, Path(temp_dir))

                file_name = f'{self.recording_name}{RECORDING_POSTFIX_NAME}.{extension}'
                file_path = Path(temp_dir, file_name)
                self.assertTrue(file_path.is_file())
                self.assertNotEqual(file_path.read_text(encoding='utf-8'), '')

    def test_event_store_calculates_run_times_and_totals(self) -> None:
        event_store = EventStore()
        first_event = self.make_event('evt-1', token_usage=3)
        second_event = self.make_event('evt-2', token_usage=4)
        second_event.start_time = first_event.start_time + 0.5

        event_store.add_event(first_event)
        event_store.add_event(second_event)

        self.assertEqual(event_store.event_count, 2)
        self.assertEqual(first_event.run_time_seconds, 0.0)
        self.assertAlmostEqual(second_event.run_time_seconds, 0.5)
        self.assertAlmostEqual(event_store.events_total_run_time, 0.5)
        self.assertEqual(event_store.events_total_token_usage, 7)

    def test_event_add_attribute_is_chainable(self) -> None:
        event = self.make_event('evt-1')

        result = event.add_attribute('Key', 'Value', is_dropdown=True).add_attribute('Other', 2)

        self.assertIs(result, event)
        self.assertEqual(event.attributes[0].key, 'Key')
        self.assertTrue(event.attributes[0].is_dropdown)
        self.assertEqual(event.attributes[1].value, 2)

    def test_recorder_file_decorator_renders_file_and_cleans_up(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:

            @recorder_to_html_file(path=Path(temp_dir))
            def decorated_function() -> str:
                Recorder.add_event(
                    Event(
                        id='evt-1', object_name='Decorated', callable_name='run', type=EventType.RUN
                    )
                )
                return 'done'

            self.assertEqual(decorated_function(), 'done')

            derived_name = (
                str(decorated_function.__qualname__)
                .replace('.', '_')
                .replace('<', '')
                .replace('>', '')
                .lower()
            )
            file_path = Path(temp_dir, f'{derived_name}{RECORDING_POSTFIX_NAME}.html')
            self.assertTrue(file_path.is_file())
            self.assertNotEqual(file_path.read_text(encoding='utf-8'), '')
            self.assertNotIn(derived_name, Recorder.recordings)
