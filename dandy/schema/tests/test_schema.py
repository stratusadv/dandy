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
        print(self.person_1)
        print(self.person_2)

