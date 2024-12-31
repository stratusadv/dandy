from unittest import TestCase
from dandy.debug.debug import DebugRecorder
from example.pirate.world.intelligence.bots.ocean_selection_llm_bot import OceanSelectionLlmBot
from example.pirate.world.datasets import OCEANS

class TestDebug(TestCase):
    def test_debug_recorder(self):
        DEBUG_RECORDING_NAME = 'test'

        DebugRecorder.start_recording(DEBUG_RECORDING_NAME)

        _ = OceanSelectionLlmBot.process('Select the Ocean with the biggest islands', OCEANS)

        DebugRecorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(DebugRecorder.to_html_str(DEBUG_RECORDING_NAME) != '')

    def test_no_event_debug_recording(self):
        DEBUG_RECORDING_NAME = 'test_empty'

        DebugRecorder.start_recording(DEBUG_RECORDING_NAME)
        DebugRecorder.stop_recording(DEBUG_RECORDING_NAME)

        self.assertTrue(DebugRecorder.to_html_str(DEBUG_RECORDING_NAME) != '')

