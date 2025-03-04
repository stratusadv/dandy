import json
from unittest import TestCase

from dandy.intel import BaseIntel
from example.book.intelligence.intel import BookIntel

class TestIntel(TestCase):
    def test_intel(self):
        class TestingIntel(BaseIntel):
            pass

        intel = TestingIntel()
        self.assertIsInstance(intel, TestingIntel)

    def test_intel_inc_ex_json_schema(self):
        json_schema = BookIntel.model_inc_ex_json_schema(exclude={'characters'})
        
        print(json_schema)
        
        self.assertNotIn('characters', json_schema['properties'])
