from unittest import TestCase

from pydantic import BaseModel

from dandy.map.mapping import Mapping


class TestMap(TestCase):
    def test_map_import(self):
        self.assertTrue(type(Mapping) is type(BaseModel))

    def test_invalid_map(self):
        with self.assertRaises(ValueError):
            _ = Mapping({
                123: 'this map is invalid as it needs string keys'
            })

