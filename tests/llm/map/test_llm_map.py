from unittest import TestCase

from dandy.debug import DebugRecorder
from dandy.llm.map.llm_map import BaseLlmMap


class FunLlmMap(BaseLlmMap):
    pass
    map = {
        'someone that needs a laugh and needs clowns': 113,
        'someone is interested in seeing animals': 782,
        'someone looking for something more technical': 927,
        'someone who would be glad to get a free puppies': 391,
    }


class TestMap(TestCase):
    def test_map_validator(self):
        try:
            DebugRecorder.start_recording('test_map')

            choices = FunLlmMap.process('I really like my pet dog and hope to get another one', 2)
            self.assertIn(391, choices)
            self.assertIn(782, choices)

        finally:
            DebugRecorder.stop_recording('test_map')
            DebugRecorder.to_html_file('test_map')

