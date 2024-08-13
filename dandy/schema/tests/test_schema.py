import json
from unittest.case import TestCase

from dandy.schema.tests.schemas import PersonSchema


class TestSchema(TestCase):
    def setUp(self):
        self.person_1 = PersonSchema()
        self.person_2 = PersonSchema()

        PersonSchema.to_json_with_types()

        self.person_1.first_name = 'Fred'
        self.person_1.last_name = 'Flintstone'

        self.person_2.first_name = 'Barney'
        self.person_2.last_name = 'Rubble'

    def tearDown(self):
        pass

    def test_schema(self):
        self.assertEqual(self.person_1.first_name, 'Fred')

    def test_json_type_schema(self):
        person_dict = json.loads(PersonSchema.to_json_with_types())
        self.assertEqual(person_dict['first_name'], 'string')
