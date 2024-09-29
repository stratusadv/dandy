from unittest import TestCase
from dandy.debug.debug import DebugRecorder
from example.pirate.world.intelligence.bots.ocean_selection_llm_bot import OceanSelectionLlmBot
from example.pirate.world.datasets import OCEANS

class TestDebug(TestCase):
    def test_debug_recorder(self):
        DebugRecorder.start_recording('test')

        _ = OceanSelectionLlmBot.process('Select the Ocean with the biggest islands', OCEANS)

        DebugRecorder.stop_recording('test')

        self.assertTrue(DebugRecorder.to_html_str('test') != '')