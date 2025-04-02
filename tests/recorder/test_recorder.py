from unittest import TestCase

from dandy.recorder.recorder import Recorder
from dandy.llm import LlmBot


class TestRecorder(TestCase):
    def test_recorder(self):
        RECORDING_NAME = 'test'

        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_no_event_recording(self):
        RECORDING_NAME = 'test_empty'

        Recorder.start_recording(RECORDING_NAME)
        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

    def test_recording_json_to_str(self):
        RECORDING_NAME = 'test_json'

        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        self.assertTrue(Recorder.to_json_str(RECORDING_NAME) != '')

    def test_recorder_to_html_file(self):
        RECORDING_NAME = 'test'

        Recorder.start_recording(RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(RECORDING_NAME)

        Recorder.to_html_file(RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(RECORDING_NAME) != '')

