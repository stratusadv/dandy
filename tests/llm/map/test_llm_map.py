from unittest import TestCase

from tests.llm.map.maps import FunLlmMap, DragonLlmMap, AdventureGameLlmMap, NestedBirdMap


class TestMap(TestCase):
    def test_llm_map(self):
        values = FunLlmMap.process('I really like my pet dog and hope to get another one', 2)

        self.assertEqual(2, len(values))
        self.assertIn(391, values)
        self.assertIn(782, values)

    def test_seperated_nested_llm_map(self):
        values = AdventureGameLlmMap.process('The player usually goes left, and has a bucket with them.', 1)

        self.assertEqual(1, len(values))
        self.assertEqual(DragonLlmMap.map['Player did not bring a sword'], values[0])

    def test_combined_nested_llm_map(self):
        values = NestedBirdMap.process('I am a black bird from the famous edgar allen poe poem', 1)

        self.assertEqual(1, len(values))
        self.assertEqual(NestedBirdMap.map['the bird is dark colored']['it is a raven'], values[0])