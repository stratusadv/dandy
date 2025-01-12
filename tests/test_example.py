from unittest import TestCase

from dandy.debug.debug import DebugRecorder
from example.pirate.intelligence.workflow.pirate_story_workflow import PirateStoryWorkflow


class TestExample(TestCase):
    def setUp(self):
        self.pirate_story = ''

    def test_pirate_example(self):
        self.pirate_story = PirateStoryWorkflow.process('N/A')

        if self.pirate_story != '':
            self.assertTrue(True)
        else:
            self.assertTrue(False)
