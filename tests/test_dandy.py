from unittest import TestCase

from dandy.debug.debug import DebugRecorder
from example.pirate.intelligence.workflow.pirate_story_workflow import PirateStoryWorkflow


class TestDandy(TestCase):
    def setUp(self):
        self.pirate_story = ''

    def test_dandy(self):
        try:
            DebugRecorder.start_recording()
            self.pirate_story = PirateStoryWorkflow.process('N/A')

        except:
            import traceback
            traceback.print_exc()

            self.assertTrue(False)

        finally:
            DebugRecorder.stop_recording()
            DebugRecorder.to_html_file()
            print(self.pirate_story)
            if self.pirate_story != '':
                self.assertTrue(True)
            else:
                self.assertTrue(False)
