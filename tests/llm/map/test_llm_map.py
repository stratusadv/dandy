from unittest import TestCase, mock

from faker import Faker

from dandy.llm import BaseLlmMap
from dandy.llm.exceptions import LlmRecoverableException
from dandy.map import Map
from dandy.map.exceptions import MapRecoverableException
from dandy.recorder import recorder_to_html_file
from tests.decorators import nines_testing
from tests.llm.map.maps import FunLlmMap, DragonLlmMap, AdventureGameLlmMap, NestedBirdMap


class TestLlmMap(TestCase):
    def test_llm_map(self):
        values = FunLlmMap.process('I really like my pet dog and hope to get another one', 2)

        self.assertEqual(2, len(values))
        self.assertIn(391, values)
        self.assertIn(782, values)

    def test_seperated_nested_llm_map(self):
        values = AdventureGameLlmMap.process('The player goes left, and is carrying only a bucket on the adventure.', 1)

        self.assertEqual(1, len(values))
        self.assertEqual(DragonLlmMap.map['The player is packing other stuff'], values[0])

    def test_combined_nested_llm_map(self):
        values = NestedBirdMap.process('I am a black bird from the famous edgar allen poe poem', 1)

        self.assertEqual(1, len(values))
        self.assertEqual(NestedBirdMap.map['the bird is dark colored']['it is a raven'], values[0])

    @nines_testing()
    def test_big_user_llm_map(self):
        fake = Faker()

        pk = 976

        user_dictionary = {}

        for _ in range(fake.random_int(min=100, max=500)):
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

    @mock.patch('dandy.core.http.service.BaseHttpService.post_request')
    def test_no_keys_llm_map_retry(self, mock_post_request: mock.MagicMock):
        mock_post_request.return_value = {
                'message': {
                    'content': '{"keys": []}',
                }
            }

        with self.assertRaises(MapRecoverableException):
            value = FunLlmMap.process('I really like my pet dog and hope to get another one', 2)

    @mock.patch('dandy.core.http.service.BaseHttpService.post_request')
    def test_to_many_keys_llm_map_retry(self, mock_post_request: mock.MagicMock):
        mock_post_request.return_value = {
                'message': {
                    'content': '{"keys": ["1", "2", "3", "4"]}',
                }
            }

        with self.assertRaises(MapRecoverableException):
            value = FunLlmMap.process('I really like my pet dog and hope to get another one', 2)
