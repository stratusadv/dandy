from unittest import TestCase

from dandy.processor.processor import BaseProcessor
from dandy.processor.map.map import Map
from dandy.processor.map.exceptions import MapCriticalException


class TestMap(TestCase):
    def test_map_import(self):
        self.assertTrue(type(Map) is type(BaseProcessor))

    def test_invalid_map(self):
        with self.assertRaises(MapCriticalException):
            _ = Map(
                mapping_keys_description='Numbers to a String',
                mapping={
                    123: 'this map is invalid as it needs string keys'
                }
            )
