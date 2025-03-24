from unittest import TestCase

from pydantic import BaseModel

from dandy.map.map import Map


class TestMap(TestCase):
    def test_map_import(self):
        self.assertTrue(type(Map) is type(BaseModel))

    def test_invalid_map(self):
        with self.assertRaises(ValueError):
            _ = Map({
                123: 'this map is invalid as it needs string keys'
            })

