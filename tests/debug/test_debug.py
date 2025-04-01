from unittest import TestCase

from dandy.recorder.recorder import Recorder
from dandy.llm import LlmBot


class TestDebug(TestCase):
    def test_debug_recorder(self):
        DEBUG_RECORDING_NAME = 'test'

        Recorder.start_recording(DEBUG_RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(DEBUG_RECORDING_NAME) != '')

    def test_no_event_debug_recording(self):
        DEBUG_RECORDING_NAME = 'test_empty'

        Recorder.start_recording(DEBUG_RECORDING_NAME)
        Recorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(Recorder.to_html_str(DEBUG_RECORDING_NAME) != '')

    def test_debug_recording_json_to_str(self):
        DEBUG_RECORDING_NAME = 'test_json'

        Recorder.start_recording(DEBUG_RECORDING_NAME)

        _ = LlmBot.process('How many countries are in the world?')

        Recorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(Recorder.to_json_str(DEBUG_RECORDING_NAME) != '')

