import json
from unittest import TestCase

from docutils.nodes import title

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
        
        book_dict = BookIntel(user_input='The Book').model_dump(exclude={'characters': {'first_name', 'last_name'}, 'world': True})
        
        print(json_schema)
        
        self.assertNotIn('characters', json_schema['properties'])
