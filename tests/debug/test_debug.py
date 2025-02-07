from unittest import TestCase

from dandy.debug.debug import DebugRecorder
from dandy.contrib.llm.bots.selector_llm_bot import SelectorLlmBot
from dandy.llm import Prompt


class TestDebug(TestCase):
    def test_debug_recorder(self):
        DEBUG_RECORDING_NAME = 'test'

        DebugRecorder.start_recording(DEBUG_RECORDING_NAME)

        _ = SelectorLlmBot.process(Prompt('I would like a good letter'), ['a', 'b', 'r'])

        DebugRecorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(DebugRecorder.to_html_str(DEBUG_RECORDING_NAME) != '')

    def test_no_event_debug_recording(self):
        DEBUG_RECORDING_NAME = 'test_empty'

        DebugRecorder.start_recording(DEBUG_RECORDING_NAME)
        DebugRecorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(DebugRecorder.to_html_str(DEBUG_RECORDING_NAME) != '')

    def test_debug_recording_json_to_str(self):
        DEBUG_RECORDING_NAME = 'test_json'

        DebugRecorder.start_recording(DEBUG_RECORDING_NAME)

        _ = SelectorLlmBot.process(Prompt('I would like a good letter'), ['a', 'b', 'r'])

        DebugRecorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(DebugRecorder.to_json_str(DEBUG_RECORDING_NAME) != '')

