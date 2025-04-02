from pathlib import Path
from unittest import TestCase

from dandy.constants import RECORDER_OUTPUT_DIRECTORY, RECORDING_POSTFIX_NAME
from dandy.recorder.recorder import Recorder, _DEFAULT_RECORDER_OUTPUT_PATH
from dandy.llm import LlmBot

RENDERER_AND_EXTENSIONS = (
    ('html', '.html'),
    ('json', '.json'),
    ('markdown', '.md'),
)

RECORDING_NAME = 'test_recorder'

RECORDING_OUTPUT_FILE_PATH = Path(
    _DEFAULT_RECORDER_OUTPUT_PATH,
    f'{RECORDING_NAME}{RECORDING_POSTFIX_NAME}',
)


class TestRecorder(TestCase):
    def test_recorder(self):

        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_str('html', RECORDING_NAME) != '')

    def test_no_event_recording(self):
        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_str('html', RECORDING_NAME) != '')

    def test_recording_to_str(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, _ in RENDERER_AND_EXTENSIONS:
            self.assertTrue(Recorder.to_str(renderer, RECORDING_NAME) != '')

    def test_recorder_to_file(self):
        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        for renderer, extension in RENDERER_AND_EXTENSIONS:
            Recorder.to_file(
                renderer,
                RECORDING_NAME,
            )

            with open(RECORDING_OUTPUT_FILE_PATH.with_suffix(extension), 'r') as f:
                self.assertTrue(f.read() != '')
