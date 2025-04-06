from pathlib import Path
from unittest import TestCase

from dandy.constants import RECORDING_POSTFIX_NAME
from dandy.llm import LlmBot
from dandy.recorder import recorder_to_html_file
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


class TestRecorder(TestCase):
    def setUp(self):
        for _, extension in RENDERER_AND_EXTENSIONS:
            if Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).is_file():
                Path(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension)).unlink()

    def test_recorder(self):

        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_record_to_html_file_decorator(self):
        @recorder_to_html_file(RECORDING_NAME)
        def func():
            _ = LlmBot.process('How many countries are in the world?')

        func()

        with open(RECORDING_OUTPUT_FILE_PATH.with_suffix('.html'), 'r') as f:
            self.assertTrue(f.read() != '')

    def test_no_event_recording(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_recording_to_str(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, _ in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_str')
            self.assertTrue(render_method(RECORDING_NAME) != '')
            self.assertTrue(render_method(RECORDING_NAME) is not None)

    def test_recorder_to_file(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, extension in RENDERER_AND_EXTENSIONS:
            render_method = getattr(Recorder, f'to_{renderer}_file')

            render_method(
                RECORDING_NAME,
                DEFAULT_RECORDER_OUTPUT_PATH,
            )

            with open(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension), 'r') as f:
                self.assertTrue(f.read() != '')
