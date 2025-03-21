from unittest import TestCase

from dandy.debug.decorators import debug_recorder_to_html
from tests.llm.map.maps import FunLlmMap, AdventureGameLlmMap


class TestMap(TestCase):
    def test_map_validator(self):
        choices = FunLlmMap.process('I really like my pet dog and hope to get another one', 2)

        self.assertEqual(2, len(choices))
        self.assertIn(391, choices)
        self.assertIn(782, choices)

    @debug_recorder_to_html('test_map')
    def test_nested_map(self):
        choices = AdventureGameLlmMap.process('The player wants to go left, and has a shovel with them. What will be the outcome?', 1)

        print(choices.items)

        self.assertEqual(1, len(choices))
