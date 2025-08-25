from pathlib import Path
from unittest import TestCase

from dandy.constants import RECORDING_POSTFIX_NAME
from dandy.bot.bot import Bot
from dandy.intel import BaseIntel
from dandy.recorder import recorder_to_html_file, recorder_to_json_file, \
    recorder_to_markdown_file
from dandy.recorder.exceptions import RecorderCriticalException
from dandy.recorder.recorder import Recorder, DEFAULT_RECORDER_OUTPUT_PATH

RENDERER_AND_EXTENSIONS = (
    ('html', '.html'),
    ('json', '.json'),
    ('markdown', '.md'),
)

RECORDING_NAME = 'test_recorder'

RECORDING_OUTPUT_FILE_PATH = Path(
    DEFAULT_RECORDER_OUTPUT_PATH,
    f'{RECORDING_NAME}{RECORDING_POSTFIX_NAME}',
)


class DefaultIntel(BaseIntel):
    text: str


class TestRecorder(TestCase):
    @classmethod
    def setUpClass(cls):
        for _, extension in RENDERER_AND_EXTENSIONS:
            if Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).is_file():
                Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).unlink()

    def test_recorder(self):

        Recorder.start_recording(RECORDING_NAME)

        _ = Bot().llm.prompt_to_intel(
            prompt='How many countries are in the world?',
            intel_class=DefaultIntel
        )

        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_record_to_html_file_decorator(self):
        @recorder_to_html_file(RECORDING_NAME)
        def func():
            _ = Bot().llm.prompt_to_intel(
                prompt='How many countries are in the world?',
                intel_class=DefaultIntel
            )

        func()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.html'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_record_to_json_file_decorator(self):
        @recorder_to_json_file(RECORDING_NAME)
        def func():
            _ = Bot().llm.prompt_to_intel(
                prompt='How many countries are in the world?',
                intel_class=DefaultIntel
            )

        func()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.json'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_record_to_md_file_decorator(self):
        @recorder_to_markdown_file(RECORDING_NAME)
        def func():
            _ = Bot().llm.prompt_to_intel(
                prompt='How many countries are in the world?',
                intel_class=DefaultIntel
            )

        func()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.md'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_no_event_recording(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_recording_to_str(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = Bot().llm.prompt_to_intel(
            prompt='How many countries are in the world?',
            intel_class=DefaultIntel
        )

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, _ in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_str')
            self.assertTrue(render_method(RECORDING_NAME) != '')
            self.assertTrue(render_method(RECORDING_NAME) is not None)

    def test_recorder_to_file(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = Bot().llm.prompt_to_intel(
            prompt='How many countries are in the world?',
            intel_class=DefaultIntel
        )

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, extension in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_file')

            render_method(
                RECORDING_NAME,
                DEFAULT_RECORDER_OUTPUT_PATH,
            )

            with open(
                    RECORDING_OUTPUT_FILE_PATH.with_suffix(extension),
                    'r',
                    encoding='utf-8'
            ) as f:
                self.assertTrue(f.read() != '')

    def test_recorder_to_file_with_emoji(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = Bot().llm.prompt_to_intel(
            prompt='How many countries are in the 🌎? please respond with emojis!',
            intel_class=DefaultIntel
        )

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, extension in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_file')

            render_method(
                RECORDING_NAME,
                DEFAULT_RECORDER_OUTPUT_PATH,
            )

            with open(
                    RECORDING_OUTPUT_FILE_PATH.with_suffix(extension),
                    'r',
                    encoding='utf-8'
            ) as f:
                self.assertTrue(f.read() != '')

    def test_invalid_recorder_name_throws_critical_exception(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        Recorder.check_recording_is_valid(RECORDING_NAME)

        invalid_recorder_name = f'invalid_{RECORDING_NAME}'
        exception_message = f'Recording "{invalid_recorder_name}" does not exist. Choices are {list(Recorder.recordings.keys())}'

        with self.assertRaises(RecorderCriticalException) as recorder_exception:
            Recorder.check_recording_is_valid(invalid_recorder_name)
