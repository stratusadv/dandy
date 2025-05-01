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
        self.assertEqual(DragonLlmMap.map['Player did not bring a sword'], values[0])

    def test_combined_nested_llm_map(self):
        values = NestedBirdMap.process('I am a black bird from the famous edgar allen poe poem', 1)

        self.assertEqual(1, len(values))
        self.assertEqual(NestedBirdMap.map['the bird is dark colored']['it is a raven'], values[0])

    @recorder_to_html_file('test_big_user_llm_map')
    def test_big_user_llm_map(self):
        fake = Faker()

        first_name = ''
        pk = 976

        first_name_count = {}

        user_dictionary = {}

        for i in range(fake.random_int(min=100, max=200)):
            first_name = fake.first_name()

            for j in range(fake.random_int(min=3, max=7)):
                first_name_count[first_name] = first_name_count.get(first_name, 0) + 1
                pk += 1

                user_dictionary[f'{first_name} {fake.last_name()}'] = pk

        class UserLlmMap(BaseLlmMap):
            map_keys_description = 'Employee Names'
            map = Map(user_dictionary)

        values = UserLlmMap.process(
            f'I am looking for employee {first_name}',
            10
        )

        print(first_name_count[first_name])

        self.assertEqual(
            first_name_count[first_name],
            len(values)
        )
