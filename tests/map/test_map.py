from unittest import TestCase

from pydantic import BaseModel

from dandy.map.map import Map


class TestMap(TestCase):
    def test_map_import(self):
        self.assertTrue(type(Map) is type(BaseModel))