from unittest import TestCase

from faker import Faker

from dandy.llm import BaseLlmMap
from dandy.map import Map
from dandy.recorder import recorder_to_html_file
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
        self.assertEqual(DragonLlmMap.map['The player did not bring a sword'], values[0])

    def test_combined_nested_llm_map(self):
        values = NestedBirdMap.process('I am a black bird from the famous edgar allen poe poem', 1)

        self.assertEqual(1, len(values))
        self.assertEqual(NestedBirdMap.map['the bird is dark colored']['it is a raven'], values[0])

    @recorder_to_html_file('test_big_user_llm_map')
    def test_big_user_llm_map(self):
        fake = Faker()

        pk = 976

        user_dictionary = {}

        for _ in range(fake.random_int(min=1000, max=1200)):
            pk += fake.random_int(min=5, max=50)
            user_dictionary[f'{fake.unique.name()}'] = pk

        class UserLlmMap(BaseLlmMap):
            map_keys_description = 'Employee First and Last Names'
            map = Map(user_dictionary)

        name = fake.random_element(user_dictionary.keys())

        values = UserLlmMap.process(
            f'I am looking for {name}',
        )

        self.assertEqual(
            name,
            {val: key for key, val in user_dictionary.items()}[values[0]]
        )
